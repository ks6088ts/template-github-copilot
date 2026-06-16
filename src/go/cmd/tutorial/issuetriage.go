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
	"os"
	"os/signal"
	"sync"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/spf13/cobra"
)

const issueTriageSystemMessage = "You are an expert GitHub issue triage assistant. " +
	"Use list_issues to fetch open issues, classify each one as 'bug', " +
	"'enhancement', or 'documentation', then call label_issue to apply the " +
	"appropriate label. After triaging all issues, summarise your actions."

// ---------------------------------------------------------------------------
// Custom tool input/output schemas
//
// DefineTool generates a JSON schema from these structs. The `jsonschema` tag
// becomes the field description that Copilot sees when deciding how to call the
// tool, while the `json` tag controls the wire format.
// ---------------------------------------------------------------------------

// listIssuesInput has no fields: list_issues takes no arguments.
type listIssuesInput struct{}

type issueItem struct {
	ID     int      `json:"id"`
	Title  string   `json:"title"`
	Body   string   `json:"body"`
	Labels []string `json:"labels"`
}

type listIssuesOutput struct {
	Issues []issueItem `json:"issues"`
}

type labelIssueInput struct {
	IssueID int      `json:"issue_id" jsonschema:"numeric ID of the issue to label"`
	Labels  []string `json:"labels" jsonschema:"labels to apply (e.g. bug, enhancement, documentation)"`
}

type labelIssueOutput struct {
	Success       bool     `json:"success"`
	IssueID       int      `json:"issue_id"`
	AppliedLabels []string `json:"applied_labels"`
}

// triageRecord captures what the agent actually applied so the caller can
// observe the tool-calling agent's decisions.
type triageRecord struct {
	ID     int      `json:"id"`
	Labels []string `json:"labels"`
}

// sampleIssues is embedded so the tutorial runs without any external API calls.
var sampleIssues = []issueItem{
	{
		ID:    1,
		Title: "Application crashes when uploading files larger than 100 MB",
		Body: "Steps to reproduce: open the upload dialog, select a file > 100 MB, click Upload. " +
			"Expected: file uploads successfully. Actual: the app throws an unhandled exception.",
		Labels: []string{},
	},
	{
		ID:     2,
		Title:  "Add dark mode support",
		Body:   "It would be great to have a dark mode option in the settings panel.",
		Labels: []string{},
	},
	{
		ID:     3,
		Title:  "Typo in README: 'recieve' should be 'receive'",
		Body:   "Line 42 of README.md contains a typo.",
		Labels: []string{},
	},
}

// issueTriageCmd is the Go counterpart of src/python/scripts/tutorials/02_issue_triage.py.
//
// It registers two custom tools (list_issues, label_issue) via copilot.DefineTool
// and lets Copilot drive a tool-calling agent loop that triages sample issues.
var issueTriageCmd = &cobra.Command{
	Use:   "issue-triage",
	Short: "Tool-calling issue triage agent using copilot.DefineTool",
	Long: `Issue triage bot built on the GitHub Copilot SDK custom tools API.

Registers two typed tools (list_issues, label_issue) with copilot.DefineTool and
lets Copilot classify each sample issue as a bug, enhancement, or documentation
change, then apply the matching label. No external GitHub API calls are made.

Equivalent Python tutorial:
    src/python/scripts/tutorials/02_issue_triage.py
See the tutorial docs for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/go/tutorials/02_issue_triage.md     (English)
    docs/copilot_sdk_tutorial/go/tutorials/02_issue_triage.ja.md  (日本語)`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running issue-triage", "cliURL", cliURL)

		err = runIssueTriage(ctx, cliURL)
		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	tutorialCmd.AddCommand(issueTriageCmd)

	issueTriageCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
}

// runIssueTriage wires up the custom tools, drives one triage turn, and prints a summary.
func runIssueTriage(ctx context.Context, cliURL string) error {
	// triaged accumulates every label_issue call. Tool handlers may run on
	// different goroutines, so guard the shared slice with a mutex.
	var (
		mu      sync.Mutex
		triaged []triageRecord
	)

	// list_issues returns the embedded sample issues.
	listIssues := copilot.DefineTool(
		"list_issues",
		"Return the list of open GitHub issues to triage.",
		func(_ listIssuesInput, _ copilot.ToolInvocation) (listIssuesOutput, error) {
			return listIssuesOutput{Issues: sampleIssues}, nil
		},
	)

	// label_issue records the applied labels and echoes them back to Copilot.
	labelIssue := copilot.DefineTool(
		"label_issue",
		"Apply one or more labels to a GitHub issue.",
		func(in labelIssueInput, _ copilot.ToolInvocation) (labelIssueOutput, error) {
			mu.Lock()
			triaged = append(triaged, triageRecord{ID: in.IssueID, Labels: in.Labels})
			mu.Unlock()
			return labelIssueOutput{
				Success:       true,
				IssueID:       in.IssueID,
				AppliedLabels: in.Labels,
			}, nil
		},
	)

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
		OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
		Tools:               []copilot.Tool{listIssues, labelIssue},
		Streaming:           copilot.Bool(false),
		SystemMessage:       &copilot.SystemMessageConfig{Mode: "replace", Content: issueTriageSystemMessage},
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %w", err)
	}

	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.ToolExecutionStartData:
			fmt.Fprintf(os.Stderr, "[Tool] Calling: %s\n", data.ToolName)
		case *copilot.SessionErrorData:
			fmt.Fprintf(os.Stderr, "[Error] %s\n", data.Message)
		}
	})

	reply, err := session.SendPromptAndWait(ctx, "Please triage all open issues and apply the appropriate labels.")
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
	applied := triaged
	mu.Unlock()

	labelsJSON, err := json.MarshalIndent(applied, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to encode applied labels: %w", err)
	}

	fmt.Println("=== Triage Summary ===")
	fmt.Println(content)
	fmt.Println("\n=== Applied Labels ===")
	fmt.Println(string(labelsJSON))
	return nil
}
