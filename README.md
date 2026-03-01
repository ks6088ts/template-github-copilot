[![test](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker.yaml?query=branch%3Amain)
[![infra](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml?query=branch%3Amain)
[![ghcr-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/ghcr-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/ghcr-release.yaml)
[![docker-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker-release.yaml)
[![github-pages](https://github.com/ks6088ts/template-github-copilot/actions/workflows/github-pages.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/github-pages.yaml)

# template-github-copilot

A showcase repository for multiple use cases built on the **GitHub Copilot SDK**, **Azure AI Foundry**, and **GitHub Actions**.

---

## Use Cases

| Use Case | Description | Documentation |
|---|---|---|
| [CopilotReportForge](docs/copilot_report_forge/index.md) | An extensible AI automation platform for parallel LLM query execution, structured report generation, and agentic AI workflows | [Getting Started](docs/copilot_report_forge/getting_started.md) · [Architecture](docs/copilot_report_forge/architecture.md) · [Deployment](docs/copilot_report_forge/deployment.md) |

## Infrastructure (Terraform Scenarios)

| Scenario | Description |
|---|---|
| [Azure GitHub OIDC](infra/scenarios/azure_github_oidc/README.md) | Create Azure Service Principal with OIDC for GitHub Actions |
| [GitHub Secrets](infra/scenarios/github_secrets/README.md) | Register secrets into GitHub repository environment |
| [Azure Microsoft Foundry](infra/scenarios/azure_microsoft_foundry/README.md) | Deploy Microsoft Foundry (AI Hub + AI Services) on Azure |
| [Azure Container Apps](infra/scenarios/azure_container_apps/README.md) | Deploy monolith service (Copilot CLI + API) as Azure Container App |

## License

[MIT](LICENSE)
