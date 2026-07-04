package run

import (
	"os"
	"path/filepath"
	"testing"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/github/copilot-sdk/go/rpc"
)

func TestPermissionHandlerRestrictsNonReadRequests(t *testing.T) {
	handler := permissionHandler(false)

	readDecision, err := handler(&copilot.PermissionRequestRead{}, copilot.PermissionInvocation{})
	if err != nil {
		t.Fatalf("permissionHandler(read) error = %v", err)
	}
	if _, ok := readDecision.(*rpc.PermissionDecisionApproveOnce); !ok {
		t.Fatalf("permissionHandler(read) = %T, want *rpc.PermissionDecisionApproveOnce", readDecision)
	}

	writeDecision, err := handler(&copilot.PermissionRequestWrite{}, copilot.PermissionInvocation{})
	if err != nil {
		t.Fatalf("permissionHandler(write) error = %v", err)
	}
	if _, ok := writeDecision.(*rpc.PermissionDecisionReject); !ok {
		t.Fatalf("permissionHandler(write) = %T, want *rpc.PermissionDecisionReject", writeDecision)
	}
}

func TestPermissionHandlerYoloApprovesNonReadRequests(t *testing.T) {
	handler := permissionHandler(true)

	decision, err := handler(&copilot.PermissionRequestWrite{}, copilot.PermissionInvocation{})
	if err != nil {
		t.Fatalf("permissionHandler(yolo write) error = %v", err)
	}
	if _, ok := decision.(*rpc.PermissionDecisionApproveOnce); !ok {
		t.Fatalf("permissionHandler(yolo write) = %T, want *rpc.PermissionDecisionApproveOnce", decision)
	}
}

func TestBuildSessionInputsMakesFileAttachmentsAbsolute(t *testing.T) {
	dir := t.TempDir()
	filePath := filepath.Join(dir, "input.txt")
	if err := os.WriteFile(filePath, []byte("hello"), 0o600); err != nil {
		t.Fatalf("os.WriteFile() error = %v", err)
	}

	oldWD, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd() error = %v", err)
	}
	if err := os.Chdir(dir); err != nil {
		t.Fatalf("os.Chdir() error = %v", err)
	}
	t.Cleanup(func() {
		if err := os.Chdir(oldWD); err != nil {
			t.Fatalf("restore working directory: %v", err)
		}
	})

	_, attachments, err := buildSessionInputs(RunOptions{FilePaths: []string{"input.txt"}})
	if err != nil {
		t.Fatalf("buildSessionInputs() error = %v", err)
	}
	if len(attachments) != 1 {
		t.Fatalf("len(attachments) = %d, want 1", len(attachments))
	}
	attachment, ok := attachments[0].(*copilot.AttachmentFile)
	if !ok {
		t.Fatalf("attachment = %T, want *copilot.AttachmentFile", attachments[0])
	}
	if !filepath.IsAbs(attachment.Path) {
		t.Fatalf("attachment.Path = %q, want absolute path", attachment.Path)
	}
}
