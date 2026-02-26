# --- Build stage ---
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

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/template_github_copilot /app/template_github_copilot
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

ENV PATH="/app/.venv/bin:$PATH"

# Default settings (can be overridden via docker-compose / env)
ENV API_HOST="0.0.0.0"
ENV API_PORT="8000"
# Set via compose.yaml 'environment' (e.g. copilot:3000).
# Empty means the SDK will try to spawn a local Copilot CLI subprocess.
ENV COPILOT_CLI_URL=""

EXPOSE 8000

CMD ["bash", "-c", "python scripts/api_server.py serve --verbose"]
