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
package run

import (
	"context"
	"encoding/base64"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"time"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/github/copilot-sdk/go/rpc"
	"github.com/spf13/cobra"
)

// runCmd represents the run command.
//
// It sends a single prompt to the GitHub Copilot SDK, optionally loading a
// local agents.md file as additional instructions and attaching files or
// images as prompt inputs.
var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run a Copilot session from the command line",
	Long: `Run a Copilot session with a prompt, optional model, additional
instructions from an agents.md file, and file or image attachments.

The response is streamed to stdout as it is generated. Requires the GitHub
Copilot CLI to be installed and authenticated.

By default, only read permission requests are approved automatically. Pass
--yolo to approve every tool permission request.

Examples:
  # Simple prompt with the default model
  template-github-copilot-go run --prompt "Explain goroutines in Go"

  # Specify a model
  template-github-copilot-go run --model gpt-4o --prompt "What is recursion?"

  # Attach an image (requires a vision-capable model)
  template-github-copilot-go run --model gpt-4o --image screenshot.png --prompt "What do you see?"`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		model, err := cmd.Flags().GetString("model")
		if err != nil {
			return err
		}
		prompt, err := cmd.Flags().GetString("prompt")
		if err != nil {
			return err
		}
		agentsFile, err := cmd.Flags().GetString("agents-file")
		if err != nil {
			return err
		}
		agentsMD, err := cmd.Flags().GetString("agents-md")
		if err != nil {
			return err
		}
		if agentsFile != "" && agentsMD != "" {
			return fmt.Errorf("--agents-file and --agents-md cannot both be set")
		}
		if agentsMD != "" {
			agentsFile = agentsMD
		}
		imagePaths, err := cmd.Flags().GetStringArray("image")
		if err != nil {
			return err
		}
		filePaths, err := cmd.Flags().GetStringArray("file")
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

		slog.Debug("running run",
			"model", model,
			"agentsFile", agentsFile,
			"imagePaths", imagePaths,
			"filePaths", filePaths,
			"cliURL", cliURL,
			"yolo", yolo,
		)

		err = RunSession(ctx, RunOptions{
			Model:      model,
			Prompt:     prompt,
			AgentsFile: agentsFile,
			ImagePaths: imagePaths,
			FilePaths:  filePaths,
			CLIURL:     cliURL,
			Yolo:       yolo,
		})
		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	runCmd.Flags().StringP("model", "m", "", "Model to use for the session (e.g. gpt-4o, claude-3.5-sonnet). Uses the default model when empty.")
	runCmd.Flags().StringP("prompt", "p", "Hello, Copilot!", "Prompt to send to the model")
	runCmd.Flags().StringP("agents-file", "a", "", "Path to an agents.md file whose content is appended as session instructions")
	runCmd.Flags().String("agents-md", "", "Path to an agents.md file whose content is appended as session instructions")
	runCmd.Flags().StringArrayP("image", "i", nil, "Path to an image file to attach to the message (repeatable; requires a vision-capable model)")
	runCmd.Flags().StringArray("file", nil, "Path to a non-image file to attach to the message (repeatable)")
	runCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
	runCmd.Flags().Bool("yolo", false, "Approve all Copilot tool permission requests. By default only read requests are approved.")
}

// GetCommand returns the run command for registration on the root command.
func GetCommand() *cobra.Command {
	return runCmd
}

// RunOptions holds the inputs for RunSession.
type RunOptions struct {
	// Model is the Copilot model identifier (e.g. "gpt-4o"). Uses the default
	// model when empty.
	Model string
	// Prompt is the user message to send.
	Prompt string
	// AgentsFile is the optional path to an agents.md (or any markdown) file
	// whose contents are appended as session instructions.
	AgentsFile string
	// ImagePath is the optional path to an image file attached to the message.
	// The model must support vision for this to have an effect.
	ImagePath string
	// ImagePaths are optional paths to image files attached to the message.
	// The model must support vision for these to have an effect.
	ImagePaths []string
	// FilePaths are optional non-image files attached to the message.
	FilePaths []string
	// CLIURL is the optional Copilot CLI server URL (e.g. "localhost:3000").
	// When empty, the SDK spawns the bundled CLI over stdio.
	CLIURL string
	// Yolo approves every permission request. When false, only read requests are
	// approved automatically.
	Yolo bool
}

