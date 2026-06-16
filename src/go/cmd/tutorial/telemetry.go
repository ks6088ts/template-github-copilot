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
package tutorial

import (
	"log/slog"
	"os"
	"strconv"

	copilot "github.com/github/copilot-sdk/go"
)

// telemetryConfig builds an OpenTelemetry configuration for the Copilot CLI
// process from environment variables, mirroring the Python tutorials' helper.
//
// It returns nil (telemetry disabled) unless OTEL_EXPORTER_OTLP_ENDPOINT is set,
// so the tutorials behave exactly as before when no collector is running.
//
//   - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP HTTP endpoint (e.g. http://localhost:4318).
//   - OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT: optional bool to capture
//     prompt/response content in spans.
//
// See: https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry
func telemetryConfig() *copilot.TelemetryConfig {
	endpoint := os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
	if endpoint == "" {
		return nil
	}

	cfg := &copilot.TelemetryConfig{
		OTLPEndpoint: endpoint,
		ExporterType: "otlp-http",
	}

	if v, ok := os.LookupEnv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"); ok {
		if b, err := strconv.ParseBool(v); err == nil {
			cfg.CaptureContent = copilot.Bool(b)
		}
	}

	slog.Debug("OpenTelemetry enabled", "endpoint", endpoint)
	return cfg
}

// newClientOptions returns ClientOptions wired with telemetry and, when cliURL is
// non-empty, a URI connection to an already-running Copilot CLI runtime.
//
// Tutorials pass the result to copilot.NewClient so telemetry is enabled
// consistently whether they connect over stdio (cliURL == "") or TCP.
func newClientOptions(cliURL string) *copilot.ClientOptions {
	opts := &copilot.ClientOptions{
		Telemetry: telemetryConfig(),
	}
	if cliURL != "" {
		opts.Connection = copilot.URIConnection{URL: cliURL}
	}
	return opts
}
