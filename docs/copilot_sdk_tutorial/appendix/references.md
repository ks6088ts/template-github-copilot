# References

External links and further reading for the GitHub Copilot SDK.

---

## GitHub Copilot SDK

| Resource | Link |
|----------|------|
| GitHub repository (monorepo) | [github/copilot-sdk](https://github.com/github/copilot-sdk) |
| Changelog | See GitHub releases in the repository |

### SDK Packages by Language

| Language | Package | Link |
|----------|---------|------|
| Python | `github-copilot-sdk` | [PyPI](https://pypi.org/project/github-copilot-sdk/) |
| Go | `github.com/github/copilot-sdk/go` | [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) |
| TypeScript | `@github/copilot-sdk` | [npm](https://www.npmjs.com/package/@github/copilot-sdk) |

---

## GitHub Copilot Documentation

| Resource | Link |
|----------|------|
| GitHub Copilot overview | [docs.github.com/copilot](https://docs.github.com/copilot) |
| GitHub Copilot in the CLI | [docs.github.com/copilot/github-copilot-in-the-cli](https://docs.github.com/copilot/github-copilot-in-the-cli/about-github-copilot-in-the-cli) |
| Copilot API reference | [docs.github.com/copilot/reference](https://docs.github.com/rest/copilot) |
| Personal access tokens | [docs.github.com/authentication](https://docs.github.com/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) |

---

## Azure OpenAI (for BYOK)

| Resource | Link |
|----------|------|
| Azure OpenAI Service | [learn.microsoft.com/azure/ai-services/openai](https://learn.microsoft.com/azure/ai-services/openai/) |
| Azure Identity library | [learn.microsoft.com/python/api/azure-identity](https://learn.microsoft.com/python/api/azure-identity/) |
| DefaultAzureCredential | [DefaultAzureCredential reference](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential) |

---

## Tutorial Libraries by Language

**Python**

| Library | Purpose | Link |
|---------|---------|------|
| `github-copilot-sdk` | Copilot SDK for Python | [PyPI](https://pypi.org/project/github-copilot-sdk/) |
| `pydantic` | Data validation and tool schemas | [pydantic.dev](https://docs.pydantic.dev/) |
| `azure-identity` | Entra ID authentication (BYOK) | [PyPI](https://pypi.org/project/azure-identity/) |

**Go**

| Library | Purpose | Link |
|---------|---------|------|
| `github.com/github/copilot-sdk/go` | Copilot SDK for Go | [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) |
| `github.com/spf13/cobra` | CLI command framework | [pkg.go.dev](https://pkg.go.dev/github.com/spf13/cobra) |
| `github.com/spf13/viper` | Configuration and environment binding | [pkg.go.dev](https://pkg.go.dev/github.com/spf13/viper) |

---

## SDK Source and Releases

| Resource | Link |
|----------|------|
| Monorepo issues and discussions | [github/copilot-sdk/issues](https://github.com/github/copilot-sdk/issues) |
| Releases | [github/copilot-sdk/releases](https://github.com/github/copilot-sdk/releases) |

---

## Change watchlist { #change-watchlist }

Check these sources before each workshop run. The SDK and the Copilot CLI it depends on evolve quickly, so treat this tutorial as a snapshot rather than a contract. Prefer the package registries and release notes over any version frozen in a page.

| Area to watch | Primary source | Why it matters |
|---------------|----------------|----------------|
| SDK releases and API changes | [`github/copilot-sdk` releases](https://github.com/github/copilot-sdk/releases) | Tracks SDK versions and changes to the client, session, event, tool, skill, hook, and permission APIs across languages |
| Python package version | [`github-copilot-sdk` on PyPI](https://pypi.org/project/github-copilot-sdk/) | The version the Python tutorials install and pin |
| Go package version | [Go SDK on pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) | The version the Go tutorials build against |
| SDK how-tos and reference | [GitHub Copilot SDK how-tos](https://docs.github.com/en/copilot/how-tos/copilot-sdk) | Documented workflows for server mode, authentication, and BYOK |
| CLI server behavior | [`github/copilot-cli` changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) | The SDK spawns or connects to the Copilot CLI server, so CLI flag and behavior changes affect [Getting Started](../getting_started.md) and [CLI Server Mode](../server_mode.md) |

## Recent changes reflected in this tutorial

| Date | Change | Source |
|------|--------|--------|
| 2026-07-08 | SDK v1.0.6: experimental context attribution APIs (`getContextAttribution`, `getContextHeaviestMessages`) on `session.metadata`; `SlashCommandInput.choices` for selectable literal options; experimental GitHub telemetry redirection; Python surfaces Pydantic `ValidationError` to LLM in tool arg validation | [Copilot SDK v1.0.6](https://github.com/github/copilot-sdk/releases/tag/v1.0.6) |
| 2026-07-01 | SDK v1.0.5: MCP OAuth host token handlers (`onMcpAuthRequest` callback on session config); session options for citations, excluded built-in agents, and spending limits; `getBearerToken` BYOK field renamed to `bearerTokenProvider` (also adds `sessionId` to `ProviderTokenArgs`) | [Copilot SDK v1.0.5](https://github.com/github/copilot-sdk/releases/tag/v1.0.5) |
| 2026-06-25 | SDK v1.0.4 (Python and Go): the Python package downloads the pinned CLI runtime instead of bundling it (`python -m copilot download-runtime`); adds an HTTP request callback to intercept inference requests, a `getBearerToken` callback for BYOK providers (e.g. Managed Identity), an experimental multi-provider BYOK registry, `preamble`/`preserve` system-message section controls, and `capi.enableWebSocketResponses` / `provider.transport` session options | [Copilot SDK v1.0.4](https://github.com/github/copilot-sdk/releases/tag/v1.0.4) |
| 2026-06-19 | Python and Go SDK tutorials established against the then-current SDK packages and Copilot CLI server mode | [github/copilot-sdk releases](https://github.com/github/copilot-sdk/releases) |
| 2026-06-18 | SDK v1.0.2: opt-in session memory on create/resume, tool `defer` option for tool search, `otlpProtocol` telemetry transport (`http/json` \| `http/protobuf`), `ModelBilling.tokenPrices`, and deterministic telemetry flush on client stop | [Copilot SDK v1.0.2](https://github.com/github/copilot-sdk/releases/tag/v1.0.2) |

---

## Related Projects in This Repository

| Document | Description |
|----------|-------------|
| [CopilotReportForge](../../copilot_report_forge/index.md) | Enterprise multi-persona report generation platform using this SDK |
| [Getting Started](../getting_started.md) | Environment setup for the tutorials |
