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
	"log/slog"
	"net"
	"net/http"
	"os"
	"os/signal"
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
	ID          string     `json:"id"`
	Status      TaskStatus `json:"status"`
	Result      string     `json:"result,omitempty"`
	Error       string     `json:"error,omitempty"`
	CreatedAt   time.Time  `json:"created_at"`
	CompletedAt *time.Time `json:"completed_at,omitempty"`
}

// taskStore is the in-memory store for all submitted tasks.
type taskStore struct {
	mu    sync.RWMutex
	tasks map[string]*Task
}

func newTaskStore() *taskStore {
	return &taskStore{tasks: make(map[string]*Task)}
}

func (s *taskStore) create() *Task {
	t := &Task{
		ID:        uuid.New().String(),
		Status:    TaskStatusPending,
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
  POST /tasks          Submit a new task (JSON body: prompt, model, system_message,
                       image_data, image_mime_type). Returns {"task_id": "..."}.
  GET  /tasks/{id}     Get the status and result of a previously submitted task.
  GET  /tasks          List all submitted tasks.

Tasks run asynchronously in the background. Poll GET /tasks/{id} until the
status is "done" or "failed".

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

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		addr := net.JoinHostPort(host, fmt.Sprintf("%d", port))
		slog.Info("starting Copilot task server", "addr", addr)

		return startServer(ctx, addr, cliURL)
	},
}

func init() {
	serveCmd.Flags().StringP("host", "H", "127.0.0.1", "Host address to bind the HTTP server to")
	serveCmd.Flags().IntP("port", "p", 8080, "Port to listen on")
	serveCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
}

// GetCommand returns the serve command for registration on the root command.
func GetCommand() *cobra.Command {
	return serveCmd
}

// startServer wires up the HTTP routes, starts the listener, and blocks until
// ctx is cancelled (Ctrl+C).
func startServer(ctx context.Context, addr, cliURL string) error {
	store := newTaskStore()
	mux := http.NewServeMux()

	// POST /tasks — create a new task
	mux.HandleFunc("POST /tasks", func(w http.ResponseWriter, r *http.Request) {
		handleCreateTask(w, r, store, cliURL)
	})

	// GET /tasks/{id} — get a specific task
	mux.HandleFunc("GET /tasks/{id}", func(w http.ResponseWriter, r *http.Request) {
		handleGetTask(w, r, store)
	})

	// GET /tasks — list all tasks
	mux.HandleFunc("GET /tasks", func(w http.ResponseWriter, r *http.Request) {
		handleListTasks(w, r, store)
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

// handleCreateTask handles POST /tasks.
func handleCreateTask(w http.ResponseWriter, r *http.Request, store *taskStore, defaultCLIURL string) {
	var req taskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid JSON: " + err.Error()})
		return
	}
	if strings.TrimSpace(req.Prompt) == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "prompt is required"})
		return
	}

	task := store.create()
	slog.Info("task created", "id", task.ID, "model", req.Model)

	// Run the Copilot session in the background.
	go func() {
		store.update(task.ID, func(t *Task) { t.Status = TaskStatusRunning })
		slog.Debug("task running", "id", task.ID)

		opts := run.RunOptions{
			Model:  req.Model,
			Prompt: req.Prompt,
			CLIURL: defaultCLIURL,
		}

		// If the caller supplied a system message directly, write it to a
		// temp file so RunSessionCollect can read it via AgentsFile. This
		// avoids changing the RunOptions signature for the simpler case.
		if req.SystemMessage != "" {
			tmp, createErr := os.CreateTemp("", "agents-*.md")
			if createErr != nil {
				slog.Warn("failed to create temp file for system message", "error", createErr)
			} else {
				if _, writeErr := tmp.WriteString(req.SystemMessage); writeErr != nil {
					slog.Warn("failed to write system message to temp file", "error", writeErr)
				}
				if closeErr := tmp.Close(); closeErr != nil {
					slog.Warn("failed to close system message temp file", "error", closeErr)
				}
				opts.AgentsFile = tmp.Name()
				defer os.Remove(tmp.Name())
			}
		}

		// If the caller supplied inline image data, write it to a temp file.
		if req.ImageData != "" {
			mimeType := req.ImageMIMEType
			if mimeType == "" {
				mimeType = "image/png"
			}
			ext := mimeTypeExt(mimeType)
			tmp, createErr := os.CreateTemp("", "image-*"+ext)
			if createErr != nil {
				slog.Warn("failed to create temp file for image", "error", createErr)
			} else {
				imgBytes, decErr := base64.StdEncoding.DecodeString(req.ImageData)
				if decErr != nil {
					slog.Warn("failed to decode base64 image data", "error", decErr)
				} else if _, writeErr := tmp.Write(imgBytes); writeErr != nil {
					slog.Warn("failed to write image data to temp file", "error", writeErr)
				}
				if closeErr := tmp.Close(); closeErr != nil {
					slog.Warn("failed to close image temp file", "error", closeErr)
				}
				opts.ImagePath = tmp.Name()
				defer os.Remove(tmp.Name())
			}
		}

		// Use a background context so the task keeps running even if the
		// HTTP request that created it has long since closed.
		result, err := run.RunSessionCollect(context.Background(), opts)

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
