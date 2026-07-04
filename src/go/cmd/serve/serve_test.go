package serve

import (
	"bytes"
	"encoding/base64"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

func TestParseJSONTaskRequestWritesInlineInputs(t *testing.T) {
	body := `{"prompt":"hello","model":"gpt-4o","system_message":"be concise","image_data":"` + base64.StdEncoding.EncodeToString([]byte("image")) + `","image_mime_type":"image/png"}`
	req := httptest.NewRequest(http.MethodPost, "/v1/tasks", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")

	parsed, cleanup, err := parseTaskRequest(req)
	defer cleanup()
	if err != nil {
		t.Fatalf("parseTaskRequest() error = %v", err)
	}
	if parsed.Prompt != "hello" || parsed.Model != "gpt-4o" {
		t.Fatalf("parsed = %#v, want prompt/model set", parsed)
	}
	assertFileExists(t, parsed.AgentsFile)
	assertFileExists(t, parsed.ImagePath)
}

func TestParseMultipartTaskRequestSavesAttachments(t *testing.T) {
	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	writeField(t, writer, "prompt", "hello")
	writeField(t, writer, "model", "gpt-4o")
	writeField(t, writer, "yolo", "true")
	writeFile(t, writer, "agents_md", "AGENTS.md", "instructions")
	writeFile(t, writer, "image", "screenshot.png", "image")
	writeFile(t, writer, "file", "README.md", "readme")
	if err := writer.Close(); err != nil {
		t.Fatalf("writer.Close() error = %v", err)
	}

	req := httptest.NewRequest(http.MethodPost, "/v1/tasks", &body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	parsed, cleanup, err := parseTaskRequest(req)
	defer cleanup()
	if err != nil {
		t.Fatalf("parseTaskRequest() error = %v", err)
	}
	if parsed.Yolo == nil || !*parsed.Yolo {
		t.Fatalf("parsed.Yolo = %v, want true", parsed.Yolo)
	}
	assertFileExists(t, parsed.AgentsFile)
	if len(parsed.ImagePaths) != 1 {
		t.Fatalf("len(parsed.ImagePaths) = %d, want 1", len(parsed.ImagePaths))
	}
	assertFileExists(t, parsed.ImagePaths[0])
	if len(parsed.FilePaths) != 1 {
		t.Fatalf("len(parsed.FilePaths) = %d, want 1", len(parsed.FilePaths))
	}
	assertFileExists(t, parsed.FilePaths[0])
}

func writeField(t *testing.T, writer *multipart.Writer, field, value string) {
	t.Helper()
	if err := writer.WriteField(field, value); err != nil {
		t.Fatalf("WriteField(%q) error = %v", field, err)
	}
}

func writeFile(t *testing.T, writer *multipart.Writer, field, filename, value string) {
	t.Helper()
	part, err := writer.CreateFormFile(field, filename)
	if err != nil {
		t.Fatalf("CreateFormFile(%q) error = %v", field, err)
	}
	if _, err := part.Write([]byte(value)); err != nil {
		t.Fatalf("Write(%q) error = %v", field, err)
	}
}

func assertFileExists(t *testing.T, path string) {
	t.Helper()
	if path == "" {
		t.Fatal("path is empty")
	}
	if _, err := os.Stat(path); err != nil {
		t.Fatalf("os.Stat(%q) error = %v", path, err)
	}
}