// ProgressEvent is a normalized session event emitted while a Copilot task is
// running. It is intentionally small so it can be returned by the serve API.
type ProgressEvent struct {
	Time       time.Time `json:"time"`
	Type       string    `json:"type"`
	Message    string    `json:"message,omitempty"`
	ToolName   string    `json:"tool_name,omitempty"`
	ToolCallID string    `json:"tool_call_id,omitempty"`
}

// RunSession creates a Copilot session with the given options and streams the
// assistant response to stdout. It is exported so the serve subcommand can
// reuse it for background task execution.
func RunSession(ctx context.Context, opts RunOptions) error {
	systemMessage, attachments, err := buildSessionInputs(opts)
	if err != nil {
		return err
	}

	client, session, err := newSession(ctx, opts, systemMessage, copilot.Bool(true))
	if err != nil {
		return err
	}
	defer func() { _ = client.Stop() }()

	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.AssistantMessageDeltaData:
			fmt.Print(data.DeltaContent)
		case *copilot.SessionErrorData:
			fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
		}
	})

	if _, err := session.SendAndWait(ctx, copilot.MessageOptions{
		Prompt:      opts.Prompt,
		Attachments: attachments,
	}); err != nil {
		return err
	}

	// Ensure a newline after the streamed output.
	fmt.Println()
	return nil
}

// RunSessionCollect works like RunSession but captures the full assistant
// response in a string instead of writing it to stdout. It is used by the
// serve subcommand to collect task output.
func RunSessionCollect(ctx context.Context, opts RunOptions) (string, error) {
	return RunSessionCollectWithEvents(ctx, opts, nil)
}

// RunSessionCollectWithEvents works like RunSessionCollect and reports compact
// progress events to onProgress while the session runs.
func RunSessionCollectWithEvents(ctx context.Context, opts RunOptions, onProgress func(ProgressEvent)) (string, error) {
	systemMessage, attachments, err := buildSessionInputs(opts)
	if err != nil {
		return "", err
	}

	client, session, err := newSession(ctx, opts, systemMessage, copilot.Bool(false))
	if err != nil {
		return "", err
	}
	defer func() { _ = client.Stop() }()

	session.On(func(event copilot.SessionEvent) {
		if onProgress == nil {
			return
		}
		emitProgressEvent(onProgress, event)
	})

	reply, err := session.SendAndWait(ctx, copilot.MessageOptions{
		Prompt:      opts.Prompt,
		Attachments: attachments,
	})
	if err != nil {
		return "", err
	}

	if reply != nil {
		if data, ok := reply.Data.(*copilot.AssistantMessageData); ok {
			return data.Content, nil
		}
	}
	return "", nil
}

func emitProgressEvent(onProgress func(ProgressEvent), event copilot.SessionEvent) {
	progress := ProgressEvent{
		Time: event.Timestamp,
		Type: string(event.Type()),
	}
	if progress.Time.IsZero() {
		progress.Time = time.Now().UTC()
	}

	switch data := event.Data.(type) {
	case *copilot.ToolExecutionStartData:
		progress.ToolName = data.ToolName
		progress.ToolCallID = data.ToolCallID
		progress.Message = "tool execution started"
	case *copilot.ToolExecutionProgressData:
		progress.ToolCallID = data.ToolCallID
		progress.Message = data.ProgressMessage
	case *copilot.ToolExecutionCompleteData:
		progress.ToolCallID = data.ToolCallID
		if data.Success {
			progress.Message = "tool execution completed"
		} else if data.Error != nil {
			progress.Message = data.Error.Message
		} else {
			progress.Message = "tool execution failed"
		}
	case *copilot.AssistantMessageData:
		progress.Message = "assistant message completed"
	case *copilot.SessionErrorData:
		progress.Message = data.Message
	default:
		return
	}

	onProgress(progress)
}

