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
	"fmt"
	"log/slog"
	"os"
	"os/signal"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/spf13/cobra"
)

const streamingReviewSystemMessage = "You are a senior software engineer conducting a thorough code review. " +
	"For each change in the diff: identify bugs, security issues, and style problems. " +
	"Be concise but precise. Use Markdown formatting."

// sampleDiff is embedded so the script runs without external files.
const sampleDiff = `diff --git a/src/auth.py b/src/auth.py
index 1a2b3c4..5d6e7f8 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -12,7 +12,7 @@ import hashlib
 def hash_password(password: str) -> str:
-    return hashlib.md5(password.encode()).hexdigest()
+    return hashlib.sha256(password.encode()).hexdigest()

@@ -28,6 +28,12 @@ def verify_token(token: str) -> bool:
     if not token:
         return False
+    # TODO: add expiry check
     return token in _valid_tokens

+def delete_user(user_id: int) -> None:
+    # WARNING: no authorization check
+    db.execute("DELETE FROM users WHERE id = %s" % user_id)
`

// streamingReviewCmd is the Go counterpart of src/python/scripts/tutorials/03_streaming_review.py.
//
// It streams a code review token by token via AssistantMessageDeltaData, so the
// response appears incrementally instead of all at once.
var streamingReviewCmd = &cobra.Command{
	Use:   "streaming-review",
	Short: "Streaming code review that prints tokens as they arrive",
	Long: `Streaming code review built on the GitHub Copilot SDK.

Enables streaming so assistant.message_delta events deliver tokens incrementally.
The subcommand reviews a built-in sample diff (or one you pass with --diff) and
prints the review to stdout as it is generated.

Equivalent Python tutorial:
    src/python/scripts/tutorials/03_streaming_review.py
See the tutorial docs for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/go/tutorials/03_streaming_review.md     (English)
    docs/copilot_sdk_tutorial/go/tutorials/03_streaming_review.ja.md  (日本語)`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}
		diffPath, err := cmd.Flags().GetString("diff")
		if err != nil {
			return err
		}

		diffText := sampleDiff
		if diffPath != "" {
			data, readErr := os.ReadFile(diffPath)
			if readErr != nil {
				return fmt.Errorf("diff file not found: %s: %w", diffPath, readErr)
			}
			diffText = string(data)
		} else {
			fmt.Fprintln(os.Stderr, "[Info] Using built-in sample diff. Pass --diff <path> to use your own.")
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running streaming-review", "cliURL", cliURL, "diffPath", diffPath)

		err = runStreamingReview(ctx, cliURL, diffText)
		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	tutorialCmd.AddCommand(streamingReviewCmd)

	streamingReviewCmd.Flags().StringP("diff", "d", "", "Path to a unified diff file (uses built-in sample if not provided)")
	streamingReviewCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
}

// runStreamingReview creates a streaming session and prints the review as it arrives.
func runStreamingReview(ctx context.Context, cliURL, diffText string) error {
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
		Streaming:           copilot.Bool(true), // ← streaming enabled
		SystemMessage:       &copilot.SystemMessageConfig{Mode: "replace", Content: streamingReviewSystemMessage},
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %w", err)
	}

	fmt.Println("=== Streaming Code Review ===")
	fmt.Println()

	// Stream tokens to stdout as they arrive.
	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.AssistantMessageDeltaData:
			fmt.Print(data.DeltaContent)
		case *copilot.SessionErrorData:
			fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
		}
	})

	prompt := fmt.Sprintf("Please review the following diff and provide feedback:\n\n```diff\n%s\n```", diffText)
	if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
		return err
	}

	fmt.Println("\n\n=== Review Complete ===")
	return nil
}
