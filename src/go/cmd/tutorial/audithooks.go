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
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"math"
	"os"
	"os/signal"
	"sync"
	"time"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/github/copilot-sdk/go/rpc"
	"github.com/spf13/cobra"
)

const auditHooksSystemMessage = "You are an operations assistant with access to a delete_record tool. " +
	"When asked to delete a record, call the delete_record tool. " +
	"If a tool call is denied, clearly state that the action was blocked by policy and do not retry."

// ---------------------------------------------------------------------------
// Custom tool — a destructive action an audit policy may want to block
// ---------------------------------------------------------------------------

type deleteRecordInput struct {
	RecordID int `json:"record_id" jsonschema:"numeric ID of the customer record to delete"`
}

type deleteRecordOutput struct {
	Success  bool   `json:"success"`
	RecordID int    `json:"record_id"`
	Message  string `json:"message"`
}

// auditEntry is one line in the audit log.
type auditEntry struct {
	TS     float64 `json:"ts"`
	Event  string  `json:"event"`
	Detail string  `json:"detail,omitempty"`
}

// auditHooksCmd is the Go counterpart of src/python/scripts/tutorials/05_audit_hooks.py.
//
// A custom delete_record tool models a destructive operation. The permission
// handler either approves or (with --deny-tools) rejects the call, and every
// session event is recorded to an audit log.
var auditHooksCmd = &cobra.Command{
	Use:   "audit-hooks",
	Short: "Audit logging via session events and a permission handler",
	Long: `Audit logging built on the GitHub Copilot SDK session events and permission handling.

A custom delete_record tool models a destructive operation that an audit policy
may want to block. Run with --deny-tools to see the permission handler reject the
call — the tool implementation never runs and the audit log records the denial.

Equivalent Python tutorial:
    src/python/scripts/tutorials/05_audit_hooks.py
See the tutorial docs for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/go/tutorials/05_audit_hooks.md     (English)
    docs/copilot_sdk_tutorial/go/tutorials/05_audit_hooks.ja.md  (日本語)`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		prompt, err := cmd.Flags().GetString("prompt")
		if err != nil {
			return err
		}
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}
		denyTools, err := cmd.Flags().GetBool("deny-tools")
		if err != nil {
			return err
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running audit-hooks", "cliURL", cliURL, "denyTools", denyTools)

		err = runAuditHooks(ctx, cliURL, prompt, denyTools)
		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	tutorialCmd.AddCommand(auditHooksCmd)

	auditHooksCmd.Flags().StringP("prompt", "p", "Delete the customer record with ID 42 using the delete_record tool, then confirm what happened.", "Prompt to send to Copilot")
	auditHooksCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
	auditHooksCmd.Flags().Bool("deny-tools", false, "Use a permission handler that denies all tool executions")
}