// buildSessionInputs reads the optional agents file and builds any image
// attachments. It is shared between RunSession and RunSessionCollect to avoid
// duplicating the setup logic.
func buildSessionInputs(opts RunOptions) (systemMessage string, attachments []copilot.Attachment, err error) {
	if opts.AgentsFile != "" {
		data, readErr := os.ReadFile(opts.AgentsFile)
		if readErr != nil {
			return "", nil, fmt.Errorf("failed to read agents file %q: %w", opts.AgentsFile, readErr)
		}
		systemMessage = string(data)
	}

	imagePaths := make([]string, 0, len(opts.ImagePaths)+1)
	if opts.ImagePath != "" {
		imagePaths = append(imagePaths, opts.ImagePath)
	}
	imagePaths = append(imagePaths, opts.ImagePaths...)
	for _, imagePath := range imagePaths {
		data, readErr := os.ReadFile(imagePath)
		if readErr != nil {
			return "", nil, fmt.Errorf("failed to read image file %q: %w", imagePath, readErr)
		}
		mimeType := imageMIMEType(imagePath)
		displayName := filepath.Base(imagePath)
		attachments = append(attachments, &copilot.AttachmentBlob{
			Data:        base64.StdEncoding.EncodeToString(data),
			MIMEType:    mimeType,
			DisplayName: &displayName,
		})
		slog.Debug("attached image", "path", imagePath, "mimeType", mimeType)
	}

	for _, filePath := range opts.FilePaths {
		absPath, absErr := filepath.Abs(filePath)
		if absErr != nil {
			return "", nil, fmt.Errorf("failed to resolve file path %q: %w", filePath, absErr)
		}
		if _, statErr := os.Stat(absPath); statErr != nil {
			return "", nil, fmt.Errorf("failed to stat file %q: %w", filePath, statErr)
		}
		attachments = append(attachments, &copilot.AttachmentFile{
			DisplayName: filepath.Base(absPath),
			Path:        absPath,
		})
		slog.Debug("attached file", "path", absPath)
	}

	return systemMessage, attachments, nil
}

// newSession starts a Copilot client and creates a session with the given
// options. The caller is responsible for calling client.Stop().
func newSession(ctx context.Context, opts RunOptions, systemMessage string, streaming *bool) (*copilot.Client, *copilot.Session, error) {
	clientOpts := &copilot.ClientOptions{}
	if opts.CLIURL != "" {
		slog.Debug("connecting to running Copilot CLI", "url", opts.CLIURL)
		clientOpts.Connection = copilot.URIConnection{URL: opts.CLIURL}
	} else {
		slog.Debug("launching bundled Copilot CLI over stdio")
	}
	client := copilot.NewClient(clientOpts)

	if err := client.Start(ctx); err != nil {
		return nil, nil, fmt.Errorf("failed to start Copilot client: %w", err)
	}

	sessionCfg := &copilot.SessionConfig{
		OnPermissionRequest: permissionHandler(opts.Yolo),
		Streaming:           streaming,
	}
	if opts.Model != "" {
		sessionCfg.Model = opts.Model
	}
	if systemMessage != "" {
		sessionCfg.SystemMessage = &copilot.SystemMessageConfig{
			Mode:    "append",
			Content: systemMessage,
		}
	}

	session, err := client.CreateSession(ctx, sessionCfg)
	if err != nil {
		_ = client.Stop()
		return nil, nil, fmt.Errorf("failed to create session: %w", err)
	}
	slog.Debug("session created", "model", opts.Model, "streaming", streaming)

	return client, session, nil
}

func permissionHandler(yolo bool) copilot.PermissionHandlerFunc {
	if yolo {
		return copilot.PermissionHandler.ApproveAll
	}
	return func(request copilot.PermissionRequest, _ copilot.PermissionInvocation) (rpc.PermissionDecision, error) {
		switch request.(type) {
		case *copilot.PermissionRequestRead:
			return &rpc.PermissionDecisionApproveOnce{}, nil
		default:
			feedback := "Permission denied by default. Re-run with --yolo to approve all tool permission requests."
			return &rpc.PermissionDecisionReject{Feedback: &feedback}, nil
		}
	}
}

// imageMIMEType returns an image MIME type based on the file extension.
func imageMIMEType(path string) string {
	switch strings.ToLower(filepath.Ext(path)) {
	case ".jpg", ".jpeg":
		return "image/jpeg"
	case ".png":
		return "image/png"
	case ".gif":
		return "image/gif"
	case ".webp":
		return "image/webp"
	default:
		return "application/octet-stream"
	}
}
