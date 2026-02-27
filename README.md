[![test](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/test.yaml?query=branch%3Amain)
[![docker](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker.yaml?query=branch%3Amain)
[![infra](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml/badge.svg?branch=main)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/infra.yaml?query=branch%3Amain)
[![ghcr-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/ghcr-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/ghcr-release.yaml)
[![docker-release](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker-release.yaml/badge.svg)](https://github.com/ks6088ts/template-github-copilot/actions/workflows/docker-release.yaml)

# template-github-copilot

A showcase repository for multiple use cases built on the **GitHub Copilot SDK**, **Azure AI Foundry**, and **GitHub Actions**.

---

## Core Concept

CopilotReportForge is built on one central idea: **automated report generation through multi-persona parallel agent execution.**

By combining multiple AI personas, parallel processing, and fully automated pipelines, the platform transforms ad-hoc LLM interactions into governed, repeatable, and auditable workflows -- without managing any AI infrastructure.

### Pillar 1: Multi-Persona Parallel Execution

1. Define a single topic (prompt) -- for example, "Evaluate the new wireless headphones"
2. Define multiple personas (quality engineer, consumer researcher, regulatory specialist, etc.) as system prompts
3. Launch all personas as AI agents in parallel using `asyncio.gather`, with each agent producing structured JSON output from its specialized perspective
4. Aggregate all agent results into one `ReportOutput` (Pydantic model)

Personas are **configuration, not code**. By simply swapping system prompts, you can switch from a food industry evaluation panel to a financial risk committee to an architectural compliance review -- without changing the code.

### Pillar 2: 24/7 Autonomous Operation

The entire pipeline runs via GitHub Actions schedule (cron), `workflow_dispatch`, or API triggers:

- Reports can be continuously generated on different topics without human intervention
- The system operates 24 hours a day, regardless of time zone, improving accuracy with each iteration
- Generated reports are stored in Azure Blob Storage and shared to Teams/Slack via SAS URL

### Pillar 3: Domain Agnostic

The persona + parallel execution model can be applied to any industry. The table below shows eight representative use cases:

| Industry | Persona Example | Evaluation Dimensions |
|---|---|---|
| **Manufacturing** | Sensory panelist, Quality engineer | Texture, durability, regulatory compliance |
| **Real Estate** | Layout evaluator, ADA compliance reviewer | Accessibility, traffic flow, space utilization |
| **Healthcare** | Clinical pharmacist, Guideline reviewer | Drug interactions, dosage, contraindications |
| **Finance** | Credit analyst, Compliance officer | Credit exposure, market risk, regulatory adherence |
| **Education** | Curriculum designer, Assessment specialist | Learning objectives, rubric design, lesson plans |
| **Creative** | Brand strategist, Cultural sensitivity reviewer | Inclusivity, brand alignment, market resonance |
| **Legal** | Contract analyst, Regulatory compliance officer | Clause analysis, risk assessment, jurisdictional review |
| **Retail** | Merchandising analyst, Customer experience reviewer | Product placement, pricing strategy, customer satisfaction |

---

## Architecture Overview

![Architecture Overview](https://github.com/user-attachments/assets/71d893b0-99f6-4b14-aca6-c4ec1bb965ee)

**Steps:**

1. Developer accesses GitHub.com
2. Developer triggers GitHub Actions in GitHub.com
3. GitHub Actions connects to Microsoft Azure via OIDC
4. Execute a report service built with the GitHub Copilot SDK
5. Interact with agents in Microsoft Foundry if needed
6. Store generated reports in a storage account
7. Send notification messages to collaboration tools (e.g., Microsoft Teams, Slack)

> For component-level details and data flows, see [Architecture](docs/copilot_report_forge/architecture.md).

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

## License

[MIT](LICENSE)
