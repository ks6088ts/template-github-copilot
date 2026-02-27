# Running Containers Locally

This guide explains how to run the copilot and api services locally using Docker Compose. Three methods are available depending on your image source:

| Method | Compose File | Image Source |
|--------|--------------|---------------|
| Local Build | `compose.yaml` | Built from source |
| Docker Hub | `compose.docker.yaml` | `docker.io` |
| GitHub Packages | `compose.docker.yaml` | `ghcr.io` |

## Prerequisites

- Docker and Docker Compose installed
- A Copilot GitHub Token (`COPILOT_GITHUB_TOKEN`)
- (For GitHub Packages) GitHub Personal Access Token (PAT) with the `read:packages` scope
- (For Docker Hub) A Docker Hub account

## 1. Set Up Environment Variables

Create a `.env` file under `src/python/` with the required environment variables.

```bash
cd src/python

cat <<EOF > .env
COPILOT_GITHUB_TOKEN=<your-copilot-github-token>
COPILOT_MODEL=gpt-5-mini

# OAuth GitHub App Settings (required for the web UI login flow)
GITHUB_CLIENT_ID=<your-oauth-app-client-id>
GITHUB_CLIENT_SECRET=<your-oauth-app-client-secret>
SESSION_SECRET=<random-string>
EOF
```

> Include any additional environment variables required by the api service in the `.env` file. See the [GitHub OAuth App Setup](github_oauth_app.md) guide for creating the OAuth App and generating these values.

## 2. Start with Docker Compose

### Option A: Local Build

Build images from source and start the services. Uses `compose.yaml`.

```bash
cd src/python
docker compose up --build
```

### Option B: Docker Hub Images

Pull and run pre-built images from Docker Hub. Uses `compose.docker.yaml`.

```bash
cd src/python

# Log in to Docker Hub (required for private images)
docker login -u <your-dockerhub-username>

# Start the services
docker compose -f compose.docker.yaml up
```

> `compose.docker.yaml` uses `docker.io` as the default registry.

### Option C: GitHub Packages (ghcr.io) Images

Pull and run pre-built images from GitHub Container Registry. Uses the same `compose.docker.yaml` with the `CONTAINER_REGISTRY` environment variable set to `ghcr.io`.

```bash
cd src/python

# Log in to GitHub Container Registry
echo "$GITHUB_PAT" | docker login ghcr.io -u <your-github-username> --password-stdin

# Start the services with CONTAINER_REGISTRY override
CONTAINER_REGISTRY=ghcr.io docker compose -f compose.docker.yaml up
```

## 3. Verify

Once the services are running, verify by accessing the API docs:

```bash
curl http://localhost:8000/docs
```

## 4. Stop

```bash
# For local build
docker compose down

# For Docker Hub / GitHub Packages
docker compose -f compose.docker.yaml down
```

## Specifying Image Versions

By default, `compose.docker.yaml` uses the `latest` tag. You can pin a specific version by editing the compose file or using environment variables.

Available tags can be found on:

- [GitHub Packages](https://github.com/ks6088ts/template-github-copilot/pkgs)
- [Docker Hub](https://hub.docker.com/u/ks6088ts)

## Publishing Images to Registries

### GitHub Container Registry (ghcr.io)

No additional secrets are needed. The `GITHUB_TOKEN` provided by GitHub Actions is used automatically. See the [ghcr-release workflow](../../.github/workflows/ghcr-release.yaml) for details.

### Docker Hub

To publish the docker image to Docker Hub, you need to [create access token](https://app.docker.com/settings/personal-access-tokens/create) and set the following secrets in the repository settings.

```shell
gh secret set DOCKERHUB_USERNAME --body $DOCKERHUB_USERNAME
gh secret set DOCKERHUB_TOKEN --body $DOCKERHUB_TOKEN
```

See the [docker-release workflow](../../.github/workflows/docker-release.yaml) for details.
