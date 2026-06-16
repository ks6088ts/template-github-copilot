# Tutorial 2: Issue Triage Bot

**Subcommand:** `tutorial issue-triage`
**Source:** [`src/go/cmd/tutorial/issuetriage.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/issuetriage.go)

---

## What You Will Learn

- How to declare typed tool inputs and outputs with struct tags
- How to create tools with `copilot.DefineTool`, which generates a JSON schema from your types
- How to register tools on a session via `SessionConfig.Tools`
- How a tool-calling agent loop drives multiple tool calls from a single prompt
- How to observe tool calls through `ToolExecutionStartData` events

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- The Go CLI built with `make build` (see [Getting Started](../getting_started.md))

---

## Step 1 — Declare typed tool inputs and outputs

`copilot.DefineTool` turns a Go function into a tool. The argument and return types become the tool's JSON schema, so Copilot knows how to call it. The `jsonschema` struct tag supplies the field description shown to the model, while the `json` tag controls the wire format:

```go
// list_issues takes no arguments.
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
```

---

## Step 2 — Create tools with DefineTool

`copilot.DefineTool[T, U](name, description, handler)` is generic over the input type `T` and output type `U`. The handler receives the decoded arguments plus a `copilot.ToolInvocation` and returns a typed result — non-string results are JSON-serialized automatically:

```go
var (
    mu      sync.Mutex
    triaged []triageRecord
)

listIssues := copilot.DefineTool(
    "list_issues",
    "Return the list of open GitHub issues to triage.",
    func(_ listIssuesInput, _ copilot.ToolInvocation) (listIssuesOutput, error) {
        return listIssuesOutput{Issues: sampleIssues}, nil
    },
)

labelIssue := copilot.DefineTool(
    "label_issue",
    "Apply one or more labels to a GitHub issue.",
    func(in labelIssueInput, _ copilot.ToolInvocation) (labelIssueOutput, error) {
        mu.Lock()
        triaged = append(triaged, triageRecord{ID: in.IssueID, Labels: in.Labels})
        mu.Unlock()
        return labelIssueOutput{Success: true, IssueID: in.IssueID, AppliedLabels: in.Labels}, nil
    },
)
```

> **Note:** Tool handlers may be invoked from different goroutines, so guard any shared state (here the `triaged` slice) with a `sync.Mutex`.

---

## Step 3 — Register the tools on the session

Pass the tools to `SessionConfig.Tools`. The system message tells Copilot how to use them. This run uses `Streaming: copilot.Bool(false)` because we only care about the final summary, not incremental tokens:

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Tools:               []copilot.Tool{listIssues, labelIssue},
    Streaming:           copilot.Bool(false),
    SystemMessage: &copilot.SystemMessageConfig{
        Mode: "replace",
        Content: "You are an expert GitHub issue triage assistant. " +
            "Use list_issues to fetch open issues, classify each one as 'bug', " +
            "'enhancement', or 'documentation', then call label_issue to apply the " +
            "appropriate label. After triaging all issues, summarise your actions.",
    },
})
```

> **Note:** `Mode: "replace"` swaps in your system message entirely. Because custom tools are registered, `OnPermissionRequest` fires before each tool runs — `ApproveAll` lets every call through.

---

## Step 4 — Observe tool calls through events

Register an event handler to watch the agent work. `ToolExecutionStartData` fires each time Copilot invokes one of your tools:

```go
session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.ToolExecutionStartData:
        fmt.Fprintf(os.Stderr, "[Tool] Calling: %s\n", data.ToolName)
    case *copilot.SessionErrorData:
        fmt.Fprintf(os.Stderr, "[Error] %s\n", data.Message)
    }
})
```

---

## Step 5 — Run the triage turn and collect results

A single prompt kicks off the agent loop. Copilot decides to call `list_issues`, classifies each item, calls `label_issue` for each, then returns a summary. `SendPromptAndWait` blocks until the session is idle:

```go
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

labelsJSON, _ := json.MarshalIndent(applied, "", "  ")
fmt.Println("=== Triage Summary ===")
fmt.Println(content)
fmt.Println("\n=== Applied Labels ===")
fmt.Println(string(labelsJSON))
```

---

## Run the Subcommand

Build the CLI first, then run the `issue-triage` subcommand from the `src/go` directory:

```bash
cd src/go
make build

# Triage the built-in sample issues
./dist/template-github-copilot-go tutorial issue-triage

# Connect to a standalone CLI server (optional — only when one is running in TCP mode)
./dist/template-github-copilot-go tutorial issue-triage --cli-url localhost:3000
```

### Flags

| Flag | Shorthand | Default | Description |
|------|-----------|---------|-------------|
| `--cli-url` | `-c` | _(empty)_ | Optional Copilot CLI server URL (e.g. `localhost:3000`) |

> The global `--verbose`/`-v` flag lowers the log level to `DEBUG`, surfacing the client connection mode and session lifecycle.

---

## Next Steps

- Tutorial 3 — [Streaming Review](03_streaming_review.md): stream the response token by token
- Tutorial 5 — [Audit Log](05_audit_hooks.md): deny tool calls with a custom permission handler
- Browse the full Go API on [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go)
