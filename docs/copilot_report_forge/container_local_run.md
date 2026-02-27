# Running Containers Locally

> **Navigation:** [CopilotReportForge](index.md) > **Running Containers Locally**
>
> **See also:** [Getting Started](getting_started.md) · [Web UI Guide](web_ui_guide.md)

---

## Overview

CopilotReportForge provides Docker Compose configurations for running the platform locally in containers. Three methods are available depending on your image source:

| Method | Compose File | Image Source |
|---|---|---|
| Local Build | `compose.yaml` | Built from source |
| Docker Hub | `compose.docker.yaml` | `docker.io` |
| GitHub Packages | `compose.docker.yaml` | `ghcr.io` |

---

## Prerequisites

- Docker and Docker Compose installed
- A Copilot GitHub Token (`COPILOT_GITHUB_TOKEN`)
- (GitHub Packages) A GitHub Personal Access Token with `read:packages` scope
- (Docker Hub) A Docker Hub account

---

## Setup

### 1. Create Environment File

Create a `.env` file under `src/python/` with the required environment variables:

```bash
COPILOT_GITHUB_TOKEN=your-copilot-token
```

### 2. Run with Local Build

```bash
cd src/python
docker compose up --build
```

### 3. Run with Pre-built Images (Docker Hub)

```bash
cd src/python
docker compose -f compose.docker.yaml up
```

### 4. Run with Pre-built Images (GitHub Packages)

```bash
# Authenticate with GitHub Container Registry
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull and run
cd src/python
CONTAINER_REGISTRY=ghcr.io docker compose -f compose.docker.yaml up
```

---

## Services

| Service | Port | Description | Profile |
|---|---|---|---|
| `copilot` | `3000` | Copilot CLI server | default |
| `api` | `8000` | Web application with chat and report UI | default |
| `monolith` | `3000`, `8000` | Single container running both Copilot CLI and API via supervisord | `monolith` |

### Running the Monolith Service

The `monolith` service bundles both the Copilot CLI and API server into a single container using supervisord. It is activated via a Docker Compose profile:

```bash
# Local build
cd src/python
docker compose --profile monolith up monolith --build

# Pre-built images (Docker Hub)
cd src/python
docker compose -f compose.docker.yaml --profile monolith up monolith
```

This is the same image used for the [Azure Container Apps deployment](../../infra/scenarios/azure_container_apps/README.md).

---

## Common Operations

```bash
# Stop all services
docker compose down

# Rebuild after code changes
docker compose up --build

# View logs
docker compose logs -f

# Run a specific service
docker compose up api
```
