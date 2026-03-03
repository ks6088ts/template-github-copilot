FROM node:22-slim

ARG COPILOT_CLI_VERSION=0.0.420

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install copilot CLI
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://gh.io/copilot-install | VERSION="${COPILOT_CLI_VERSION}" bash && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Default model (overridable via environment variable)
ENV COPILOT_MODEL="gpt-5-mini"

EXPOSE 3000

CMD ["bash", "-c", "copilot --server --port 3000 --log-level all --allow-all-tools --allow-all-paths --allow-all-urls --model ${COPILOT_MODEL}"]
