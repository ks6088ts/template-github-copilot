# Tutorial 3: Streaming Review

**Subcommand:** `tutorial streaming-review`
**Source:** [`src/go/cmd/tutorial/streamingreview.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/streamingreview.go)

---

## What You Will Learn

- How to enable streaming with `Streaming: copilot.Bool(true)`
- How to consume streaming tokens via `AssistantMessageDeltaData`
- How to print a response incrementally as it is generated
- How to feed the model a unified diff read from a file or a built-in sample

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- The Go CLI built with `make build` (see [Getting Started](../getting_started.md))

---

## Step 1 — Enable streaming on the session

Streaming is a session-level setting. With `Streaming: copilot.Bool(true)`, the runtime emits `assistant.message_delta` events as the response is generated instead of delivering it all at once:

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true), // ← streaming enabled
    SystemMessage: &copilot.SystemMessageConfig{
        Mode: "replace",
        Content: "You are a senior software engineer conducting a thorough code review. " +
            "For each change in the diff: identify bugs, security issues, and style problems. " +
            "Be concise but precise. Use Markdown formatting.",
    },
})
```

---

## Step 2 — Print delta tokens as they arrive

Each `AssistantMessageDeltaData` event carries a `DeltaContent` fragment. Print it without a trailing newline so the output reads as continuous text:

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

> **Note:** With streaming enabled, the complete message still arrives as `AssistantMessageData` at the end of the turn. Use the deltas for live output and the full message when you need the final text in one piece.

---

## Step 3 — Send the diff and wait for completion

Embed the diff in the prompt inside a fenced code block. `SendPromptAndWait` blocks until the session is idle; by then every delta has already been printed by the handler:

```go
prompt := fmt.Sprintf("Please review the following diff and provide feedback:\n\n```diff\n%s\n```", diffText)
if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
    return err
}
fmt.Println("\n\n=== Review Complete ===")
```

The subcommand reviews a built-in sample diff by default. Pass `--diff <path>` to review your own unified diff; the file is read with `os.ReadFile` before the session starts.

---

## Run the Subcommand

Build the CLI first, then run the `streaming-review` subcommand from the `src/go` directory:

```bash
cd src/go
make build

# Review the built-in sample diff
./dist/template-github-copilot-go tutorial streaming-review

# Review your own unified diff
git diff > /tmp/changes.diff
./dist/template-github-copilot-go tutorial streaming-review --diff /tmp/changes.diff
```

### Flags

| Flag | Shorthand | Default | Description |
|------|-----------|---------|-------------|
| `--diff` | `-d` | _(empty)_ | Path to a unified diff file (uses the built-in sample if not provided) |
| `--cli-url` | `-c` | _(empty)_ | Optional Copilot CLI server URL (e.g. `localhost:3000`) |

> The global `--verbose`/`-v` flag lowers the log level to `DEBUG`, surfacing the client connection mode and session lifecycle.

---

## Next Steps

- Tutorial 4 — [Skills Doc Generation](04_skills_docgen.md): load reusable instructions from `SKILL.md` files
- Tutorial 1 — [CLI Chatbot](01_chat_bot.md): the streaming basics in an interactive loop
- Browse the full Go API on [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go)
