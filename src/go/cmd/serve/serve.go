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
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"mime/multipart"
	"net"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/ks6088ts/template-github-copilot/src/go/cmd/run"
	"github.com/spf13/cobra"
)

// TaskStatus represents the lifecycle state of an async task.
type TaskStatus string

const (
	TaskStatusPending TaskStatus = "pending"
	TaskStatusRunning TaskStatus = "running"
	TaskStatusDone    TaskStatus = "done"
	TaskStatusFailed  TaskStatus = "failed"
)

// Task holds the state of a single Copilot run submitted via the HTTP API.
type Task struct {
	ID          string              `json:"id"`
	Status      TaskStatus          `json:"status"`
	Prompt      string              `json:"prompt,omitempty"`
	Model       string              `json:"model,omitempty"`
	Progress    []run.ProgressEvent `json:"progress,omitempty"`
	Result      string              `json:"result,omitempty"`
	Error       string              `json:"error,omitempty"`
	CreatedAt   time.Time           `json:"created_at"`
	CompletedAt *time.Time          `json:"completed_at,omitempty"`
}

// taskStore is the in-memory store for all submitted tasks.
type taskStore struct {
	mu    sync.RWMutex
	tasks map[string]*Task
}

func newTaskStore() *taskStore {
	return &taskStore{tasks: make(map[string]*Task)}
}

func (s *taskStore) create(prompt, model string) *Task {
	t := &Task{
		ID:        uuid.New().String(),
		Status:    TaskStatusPending,
		Prompt:    prompt,
		Model:     model,
		CreatedAt: time.Now().UTC(),
	}
	s.mu.Lock()
	s.tasks[t.ID] = t
	s.mu.Unlock()
	return t
}

func (s *taskStore) get(id string) (Task, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	t, ok := s.tasks[id]
	if !ok {
		return Task{}, false
	}
	// Return a copy to avoid a data race between the caller reading fields
	// and the background goroutine updating the task concurrently.
	return *t, true
}

func (s *taskStore) update(id string, fn func(*Task)) {
	s.mu.Lock()
	if t, ok := s.tasks[id]; ok {
		fn(t)
	}
	s.mu.Unlock()
}

// taskRequest is the JSON body accepted by POST /tasks.
type taskRequest struct {
	// Prompt is the user message to send to Copilot (required).
	Prompt string `json:"prompt"`
	// Model is the optional model identifier (e.g. "gpt-4o").
	Model string `json:"model,omitempty"`
	// SystemMessage is an optional system/instruction message for the session.
	// Use this to pass the contents of an agents.md file directly.
	SystemMessage string `json:"system_message,omitempty"`
	// ImageData is optional base64-encoded image bytes.
	ImageData string `json:"image_data,omitempty"`
	// ImageMIMEType is the MIME type for ImageData (e.g. "image/png").
	ImageMIMEType string `json:"image_mime_type,omitempty"`
	// Yolo approves every tool permission request for this task. When nil, the
	// server default is used.
	Yolo *bool `json:"yolo,omitempty"`

	AgentsFile string   `json:"-"`
	ImagePath  string   `json:"-"`
	ImagePaths []string `json:"-"`
	FilePaths  []string `json:"-"`
}

// taskCreatedResponse is the JSON body returned by POST /tasks.
type taskCreatedResponse struct {
	TaskID string `json:"task_id"`
}

// serveCmd represents the serve command.
var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Start an HTTP server to run Copilot tasks via a Web API",
	Long: `Start an HTTP server that exposes a REST API for submitting Copilot
prompt tasks and tracking their progress.

Endpoints:
	POST /v1/tasks       Submit a new task. Accepts JSON or multipart/form-data.
	GET  /v1/tasks/{id}  Get the status, progress, and result of a task.
	GET  /v1/tasks       List submitted tasks.
	GET  /healthz        Health check.

Tasks run asynchronously in the background. Poll GET /v1/tasks/{id} until the
status is "done" or "failed". The unversioned /tasks endpoints are also
available for compatibility.

By default, only read permission requests are approved automatically. Pass
--yolo to make task execution approve every tool permission request.

Examples:
  # Start the server on the default address
  template-github-copilot-go serve

  # Custom host and port
  template-github-copilot-go serve --host 0.0.0.0 --port 9090

  # Use a running Copilot CLI server
  template-github-copilot-go serve --cli-url localhost:3000`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		host, err := cmd.Flags().GetString("host")
		if err != nil {
			return err
		}
		port, err := cmd.Flags().GetInt("port")
		if err != nil {
			return err
		}
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}
		yolo, err := cmd.Flags().GetBool("yolo")
		if err != nil {
			return err
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		addr := net.JoinHostPort(host, fmt.Sprintf("%d", port))
		slog.Info("starting Copilot task server", "addr", addr)

		return startServer(ctx, addr, cliURL, yolo)
	},
}

