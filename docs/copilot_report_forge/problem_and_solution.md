# Problem & Solution

> **Navigation:** [README](../../README.md) > **Problem & Solution**
>
> **See also:** [Architecture](architecture.md) · [Deployment](deployment.md) · [Responsible AI](responsible_ai.md)

---

## Problem Definition

Organizations across every industry are recognizing the transformative potential of Large Language Models (LLMs), yet face significant barriers to operationalizing AI at scale.

### 1. Manual, Ad-Hoc AI Usage

Professionals interact with LLMs through browser-based chat UIs on a case-by-case basis. Insights are copy-pasted into documents, spreadsheets, or messaging tools with no structured output, version control, or audit trail. This pattern repeats across industries — product managers evaluating features, real estate agents assessing properties, clinicians summarizing patient notes.

### 2. Custom Inference Infrastructure Overhead

Hosting or fine-tuning models requires GPU provisioning, model serving frameworks (vLLM, TGI), monitoring, and security hardening. This imposes significant cost and operational burden for teams whose primary need is text generation and evaluation, not model research.

### 3. Secrets Management Fragility

Connecting CI/CD pipelines to cloud services typically involves long-lived API keys stored as repository secrets. These keys are difficult to rotate, easy to leak, and violate zero-trust principles — a critical concern in regulated industries like healthcare, finance, and government.

### 4. Lack of Structured, Multi-Perspective Output

When LLM responses are used for reporting, evaluation, or decision support, there is no standard format for:
- Aggregating results from **multiple queries** (or multiple AI personas) into a single document
- Tracking success/failure across batch operations
- Distributing results securely to stakeholders who may not have direct system access

### 5. No Framework for Multi-Persona AI Evaluation

Many real-world evaluation tasks require **multiple expert perspectives** — e.g., a product needs feedback from a quality engineer, a consumer researcher, and a regulatory specialist simultaneously. Existing tools provide no way to parallelize persona-driven queries and aggregate their outputs into a unified report.

### 6. Reproducibility and Governance Gaps

Infrastructure setup is manual or documented only in wikis. There is no codified, version-controlled process for provisioning cloud resources, registering secrets, or deploying AI services — leading to configuration drift and audit gaps.

---

## Solution

**CopilotReportForge** addresses each of these challenges with a cohesive, production-ready platform designed for cross-industry applicability:

### Automated, Parallel Multi-Persona Queries

The GitHub Copilot SDK enables programmatic, parallel chat sessions. Multiple queries are sent concurrently via `asyncio.gather`, each with its own system prompt (persona), and results are aggregated into a structured `ReportOutput` JSON schema with fields for `query`, `response`, `error`, `total`, `succeeded`, and `failed`.

**Cross-industry impact:** A product development team can run parallel evaluations from the perspectives of "Quality Engineer", "Consumer Researcher", and "Regulatory Specialist" — each producing independent, structured feedback in a single workflow execution.

### Zero Infrastructure for Model Hosting

By leveraging the GitHub Copilot CLI as a local proxy to hosted LLM models (GPT-5-mini, GPT-5, Claude), teams avoid deploying or managing any inference infrastructure. The Copilot CLI handles authentication, model routing, and rate limiting transparently.

### Passwordless OIDC Authentication

GitHub Actions authenticates to Azure via OpenID Connect (OIDC) federated identity credentials. No long-lived secrets are stored for Azure access. The Terraform `azure_github_oidc` scenario provisions:

- An Entra ID application and service principal
- A federated identity credential trusting the GitHub OIDC provider
- RBAC role assignments (Contributor, Storage Blob Data Contributor, Storage Blob Delegator)

### Structured Output with Secure Sharing

Reports are serialized as JSON, uploaded to Azure Blob Storage, and shared via time-limited SAS URLs. This provides:

- Immutable, versioned artifacts (blob name includes timestamp or run ID)
- Controlled access (SAS URLs expire after a configurable duration)
- Integration with downstream systems (any HTTP client can fetch the report)

