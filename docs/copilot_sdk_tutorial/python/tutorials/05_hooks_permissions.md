# Tutorial 5: Audit Log with Session Hooks and Permission Handling

**Script:** [`src/python/scripts/tutorials/05_audit_hooks.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/05_audit_hooks.py)

---

## What You Will Learn

- How to intercept all session events via `session.on()`
- How to implement a custom `on_permission_request` handler
- How to approve or deny specific tool executions
- Why the permission handler only fires when the session registers a tool
- How to build a structured audit log from the event stream

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- `github-copilot-sdk` installed

---

## Session Hooks

`session.on(handler)` is the primary way to observe everything that happens in a session. Every event — from turn starts to tool calls to errors — passes through your handler.

This makes `session.on` ideal for:

- **Audit logging** — record who called what and when
- **Monitoring** — track tool usage, latency, and errors
- **Progress display** — show users what the agent is doing in real time
- **Testing** — assert that specific events occurred in the right order

---

## Step 1 — Build an audit log with session events

```python
import time
import json
from typing import Any
from copilot.generated.session_events import SessionEventType

audit_log: list[dict[str, Any]] = []
start_time = time.time()

def record(event_name: str, detail: str = "") -> None:
    audit_log.append({
        "ts": round(time.time() - start_time, 3),
        "event": event_name,
        "detail": detail,
    })

def on_event(event: Any) -> None:
    et = event.type
    if et == SessionEventType.ASSISTANT_TURN_START:
        record("TURN_START")
    elif et == SessionEventType.ASSISTANT_INTENT:
        record("INTENT", event.data.intent)
    elif et == SessionEventType.TOOL_EXECUTION_START:
        record("TOOL_START", event.data.tool_name)
    elif et == SessionEventType.TOOL_EXECUTION_COMPLETE:
        err = getattr(event.data, "error", None)
        record("TOOL_COMPLETE", f"error={err.message if err else None}")
    elif et == SessionEventType.ASSISTANT_TURN_END:
        record("TURN_END")
    elif et == SessionEventType.SESSION_IDLE:
        record("SESSION_IDLE")
    elif et == SessionEventType.SESSION_ERROR:
        record("SESSION_ERROR", event.data.message)

session.on(on_event)
```

---

## Step 2 — Register a tool and a permission handler

The `on_permission_request` callback is invoked before **every tool execution** — so if a session registers no tools, the handler never fires. This tutorial registers a `delete_record` tool that models a destructive action an audit policy may want to block:

```python
from copilot.tools import define_tool
from pydantic import BaseModel


class DeleteRecordInput(BaseModel):
    record_id: int


class DeleteRecordOutput(BaseModel):
    success: bool
    record_id: int
    message: str


deleted_records: list[int] = []


@define_tool(
    name="delete_record",
    description="Permanently delete a customer record by its numeric ID.",
)
def delete_record(input: DeleteRecordInput) -> DeleteRecordOutput:
    deleted_records.append(input.record_id)
    return DeleteRecordOutput(
        success=True,
        record_id=input.record_id,
        message=f"Record {input.record_id} permanently deleted.",
    )
```

The handler returns `PermissionDecisionApproveOnce()` to allow a call or `PermissionDecisionReject(feedback=...)` to block it. Record the decision in the audit log so you can see it later:

```python
from copilot.generated.rpc import (
    PermissionDecisionApproveOnce,
    PermissionDecisionReject,
)
from copilot.generated.session_events import PermissionRequest
from copilot.session import PermissionRequestResult

def permission_handler(
    request: PermissionRequest,
    context: dict,
) -> PermissionRequestResult:
    tool_name = getattr(request, "tool_name", "unknown")

    # Example: deny all tool calls (useful for read-only auditing)
    if deny_tools:
        record("PERMISSION_DENIED", f"tool={tool_name}")
        print(f"[Permission] DENIED: {tool_name}")
        return PermissionDecisionReject(feedback="Tool execution denied by audit policy")

    record("PERMISSION_APPROVED", f"tool={tool_name}")
    print(f"[Permission] APPROVED: {tool_name}")
    return PermissionDecisionApproveOnce()
```

Register the tool and handler when you create the session:

```python
session = await client.create_session(
    on_permission_request=permission_handler,
    tools=[delete_record],
    streaming=False,
    system_message=SystemMessageReplaceConfig(
        mode="replace",
        content="You are an operations assistant with access to a delete_record tool.",
    ),
)
```

---

## Step 3 — Run and inspect the audit log

```python
reply = await session.send_and_wait(prompt, timeout=300)
content = getattr(reply.data, "content", None) if reply else "(no response)"
print(content)

print("\n=== Audit Log ===")
print(json.dumps(audit_log, indent=2))
```

Sample audit log output (default — the policy **approves** the `delete_record` call):

```json
[
  {"ts": 1.584, "event": "SEND", "detail": "Delete the customer record with ID 42..."},
  {"ts": 4.085, "event": "TURN_START", "detail": ""},
  {"ts": 6.8, "event": "TOOL_START", "detail": "delete_record"},
  {"ts": 6.8, "event": "PERMISSION_APPROVED", "detail": "tool=delete_record"},
  {"ts": 6.82, "event": "TOOL_COMPLETE", "detail": "error=None"},
  {"ts": 6.82, "event": "TURN_END", "detail": ""},
  {"ts": 9.615, "event": "SESSION_IDLE", "detail": ""}
]
```

Run with `--deny-tools` and the handler returns `PermissionDecisionReject(...)`: the `delete_record` implementation never runs, the audit log records `PERMISSION_DENIED`, and the assistant reports that the action was blocked by policy.

---

## Permission Handler Patterns

| Pattern | Use Case |
|---------|---------|
| `PermissionDecisionApproveOnce()` for all | Development / trusted environments |
| `PermissionDecisionReject(...)` for all | Read-only audit mode — no side effects |
| Approve by tool name | Allow specific safe tools, deny risky ones |
| Prompt user | Interactive approval for sensitive actions |
| Log then approve | Record every tool call without blocking |

---

## Run the Script

```bash
cd src/python

# Approve the delete_record tool (default) — the record is deleted
uv run python scripts/tutorials/05_audit_hooks.py

# Deny all tool calls — the delete_record call is blocked and never runs
uv run python scripts/tutorials/05_audit_hooks.py --deny-tools

# Send your own prompt
uv run python scripts/tutorials/05_audit_hooks.py \
    --prompt "Delete the customer record with ID 7 using the delete_record tool."

# Custom CLI server (optional)
uv run python scripts/tutorials/05_audit_hooks.py --cli-url localhost:3000
```

---

## Key Takeaways

- `session.on(handler)` intercepts every session event — use it for logging, monitoring, and testing
- `on_permission_request` is called before every tool execution and controls whether it runs
- The handler only fires when the session registers a tool — with `tools=[]` it is never invoked
- Both hooks receive rich event data (tool name, intent, error details, etc.)
- Build a timestamped audit log to track the agent's full behaviour across a session
- A `PermissionDecisionReject(...)` response blocks the tool but lets the session continue

---

## Next Tutorial

[Tutorial 6: BYOK with Azure OpenAI →](06_byok.md)
