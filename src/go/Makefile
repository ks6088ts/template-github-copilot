# Git
GIT_REVISION ?= $(shell git rev-parse --short HEAD)
GIT_TAG ?= $(shell git describe --tags --abbrev=0 --always | sed -e s/v//g)

# Go
GOOS ?= $(shell go env GOOS)
GOARCH ?= $(shell go env GOARCH)
GOBUILD ?= GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=0 go build
LDFLAGS ?= '-s -w \
	-X "github.com/ks6088ts/template-github-copilot/src/go/internal.Revision=$(GIT_REVISION)" \
	-X "github.com/ks6088ts/template-github-copilot/src/go/internal.Version=$(GIT_TAG)" \
'

# Docker
DOCKER_REPO_NAME ?= ks6088ts
DOCKER_IMAGE_NAME ?= template-github-copilot-go
DOCKER_COMMAND ?=

# Tools
TOOLS_DIR ?= /usr/local/bin
# https://github.com/golangci/golangci-lint/releases
GOLANGCI_LINT_VERSION ?= 2.11.3
# https://github.com/aquasecurity/trivy/releases
TRIVY_VERSION ?= 0.69.3

# Misc
OUTPUT_DIR ?= dist
OUTPUT ?= $(OUTPUT_DIR)/template-github-copilot-go

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

.PHONY: install-deps-dev
install-deps-dev: ## install dependencies for development
	@# https://golangci-lint.run/welcome/install/#local-installation
	@which golangci-lint || curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(TOOLS_DIR) v$(GOLANGCI_LINT_VERSION)
	@# https://goreleaser.com/install/
	@which goreleaser || go install github.com/goreleaser/goreleaser/v2@latest
	@# https://aquasecurity.github.io/trivy/v0.18.3/installation/#install-script
	@which trivy || curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b $(TOOLS_DIR) v$(TRIVY_VERSION)
	@which actionlint || echo "install actionlint https://github.com/rhysd/actionlint"
	@# https://github.com/swaggo/swag — dev-only, not a runtime dependency
	@which swag || go install github.com/swaggo/swag/v2/cmd/swag@latest

.PHONY: openapi
openapi: ## regenerate the OpenAPI spec from handler annotations (requires swag v2)
	swag init --v3.1 -g cmd/serve/doc.go -o cmd/serve/webui --ot yaml

.PHONY: format-check
format-check: ## format check
	@# https://stackoverflow.com/a/67962664
	test -z "$$(gofmt -e -l -s .)"

.PHONY: format
format: ## format code
	gofmt -e -l -s -w .

.PHONY: lint
lint: ## lint
	golangci-lint run -v
	actionlint

.PHONY: test
test: ## run tests
	go test -cover -v ./...

.PHONY: build
build: ## build applications
	go mod tidy
	mkdir -p $(OUTPUT_DIR)
	$(GOBUILD) -ldflags=$(LDFLAGS) -trimpath -o $(OUTPUT) .

.PHONY: ci-test
ci-test: install-deps-dev format-check lint test build ## run CI test

.PHONY: update
update: ## update
	@# https://stackoverflow.com/a/67202539/4457856
	go get -u ./...
	go mod tidy

.PHONY: release
release: ## release applications
	goreleaser release --snapshot --clean

# ---
# Docker
# ---

.PHONY: docker-build
docker-build: ## build Docker image
	docker build \
		-t $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG) \
		--build-arg GIT_REVISION=$(GIT_REVISION) \
		--build-arg GIT_TAG=$(GIT_TAG) \
		.

.PHONY: docker-run
docker-run: ## run Docker container
	docker run --rm $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG) $(DOCKER_COMMAND)

.PHONY: docker-lint
docker-lint: ## lint Dockerfile
	docker run --rm -i hadolint/hadolint < Dockerfile

.PHONY: docker-scan
docker-scan: ## scan Docker image
	trivy image $(DOCKER_REPO_NAME)/$(DOCKER_IMAGE_NAME):$(GIT_TAG)

.PHONY: ci-test-docker
ci-test-docker: install-deps-dev docker-lint docker-build docker-scan docker-run ## run CI test for Docker
