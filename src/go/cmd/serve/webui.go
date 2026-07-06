/*
Copyright © 2024 ks6088ts

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
package serve

import (
	"embed"
	"io/fs"
	"net/http"
)

//go:embed webui
var webuiFS embed.FS

// registerWebUI registers the static web UI and OpenAPI spec routes on mux.
//
//   - GET /docs/        — serves the embedded Scalar API reference page.
//   - GET /swagger.yaml — serves the embedded OpenAPI 3.1 spec.
//   - GET /{$}          — redirects the root path to /docs/.
func registerWebUI(mux *http.ServeMux) {
	sub, err := fs.Sub(webuiFS, "webui")
	if err != nil {
		// This can only fail if the embed directive is wrong, which would be a
		// compile-time/init-time programming error rather than a runtime error.
		panic("webui: fs.Sub failed: " + err.Error())
	}

	fileServer := http.FileServerFS(sub)

	// Serve the full /docs/ tree (index.html, scalar.standalone.js, etc.)
	mux.Handle("GET /docs/", http.StripPrefix("/docs/", fileServer))

	// Expose the OpenAPI spec at the root level for convenience.
	mux.HandleFunc("GET /swagger.yaml", func(w http.ResponseWriter, r *http.Request) {
		r.URL.Path = "/swagger.yaml"
		fileServer.ServeHTTP(w, r)
	})

	// Redirect root to the docs UI.
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/docs/", http.StatusFound)
	})
}
