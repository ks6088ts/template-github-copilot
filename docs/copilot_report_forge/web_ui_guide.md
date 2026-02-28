# Web UI Guide

> **Navigation:** [CopilotReportForge](index.md) > **Web UI Guide**
>
> **See also:** [Getting Started](getting_started.md) · [GitHub OAuth App Setup](github_oauth_app.md)

---

## Overview

CopilotReportForge includes a browser-based interface for interactive AI chat and parallel report generation. The Web UI is powered by the same Copilot SDK used in CLI and GitHub Actions workflows, providing a consistent experience across all interfaces.

### Web UI Architecture

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
    subgraph Browser["Browser (Single Page)"]
        LOGIN["Login Screen"]
        CHAT["Chat Tab"]
        REPORT["Report Tab"]
    end

    subgraph Server["FastAPI Server"]
        AUTH_EP["OAuth Endpoints<br/>/auth/login, /auth/callback"]
        CHAT_EP["POST /api/chat"]
        REPORT_EP["POST /api/report"]
        SESSION["In-Memory Session Store<br/>(HMAC-SHA256 Signed Cookie)"]
    end

    subgraph External["External Services"]
        GH_OAUTH["GitHub OAuth<br/>(Authorization Server)"]
        GH_API["GitHub API<br/>(/user)"]
        COPILOT["Copilot SDK"]
        LLM["Hosted LLMs"]
    end

    LOGIN -- "Sign in with GitHub" --> AUTH_EP
    AUTH_EP <-- "OAuth code exchange" --> GH_OAUTH
    AUTH_EP <-- "Fetch user info" --> GH_API
    AUTH_EP -- "Set signed cookie" --> SESSION

    CHAT -- "POST /api/chat" --> CHAT_EP
    CHAT_EP -- "Verify session" --> SESSION
    CHAT_EP -- "Send message" --> COPILOT
    COPILOT -- "Query" --> LLM

    REPORT -- "POST /api/report" --> REPORT_EP
    REPORT_EP -- "Verify session" --> SESSION
    REPORT_EP -- "Parallel queries<br/>(asyncio.gather)" --> COPILOT
```

### Key Features

| Feature | Description |
|---|---|
| **GitHub OAuth Login** | Authenticate with your GitHub identity — no API keys needed |
| **Interactive Chat** | Real-time conversational interface with hosted LLMs |
| **Report Panel** | Configure and execute parallel multi-query evaluations |
| **Theme Toggle** | Switch between light and dark themes |
| **Swagger UI** | Built-in API documentation at `/docs` |

---

## Login Screen

When you open the application, you see a login page with a **"Sign in with GitHub"** button. Clicking it initiates the GitHub OAuth flow (see [GitHub OAuth App Setup](github_oauth_app.md)).

![Login Screen](images/01_login_screen.png)

### GitHub OAuth Authentication Flow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant Browser
    participant Server as FastAPI Server
    participant GitHub as GitHub OAuth
    participant API as GitHub API (/user)

    Browser->>Server: GET /auth/login
    Server->>Server: Generate random state token
    Server->>Server: Create in-memory session
    Server-->>Browser: 302 Redirect to GitHub<br/>(client_id, state, scope=copilot)

    Browser->>GitHub: Authorize application
    GitHub-->>Browser: 302 Redirect to /auth/callback<br/>(code, state)

    Browser->>Server: GET /auth/callback?code=...&state=...
    Server->>Server: Verify state (CSRF protection)
    Server->>GitHub: POST /login/oauth/access_token<br/>(client_id, client_secret, code)
    GitHub-->>Server: access_token (github_token)
    Server->>API: GET /user (Authorization: token)
    API-->>Server: User info (login, avatar_url)
    Server->>Server: Store github_token + user info in session
    Server-->>Browser: 302 Redirect to /<br/>(Set-Cookie: signed session ID)

    Browser->>Server: GET /api/me (Cookie)
    Server->>Server: Verify HMAC-SHA256 signature
    Server-->>Browser: UserInfo (login, avatar)
    Browser->>Browser: Show Chat UI
```

After successful authentication, you are redirected to the chat interface.

---

## Chat Interface

The chat interface provides a conversational experience with hosted LLMs.

