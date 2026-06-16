# Tutorial 6: BYOK Azure OpenAI

**Subcommand:** `tutorial byok-azure-openai`
**Source:** [`src/go/cmd/tutorial/byokazureopenai.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/byokazureopenai.go)

---

## What You Will Learn

- How to route a session through your own model provider with `SessionConfig.Provider`
- How to configure `copilot.ProviderConfig` for Azure OpenAI
- How to authenticate with an API key or an Entra ID bearer token
- How to obtain an Entra ID token with `DefaultAzureCredential`

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- The Go CLI built with `make build` (see [Getting Started](../getting_started.md))
- An Azure OpenAI deployment, plus either its API key or RBAC access for Entra ID authentication

---

## Step 1 — Build the Azure ProviderConfig

`copilot.ProviderConfig` describes a Bring Your Own Key (BYOK) provider. For Azure, set `Type: "azure"` and the deployment `BaseURL`. Supply an API key via `APIKey` or an Entra ID token via `BearerToken` — `BearerToken` takes precedence when both are set:

```go
provider := &copilot.ProviderConfig{
    Type:    "azure",
    BaseURL: baseURL,
}
switch auth {
case "api-key":
    provider.APIKey = apiKey
case "entra":
    bearerToken, err := buildEntraBearerToken(ctx)
    if err != nil {
        return err
    }
    provider.BearerToken = bearerToken
}
```

---

## Step 2 — Obtain an Entra ID bearer token

For keyless authentication, `DefaultAzureCredential` resolves credentials from the environment, a managed identity, the Azure CLI, and more. Request a token for the Cognitive Services scope:

```go
import (
    "github.com/Azure/azure-sdk-for-go/sdk/azcore/policy"
    "github.com/Azure/azure-sdk-for-go/sdk/azidentity"
)

func buildEntraBearerToken(ctx context.Context) (string, error) {
    credential, err := azidentity.NewDefaultAzureCredential(nil)
    if err != nil {
        return "", fmt.Errorf("failed to create Azure credential: %w", err)
    }
    token, err := credential.GetToken(ctx, policy.TokenRequestOptions{
        Scopes: []string{"https://cognitiveservices.azure.com/.default"},
    })
    if err != nil {
        return "", fmt.Errorf("failed to acquire Entra ID token: %w", err)
    }
    return token.Token, nil
}
```

> **Note:** For Entra ID authentication, sign in with `az login` (or configure a managed identity) and grant your principal the **Cognitive Services OpenAI User** role on the Azure OpenAI resource.

---

## Step 3 — Attach the provider to the session

Pass the provider and the model (deployment) name to `CreateSession`. Here the system message uses append mode (the default) so the SDK foundation is preserved and your instruction is added on top:

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true),
    Model:               model,
    Provider:            provider,
    SystemMessage:       &copilot.SystemMessageConfig{Content: "You are a helpful assistant powered by Azure OpenAI."},
})
```

> **Note:** When a custom provider is configured, GitHub-side session telemetry is automatically disabled. Requests go directly to your Azure OpenAI deployment.

---

## Step 4 — Stream the response

With streaming enabled, print delta tokens as they arrive:

```go
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
```

---

## Run the Subcommand

Set your Azure OpenAI details via environment variables (or pass the matching flags), then run from the `src/go` directory:

```bash
cd src/go
make build

# API key authentication (default)
export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deployment>"
export BYOK_API_KEY="<your-api-key>"
export BYOK_MODEL="gpt-4o"
./dist/template-github-copilot-go tutorial byok-azure-openai

# Entra ID authentication (keyless)
az login
export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deployment>"
export BYOK_MODEL="gpt-4o"
./dist/template-github-copilot-go tutorial byok-azure-openai --auth entra
```

### Flags

| Flag | Shorthand | Default | Description |
|------|-----------|---------|-------------|
| `--prompt` | `-p` | `Briefly explain what BYOK means …` | Prompt to send |
| `--auth` | | `api-key` | Authentication method: `api-key` or `entra` |
| `--base-url` | | `$BYOK_BASE_URL` | Azure OpenAI deployment base URL |
| `--api-key` | | `$BYOK_API_KEY` | Azure OpenAI API key (api-key auth) |
| `--model` | | `$BYOK_MODEL` or `gpt-4o` | Model/deployment name |
| `--cli-url` | `-c` | _(empty)_ | Optional Copilot CLI server URL (e.g. `localhost:3000`) |

### Environment variables

| Variable | Description |
|----------|-------------|
| `BYOK_BASE_URL` | Azure OpenAI deployment base URL (required) |
| `BYOK_API_KEY` | Azure OpenAI API key (required for `api-key` auth) |
| `BYOK_MODEL` | Model/deployment name (defaults to `gpt-4o`) |

> The global `--verbose`/`-v` flag lowers the log level to `DEBUG`, surfacing the client connection mode and session lifecycle.

---

## Next Steps

- Tutorial 1 — [CLI Chatbot](01_chat_bot.md): the same streaming flow on GitHub-hosted models
- [Architecture](../../architecture.md): how the SDK, CLI, and providers interact
- Browse the full Go API on [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go)
