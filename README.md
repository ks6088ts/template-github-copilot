[![test](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml?query=branch%3Amain)
[![infra](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml?query=branch%3Amain)

# template-github-copilot

A comprehensive template for building automation workflows powered by the **GitHub Copilot SDK**. It integrates GitHub Actions, Azure Blob Storage, and Terraform-managed infrastructure to enable AI-driven report generation, parallel chat sessions, and more.

## Key Features

- **Copilot SDK Integration** — Chat, parallel queries, and report generation via the GitHub Copilot SDK
- **GitHub Actions Workflows** — On-demand AI prompts, report generation with Azure Blob Storage upload
- **Infrastructure as Code** — Terraform scenarios for Azure OIDC and GitHub Secrets management
- **OIDC Authentication** — Passwordless GitHub Actions ↔ Azure authentication

## Documentation

| Document | Description |
|---|---|
| [Getting Started](docs/getting_started.md) | Prerequisites, quick start, infrastructure setup, workflows, and CLI reference |
| [References](docs/references.md) | External links and resources |

## Infrastructure (Terraform Scenarios)

| Scenario | Description |
|---|---|
| [Azure GitHub OIDC](infra/scenarios/azure_github_oidc/README.md) | Create Azure Service Principal with OIDC for GitHub Actions |
| [GitHub Secrets](infra/scenarios/github_secrets/README.md) | Register secrets into GitHub repository environment |

## License

[MIT](LICENSE)
