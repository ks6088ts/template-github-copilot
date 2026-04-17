# Translation Rules for Material for MkDocs i18n

These rules are authoritative for the `mkdocs-i18n-translator` skill. Follow them exactly when producing or reviewing translations.

## 📘 Prerequisites (strict)

- English file: `hoge.md`
- Japanese file: `hoge.ja.md`
- Place translated files **in the same directory** as the source.
- Do **not** change any structure other than the filename.
- The site must use the Material for MkDocs `i18n` plugin with `docs_structure: suffix`.

## ⚠️ Translation rules (most important)

### 1. Never change Markdown structure

Preserve all of the following exactly as in the source:

- Headings (`#`, `##`, …)
- Lists (`-`, `*`, numbered)
- Tables (column count, alignment, separators)
- Line breaks and blank lines
- Block quotes, admonitions, HTML blocks

### 2. Do not translate the following

- Code blocks (anything inside ` ``` … ``` `)
- Inline code (`` `code` ``)
- URLs
- Image paths
- File paths, command names, environment variable names

### 3. Do not break links

- In `[text](link)`, the `link` is **forbidden to change**.
- Only the `text` portion may be translated.
- Reference-style link definitions (`[id]: url`) must keep `id` and `url` unchanged.
- Anchors (`#section-id`) must remain unchanged.

### 4. Keep terminology consistent

- Translate the same source term with the same target term throughout the project.
- Keep established technical terms in English when that is the natural usage in the target language (e.g. "repository", "pull request", "OAuth").
- When both forms appear acceptable, prefer the form already used elsewhere in `docs/`.

## 📥 Input

- `source_file_path`: source path, e.g. `docs/hoge.md`
- `source_content`: the Markdown body
- `source_lang`: e.g. `en`
- `target_lang`: e.g. `ja`

## 📤 Output

Produce the following:

### 1. `translated_file_path`

Convert `{name}.md` → `{name}.{target_lang}.md`.

Example:

- `docs/hoge.md` → `docs/hoge.ja.md`
- `docs/guide/getting_started.md` → `docs/guide/getting_started.ja.md`

### 2. `translated_content`

- Markdown format
- Structure fully preserved
- Translated into the target language

## 💡 Translation style

- Natural, concise prose appropriate for technical documentation.
- Meaning-based, not literal word-for-word translation.
- Avoid redundant expressions; prefer clarity and brevity.
- Match the tone already established in existing translated files in the same project.

## 🧪 Additional rules (important)

- **Never change the original line order.** Translated lines appear in the same order as the source.
- If a passage is ambiguous or untranslatable, **leave the original text in place** rather than guessing.
- For YAML frontmatter:
  - Keep every key unchanged.
  - Translate only human-readable string **values** (e.g. `title`, `description`).
  - Do not translate values that are identifiers, slugs, booleans, dates, or paths.

## ✅ Self-check before finishing

Run through this checklist for every translated file:

- [ ] Output path ends with `.{target_lang}.md` and lives beside the source.
- [ ] Heading levels and count match the source.
- [ ] Every code fence in the source is present and unchanged.
- [ ] Every link target (URL, relative path, anchor) is unchanged.
- [ ] No new or removed lines except as required by natural target-language phrasing.
- [ ] Terminology matches other files in `docs/`.
- [ ] Frontmatter keys are unchanged; only prose values are translated.
- [ ] `mkdocs.yml` was updated **only** if a brand-new source `.md` was added, and only with the English path.