// runAuditHooks registers a destructive tool, gates it behind a permission
// handler, records every session event, and prints the resulting audit log.
func runAuditHooks(ctx context.Context, cliURL, prompt string, denyTools bool) error {
	var (
		mu       sync.Mutex
		auditLog []auditEntry
		deleted  []int
	)
	start := time.Now()

	// record appends one timestamped entry to the audit log.
	record := func(event, detail string) {
		mu.Lock()
		auditLog = append(auditLog, auditEntry{
			TS:     math.Round(time.Since(start).Seconds()*1000) / 1000,
			Event:  event,
			Detail: detail,
		})
		mu.Unlock()
	}

	// delete_record records which records were actually deleted so the caller
	// can observe whether the permission handler allowed the call.
	deleteRecord := copilot.DefineTool(
		"delete_record",
		"Permanently delete a customer record by its numeric ID.",
		func(in deleteRecordInput, _ copilot.ToolInvocation) (deleteRecordOutput, error) {
			mu.Lock()
			deleted = append(deleted, in.RecordID)
			mu.Unlock()
			return deleteRecordOutput{
				Success:  true,
				RecordID: in.RecordID,
				Message:  fmt.Sprintf("Record %d permanently deleted.", in.RecordID),
			}, nil
		},
	)

	// permissionHandler approves or denies every tool call. It fires because the
	// session registers a custom tool; with no tools it would never be invoked.
	permissionHandler := func(request copilot.PermissionRequest, _ copilot.PermissionInvocation) (rpc.PermissionDecision, error) {
		toolName := "unknown"
		if ct, ok := request.(*copilot.PermissionRequestCustomTool); ok {
			toolName = ct.ToolName
		}
		if denyTools {
			record("PERMISSION_DENIED", "tool="+toolName)
			fmt.Fprintf(os.Stderr, "[Permission] DENIED tool execution: %s\n", toolName)
			feedback := "Tool execution denied by audit policy"
			return &rpc.PermissionDecisionReject{Feedback: &feedback}, nil
		}
		record("PERMISSION_APPROVED", "tool="+toolName)
		fmt.Fprintf(os.Stderr, "[Permission] APPROVED tool execution: %s\n", toolName)
		return &rpc.PermissionDecisionApproveOnce{}, nil
	}

	var client *copilot.Client
	if cliURL != "" {
		client = copilot.NewClient(newClientOptions(cliURL))
	} else {
		client = copilot.NewClient(newClientOptions(cliURL))
	}

	if err := client.Start(ctx); err != nil {
		return fmt.Errorf("failed to start Copilot client: %w", err)
	}
	defer func() { _ = client.Stop() }()

	session, err := client.CreateSession(ctx, &copilot.SessionConfig{
		OnPermissionRequest: permissionHandler,
		Tools:               []copilot.Tool{deleteRecord},
		Streaming:           copilot.Bool(false),
		SystemMessage:       &copilot.SystemMessageConfig{Mode: "replace", Content: auditHooksSystemMessage},
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %w", err)
	}

	// Event hook — records every session event of interest.
	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.AssistantTurnStartData:
			record("TURN_START", "")
		case *copilot.AssistantIntentData:
			record("INTENT", data.Intent)
		case *copilot.ToolExecutionStartData:
			record("TOOL_START", data.ToolName)
			fmt.Fprintf(os.Stderr, "[Tool] Starting: %s\n", data.ToolName)
		case *copilot.ToolExecutionCompleteData:
			detail := "error=<nil>"
			if data.Error != nil {
				detail = "error=" + data.Error.Message
			}
			record("TOOL_COMPLETE", detail)
		case *copilot.AssistantTurnEndData:
			record("TURN_END", "")
		case *copilot.SessionIdleData:
			record("SESSION_IDLE", "")
		case *copilot.SessionErrorData:
			record("SESSION_ERROR", data.Message)
			fmt.Fprintf(os.Stderr, "[Error] %s\n", data.Message)
		}
	})

	promptDetail := prompt
	if len(promptDetail) > 80 {
		promptDetail = promptDetail[:80]
	}
	record("SEND", promptDetail)

	reply, err := session.SendPromptAndWait(ctx, prompt)
	if err != nil {
		return err
	}

	content := "(no response)"
	if reply != nil {
		if data, ok := reply.Data.(*copilot.AssistantMessageData); ok {
			content = data.Content
		}
	}

	mu.Lock()
	deletedSnapshot := deleted
	logJSON, marshalErr := json.MarshalIndent(auditLog, "", "  ")
	mu.Unlock()
	if marshalErr != nil {
		return fmt.Errorf("failed to encode audit log: %w", marshalErr)
	}

	fmt.Println("=== Response ===")
	fmt.Println(content)
	fmt.Println("\n=== Deleted Records ===")
	if len(deletedSnapshot) == 0 {
		fmt.Println("(none — tool was not executed)")
	} else {
		fmt.Println(deletedSnapshot)
	}
	fmt.Println("\n=== Audit Log ===")
	fmt.Println(string(logJSON))
	return nil
}
