# Tutorial 1: CLI Chatbot

**Script:** [`src/python/scripts/tutorials/01_chat_bot.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/01_chat_bot.py)

---

## What You Will Learn

- How to create a `CopilotClient` and connect to the CLI server
- How to create a session with a system message and permission handler
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
from copilot import CopilotClient, RuntimeConnection

# Default: SDK launches the CLI over stdio
client = CopilotClient()

# Optional: connect to an already-running CLI server
# client = CopilotClient(connection=RuntimeConnection.for_uri("localhost:3000"))

await client.start()
```

> **Note:** `await client.start()` establishes the JSON-RPC connection. Call it before creating any sessions.

---

## Step 2 — Configure the session

`create_session` accepts keyword arguments that group everything related to a single conversation:

```python
from copilot.generated.rpc import PermissionDecisionApproveOnce
from copilot.generated.session_events import PermissionRequest
from copilot.session import PermissionRequestResult, SystemMessageAppendConfig

def approve_all(request: PermissionRequest, context: dict) -> PermissionRequestResult:
    return PermissionDecisionApproveOnce()

session = await client.create_session(
    on_permission_request=approve_all,
    tools=[],
    streaming=True,
    system_message=SystemMessageAppendConfig(
        content="You are a helpful assistant."
    ),
)
```

**Key fields:**

| Field | Description |
|-------|-------------|
| `on_permission_request` | Called before each tool execution — return `PermissionDecisionApproveOnce()` or `PermissionDecisionReject(feedback=...)` |
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
reply = await session.send_and_wait(
    "What is GitHub Copilot?",
    timeout=300,
)
content = getattr(reply.data, "content", None) if reply else "(no response)"
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
    await session.send_and_wait(user_input, timeout=300)
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

## Connecting to a Standalone CLI Server (TCP)

By default the SDK launches the `copilot` CLI as a subprocess and talks to it
over stdio. Alternatively, you can run the CLI as a long-lived TCP server and
connect to it from one or more SDK clients via `--cli-url`. This is useful when
you want to share a single authenticated CLI process across multiple runs.

### Step 1 — Start the CLI server

In a separate terminal, start the CLI in headless TCP mode:

```bash
copilot --headless --no-auto-update --log-level info --port 3000
```

When startup succeeds you will see:

```text
CLI server listening on port 3000
```

> **Note:** `--headless` and `--port` are not shown in `copilot --help`, but
> they are the same arguments the SDK uses internally when spawning a TCP
> runtime, and they work as expected.

### Step 2 — Connect from the SDK client

In another terminal, point the script at the running server:

```bash
cd src/python

# Single prompt
uv run python scripts/tutorials/01_chat_bot.py --cli-url localhost:3000 --prompt "Reply with exactly: connection ok"

# Interactive loop
uv run python scripts/tutorials/01_chat_bot.py --cli-url localhost:3000 --loop
```

A successful run returns the assistant's response (e.g. `connection ok`).

### Troubleshooting & notes

- **`Session was not created with authentication info or custom provider`** —
  This happens when the server is started with `--no-auto-login`, leaving it
  without credentials. **Do not pass `--no-auto-login`** for this scenario; let
  the server reuse your logged-in user (already authenticated via
  `gh auth login` or the `copilot` login flow).
- **`No COPILOT_CONNECTION_TOKEN was set` warning** — Without a token the server
  accepts connections from any client. This is fine for local testing. To
  restrict access, set `COPILOT_CONNECTION_TOKEN` in the server's environment
  and pass the same token from the client:

  ```python
  from copilot import CopilotClient, RuntimeConnection

  client = CopilotClient(
      connection=RuntimeConnection.for_uri(
          "localhost:3000",
          connection_token="your-shared-secret",
      )
  )
  ```

---

## Key Takeaways

- `CopilotClient` → `create_session` → `send_and_wait` is the basic pattern
- `create_session` parameters control the persona, tools, streaming, and permissions
- `session.on(handler)` receives all events including streaming deltas
- A session can be reused for multi-turn conversations
- `send_and_wait` blocks until the response is complete

---

## Next Tutorial

[Tutorial 2: Issue Triage Bot with Custom Tools →](02_custom_tools.md)
