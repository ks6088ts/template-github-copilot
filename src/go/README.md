[![go-test](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-test.yaml?query=branch%3Amain)
[![go-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-release.yaml)
[![Go Report Card](https://goreportcard.com/badge/github.com/ks6088ts/template-github-copilot/src/go)](https://goreportcard.com/report/github.com/ks6088ts/template-github-copilot/src/go)
[![Go Reference](https://pkg.go.dev/badge/github.com/ks6088ts/template-github-copilot/src/go.svg)](https://pkg.go.dev/github.com/ks6088ts/template-github-copilot/src/go)

# template-github-copilot-go

A Go CLI that demonstrates the [GitHub Copilot SDK for Go](https://pkg.go.dev/github.com/github/copilot-sdk/go) through runnable tutorial subcommands. See the [tutorial subcommand reference](cmd/tutorial/README.md) and the [documentation site](https://ks6088ts.github.io/template-github-copilot/copilot_sdk_tutorial/go/).

## Prerequisites

- [Go 1.26+](https://go.dev/doc/install)
- [GNU Make](https://www.gnu.org/software/make/)
- Authenticated GitHub Copilot CLI access for commands that create Copilot SDK sessions

## Usage

### One-shot task runner

Use `run` to send one prompt to a Copilot SDK session. You can choose a model,
append instructions from an `agents.md` file, and attach image or file inputs.

```shell
# simple prompt with the default model
go run . run --prompt "Explain goroutines in Go"

# choose a model
go run . run --model gpt-5-mini --prompt "Summarize this repository"

# append local agent instructions
go run . run --agents-md AGENTS.md --prompt "Review this task"

# attach image and file inputs
go run . run --image screenshot.png --file README.md --prompt "Evaluate these inputs"
```

By default, `run` automatically approves only read permission requests from the
agent. Use `--yolo` only when the prompt and working directory are trusted,
because it approves every tool permission request.

### HTTP task server

Use `serve` to expose the same task execution flow over HTTP. Tasks run
asynchronously and are stored in memory for the lifetime of the server process.

```shell
# start the server on 127.0.0.1:8080
go run . serve

# submit a JSON task
curl -sS http://127.0.0.1:8080/v1/tasks \
 -H 'Content-Type: application/json' \
 -d '{"prompt":"Explain goroutines in Go","model":"gpt-5-mini"}'

# submit a multipart task with attachments
curl -sS http://127.0.0.1:8080/v1/tasks \
 -F 'prompt=Evaluate these inputs' \
 -F 'model=gpt-5-mini' \
 -F 'agents_md=@AGENTS.md' \
 -F 'image=@screenshot.png' \
 -F 'file=@README.md'

# poll task status, progress, and result
curl -sS http://127.0.0.1:8080/v1/tasks/<task_id>
```

The server also exposes `GET /v1/tasks` to list tasks and `GET /healthz` for a
health check. Unversioned `/tasks` endpoints remain available for compatibility.
Like `run`, `serve` defaults to read-only permission approval; pass `--yolo` to
change the server default, or set `yolo=true` on an individual task request.

#### Browser UI (Scalar API reference)

Once the server is running, open **http://127.0.0.1:8080/docs/** in your
browser to access the built-in Scalar API reference UI. From there you can
explore all endpoints and send requests interactively using the built-in
try-console.

Key points:

- The UI is **fully offline** — the Scalar bundle and the OpenAPI spec are
  embedded in the binary; no network access is required.
- The OpenAPI 3.1 spec is also available at `GET /swagger.yaml`.
- `GET /` redirects to `/docs/`.

To regenerate the spec after changing handler annotations, install `swag` (once)
and run `make openapi`:

```shell
# install swag v2 (dev tool only, not a runtime dependency)
make install-deps-dev

# regenerate cmd/serve/webui/swagger.yaml from handler annotations
make openapi
```

## Development instructions

### Local development

Use Makefile to run the project locally.

```shell
# help
make

# install dependencies for development
make install-deps-dev

# run tests
make test

# build applications
make build

# run CI tests
make ci-test

# release applications
make release
```

### Docker development

```shell
# build docker image
make docker-build

# run docker container
make docker-run

# run CI tests in docker container
make ci-test-docker
```

## Deployment instructions

### Docker Hub

To publish the docker image to Docker Hub, you need to [create access token](https://app.docker.com/settings/personal-access-tokens/create) and set the following secrets in the repository settings.

```shell
gh secret set DOCKERHUB_USERNAME --body $DOCKERHUB_USERNAME
gh secret set DOCKERHUB_TOKEN --body $DOCKERHUB_TOKEN
```
