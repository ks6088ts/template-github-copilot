# Responsible AI Notes

> **Navigation:** [README](../../README.md) > **Responsible AI**
>
> **See also:** [Problem & Solution](problem_and_solution.md) · [Architecture](architecture.md) · [Deployment](deployment.md)

---

## Overview

CopilotReportForge uses Large Language Models (LLMs) via the GitHub Copilot SDK and Azure AI Foundry to generate text-based reports, power agentic workflows, and enable multi-persona AI evaluations. Because the platform is designed for **cross-industry use** — from product development and real estate to healthcare and finance — responsible AI considerations must be evaluated in the context of each deployment domain.

---

## Intended Use

| Aspect | Description |
|---|---|
| **Primary Use Case** | Automated generation of structured reports, evaluations, and assessments from parallel LLM queries |
| **Target Users** | Enterprise teams, product managers, domain specialists, operations teams integrating AI into workflows |
| **Deployment Context** | GitHub Actions workflows, CLI tools, Azure Blob Storage for artifact distribution |
| **Cross-Industry Applications** | Product sensory evaluation, real estate layout assessment, clinical summaries, financial risk analysis, curriculum design, creative review |
| **Not Intended For** | Medical diagnosis, legal advice, financial trading decisions, autonomous safety-critical decision-making, or any context where AI output replaces qualified human judgment without review |

---

## Fairness

### Potential Risks

- **Bias in model outputs:** LLMs may reflect biases present in their training data, which can surface in generated evaluations and reports — particularly when assessing products, properties, or people across different demographic or cultural contexts.
- **Unequal performance across domains:** Model accuracy and depth may vary significantly across industries, languages, and cultural contexts. A persona configured as a "sensory panelist" may produce less reliable results for unfamiliar product categories.
- **Persona-induced bias:** System prompts that define AI personas (e.g., "You are a luxury real estate appraiser") may inadvertently introduce systematic biases in evaluation criteria.

### Mitigations

- **System prompts:** Use clear, specific system prompts that constrain the model's behavior and output format. The template supports `SystemMessageReplaceConfig` to set explicit instructions per session.
- **Multi-persona balance:** When using multiple AI personas for evaluation, include diverse perspectives to counterbalance individual biases (e.g., pair a "market analyst" with a "consumer advocate").
- **Human review:** Generated reports should be reviewed by a qualified human before being used for decision-making or external distribution — regardless of domain.
- **Query design:** Frame queries neutrally and avoid prompts that could elicit biased or discriminatory content.

---

## Transparency

### How This System Works

1. Users submit natural-language queries via GitHub Actions `workflow_dispatch`, CLI commands, or programmatic API calls.
2. Queries are sent in parallel to hosted LLM models through the GitHub Copilot SDK, each with a configurable system prompt (persona).
3. For agentic workflows, queries may be routed to Microsoft Foundry Agents with domain-specific instructions and access to reference data in Blob Storage.
4. Model responses are aggregated into a structured JSON report (`ReportOutput`).
5. Reports are uploaded to Azure Blob Storage and shared via time-limited SAS URLs.

### What Users Should Know

- **Model selection matters:** Different models (GPT-5-mini, GPT-5, Claude) have different capabilities, costs, and behavior characteristics. Choose the model appropriate for your use case and risk level.
- **No guaranteed accuracy:** LLM outputs may contain factual errors, hallucinations, or outdated information. The `ReportOutput` schema includes `error` fields to surface failures, but successful responses are not validated for factual correctness.
- **System prompts influence output:** The system prompt directly shapes model behavior. Changing the system prompt will change the nature, quality, and potential biases of outputs.
- **Domain expertise is not replaced:** AI personas configured via system prompts simulate domain expertise but do not possess actual professional qualifications, certifications, or accountability.

---

## Reliability & Safety

### Potential Risks

- **Hallucination:** Models may generate plausible but factually incorrect statements — particularly dangerous in healthcare, legal, and financial contexts.
- **Prompt injection:** Malicious or unintended content in queries could manipulate model behavior, especially when queries are sourced from external inputs.
- **Service availability:** Copilot SDK and Azure services may experience outages or rate limiting.
- **Domain misapplication:** Using the platform for high-stakes decisions (medical, legal, financial) without adequate human oversight could lead to harmful outcomes.

### Mitigations

- **Structured output validation:** All outputs are validated through Pydantic models (`ReportResult`, `ReportOutput`) with explicit `error` fields.
- **Error handling:** The `run_parallel_chat` function catches exceptions per query and records them without failing the entire batch.
- **Permission handling:** The SDK's `PermissionRequest` system provides a control point for tool execution approval. The default `approve_all` handler should be replaced with a restrictive policy in production.
- **Rate limiting:** The Copilot CLI server manages rate limiting with the upstream LLM provider.
- **Domain-appropriate guardrails:** For regulated industries, integrate Azure AI Content Safety or equivalent filtering before distributing reports.

