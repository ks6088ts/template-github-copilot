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

	copilot "github.com/github/copilot-sdk/go"
	"github.com/spf13/cobra"
)

// runCmd represents the run command.
//
// It sends a single prompt to the GitHub Copilot SDK, optionally loading a
// system message from an agents.md file and attaching an image for
// vision-capable models.
var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run a Copilot session from the command line",
	Long: `Run a Copilot session with a prompt, optional model, system message from
an agents.md file, and image attachment for vision-capable models.

The response is streamed to stdout as it is generated. Requires the GitHub
Copilot CLI to be installed and authenticated.

Examples:
  # Simple prompt with the default model
  template-github-copilot-go run --prompt "Explain goroutines in Go"

  # Specify a model
  template-github-copilot-go run --model gpt-4o --prompt "What is recursion?"

  # Load a system message from agents.md
  template-github-copilot-go run --agents-file agents.md --prompt "Summarise the project"

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
		imagePath, err := cmd.Flags().GetString("image")
		if err != nil {
			return err
		}
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running run",
			"model", model,
			"agentsFile", agentsFile,
			"imagePath", imagePath,
			"cliURL", cliURL,
		)

		err = RunSession(ctx, RunOptions{
			Model:      model,
			Prompt:     prompt,
			AgentsFile: agentsFile,
			ImagePath:  imagePath,
			CLIURL:     cliURL,
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
	runCmd.Flags().StringP("agents-file", "a", "", "Path to an agents.md file whose content is used as the system message")
	runCmd.Flags().StringP("image", "i", "", "Path to an image file to attach to the message (requires a vision-capable model)")
	runCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
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
	// whose contents are used as the session system message.
	AgentsFile string
	// ImagePath is the optional path to an image file attached to the message.
	// The model must support vision for this to have an effect.
	ImagePath string
	// CLIURL is the optional Copilot CLI server URL (e.g. "localhost:3000").
	// When empty, the SDK spawns the bundled CLI over stdio.
	CLIURL string
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
	systemMessage, attachments, err := buildSessionInputs(opts)
	if err != nil {
		return "", err
	}

	client, session, err := newSession(ctx, opts, systemMessage, copilot.Bool(false))
	if err != nil {
		return "", err
	}
	defer func() { _ = client.Stop() }()

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

	if opts.ImagePath != "" {
		data, readErr := os.ReadFile(opts.ImagePath)
		if readErr != nil {
			return "", nil, fmt.Errorf("failed to read image file %q: %w", opts.ImagePath, readErr)
		}
		mimeType := imageMIMEType(opts.ImagePath)
		displayName := filepath.Base(opts.ImagePath)
		attachments = append(attachments, &copilot.AttachmentBlob{
			Data:        base64.StdEncoding.EncodeToString(data),
			MIMEType:    mimeType,
			DisplayName: &displayName,
		})
		slog.Debug("attached image", "path", opts.ImagePath, "mimeType", mimeType)
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
		OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
		Streaming:           streaming,
	}
	if opts.Model != "" {
		sessionCfg.Model = opts.Model
	}
	if systemMessage != "" {
		sessionCfg.SystemMessage = &copilot.SystemMessageConfig{
			Mode:    "replace",
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
