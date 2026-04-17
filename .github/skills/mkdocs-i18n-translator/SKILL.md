---
name: mkdocs-i18n-translator
description: Translate Markdown files under `docs/` following the Material for MkDocs i18n plugin rules, emitting language-suffixed files (e.g. `hoge.md` → `hoge.ja.md`) while preserving Markdown structure. Also updates `mkdocs.yml` nav when new source files are added. Use when the user asks to translate docs, add Japanese (or any locale) versions of pages, or maintain multilingual MkDocs sites that use the `i18n` plugin with `docs_structure: suffix`.
---

# MkDocs i18n Translation Skill

Translate Markdown documents in this repository according to the Material for MkDocs i18n plugin convention (`docs_structure: suffix`) and keep `mkdocs.yml` consistent.

Always load and follow the detailed rules in [references/rules.md](references/rules.md) before translating. Those rules are authoritative; this file describes the workflow.

## When to use

- The user asks to translate files under `docs/` to another language (default: Japanese `ja`).
- The user adds a new English page and wants the Japanese counterpart.
- The user asks to review/fix existing translations for consistency with the rules.

## Inputs

- `source_file_path`: path to the source Markdown file (e.g. `docs/guide/getting_started.md`).
- `source_lang` (default `en`): language of the source.
- `target_lang` (default `ja`): target locale code. Must be one of the `locale` values listed under `plugins.i18n.languages` in `mkdocs.yml`.

If the user does not specify files, infer the set of targets by listing `docs/**/*.md` and excluding files that already have a `.{target_lang}.md` sibling.

## Workflow

1. **Verify configuration.** Read `mkdocs.yml` and confirm:
   - `plugins.i18n.docs_structure: suffix` is set.
   - `target_lang` is listed under `plugins.i18n.languages`.
   If not, stop and ask the user before proceeding.

2. **Resolve output path.** Convert `foo/bar.md` → `foo/bar.{target_lang}.md`. Never translate a file whose name already contains a language suffix (e.g. `*.ja.md`). Place the output in the **same directory** as the source.

3. **Translate the content.** Apply every rule in [references/rules.md](references/rules.md). Key invariants:
   - Preserve Markdown structure exactly (headings, lists, tables, blank lines, line order).
   - Do not modify code blocks, inline code, URLs, image paths, or link targets.
   - For links `[text](url)`, translate only `text`.
   - Maintain consistent terminology across files; keep well-known technical terms in English when idiomatic.
   - Preserve YAML frontmatter keys; translate only values that are human-readable prose.

4. **Write the translated file.** Create the new file at the resolved output path. Do not overwrite an existing translation without explicit confirmation from the user.

5. **Update `mkdocs.yml` when adding new source files.** If (and only if) the source `.md` file itself is new and not yet referenced in `nav:`, add it to `nav:` using the **English path** (the i18n plugin resolves the localized variants automatically). Do not add `*.ja.md` entries to `nav:`. Keep existing ordering and indentation style.

6. **Verify.** Re-read the output and confirm:
   - The file parses as Markdown (headings level-balanced, code fences closed).
   - No link targets or code blocks were altered.
   - Line count is close to the source (±a few lines only when natural in the target language).

## Output format

For each translated file, report:

- `translated_file_path`: resolved output path.
- Brief 1-line summary of any `mkdocs.yml` change, or "no nav change".

## Non-goals

- Do not restructure the docs tree or rename existing files.
- Do not translate filenames, anchors, or slugs.
- Do not add new content beyond what exists in the source.

## References

- [references/rules.md](references/rules.md) — complete translation rules (structure preservation, do-not-translate list, style guide).
- Material for MkDocs i18n plugin: `docs_structure: suffix` convention.
