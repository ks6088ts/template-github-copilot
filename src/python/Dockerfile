# =============================================================
# Monolithic image: Copilot CLI (Node.js) + API server (Python)
# =============================================================

# --- Build stage: Python dependencies ---
FROM python:3.13-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# Copy application source
COPY template_github_copilot/ template_github_copilot/
COPY scripts/ scripts/
RUN uv sync --no-dev

# --- Runtime stage ---
FROM python:3.13-slim-bookworm AS runtime

ARG COPILOT_CLI_VERSION=0.0.418

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ---- Install Node.js (for Copilot CLI) ----
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get purge -y gnupg && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# ---- Install Copilot CLI ----
RUN curl -fsSL https://gh.io/copilot-install | VERSION="${COPILOT_CLI_VERSION}" bash && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# ---- Install supervisord (process manager) ----
# hadolint ignore=DL3013
RUN pip install --no-cache-dir supervisor

WORKDIR /app

# ---- Copy Python app from builder ----
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/template_github_copilot /app/template_github_copilot
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

ENV PATH="/app/.venv/bin:$PATH"

# ---- Default environment variables ----
ENV API_HOST="0.0.0.0"
ENV API_PORT="8000"
ENV COPILOT_CLI_URL="127.0.0.1:3000"
ENV COPILOT_MODEL="gpt-5-mini"

# ---- Supervisord configuration ----
COPY <<'EOF' /etc/supervisord.conf
[supervisord]
nodaemon=true
logfile=/dev/stdout
logfile_maxbytes=0
loglevel=info

[program:copilot]
command=bash -c "copilot --server --port 3000 --log-level all --allow-all-tools --allow-all-paths --allow-all-urls --model %(ENV_COPILOT_MODEL)s"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:api]
command=python scripts/api_server.py serve --verbose
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

EXPOSE 3000 8000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
