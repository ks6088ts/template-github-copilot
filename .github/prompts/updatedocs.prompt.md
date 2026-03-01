---
agent: 'agent'
description: 'Update documentation by analyzing the current docs and codebase, identifying gaps, and generating new content to fill those gaps.'
---

To update documentation, analyze the current documentation and codebase to identify any gaps or outdated information. Then, generate new content to fill those gaps and ensure that the documentation is accurate and up-to-date.

## Japanese Translation

This project uses [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) with the [i18n plugin](https://ultrabug.github.io/mkdocs-static-i18n/) configured as `docs_structure: suffix`. English (`*.md`) is the default language.

### Rules

1. **English is the source of truth.** Always write or update the English (`*.md`) documentation first, then create or update the corresponding Japanese translation.
2. **Naming convention:** For each `FILENAME.md`, place the Japanese translation as `FILENAME.ja.md` in the **same directory**.
   - Example: `docs/index.md` → `docs/index.ja.md`
3. **Scope:** When creating or updating documentation, check whether a `.ja.md` counterpart exists. If it does not, create one. If it already exists, update it to stay in sync with the English version.
4. **Translation quality:**
   - Translate all prose, headings, and descriptions into natural Japanese.
   - Keep code blocks, command examples, variable names, file paths, and URLs unchanged.
   - Preserve the same Markdown structure (headings, lists, admonitions, Mermaid diagrams, etc.) as the English source.
5. **Do not modify `mkdocs.yml` nav entries.** The i18n plugin automatically resolves the suffix-based translations; no additional nav configuration is needed.