### Foundry Agent Integration for Domain-Specific AI

For advanced scenarios, the platform integrates Microsoft Foundry Agents via custom Copilot tools. This enables:

- **Domain-specific AI personas** — Create agents with tailored instructions (e.g., "You are a real estate layout evaluator specializing in ADA compliance")
- **Reference data access** — Agents can reference documents, images, and layouts stored in Azure Blob Storage
- **Multi-agent orchestration** — The Copilot session autonomously delegates to the appropriate Foundry Agent based on the query context

**Real Estate Example:** Upload floor plan images to Blob Storage, configure a Foundry Agent as a "layout reviewer", and dispatch queries like "Evaluate accessibility of layout plan A" — the agent references the stored floor plan and produces a structured evaluation.

### Infrastructure as Code

All Azure and GitHub resources are managed via Terraform:

| Scenario | What It Provisions |
|---|---|
| `azure_github_oidc` | Entra ID app, service principal, federated credential, RBAC roles |
| `github_secrets` | GitHub environment with ARM_CLIENT_ID, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID, ARM_USE_OIDC, COPILOT_GITHUB_TOKEN |
| `azure_microsoft_foundry` | Resource group, AI Foundry account, project, model deployments |

### Notification and Integration

A Slack notification CLI (`scripts/slacks.py`) enables real-time alerts when reports are generated, making it easy to integrate AI-driven outputs into existing team communication workflows.

---

## Cross-Industry Applicability

The platform's design — **parameterized system prompts as personas**, **queries as evaluation dimensions**, **Foundry Agents as domain specialists**, and **Blob Storage as a reference data layer** — makes it applicable far beyond software engineering:

| Industry | Use Case | System Prompt (Persona) | Queries (Dimensions) |
|---|---|---|---|
| **Manufacturing** | Sensory evaluation report for new product | "You are a sensory panelist specializing in texture analysis" | Texture, aroma, visual appeal, mouthfeel |
| **Real Estate** | Floor plan accessibility evaluation | "You are an ADA compliance evaluator" | Wheelchair access, door widths, egress routes |
| **Healthcare** | Clinical guideline summary | "You are a board-certified pharmacist" | Drug interactions, dosage guidelines, contraindications |
| **Education** | Multi-subject curriculum design | "You are a K-12 curriculum designer" | Learning objectives, assessment rubrics, lesson plans |
| **Finance** | Deal memo risk analysis | "You are a credit risk analyst" | Credit exposure, market risk, regulatory compliance |
| **Creative** | Brand campaign evaluation | "You are a cultural sensitivity reviewer" | Inclusivity, brand alignment, market resonance |
| **Construction** | Building code compliance | "You are a structural engineer" | Load-bearing analysis, fire safety, material specs |
| **R&D** | Patent novelty assessment | "You are a patent attorney" | Prior art, novelty claims, commercial potential |

---

## Design Rationale

| Decision | Rationale |
|---|---|
| **GitHub Copilot SDK over raw API calls** | Provides session management, event streaming, tool integration, and permission handling out of the box |
| **Typer-based CLIs** | Consistent, testable CLI interface with auto-generated help; composable with `make` targets |
| **Pydantic models for I/O** | Enforces schema validation, enables JSON serialization, and documents data contracts |
| **asyncio for parallelism** | Lightweight concurrency for I/O-bound LLM calls without threading complexity |
| **Terraform over ARM/Bicep** | Multi-cloud capable, state management, plan/apply workflow, module reuse |
| **OIDC over service principal secrets** | Eliminates secret rotation, reduces blast radius, aligns with zero-trust |
| **SAS URLs over public blob access** | Time-bounded, revocable, scoped to individual blobs |
| **Foundry Agents as Copilot tools** | Enables autonomous agent delegation within Copilot sessions — no manual orchestration |
| **System prompt as persona parameter** | Makes domain adaptation a configuration change, not a code change |
