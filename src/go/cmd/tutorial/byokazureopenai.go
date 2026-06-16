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

	"github.com/Azure/azure-sdk-for-go/sdk/azcore/policy"
	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	copilot "github.com/github/copilot-sdk/go"
	"github.com/spf13/cobra"
)

const byokSystemMessage = "You are a helpful assistant powered by Azure OpenAI."

// entraScope is the OAuth scope required to call Azure OpenAI with an Entra ID
// bearer token.
const entraScope = "https://cognitiveservices.azure.com/.default"

// byokAzureOpenAICmd is the Go counterpart of src/python/scripts/tutorials/06_byok_azure_openai.py.
//
// It routes the session through Azure OpenAI (BYOK) using a ProviderConfig,
// authenticating with either an API key or an Entra ID bearer token.
var byokAzureOpenAICmd = &cobra.Command{
	Use:   "byok-azure-openai",
	Short: "Bring Your Own Key: run a session through Azure OpenAI",
	Long: `BYOK (Bring Your Own Key) built on the GitHub Copilot SDK ProviderConfig.

Routes the session through an Azure OpenAI deployment instead of GitHub-hosted
models. Authenticate with an API key (--auth api-key) or an Entra ID bearer token
obtained via DefaultAzureCredential (--auth entra).

Equivalent Python tutorial:
    src/python/scripts/tutorials/06_byok_azure_openai.py
See the tutorial docs for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/go/tutorials/06_byok_azure_openai.md     (English)
    docs/copilot_sdk_tutorial/go/tutorials/06_byok_azure_openai.ja.md  (日本語)`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		prompt, err := cmd.Flags().GetString("prompt")
		if err != nil {
			return err
		}
		cliURL, err := cmd.Flags().GetString("cli-url")
		if err != nil {
			return err
		}
		auth, err := cmd.Flags().GetString("auth")
		if err != nil {
			return err
		}
		baseURL, err := cmd.Flags().GetString("base-url")
		if err != nil {
			return err
		}
		apiKey, err := cmd.Flags().GetString("api-key")
		if err != nil {
			return err
		}
		model, err := cmd.Flags().GetString("model")
		if err != nil {
			return err
		}

		if auth != "api-key" && auth != "entra" {
			return fmt.Errorf("--auth must be 'api-key' or 'entra', got %q", auth)
		}
		if baseURL == "" {
			return fmt.Errorf("--base-url (or BYOK_BASE_URL env var) is required for BYOK mode")
		}

		ctx, stop := signal.NotifyContext(cmd.Context(), os.Interrupt)
		defer stop()

		slog.Debug("running byok-azure-openai", "cliURL", cliURL, "auth", auth, "model", model)

		err = runByokAzureOpenAI(ctx, cliURL, prompt, auth, baseURL, apiKey, model)
		if ctx.Err() != nil {
			fmt.Println("\nBye!")
			return nil
		}
		return err
	},
}

func init() {
	tutorialCmd.AddCommand(byokAzureOpenAICmd)

	byokAzureOpenAICmd.Flags().StringP("prompt", "p", "Briefly explain what BYOK means in the context of AI APIs.", "Prompt to send")
	byokAzureOpenAICmd.Flags().StringP("cli-url", "c", "", "Optional Copilot CLI server URL (e.g. localhost:3000). When omitted, the SDK launches the copilot CLI over stdio.")
	byokAzureOpenAICmd.Flags().String("auth", "api-key", "Authentication method: api-key (default) or entra (Entra ID bearer token)")
	byokAzureOpenAICmd.Flags().String("base-url", os.Getenv("BYOK_BASE_URL"), "Azure OpenAI deployment base URL (defaults to BYOK_BASE_URL env var)")
	byokAzureOpenAICmd.Flags().String("api-key", os.Getenv("BYOK_API_KEY"), "Azure OpenAI API key (defaults to BYOK_API_KEY env var)")
	byokAzureOpenAICmd.Flags().String("model", byokModelDefault(), "Model/deployment name (defaults to BYOK_MODEL env var, or gpt-4o)")
}

// byokModelDefault resolves the default model from the BYOK_MODEL env var,
// falling back to gpt-4o.
func byokModelDefault() string {
	if v := os.Getenv("BYOK_MODEL"); v != "" {
		return v
	}
	return "gpt-4o"
}

// buildEntraBearerToken obtains an Azure Entra ID bearer token via DefaultAzureCredential.
func buildEntraBearerToken(ctx context.Context) (string, error) {
	credential, err := azidentity.NewDefaultAzureCredential(nil)
	if err != nil {
		return "", fmt.Errorf("failed to create Azure credential: %w", err)
	}
	token, err := credential.GetToken(ctx, policy.TokenRequestOptions{
		Scopes: []string{entraScope},
	})
	if err != nil {
		return "", fmt.Errorf("failed to acquire Entra ID token: %w", err)
	}
	return token.Token, nil
}

// runByokAzureOpenAI builds an Azure ProviderConfig and streams a single response.
func runByokAzureOpenAI(ctx context.Context, cliURL, prompt, auth, baseURL, apiKey, model string) error {
	provider := &copilot.ProviderConfig{
		Type:    "azure",
		BaseURL: baseURL,
	}
	switch auth {
	case "api-key":
		if apiKey == "" {
			return fmt.Errorf("--api-key (or BYOK_API_KEY env var) is required for api-key auth")
		}
		provider.APIKey = apiKey
		fmt.Fprintf(os.Stderr, "[Auth] Using API key authentication — model: %s\n", model)
	case "entra":
		bearerToken, err := buildEntraBearerToken(ctx)
		if err != nil {
			return err
		}
		provider.BearerToken = bearerToken
		fmt.Fprintf(os.Stderr, "[Auth] Using Entra ID bearer token — model: %s\n", model)
	}

	var client *copilot.Client
	if cliURL != "" {
		client = copilot.NewClient(&copilot.ClientOptions{
			Connection: copilot.URIConnection{URL: cliURL},
		})
	} else {
		client = copilot.NewClient(nil)
	}

	if err := client.Start(ctx); err != nil {
		return fmt.Errorf("failed to start Copilot client: %w", err)
	}
	defer func() { _ = client.Stop() }()

	session, err := client.CreateSession(ctx, &copilot.SessionConfig{
		OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
		Streaming:           copilot.Bool(true),
		Model:               model,
		Provider:            provider,
		SystemMessage:       &copilot.SystemMessageConfig{Content: byokSystemMessage},
	})
	if err != nil {
		return fmt.Errorf("failed to create session: %w", err)
	}

	fmt.Printf("\nYou: %s\nCopilot: ", prompt)

	session.On(func(event copilot.SessionEvent) {
		switch data := event.Data.(type) {
		case *copilot.AssistantMessageDeltaData:
			fmt.Print(data.DeltaContent)
		case *copilot.SessionErrorData:
			fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
		}
	})

	if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
		return err
	}

	fmt.Println()
	return nil
}
