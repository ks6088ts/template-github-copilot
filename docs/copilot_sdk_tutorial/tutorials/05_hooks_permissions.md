# Tutorial 5: Audit Log with Session Hooks and Permission Handling

**Script:** [`src/python/scripts/tutorials/05_audit_hooks.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/05_audit_hooks.py)

---

## What You Will Learn

- How to intercept all session events via `session.on()`
- How to implement a custom `on_permission_request` handler
- How to approve or deny specific tool executions
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

## Step 2 — Implement a permission handler

The `on_permission_request` callback is invoked before **every** tool execution. Return `approved` or `denied` based on your policy:

```python
from copilot.types import PermissionRequest, PermissionRequestResult

def permission_handler(
    request: PermissionRequest,
    context: dict,
) -> PermissionRequestResult:
    tool_name = getattr(request, "tool_name", "unknown")

    # Example: deny all tool calls (useful for read-only auditing)
    if should_deny(tool_name):
        print(f"[Permission] DENIED: {tool_name}")
        return PermissionRequestResult(kind="denied-interactively-by-user", rules=[])

    print(f"[Permission] APPROVED: {tool_name}")
    return PermissionRequestResult(kind="approved", rules=[])
```

Register it in the session config:

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=permission_handler,
        ...
    )
)
```

---

## Step 3 — Run and inspect the audit log

```python
reply = await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
print(reply.data.content)

print("\n=== Audit Log ===")
print(json.dumps(audit_log, indent=2))
```

Sample audit log output:

```json
[
  {"ts": 0.001, "event": "SEND", "detail": "What are 3 best practices..."},
  {"ts": 0.012, "event": "TURN_START", "detail": ""},
  {"ts": 0.015, "event": "INTENT", "detail": "answer_question"},
  {"ts": 2.341, "event": "TURN_END", "detail": ""},
  {"ts": 2.342, "event": "SESSION_IDLE", "detail": ""}
]
```

---

## Permission Handler Patterns

| Pattern | Use Case |
|---------|---------|
| `approved` for all | Development / trusted environments |
| `denied` for all | Read-only audit mode — no side effects |
| Approve by tool name | Allow specific safe tools, deny risky ones |
| Prompt user | Interactive approval for sensitive actions |
| Log then approve | Record every tool call without blocking |

---

## Run the Script

```bash
cd src/python

# Approve all tools (default)
uv run python scripts/tutorials/05_audit_hooks.py \
    --prompt "What are best practices for Python error handling?"

# Deny all tool calls
uv run python scripts/tutorials/05_audit_hooks.py --deny-tools

# Custom CLI server (optional)
uv run python scripts/tutorials/05_audit_hooks.py --cli-url localhost:3000
```

---

## Key Takeaways

- `session.on(handler)` intercepts every session event — use it for logging, monitoring, and testing
- `on_permission_request` is called before every tool execution and controls whether it runs
- Both hooks receive rich event data (tool name, intent, error details, etc.)
- Build a timestamped audit log to track the agent's full behaviour across a session
- `denied` responses from the permission handler still allow the session to continue

---

## Next Tutorial

[Tutorial 6: BYOK with Azure OpenAI →](06_byok.md)
