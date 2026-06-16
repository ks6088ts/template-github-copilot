# Tutorial 1: CLI Chatbot

**Subcommand:** `tutorial chat-bot`
**Source:** [`src/go/cmd/tutorial/chatbot.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/chatbot.go)

---

## What You Will Learn

- How to create a `copilot.Client` and start it
- How to create a session with a system message and permission handler
- How to send a single prompt and receive a response
- How to consume streaming tokens via `AssistantMessageDeltaData`
- How to run an interactive chat loop that exits cleanly on `Ctrl+C`

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- The Go CLI built with `make build` (see [Getting Started](../getting_started.md))

---

## Step 1 — Create and start the client

The `copilot.Client` is the main entry point. By default it launches the `copilot` binary as a subprocess and talks to it over stdio. Pass a `Connection` only if you already have a Copilot CLI running in TCP mode:

```go
import (
    "context"

    copilot "github.com/github/copilot-sdk/go"
)

// Default: SDK launches the CLI over stdio
client := copilot.NewClient(nil)

// Optional: connect to an already-running CLI server (TCP mode)
// client := copilot.NewClient(&copilot.ClientOptions{
//     Connection: copilot.URIConnection{URL: "localhost:3000"},
// })

if err := client.Start(ctx); err != nil {
    return fmt.Errorf("failed to start Copilot client: %w", err)
}
defer func() { _ = client.Stop() }()
```

> **Note:** `client.Start(ctx)` establishes the JSON-RPC connection. Call it before creating any sessions, and pair it with `client.Stop()` (here via `defer`) to release the subprocess.

---

## Step 2 — Configure the session

`CreateSession` accepts a `*copilot.SessionConfig` that groups everything related to a single conversation:

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true),
    SystemMessage:       &copilot.SystemMessageConfig{Content: "You are a helpful assistant."},
})
if err != nil {
    return fmt.Errorf("failed to create session: %w", err)
}
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `OnPermissionRequest` | Called before each tool execution. `copilot.PermissionHandler.ApproveAll` approves every request |
| `Streaming` | `copilot.Bool(true)` receives tokens incrementally; omit (or `false`) to wait for the full response |
| `SystemMessage` | Sets the assistant's persona via `&copilot.SystemMessageConfig{Content: ...}` |

---

## Step 3 — Handle session events

Session events are pushed via `session.On(handler)`. The Go SDK delivers each event's payload as `event.Data`, which you inspect with a type switch — this is where streaming output and errors arrive:

```go
session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.AssistantMessageDeltaData:
        fmt.Print(data.DeltaContent)
    case *copilot.SessionErrorData:
        fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
    }
})
```

**Common event payload types:**

| Type | When it fires |
|------|---------------|
| `*copilot.AssistantMessageDeltaData` | A streaming token arrives |
| `*copilot.AssistantMessageData` | The complete assistant message is ready |
| `*copilot.SessionErrorData` | An error occurred |

---

## Step 4 — Send a prompt

```go
reply, err := session.SendPromptAndWait(ctx, prompt)
if err != nil {
    return err
}

var content string
if reply != nil {
    if data, ok := reply.Data.(*copilot.AssistantMessageData); ok {
        content = data.Content
    }
}
```

`SendPromptAndWait` blocks until the session becomes idle. During that time, streaming deltas are delivered to the handler you registered with `session.On`. The returned `reply` carries the full message in its `Data` field.

---

## Step 5 — Interactive chat loop

For a multi-turn conversation, keep the session alive and call `SendPromptAndWait` in a loop. Stdin is read from a goroutine so that `Ctrl+C` (context cancellation) can interrupt the otherwise-blocking read:

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
defer stop()

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
            return nil // EOF on stdin
        }
        userInput := strings.TrimSpace(line)
        if userInput == "" {
            continue
        }
        fmt.Print("Copilot: ")
        if _, err := session.SendPromptAndWait(ctx, userInput); err != nil {
            return err
        }
        fmt.Println()
    }
}
```

---

## Run the Subcommand

Build the CLI first, then run the `chat-bot` subcommand from the `src/go` directory:

```bash
cd src/go
make build

# Single prompt
./dist/template-github-copilot-go tutorial chat-bot --prompt "Explain goroutines in Go"

# Interactive loop (Ctrl+C or EOF to exit)
./dist/template-github-copilot-go tutorial chat-bot --loop

# Custom CLI server URL (optional — only when a CLI server is running in TCP mode)
./dist/template-github-copilot-go tutorial chat-bot --cli-url localhost:3000 --loop
```

### Flags

| Flag | Shorthand | Default | Description |
|------|-----------|---------|-------------|
| `--prompt` | `-p` | `Hello, Copilot! What can you do?` | Prompt to send (single-shot mode) |
| `--cli-url` | `-c` | _(empty)_ | Optional Copilot CLI server URL (e.g. `localhost:3000`) |
| `--loop` | `-l` | `false` | Run in interactive chat loop mode (Ctrl+C to exit) |

> The global `--verbose`/`-v` flag lowers the log level to `DEBUG`, surfacing the client connection mode and session lifecycle.

---

## Connecting to a Standalone CLI Server (TCP)

By default the SDK launches the `copilot` CLI as a subprocess and talks to it over stdio. Alternatively, you can run the CLI as a long-lived TCP server and connect to it via `--cli-url`. This is useful when you want to share a single authenticated CLI process across multiple runs.

### Step 1 — Start the CLI server

In a separate terminal, start the CLI in server mode:

```bash
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
copilot --server --port 3000 --log-level all \
  --allow-all-tools --allow-all-paths --allow-all-urls
```

### Step 2 — Connect from the subcommand

In another terminal, point the subcommand at the running server:

```bash
cd src/go
./dist/template-github-copilot-go tutorial chat-bot \
  --cli-url localhost:3000 --prompt "Reply with exactly: connection ok"
```

A successful run returns the assistant's response (e.g. `connection ok`).

---

## Next Steps

- Browse the full Go API on [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go)
