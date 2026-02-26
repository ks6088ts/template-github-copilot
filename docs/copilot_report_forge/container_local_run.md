# Running Containers Locally

This guide explains how to run the copilot and api services locally using container images published to GitHub Packages (ghcr.io).

## Prerequisites

- Docker and Docker Compose installed
- A GitHub Personal Access Token (PAT) with the `read:packages` scope
- A Copilot GitHub Token (`COPILOT_GITHUB_TOKEN`)

## 1. Log in to GitHub Container Registry

```bash
echo "$GITHUB_PAT" | docker login ghcr.io -u <your-github-username> --password-stdin
```

## 2. Set Up Environment Variables

Create a `.env` file under `src/python/` with the required environment variables.

```bash
cd src/python

cat <<EOF > .env
COPILOT_GITHUB_TOKEN=<your-copilot-github-token>
COPILOT_MODEL=gpt-5-mini
EOF
```

> Include any additional environment variables required by the api service in the `.env` file.

## 3. Start with Docker Compose (Local Build)

To build from source and start the services:

```bash
cd src/python
docker compose up --build
```

## 4. Start with Docker Compose (GitHub Packages Images)

To pull and run pre-built images from GitHub Packages, create a `compose.ghcr.yaml` file under `src/python/`:

```yaml
services:
  copilot:
    image: ghcr.io/ks6088ts/template-github-copilot-copilot:latest
    environment:
      - COPILOT_GITHUB_TOKEN=${COPILOT_GITHUB_TOKEN}
      - COPILOT_MODEL=${COPILOT_MODEL:-gpt-5-mini}
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD-SHELL", "node -e \"const c=require('net').createConnection(3000,'127.0.0.1',()=>{c.end();process.exit(0)});c.on('error',()=>process.exit(1))\""]
      interval: 5s
      timeout: 10s
      retries: 10
      start_period: 10s

  api:
    image: ghcr.io/ks6088ts/template-github-copilot-api:latest
    env_file:
      - .env
    environment:
      - COPILOT_CLI_URL=copilot:3000
      - API_HOST=0.0.0.0
      - API_PORT=8000
    ports:
      - "8000:8000"
    depends_on:
      copilot:
        condition: service_healthy
```

Then start the services:

```bash
cd src/python
docker compose -f compose.ghcr.yaml up
```

## 5. Verify

Once the services are running, verify by accessing the API docs:

```bash
curl http://localhost:8000/docs
```

## 6. Stop

```bash
docker compose down
# or
docker compose -f compose.ghcr.yaml down
```

## Specifying Image Versions

You can pin a specific version instead of `latest`:

```yaml
image: ghcr.io/ks6088ts/template-github-copilot-copilot:1.0.0
image: ghcr.io/ks6088ts/template-github-copilot-api:1.0.0
```

Available tags can be found on [GitHub Packages](https://github.com/ks6088ts/template-github-copilot/pkgs).

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
