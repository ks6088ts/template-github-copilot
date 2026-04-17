# Architecture

This page explains how the GitHub Copilot SDK, the Copilot CLI server, and the GitHub Copilot API interact with each other — and how your Python scripts fit into the picture.

---

## High-Level Architecture

```mermaid
graph TD
    A[Tutorial Reader] -->|python script.py| S[src/python/scripts/tutorials/*.py]
    S -->|SDK Client| B[CopilotClient]
    B -->|JSON-RPC over stdio| C[Copilot CLI Server]
    C -->|HTTPS API Call| D[GitHub Copilot API]
    C -->|Tool Execution| E[Built-in Tools]
    C -->|Custom Tool| F[User-defined Tools<br/>@define_tool]
    C -->|Skills| G[SKILL.md Files]

    style A fill:#e1f5fe
    style S fill:#c8e6c9
    style B fill:#bbdefb
    style C fill:#90caf9
    style D fill:#64b5f6
    style E fill:#fff9c4
    style F fill:#ffe0b2
    style G fill:#f8bbd0
```

---

## Components

### CopilotClient

The `CopilotClient` class is the entry point of the SDK. It connects to the Copilot CLI server via **JSON-RPC over stdio** (when spawning a subprocess) or over a **TCP socket** (when connecting to an existing server on `localhost:3000`).

```python
from copilot import CopilotClient
from copilot.types import CopilotClientOptions

client = CopilotClient(
    options=CopilotClientOptions(cli_url="localhost:3000")
)
await client.start()
```

### Session

A **session** is a stateful conversation context. Each session has its own:

- System message (persona)
- Tool registry
- Permission handler
- Streaming configuration
- Optional provider override (for BYOK)

```python
session = await client.create_session(SessionConfig(...))
```

### Copilot CLI Server

The Copilot CLI server (`gh copilot serve`) is an out-of-process daemon that:

1. Authenticates with the GitHub Copilot API using your GitHub token
2. Receives requests from the SDK over the JSON-RPC channel
3. Calls the Copilot API (LLM inference)
4. Executes tool calls (built-in or user-defined)
5. Streams results back to the SDK

The SDK communicates with this server — **not** directly with the GitHub API.

### Tools

Tools extend the agent's capabilities. There are two kinds:

| Type | How to define | Example |
|------|--------------|---------|
| Built-in | Provided by the Copilot CLI server | File system, web search |
| Custom | `@define_tool` decorator | GitHub API calls, database queries |

Custom tools are registered per-session in `SessionConfig(tools=[...])`.

### Skills

Skills are Markdown files (`SKILL.md`) that define specialized agent behaviours. They are loaded from a **skills directory** configured in `CopilotClientOptions`.

```
skills/
├── docgen/
│   └── SKILL.md
└── coding-standards/
    └── SKILL.md
```

---

## Request/Response Flow

```mermaid
sequenceDiagram
    participant Script as Python Script
    participant SDK as CopilotClient
    participant CLI as Copilot CLI Server
    participant API as GitHub Copilot API

    Script->>SDK: client.create_session(config)
    SDK->>CLI: JSON-RPC: create_session
    CLI-->>SDK: session_id

    Script->>SDK: session.send_and_wait(prompt)
    SDK->>CLI: JSON-RPC: send_message
    CLI->>API: LLM inference request
    API-->>CLI: streaming tokens
    CLI-->>SDK: SessionEvents (delta, tool_call, ...)
    SDK-->>Script: events via session.on(handler)
    CLI-->>SDK: SESSION_IDLE (final)
    SDK-->>Script: reply object
```

---

## BYOK Flow

When BYOK is used, the Copilot CLI server routes requests to **your** model endpoint instead of the default Copilot API:

```mermaid
graph LR
    SDK[CopilotClient] --> CLI[Copilot CLI Server]
    CLI -->|ProviderConfig: type=azure| AOAI[Azure OpenAI]
    CLI -->|ProviderConfig: type=openai| OAI[OpenAI API]

    style AOAI fill:#0078d4,color:#fff
    style OAI fill:#412991,color:#fff
```

The `ProviderConfig` is passed in the `SessionConfig` and tells the CLI server which endpoint and credentials to use.

---

## Key Design Principles

1. **Out-of-process execution** — The Copilot CLI server runs in a separate process; the SDK communicates via IPC. This isolates credentials and authentication from your script.

2. **Event-driven** — All session activity is modelled as events (`SessionEventType`). Your handler receives events as they arrive — enabling real-time streaming.

3. **Permission gates** — Every tool execution passes through `on_permission_request`. You control whether to approve or deny each operation.

4. **Session isolation** — Each session is independent. Multiple sessions can run concurrently in the same process (useful for parallel workloads).
