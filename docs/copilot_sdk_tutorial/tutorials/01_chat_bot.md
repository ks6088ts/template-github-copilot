# Tutorial 1: CLI Chatbot

**Script:** [`src/python/scripts/tutorials/01_chat_bot.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/01_chat_bot.py)

---

## What You Will Learn

- How to create a `CopilotClient` and connect to the CLI server
- How to create a `SessionConfig` with a system message and permission handler
- How to send a single prompt and receive a response
- How to consume streaming tokens via `ASSISTANT_MESSAGE_DELTA`
- How to run an interactive chat loop

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- `github-copilot-sdk` installed

---

## Step 1 — Create and start the client

The `CopilotClient` is the main entry point. By default it launches the `copilot` binary as a subprocess and talks to it over stdio. Pass `cli_url` only if you already have a Copilot CLI running in TCP mode:

```python
from copilot import CopilotClient
from copilot.types import CopilotClientOptions

# Default: SDK launches the CLI over stdio
client = CopilotClient()

# Optional: connect to an already-running CLI server
# client = CopilotClient(options=CopilotClientOptions(cli_url="localhost:3000"))

await client.start()
```

> **Note:** `await client.start()` establishes the JSON-RPC connection. Call it before creating any sessions.

---

## Step 2 — Configure the session

A `SessionConfig` groups everything related to a single conversation:

```python
from copilot.types import (
    PermissionRequest,
    PermissionRequestResult,
    SessionConfig,
    SystemMessageAppendConfig,
)

def approve_all(request: PermissionRequest, context: dict) -> PermissionRequestResult:
    return PermissionRequestResult(kind="approved", rules=[])

session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        system_message=SystemMessageAppendConfig(
            content="You are a helpful assistant."
        ),
    )
)
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `on_permission_request` | Called before each tool execution — return `approved` or `denied` |
| `tools` | List of custom tools to register (empty for a plain chat session) |
| `streaming` | Whether to receive tokens incrementally (`True`) or wait for the full response (`False`) |
| `system_message` | Sets the assistant's persona |

---

## Step 3 — Handle session events

Session events are pushed via `session.on(handler)`. This is where streaming output and status updates arrive:

```python
from copilot.generated.session_events import SessionEventType

def on_event(event) -> None:
    if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
        print(event.data.delta_content, end="", flush=True)
    elif event.type == SessionEventType.SESSION_ERROR:
        print(f"\n[Error] {event.data.message}")

session.on(on_event)
```

**Common event types:**

| Event | When it fires |
|-------|--------------|
| `ASSISTANT_TURN_START` | Copilot starts processing |
| `ASSISTANT_MESSAGE_DELTA` | A streaming token arrives |
| `TOOL_EXECUTION_START` | A tool is about to run |
| `TOOL_EXECUTION_COMPLETE` | A tool finished |
| `ASSISTANT_TURN_END` | Processing finished |
| `SESSION_IDLE` | Session is ready for the next message |
| `SESSION_ERROR` | An error occurred |

---

## Step 4 — Send a prompt

```python
from copilot.types import MessageOptions

reply = await session.send_and_wait(
    MessageOptions(prompt="What is GitHub Copilot?"),
    timeout=300,
)
content = reply.data.content if reply else "(no response)"
print(content)
```

`send_and_wait` blocks until the session reaches `SESSION_IDLE`. During that time, streaming events are delivered to your `on_event` handler.

---

## Step 5 — Interactive chat loop

For a multi-turn conversation, keep the session alive and call `send_and_wait` in a loop:

```python
print("Chat with Copilot (Ctrl+C to quit)\n")
while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    print("Copilot: ", end="")
    await session.send_and_wait(MessageOptions(prompt=user_input), timeout=300)
    print()
```

---

## Run the Script

Run the scripts from the `src/python` directory so `uv` picks up the project's
virtual environment automatically:

```bash
cd src/python

# Single prompt
uv run python scripts/tutorials/01_chat_bot.py --prompt "Explain async/await in Python"

# Interactive loop
uv run python scripts/tutorials/01_chat_bot.py --loop

# Custom CLI server URL (optional — only when a CLI server is running in TCP mode)
uv run python scripts/tutorials/01_chat_bot.py --cli-url localhost:3000 --loop
```

---

## Key Takeaways

- `CopilotClient` → `create_session` → `send_and_wait` is the basic pattern
- `SessionConfig` controls the persona, tools, streaming, and permissions
- `session.on(handler)` receives all events including streaming deltas
- A session can be reused for multi-turn conversations
- `send_and_wait` blocks until the response is complete

---

## Next Tutorial

[Tutorial 2: Issue Triage Bot with Custom Tools →](02_custom_tools.md)
