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
	"path/filepath"

	copilot "github.com/github/copilot-sdk/go"
	"github.com/spf13/cobra"
)

const skillsDocgenSystemMessage = "You are a Go documentation specialist. " +
	"Generate clear, complete godoc-style doc comments for all exported functions " +
	"in the provided code. Return only the updated code with doc comments added."

// defaultSkillsDir is resolved relative to the working directory the docs tell
// users to run from (src/go), so `skills-docgen` finds the bundled SKILL.md
// files at cmd/tutorial/skills without any flags.
const defaultSkillsDir = "cmd/tutorial/skills"

// sampleGoCode is the input the docgen skill annotates. The functions
// deliberately ship without doc comments.
const sampleGoCode = `func CalculateDiscount(price, discountPct float64) (float64, error) {
    if discountPct < 0 || discountPct > 100 {
        return 0, fmt.Errorf("discountPct must be between 0 and 100")
    }
    return price * (1 - discountPct/100), nil
}

func BatchProcess(items []string, handler func(string) (string, error)) []string {
    results := make([]string, 0, len(items))
    for _, item := range items {
        out, err := handler(item)
        if err != nil {
            results = append(results, "ERROR: "+err.Error())
            continue
        }
        results = append(results, out)
    }
    return results
}
`

// skillsDocgenCmd is the Go counterpart of src/python/scripts/tutorials/04_skills_docgen.py.
//
// It loads SKILL.md files from a skills directory via SessionConfig.SkillDirectories,
// then asks Copilot to document sample Go code using the loaded docgen skill.
var skillsDocgenCmd = &cobra.Command{
	Use:   "skills-docgen",
	Short: "Document Go code using skills loaded from SKILL.md files",
	Long: `Documentation generation built on the GitHub Copilot SDK skills feature.

Loads SKILL.md files from a skills directory (SessionConfig.SkillDirectories) and
asks Copilot to add godoc-style doc comments to sample Go code using the loaded
docgen skill. Bundled skills live at cmd/tutorial/skills.

Equivalent Python tutorial:
    src/python/scripts/tutorials/04_skills_docgen.py
See the tutorial docs for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/go/tutorials/04_skills_docgen.md     (English)
    docs/copilot_sdk_tutorial/go/tutorials/04_skills_docgen.ja.md  (日本語)`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}
		skillsDir, err := cmd.Flags().GetString("skills-dir")
		if err != nil {
			return err
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running skills-docgen", "cliURL", cliURL, "skillsDir", skillsDir)

		err = runSkillsDocgen(ctx, cliURL, skillsDir)
		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	tutorialCmd.AddCommand(skillsDocgenCmd)

	skillsDocgenCmd.Flags().StringP("skills-dir", "s", defaultSkillsDir, "Path to the skills directory containing SKILL.md files (relative to the current directory)")
	skillsDocgenCmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
}

// runSkillsDocgen loads skills (when the directory exists) and generates documentation.
func runSkillsDocgen(ctx context.Context, cliURL, skillsDir string) error {
	// Resolve to an absolute path so the CLI runtime locates the skills
	// regardless of its own working directory.
	var skillDirectories []string
	if absDir, err := filepath.Abs(skillsDir); err == nil {
		if info, statErr := os.Stat(absDir); statErr == nil && info.IsDir() {
			skillDirectories = []string{absDir}
			fmt.Fprintf(os.Stderr, "[Info] Loading skills from: %s\n", absDir)
		} else {
			fmt.Fprintf(os.Stderr, "[Warning] Skills directory not found: %s. Running without skills.\n", skillsDir)
		}
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
		OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
		Streaming:           copilot.Bool(true),
		SkillDirectories:    skillDirectories,
		SystemMessage:       &copilot.SystemMessageConfig{Mode: "replace", Content: skillsDocgenSystemMessage},
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %w", err)
	}

	fmt.Println("=== Generating Documentation ===")
	fmt.Println()

	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.AssistantMessageDeltaData:
			fmt.Print(data.DeltaContent)
		case *copilot.ToolExecutionStartData:
			fmt.Fprintf(os.Stderr, "\n[Skill] Running: %s\n", data.ToolName)
		case *copilot.SessionErrorData:
			fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
		}
	})

	prompt := fmt.Sprintf("Please add godoc-style doc comments to all functions in the following code:\n\n```go\n%s\n```", sampleGoCode)
	if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
		return err
	}

	fmt.Println("\n\n=== Done ===")
	return nil
}