![Chat Screen](images/05_chat_ui.png)

| Element | Description |
|---|---|
| **Message input** | Type your prompt and press Enter or click Send |
| **Conversation history** | Messages are displayed in chronological order |
| **Model indicator** | Shows which LLM model is being used |
| **Clear button** | Reset the conversation |

Each message creates an independent Copilot SDK session. Responses are streamed in real time.

### Chat Communication Flow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant Browser
    participant Server as FastAPI Server
    participant SDK as Copilot SDK Client
    participant LLM as Hosted LLM

    Browser->>Server: POST /api/chat<br/>{"message": "user text"}
    Server->>Server: Verify signed cookie → get github_token

    Server->>SDK: create_copilot_client(github_token)
    SDK->>SDK: start()
    Server->>SDK: create_session(config)
    SDK-->>Server: Copilot Session

    Server->>SDK: send_and_wait(message)
    SDK->>LLM: Query with user message
    LLM-->>SDK: LLM Response
    SDK-->>Server: Response data

    Server-->>Browser: {"reply": "copilot response text"}
    Browser->>Browser: Append message to conversation
```

---

## Report Panel

The report panel enables parallel execution of multiple LLM queries with a configurable system prompt.

![Report Panel](images/06_report_form.png)

### How to Use

1. **Set the system prompt** — Define the AI persona (e.g., "You are a senior architect reviewing system designs")
2. **Enter queries** — One per line, each will execute in a separate LLM session
3. **Click Generate** — All queries execute in parallel
4. **Review results** — Each query shows its response and success/failure status

### Report Output

The generated report includes:
- Total number of queries executed
- Per-query results with success/failure indicators
- Aggregated summary
- Option to download as JSON

### Report Generation Flow

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
    participant Browser
    participant Server as FastAPI Server
    participant SDK as Copilot SDK Client
    participant LLM as Hosted LLM

    Browser->>Server: POST /api/report<br/>{"system_prompt": "...", "queries": ["Q1","Q2","Q3"]}
    Server->>Server: Verify signed cookie → get github_token

    Server->>SDK: run_parallel_chat(queries, system_prompt, github_token)

    par asyncio.gather - Parallel Execution
        SDK->>LLM: Query 1 (with system_prompt)
        LLM-->>SDK: Response 1
    and
        SDK->>LLM: Query 2 (with system_prompt)
        LLM-->>SDK: Response 2
    and
        SDK->>LLM: Query N (with system_prompt)
        LLM-->>SDK: Response N
    end

    SDK->>SDK: Aggregate results<br/>(total, succeeded, failed)
    SDK-->>Server: ReportOutput (JSON)
    Server-->>Browser: ReportOutput<br/>{"total": N, "succeeded": M, "results": [...]}
    Browser->>Browser: Render report with stats
```

---

## Theme Toggle

Click the theme toggle button (sun/moon icon) in the navigation bar to switch between light and dark modes. The preference is saved in your browser's local storage.

---

## API Documentation

The application includes auto-generated API documentation accessible at:

| URL | Interface |
|---|---|
| `/docs` | Swagger UI — interactive API explorer |
| `/redoc` | ReDoc — alternative API documentation |

### Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Login page |
| `GET` | `/auth/login` | Initiate GitHub OAuth flow |
| `GET` | `/auth/callback` | OAuth callback handler |
| `GET` | `/auth/logout` | Clear session and redirect to login |
| `GET` | `/api/me` | Return authenticated user info (login, avatar) |
| `POST` | `/api/chat` | Send a chat message |
| `POST` | `/api/report` | Generate a parallel report |
| `POST` | `/api/report/generate` | Generate a report, upload to Azure Blob Storage, and return a SAS URL |
| `POST` | `/api/report/upload` | Upload an existing report to Azure Blob Storage and return a SAS URL |

---

## Running the Web UI

### Local Development

```bash
cd src/python
export GITHUB_CLIENT_ID="your-client-id"
export GITHUB_CLIENT_SECRET="your-client-secret"
export SESSION_SECRET="a-random-secret-string"
make copilot-api
```

Then open `http://localhost:8000`.

### Docker

```bash
cd src/python
docker compose up --build
```

See [Running Containers Locally](container_local_run.md) for detailed container usage.