func init() {
	serveCmd.Flags().StringP("host", "H", "127.0.0.1", "Host address to bind the HTTP server to")
	serveCmd.Flags().IntP("port", "p", 8080, "Port to listen on")
	serveCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
	serveCmd.Flags().Bool("yolo", false, "Approve all Copilot tool permission requests for submitted tasks. By default only read requests are approved.")
}

// GetCommand returns the serve command for registration on the root command.
func GetCommand() *cobra.Command {
	return serveCmd
}

// startServer wires up the HTTP routes, starts the listener, and blocks until
// ctx is cancelled (Ctrl+C).
func startServer(ctx context.Context, addr, cliURL string, defaultYolo bool) error {
	store := newTaskStore()
	mux := http.NewServeMux()

	createTask := func(w http.ResponseWriter, r *http.Request) {
		handleCreateTask(w, r, store, cliURL, defaultYolo)
	}
	getTask := func(w http.ResponseWriter, r *http.Request) {
		handleGetTask(w, r, store)
	}
	listTasks := func(w http.ResponseWriter, r *http.Request) {
		handleListTasks(w, r, store)
	}

	// POST /tasks — create a new task
	mux.HandleFunc("POST /tasks", createTask)
	mux.HandleFunc("POST /v1/tasks", createTask)

	// GET /tasks/{id} — get a specific task
	mux.HandleFunc("GET /tasks/{id}", getTask)
	mux.HandleFunc("GET /v1/tasks/{id}", getTask)

	// GET /tasks — list all tasks
	mux.HandleFunc("GET /tasks", listTasks)
	mux.HandleFunc("GET /v1/tasks", listTasks)
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})

	srv := &http.Server{
		Addr:              addr,
		Handler:           mux,
		ReadHeaderTimeout: 10 * time.Second,
	}

	errCh := make(chan error, 1)
	go func() {
		slog.Info("HTTP server listening", "addr", addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			errCh <- err
		}
		close(errCh)
	}()

	select {
	case err := <-errCh:
		return fmt.Errorf("server error: %w", err)
	case <-ctx.Done():
		slog.Info("shutting down server")
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := srv.Shutdown(shutdownCtx); err != nil {
			return fmt.Errorf("shutdown error: %w", err)
		}
		return nil
	}
}

func parseTaskRequest(r *http.Request) (taskRequest, func(), error) {
	if strings.HasPrefix(strings.ToLower(r.Header.Get("Content-Type")), "multipart/form-data") {
		return parseMultipartTaskRequest(r)
	}
	return parseJSONTaskRequest(r)
}

func parseJSONTaskRequest(r *http.Request) (taskRequest, func(), error) {
	cleanup := func() {}
	var req taskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		return req, cleanup, fmt.Errorf("invalid JSON: %w", err)
	}

	var tmpDir string
	ensureTempDir := func() (string, error) {
		if tmpDir != "" {
			return tmpDir, nil
		}
		dir, err := os.MkdirTemp("", "copilot-task-*")
		if err != nil {
			return "", fmt.Errorf("failed to create temp directory: %w", err)
		}
		tmpDir = dir
		cleanup = func() { _ = os.RemoveAll(dir) }
		return dir, nil
	}

	if req.SystemMessage != "" {
		dir, err := ensureTempDir()
		if err != nil {
			return req, cleanup, err
		}
		path, err := writeTempBytes(dir, "agents.md", []byte(req.SystemMessage))
		if err != nil {
			return req, cleanup, err
		}
		req.AgentsFile = path
	}

	if req.ImageData != "" {
		mimeType := req.ImageMIMEType
		if mimeType == "" {
			mimeType = "image/png"
		}
		imgBytes, err := base64.StdEncoding.DecodeString(req.ImageData)
		if err != nil {
			return req, cleanup, fmt.Errorf("invalid image_data: %w", err)
		}
		dir, err := ensureTempDir()
		if err != nil {
			return req, cleanup, err
		}
		path, err := writeTempBytes(dir, "image"+mimeTypeExt(mimeType), imgBytes)
		if err != nil {
			return req, cleanup, err
		}
		req.ImagePath = path
	}

	return req, cleanup, nil
}

