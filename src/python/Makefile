# Git
GIT_REVISION ?= $(shell git rev-parse --short HEAD)
GIT_TAG ?= $(shell git describe --tags --abbrev=0 --always | sed -e s/v//g)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

.PHONY: info
info: ## show information
	@echo "GIT_REVISION: $(GIT_REVISION)"
	@echo "GIT_TAG: $(GIT_TAG)"

.PHONY: install-deps-dev
install-deps-dev: ## install dependencies for development
	uv sync --all-groups
	uv run pre-commit install
	@which actionlint || echo "install actionlint https://github.com/rhysd/actionlint"

.PHONY: install-deps
install-deps: ## install dependencies for production
	uv sync --no-dev

.PHONY: format-check
format-check: ## format check
	uv run ruff format --check --verbose

.PHONY: format
format: ## format code
	uv run ruff format --verbose

.PHONY: fix
fix: format ## apply auto-fixes
	uv run ruff check --fix

.PHONY: lint
lint: ## lint
	uv run ruff check .
	uv run ty check
	uv run pyrefly check
	actionlint

.PHONY: test
test: ## run tests
	uv run pytest --capture=no -vv

.PHONY: ci-test
ci-test: install-deps-dev format-check lint test ## run CI tests

.PHONY: update
update: ## update packages
	uv lock --upgrade

.PHONY: jupyterlab
jupyterlab: ## run Jupyter Lab
	uv run jupyter lab

# ---
# Docker
# ---
DOCKER_REPO_NAME ?= ks6088ts
DOCKER_IMAGE_NAME ?= template-github-copilot
DOCKER_IMAGE_NAME_API ?= template-github-copilot-api
DOCKER_IMAGE_NAME_COPILOT ?= template-github-copilot-copilot
DOCKER_COMMAND ?= python scripts/api_server.py --help

# Tools
TOOLS_DIR ?= /usr/local/bin
TRIVY_VERSION ?= 0.58.1

.PHONY: docker-build
docker-build: ## build Docker image
	docker build \
		-f Dockerfile \
		-t $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG) \
		.
	docker build \
		-f api.Dockerfile \
		-t $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME_API):$(GIT_TAG) \
		--build-arg GIT_REVISION=$(GIT_REVISION) \
		--build-arg GIT_TAG=$(GIT_TAG) \
		.
	docker build \
		-f copilot.Dockerfile \
		-t $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME_COPILOT):$(GIT_TAG) \
		--build-arg GIT_REVISION=$(GIT_REVISION) \
		--build-arg GIT_TAG=$(GIT_TAG) \
		.

.PHONY: docker-run
docker-run: ## run Docker container
	docker run --rm $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG) $(DOCKER_COMMAND)

.PHONY: docker-lint
docker-lint: ## lint Dockerfile
	docker run --rm -i hadolint/hadolint < Dockerfile
	docker run --rm -i hadolint/hadolint < api.Dockerfile
	docker run --rm -i hadolint/hadolint < copilot.Dockerfile

.PHONY: docker-scan
docker-scan: ## scan Docker image
	@# https://aquasecurity.github.io/trivy/v0.18.3/installation/#install-script
	@which trivy || curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b $(TOOLS_DIR) v$(TRIVY_VERSION)
	trivy image $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG)
	trivy image $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME_API):$(GIT_TAG)
	trivy image $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME_COPILOT):$(GIT_TAG)

.PHONY: ci-test-docker
ci-test-docker: docker-lint docker-build docker-run ## run CI test for Docker
	@echo "FIXME: issue #44 enable docker-scan"

# ---
# Docker Compose
# ---

.PHONY: compose-build
compose-build: ## build Docker Compose services
	docker compose build

.PHONY: compose-up
compose-up: ## start Docker Compose services
	docker compose up --build

.PHONY: compose-up-d
compose-up-d: ## start Docker Compose services in background
	docker compose up --build -d

.PHONY: compose-down
compose-down: ## stop Docker Compose services
	docker compose down

.PHONY: compose-logs
compose-logs: ## show Docker Compose logs
	docker compose logs -f

# ---
# Project
# ---

COPILOT_MODEL ?= gpt-5-mini

.PHONY: copilot
copilot: ## run GitHub Copilot CLI server
	copilot \
		--server \
		--port 3000 \
		--log-level all \
		--allow-all-tools --allow-all-paths --allow-all-urls \
		--model $(COPILOT_MODEL) \

.PHONY: copilot-app
copilot-app: ## run application with GitHub Copilot SDK
	uv run python scripts/chat.py chat-loop --verbose

.PHONY: copilot-api
copilot-api: ## run API server with GitHub Copilot SDK
	uv run python scripts/api_server.py serve --verbose --reload
