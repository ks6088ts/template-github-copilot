[![test](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker.yaml?query=branch%3Amain)
[![infra](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml?query=branch%3Amain)
[![go-test](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-test.yaml?query=branch%3Amain)
[![go-run](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-run.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-run.yaml)
[![ghcr-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/ghcr-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/ghcr-release.yaml)
[![docker-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker-release.yaml)
[![go-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/go-release.yaml)
[![github-pages](https://github.com/ks6088ts/template-github-copilot/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/github-pages.yaml)

# template-github-copilot

A showcase repository for multiple use cases built on the **GitHub Copilot SDK**, **Azure AI Foundry**, and **GitHub Actions**.

> 📖 **Documentation Site**: For a more readable experience, visit the [GitHub Pages documentation](https://ks6088ts.github.io/template-github-copilot/).

---

## Use Cases

| Use Case | Description | Documentation |
|---|---|---|
| [GitHub Copilot SDK Tutorial](docs/copilot_sdk_tutorial/index.md) | Language-agnostic overview of the GitHub Copilot SDK — what it is, installing the Copilot CLI, authenticating with GitHub, architecture, and CLI server mode | [Getting Started](docs/copilot_sdk_tutorial/getting_started.md) · [Architecture](docs/copilot_sdk_tutorial/architecture.md) · [CLI Server Mode](docs/copilot_sdk_tutorial/server_mode.md) |
| [GitHub Copilot SDK Tutorial (Python)](docs/copilot_sdk_tutorial/python/index.md) | Step-by-step tutorials for building Python applications with the GitHub Copilot SDK — chatbots, custom tools, streaming, skills, hooks, and BYOK | [Getting Started](docs/copilot_sdk_tutorial/python/getting_started.md) · [Scripts](src/python/scripts/tutorials/README.md) |
| [GitHub Copilot SDK Tutorial (Go)](docs/copilot_sdk_tutorial/go/index.md) | Step-by-step tutorials for building Go applications with the GitHub Copilot SDK — CLI chatbot, streaming, and interactive sessions | [Getting Started](docs/copilot_sdk_tutorial/go/getting_started.md) · [Subcommands](src/go/cmd/tutorial/README.md) |
| [CopilotReportForge](docs/copilot_report_forge/index.md) | An extensible AI automation platform for parallel LLM query execution, structured report generation, and agentic AI workflows | [Getting Started](docs/copilot_report_forge/guide/getting_started.md) · [Architecture](docs/copilot_report_forge/overview/architecture.md) · [Deployment](docs/copilot_report_forge/operations/deployment.md) |

## Infrastructure (Terraform Scenarios)

| Scenario | Description |
|---|---|
| [Azure GitHub OIDC](infra/scenarios/azure_github_oidc/README.md) | Create Azure Service Principal with OIDC for GitHub Actions |
| [GitHub Secrets](infra/scenarios/github_secrets/README.md) | Register secrets into GitHub repository environment |
| [Azure Microsoft Foundry](infra/scenarios/azure_microsoft_foundry/README.md) | Deploy Microsoft Foundry (AI Hub + AI Services) on Azure |
| [Azure Container Apps](infra/scenarios/azure_container_apps/README.md) | Deploy monolith service (Copilot CLI + API) as Azure Container App |

## License

[MIT](LICENSE)