func parseMultipartTaskRequest(r *http.Request) (taskRequest, func(), error) {
	cleanup := func() {}
	var req taskRequest
	if err := r.ParseMultipartForm(64 << 20); err != nil {
		return req, cleanup, fmt.Errorf("invalid multipart form: %w", err)
	}
	form := r.MultipartForm
	cleanup = func() {
		if form != nil {
			_ = form.RemoveAll()
		}
	}

	tmpDir, err := os.MkdirTemp("", "copilot-task-*")
	if err != nil {
		return req, cleanup, fmt.Errorf("failed to create temp directory: %w", err)
	}
	cleanup = func() {
		_ = os.RemoveAll(tmpDir)
		if form != nil {
			_ = form.RemoveAll()
		}
	}

	req.Prompt = r.FormValue("prompt")
	req.Model = r.FormValue("model")
	req.SystemMessage = r.FormValue("system_message")
	if yoloText := strings.TrimSpace(r.FormValue("yolo")); yoloText != "" {
		yolo, parseErr := strconv.ParseBool(yoloText)
		if parseErr != nil {
			return req, cleanup, fmt.Errorf("invalid yolo value %q: %w", yoloText, parseErr)
		}
		req.Yolo = &yolo
	}

	if req.SystemMessage != "" {
		path, err := writeTempBytes(tmpDir, "agents.md", []byte(req.SystemMessage))
		if err != nil {
			return req, cleanup, err
		}
		req.AgentsFile = path
	}

	agentFiles, err := saveUploadedFiles(r.MultipartForm, "agents_md", tmpDir)
	if err != nil {
		return req, cleanup, err
	}
	legacyAgentFiles, err := saveUploadedFiles(r.MultipartForm, "agents_file", tmpDir)
	if err != nil {
		return req, cleanup, err
	}
	agentFiles = append(agentFiles, legacyAgentFiles...)
	if len(agentFiles) > 0 {
		req.AgentsFile = agentFiles[0]
	}

	req.ImagePaths, err = saveUploadedFiles(r.MultipartForm, "image", tmpDir)
	if err != nil {
		return req, cleanup, err
	}
	req.FilePaths, err = saveUploadedFiles(r.MultipartForm, "file", tmpDir)
	if err != nil {
		return req, cleanup, err
	}

	return req, cleanup, nil
}

func writeTempBytes(dir, name string, data []byte) (string, error) {
	path := filepath.Join(dir, name)
	if err := os.WriteFile(path, data, 0o600); err != nil {
		return "", fmt.Errorf("failed to write temp file %q: %w", name, err)
	}
	return path, nil
}

func saveUploadedFiles(form *multipart.Form, field, dir string) ([]string, error) {
	if form == nil {
		return nil, nil
	}
	files := form.File[field]
	paths := make([]string, 0, len(files))
	for i, header := range files {
		path, err := saveUploadedFile(header, field, i, dir)
		if err != nil {
			return nil, err
		}
		paths = append(paths, path)
	}
	return paths, nil
}

