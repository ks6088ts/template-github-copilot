# Tutorial 5: Audit Log

**Subcommand:** `tutorial audit-hooks`
**Source:** [`src/go/cmd/tutorial/audithooks.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/audithooks.go)

---

## What You Will Learn

- How to write a custom permission handler that approves or denies tool calls
- How to read the tool name from a `PermissionRequest` interface value
- How to return `rpc.PermissionDecisionApproveOnce` or `rpc.PermissionDecisionReject`
- How to record every session event into a timestamped audit log
- How a denied tool call never reaches your tool implementation

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- The Go CLI built with `make build` (see [Getting Started](../getting_started.md))

---

## Step 1 — Model a destructive operation as a tool

`delete_record` stands in for an irreversible action that an audit policy may want to block. It records which IDs were actually deleted so you can observe whether the permission handler let the call through:

```go
type deleteRecordInput struct {
    RecordID int `json:"record_id" jsonschema:"numeric ID of the customer record to delete"`
}

type deleteRecordOutput struct {
    Success  bool   `json:"success"`
    RecordID int    `json:"record_id"`
    Message  string `json:"message"`
}

deleteRecord := copilot.DefineTool(
    "delete_record",
    "Permanently delete a customer record by its numeric ID.",
    func(in deleteRecordInput, _ copilot.ToolInvocation) (deleteRecordOutput, error) {
        mu.Lock()
        deleted = append(deleted, in.RecordID)
        mu.Unlock()
        return deleteRecordOutput{
            Success:  true,
            RecordID: in.RecordID,
            Message:  fmt.Sprintf("Record %d permanently deleted.", in.RecordID),
        }, nil
    },
)
```

---

## Step 2 — Write a custom permission handler

A permission handler receives the request and returns an `rpc.PermissionDecision`. `PermissionRequest` is an interface, so type-switch to `*copilot.PermissionRequestCustomTool` to read the tool name. Returning `*rpc.PermissionDecisionReject` blocks the call; the tool implementation never runs:

```go
import "github.com/github/copilot-sdk/go/rpc"

permissionHandler := func(request copilot.PermissionRequest, _ copilot.PermissionInvocation) (rpc.PermissionDecision, error) {
    toolName := "unknown"
    if ct, ok := request.(*copilot.PermissionRequestCustomTool); ok {
        toolName = ct.ToolName
    }
    if denyTools {
        record("PERMISSION_DENIED", "tool="+toolName)
        feedback := "Tool execution denied by audit policy"
        return &rpc.PermissionDecisionReject{Feedback: &feedback}, nil
    }
    record("PERMISSION_APPROVED", "tool="+toolName)
    return &rpc.PermissionDecisionApproveOnce{}, nil
}
```

> **Note:** The handler fires only because the session registers a custom tool. With no tools, no permission requests are raised.

---

## Step 3 — Record every session event

`record` appends a timestamped entry guarded by a mutex. The event handler maps each event payload to an audit entry, building a chronological trail of the agent's turn:

```go
record := func(event, detail string) {
    mu.Lock()
    auditLog = append(auditLog, auditEntry{
        TS:     math.Round(time.Since(start).Seconds()*1000) / 1000,
        Event:  event,
        Detail: detail,
    })
    mu.Unlock()
}

session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.AssistantTurnStartData:
        record("TURN_START", "")
    case *copilot.AssistantIntentData:
        record("INTENT", data.Intent)
    case *copilot.ToolExecutionStartData:
        record("TOOL_START", data.ToolName)
    case *copilot.ToolExecutionCompleteData:
        detail := "error=<nil>"
        if data.Error != nil {
            detail = "error=" + data.Error.Message
        }
        record("TOOL_COMPLETE", detail)
    case *copilot.AssistantTurnEndData:
        record("TURN_END", "")
    case *copilot.SessionIdleData:
        record("SESSION_IDLE", "")
    case *copilot.SessionErrorData:
        record("SESSION_ERROR", data.Message)
    }
})
```

---

## Step 4 — Run the turn and print the audit log

After the turn completes, print the response, the records that were actually deleted, and the full audit log as JSON:

```go
reply, err := session.SendPromptAndWait(ctx, prompt)
// ... extract content from reply.Data ...

logJSON, _ := json.MarshalIndent(auditLog, "", "  ")
fmt.Println("=== Deleted Records ===")
if len(deleted) == 0 {
    fmt.Println("(none — tool was not executed)")
} else {
    fmt.Println(deleted)
}
fmt.Println("\n=== Audit Log ===")
fmt.Println(string(logJSON))
```

When you pass `--deny-tools`, the deleted-records list stays empty: the permission handler rejected the call before `delete_record` could run, and the audit log records a `PERMISSION_DENIED` entry.

---

## Run the Subcommand

Build the CLI first, then run the `audit-hooks` subcommand from the `src/go` directory:

```bash
cd src/go
make build

# Default: the audit policy approves the delete_record tool call
./dist/template-github-copilot-go tutorial audit-hooks

# --deny-tools: the audit policy rejects the tool call (it never executes)
./dist/template-github-copilot-go tutorial audit-hooks --deny-tools
```

### Flags

| Flag | Shorthand | Default | Description |
|------|-----------|---------|-------------|
| `--prompt` | `-p` | `Delete the customer record with ID 42 …` | Prompt to send to Copilot |
| `--cli-url` | `-c` | _(empty)_ | Optional Copilot CLI server URL (e.g. `localhost:3000`) |
| `--deny-tools` | | `false` | Use a permission handler that denies all tool executions |

> The global `--verbose`/`-v` flag lowers the log level to `DEBUG`, surfacing the client connection mode and session lifecycle.

---

## Next Steps

- Tutorial 6 — [BYOK Azure OpenAI](06_byok_azure_openai.md): route the session through your own model provider
- Tutorial 2 — [Issue Triage Bot](02_issue_triage.md): the tool-calling basics without a permission policy
- Browse the full Go API on [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go)
