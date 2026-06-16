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
	"bufio"
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"strings"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/spf13/cobra"
)

const chatBotSystemMessage = "You are a helpful assistant."

// chatBotCmd is the Go counterpart of src/python/scripts/tutorials/01_chat_bot.py.
//
// It sends a single prompt (default) or runs an interactive chat loop, streaming
// the assistant response to stdout via the GitHub Copilot SDK for Go.
var chatBotCmd = &cobra.Command{
	Use:   "chat-bot",
	Short: "CLI chatbot using the GitHub Copilot SDK",
	Long: `CLI chatbot using the GitHub Copilot SDK.

By default it sends a single prompt and prints the streamed response. Use
--loop to start an interactive chat loop (Ctrl+C or EOF to exit).

Equivalent Python tutorial:
    src/python/scripts/tutorials/01_chat_bot.py
See the tutorial docs for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/go/tutorials/01_chat_bot.md     (English)
    docs/copilot_sdk_tutorial/go/tutorials/01_chat_bot.ja.md  (日本語)`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		prompt, err := cmd.Flags().GetString("prompt")
		if err != nil {
			return err
		}
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}
		loop, err := cmd.Flags().GetBool("loop")
		if err != nil {
			return err
		}

		// Cancel on Ctrl+C so the chat loop can exit cleanly, mirroring the
		// Python KeyboardInterrupt handling that prints "Bye!".
		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running chat-bot", "loop", loop, "cliURL", cliURL)

		if loop {
			err = runChatLoop(ctx, cliURL)
		} else {
			err = runChatSingle(ctx, cliURL, prompt)
		}

		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	tutorialCmd.AddCommand(chatBotCmd)

	chatBotCmd.Flags().StringP("prompt", "p", "Hello, Copilot! What can you do?", "Prompt to send (single-shot mode)")
	chatBotCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
	chatBotCmd.Flags().BoolP("loop", "l", false, "Run in interactive chat loop mode (Ctrl+C to exit)")
}

// newChatSession starts a Copilot client and creates a streaming chat session.
//
// When cliURL is non-empty the SDK connects to an already-running runtime;
// otherwise it launches the bundled copilot CLI over stdio. The returned client
// must be stopped by the caller (defer client.Stop()).
func newChatSession(ctx context.Context, cliURL string) (*copilot.Client, *copilot.Session, error) {
	var client *copilot.Client
	if cliURL != "" {
		slog.Debug("connecting to running Copilot CLI", "url", cliURL)
		client = copilot.NewClient(&copilot.ClientOptions{
			Connection: copilot.URIConnection{URL: cliURL},
		})
	} else {
		slog.Debug("launching bundled Copilot CLI over stdio")
		client = copilot.NewClient(nil)
	}

	if err := client.Start(ctx); err != nil {
		return nil, nil, fmt.Errorf("failed to start Copilot client: %w", err)
	}
	slog.Debug("Copilot client started")

	session, err := client.CreateSession(ctx, &copilot.SessionConfig{
		OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
		Streaming:           copilot.Bool(true),
		SystemMessage:       &copilot.SystemMessageConfig{Content: chatBotSystemMessage},
	})
	if err != nil {
		_ = client.Stop()
		return nil, nil, fmt.Errorf("failed to create session: %w", err)
	}
	slog.Debug("chat session created", "streaming", true)

	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.AssistantMessageDeltaData:
			fmt.Print(data.DeltaContent)
		case *copilot.SessionErrorData:
			fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
		}
	})

	return client, session, nil
}

// runChatSingle sends a single prompt and prints the streamed response.
func runChatSingle(ctx context.Context, cliURL, prompt string) error {
	client, session, err := newChatSession(ctx, cliURL)
	if err != nil {
		return err
	}
	defer func() { _ = client.Stop() }()

	reply, err := session.SendPromptAndWait(ctx, prompt)
	if err != nil {
		return err
	}

	// Ensure a newline after the streamed output.
	fmt.Println()

	var content string
	if reply != nil {
		if data, ok := reply.Data.(*copilot.AssistantMessageData); ok {
			content = data.Content
		}
	}
	if content == "" {
		fmt.Fprintln(os.Stderr, "(no response)")
	}
	return nil
}

// runChatLoop runs an interactive chat loop until Ctrl+C or EOF.
func runChatLoop(ctx context.Context, cliURL string) error {
	client, session, err := newChatSession(ctx, cliURL)
	if err != nil {
		return err
	}
	defer func() { _ = client.Stop() }()

	fmt.Println("Chat with Copilot — type your message and press Enter (Ctrl+C to quit)")
	fmt.Println()

	// Read stdin from a goroutine so Ctrl+C (context cancellation) can interrupt
	// the otherwise-blocking read.
	lines := make(chan string)
	go func() {
		scanner := bufio.NewScanner(os.Stdin)
		for scanner.Scan() {
			lines <- scanner.Text()
		}
		close(lines)
	}()

	for {
		fmt.Print("You: ")
		select {
		case <-ctx.Done():
			return nil
		case line, ok := <-lines:
			if !ok {
				// EOF on stdin.
				return nil
			}
			userInput := strings.TrimSpace(line)
			if userInput == "" {
				continue
			}
			fmt.Print("Copilot: ")
			if _, err := session.SendPromptAndWait(ctx, userInput); err != nil {
				if ctx.Err() != nil {
					return nil
				}
				return err
			}
			fmt.Println()
		}
	}
}