func saveUploadedFile(header *multipart.FileHeader, field string, index int, dir string) (string, error) {
	src, err := header.Open()
	if err != nil {
		return "", fmt.Errorf("failed to open uploaded %s file: %w", field, err)
	}

	path := filepath.Join(dir, uploadFileName(field, index, header.Filename))
	dst, err := os.Create(path)
	if err != nil {
		_ = src.Close()
		return "", fmt.Errorf("failed to create uploaded %s temp file: %w", field, err)
	}

	_, copyErr := io.Copy(dst, src)
	closeDstErr := dst.Close()
	closeSrcErr := src.Close()
	if copyErr != nil {
		return "", fmt.Errorf("failed to copy uploaded %s file: %w", field, copyErr)
	}
	if closeDstErr != nil {
		return "", fmt.Errorf("failed to close uploaded %s temp file: %w", field, closeDstErr)
	}
	if closeSrcErr != nil {
		return "", fmt.Errorf("failed to close uploaded %s file: %w", field, closeSrcErr)
	}

	return path, nil
}

func uploadFileName(field string, index int, filename string) string {
	base := filepath.Base(filename)
	if base == "." || base == string(filepath.Separator) || base == "" {
		base = "upload"
	}
	return fmt.Sprintf("%s-%d-%s", field, index, base)
}

// handleCreateTask handles POST /tasks.
func handleCreateTask(w http.ResponseWriter, r *http.Request, store *taskStore, defaultCLIURL string, defaultYolo bool) {
	req, cleanup, err := parseTaskRequest(r)
	if err != nil {
		cleanup()
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": err.Error()})
		return
	}
	if strings.TrimSpace(req.Prompt) == "" {
		cleanup()
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "prompt is required"})
		return
	}

	task := store.create(req.Prompt, req.Model)
	slog.Info("task created", "id", task.ID, "model", req.Model)

	// Run the Copilot session in the background.
	go func() {
		defer cleanup()

		store.update(task.ID, func(t *Task) { t.Status = TaskStatusRunning })
		slog.Debug("task running", "id", task.ID)

		yolo := defaultYolo
		if req.Yolo != nil {
			yolo = *req.Yolo
		}

		opts := run.RunOptions{
			Model:      req.Model,
			Prompt:     req.Prompt,
			AgentsFile: req.AgentsFile,
			ImagePath:  req.ImagePath,
			ImagePaths: req.ImagePaths,
			FilePaths:  req.FilePaths,
			CLIURL:     defaultCLIURL,
			Yolo:       yolo,
		}

		// Use a background context so the task keeps running even if the
		// HTTP request that created it has long since closed.
		result, err := run.RunSessionCollectWithEvents(context.Background(), opts, func(event run.ProgressEvent) {
			store.update(task.ID, func(t *Task) {
				t.Progress = append(t.Progress, event)
			})
		})

		now := time.Now().UTC()
		store.update(task.ID, func(t *Task) {
			t.CompletedAt = &now
			if err != nil {
				t.Status = TaskStatusFailed
				t.Error = err.Error()
				slog.Warn("task failed", "id", task.ID, "error", err)
			} else {
				t.Status = TaskStatusDone
				t.Result = result
				slog.Info("task done", "id", task.ID)
			}
		})
	}()

	writeJSON(w, http.StatusAccepted, taskCreatedResponse{TaskID: task.ID})
}

// handleGetTask handles GET /tasks/{id}.
func handleGetTask(w http.ResponseWriter, r *http.Request, store *taskStore) {
	id := r.PathValue("id")
	task, ok := store.get(id)
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "task not found"})
		return
	}
	writeJSON(w, http.StatusOK, task)
}

// handleListTasks handles GET /tasks.
func handleListTasks(w http.ResponseWriter, _ *http.Request, store *taskStore) {
	store.mu.RLock()
	tasks := make([]Task, 0, len(store.tasks))
	for _, t := range store.tasks {
		// Copy each task to avoid exposing internal pointers to concurrent writers.
		tasks = append(tasks, *t)
	}
	store.mu.RUnlock()
	writeJSON(w, http.StatusOK, tasks)
}

// writeJSON writes v as JSON with the given HTTP status code.
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(v); err != nil {
		slog.Error("failed to write JSON response", "error", err)
	}
}

// mimeTypeExt returns a file extension for common image MIME types.
func mimeTypeExt(mimeType string) string {
	switch mimeType {
	case "image/jpeg":
		return ".jpg"
	case "image/gif":
		return ".gif"
	case "image/webp":
		return ".webp"
	default:
		return ".png"
	}
}