---

## Privacy & Security

### Data Handling

| Data Type | Handling |
|---|---|
| **User queries** | Sent to hosted LLM endpoints via Copilot CLI; not stored locally beyond the session |
| **Model responses** | Serialized to JSON and uploaded to Azure Blob Storage; accessible only via SAS URL or RBAC |
| **Reference data** | Documents, images, and layouts stored in Blob Storage may be accessed by Foundry Agents during evaluation |
| **Authentication tokens** | OIDC tokens are short-lived and scoped; no long-lived secrets stored for Azure access |
| **Environment variables** | Stored in `.env` (gitignored) or GitHub environment secrets (encrypted at rest) |

### Recommendations

- **Do not include PII or sensitive data in queries** unless the storage and model hosting comply with your organization's data governance policies.
- **Review Azure Blob Storage access controls:** Ensure containers are not publicly accessible. Use private containers with SAS URL sharing only.
- **Classify reference data:** When uploading floor plans, product specs, or other reference documents to Blob Storage for agent access, ensure they are classified appropriately per your data governance policy.
- **Rotate `COPILOT_GITHUB_TOKEN`** regularly and use the minimum required scope.
- **Replace `approve_all` permission handler** in production deployments with a policy that restricts tool execution to known, audited tools.

---

## Accountability

### Human Oversight

- Generated reports carry a `system_prompt` field documenting the instructions (persona) given to the model.
- The `succeeded` / `failed` counters provide visibility into query reliability.
- All workflows run within GitHub Actions with full audit logs (run history, inputs, outputs).
- Foundry Agent interactions are logged with `agent_name` and `conversation_id` for traceability.

### Limitations to Communicate to Stakeholders

1. **LLM outputs are not verified for factual accuracy.** Treat them as drafts requiring human review — especially for domain-specific evaluations.
2. **AI personas are simulations, not experts.** A system prompt saying "You are a board-certified pharmacist" does not confer medical authority on the output.
3. **Model behavior may change over time** as the underlying LLM is updated by the provider.
4. **This template does not implement content filtering.** If content moderation is required, integrate Azure AI Content Safety or equivalent filtering before distributing reports.
5. **The template does not track provenance of model outputs.** If audit trails for individual model responses are required, extend the `ReportResult` schema with metadata such as model version, timestamp, and token usage.

---

## Cross-Industry Considerations

| Industry | Key Risk | Recommended Mitigation |
|---|---|---|
| **Healthcare** | Hallucinated medical information | Mandatory clinical review; do not use for diagnosis or treatment decisions |
| **Finance** | Inaccurate risk assessments | Human analyst sign-off required; use as decision-support only |
| **Real Estate** | Biased property evaluations | Multi-persona evaluation with diverse criteria; human appraiser review |
| **Education** | Culturally inappropriate content | Review generated curricula for cultural sensitivity and age-appropriateness |
| **Manufacturing** | Incorrect quality assessments | Use as supplementary data alongside physical testing and inspection |
| **Legal** | Hallucinated legal precedents | Never use as legal advice; require attorney review of all outputs |

---

## Sustainability

- **Right-size model selection:** Use smaller models (e.g., GPT-5-mini) for simple queries to reduce compute and energy consumption.
- **Batch queries efficiently:** The parallel execution pattern minimizes wall-clock time and session overhead compared to sequential requests.
- **Clean up resources:** Terraform `destroy` commands should be used to deprovision unused infrastructure.

---

## Checklist for Deployers

Before deploying this platform in a production or enterprise context, review the following:

- [ ] **System prompts reviewed** for appropriateness, clarity, and bias mitigation — especially when defining domain-specific personas
- [ ] **Permission handler updated** from `approve_all` to a restrictive policy
- [ ] **Human review process** established for generated reports before external distribution
- [ ] **PII/sensitive data policies** confirmed for queries sent to LLM endpoints and reference data stored in Blob Storage
- [ ] **Azure Blob Storage access** confirmed as private (no public container access)
- [ ] **SAS URL expiry** configured to the minimum viable duration
- [ ] **Content filtering** evaluated and integrated if required by organizational or regulatory policy
- [ ] **Model selection** documented with rationale for the chosen model per use case
- [ ] **Domain-specific risks** assessed and mitigated (see Cross-Industry Considerations above)
- [ ] **Stakeholders informed** that outputs are AI-generated and may contain errors
- [ ] **Incident response plan** in place for model failures, hallucinations, or misuse
