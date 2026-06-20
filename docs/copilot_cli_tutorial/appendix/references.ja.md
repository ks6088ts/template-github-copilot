# References

本ワークショップのすべての技術的記述は、以下の **一次情報** に基づいています。製品が進化している箇所では、文書に固定された値よりも、ライブのコマンド（`/help`、`/model`、`copilot help <topic>`）を優先してください。

---

## 一次情報 — GitHub 公式ドキュメント

| ドキュメント | 扱う内容 |
|--------------|----------|
| [About GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) | 概念: モード、コンテキスト管理、カスタマイズ、セキュリティ、モデル利用、サンドボックス、ACP |
| [Using GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) | How-to: セッション、Tips、カスタム指示／エージェント／スキル、MCP、コンテキストコマンド |
| [Best practices for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices) | モデル、Plan モード、無限セッション、delegate、ワークフロー、応用パターン、チーム向け指針 |
| [Installing GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli) | インストール方法と前提条件 |
| [GitHub Copilot features](https://docs.github.com/en/copilot/get-started/features) | サーフェス横断の assistive／agentic／customization／admin 分類 |
| [Adding custom instructions for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions) | 指示ファイルの場所と優先順位 |
| [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | `SKILL.md` スキルの作成 |
| [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | スキルの概念 |
| [Creating custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-custom-agents) | エージェントプロファイルのスキーマ |
| [About hooks for GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/hooks) | ライフサイクルフック |
| [About GitHub Copilot Memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory) | 永続的なリポジトリメモリ |
| [About Model Context Protocol (MCP)](https://docs.github.com/en/copilot/concepts/context/mcp) | MCP の概念 |
| [Configure MCP servers (JSON structure)](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp#writing-a-json-configuration-for-mcp-servers) | `mcp-config.json` スキーマ |
| [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review) | 自動コードレビュー |
| [About cloud and local sandboxes](https://docs.github.com/en/copilot/concepts/about-cloud-and-local-sandboxes) | サンドボックスモデル: ローカル／クラウド、セッションライフサイクル、認証、課金 |
| [Configuring local sandbox settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings) | `/sandbox` UI: General／Filesystem／Network 設定とプラットフォーム制限 |
| [Enabling or disabling cloud sandboxes for your organization](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/enabling-or-disabling-cloud-sandboxes-for-your-organization) | 組織ポリシー: Cloud Sandbox access |
| [Billing for cloud and local sandboxes](https://docs.github.com/en/billing/concepts/product-billing/cloud-and-local-sandboxes) | クラウドサンドボックスの Compute／Memory／Storage メーター |
| [Models and pricing for GitHub Copilot](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) | プレミアムリクエスト、モデルコスト |
| [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | コマンド・フラグの完全な一覧 |
| [Copilot CLI configuration directory](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) | `~/.copilot` 設定リファレンス |
| [Copilot CLI ACP server](https://docs.github.com/en/copilot/reference/copilot-cli-reference/acp-server) | Agent Client Protocol |
| [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | どのカスタマイズ機能をいつ使うか |
| [Plans for GitHub Copilot](https://github.com/features/copilot/plans) | プラン比較と価格 |

## 一次情報 — GitHub リポジトリとパッケージ

| リソース | 補足 |
|----------|------|
| [github/copilot-cli](https://github.com/github/copilot-cli) | 公式リポジトリ: README、`changelog.md`、install スクリプト、Issue、Discussions |
| [`@github/copilot`（npm）](https://www.npmjs.com/package/@github/copilot) | npm での配布 |
| [Homebrew cask `copilot-cli`](https://formulae.brew.sh/cask/copilot-cli) | macOS／Linux インストール |

## 変更ウォッチリスト { #change-watchlist }

ワークショップ実施前に、以下の情報源を確認してください。Copilot CLI は変化が速いため、静的なワークショップ資料は契約ではなくスナップショットとして扱います。

| 監視領域 | 一次情報 | 重要な理由 |
|----------|----------|------------|
| CLI リリースとコマンド挙動 | [`github/copilot-cli` changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) | CLI バージョン、新しいスラッシュコマンド（`/settings`、`/security-review`、`/worktree`）、prompt mode、MCP 設定読み込み、フック、権限、バグ修正を追跡できる |
| Copilot 全体の製品発表 | [GitHub Blog Changelog — Copilot label](https://github.blog/changelog/label/copilot/) | モデルのリリース／deprecated、public preview、プラン変更、code review 更新、sandbox、BYOK、usage metrics を追跡できる |
| モデル可用性と deprecated 情報 | [Supported models](https://docs.github.com/copilot/reference/ai-models/supported-models)、[GitHub Blog Changelog — Copilot](https://github.blog/changelog/label/copilot/) | モデル名とプランごとの利用可否は頻繁に変わる。例では固定名をコピーさせず `/model` を使わせるべき |
| BYOK／外部プロバイダーモデル | [Using your own LLM models in GitHub Copilot CLI](https://docs.github.com/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models)、[Using your LLM provider API keys with Copilot](https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-enterprise/use-your-own-api-keys) | クライアント側 BYOK と Enterprise 管理の外部プロバイダーモデルを区別するため |
| サンドボックス | [About cloud and local sandboxes](https://docs.github.com/en/copilot/concepts/about-cloud-and-local-sandboxes)、[GitHub Blog sandbox announcement](https://github.blog/changelog/2026-06-02-cloud-and-local-sandboxes-for-github-copilot-now-in-public-preview) | public preview の挙動、pricing、プラットフォーム対応、ポリシー制御が変わりうる |
| MCP と agent discovery | [MCP management](https://docs.github.com/en/copilot/concepts/mcp-management)、[`github/copilot-cli` changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) | MCP 設定場所、registry、`deferTools`、Agent finder が活発に変化している |
| Code review の挙動 | [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)、[AGENTS.md support announcement](https://github.blog/changelog/2026-06-18-copilot-code-review-agents-md-support-and-ui-improvements) | レビュー指示、draft PR review UX、timeline 表示が Demo 2 に影響する |
| 利用状況と課金シグナル | [Copilot usage metrics API](https://docs.github.com/enterprise-cloud@latest/rest/copilot/copilot-usage-metrics?apiVersion=2026-03-10)、[AI credits usage API announcement](https://github.blog/changelog/2026-06-19-ai-credits-consumed-per-user-now-in-the-copilot-usage-metrics-api) | ワークショップ運営者は AI クレジット消費と管理者レポートを正確に説明する必要がある |

### 本ワークショップに反映済みの最近の変更

| 日付 | 変更 | 出典 |
|------|------|------|
| 2026-06-19 | ユーザーレベルの Copilot usage metrics API レポートに `ai_credits_used` が追加 | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-19-ai-credits-consumed-per-user-now-in-the-copilot-usage-metrics-api) |
| 2026-06-18 | Copilot cloud-agent PR の生成リリースノートで、`@copilot` と並んで依頼した開発者もクレジット | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-18-generated-release-notes-credit-you-for-copilot-pull-requests) |
| 2026-06-18 | Copilot code review がリポジトリルートの `AGENTS.md` を読むようになった | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-18-copilot-code-review-agents-md-support-and-ui-improvements) |
| 2026-06-17 | Enterprise 管理の外部プロバイダーモデルが Copilot CLI の `/model` に表示 | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-17-copilot-cli-supports-enterprise-bring-your-own-key-byok-models) |
| 2026-06-11 | `/settings` が統一された schema-driven settings UI とインライン設定変更を提供 | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-11-copilot-cli-configure-everything-from-one-place-with-settings) |
| 2026-06-10 | `/security-review` が experimental public-preview CLI command として追加 | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli) |
| 2026-06-04 | 対応モデルで 100 万トークンコンテキストと configurable reasoning levels が利用可能に | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-04-larger-context-windows-and-configurable-reasoning-levels-for-github-copilot) |
| 2026-06-02 | Rubber duck と voice input が generally available。prompt scheduling と新 terminal UI は `/experimental` 配下 | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-02-copilot-cli-improved-ui-rubber-duck-prompt-scheduling-and-voice-input) |
| 2026-06-02 | Cloud / local sandboxes が public preview に入った | [GitHub Blog Changelog](https://github.blog/changelog/2026-06-02-cloud-and-local-sandboxes-for-github-copilot-now-in-public-preview) |
| 2026-06-02 / 2026-06-05 / 2026-06-18 | GPT-4.1、GPT-5.2/GPT-5.2-Codex、Opus 4.6 (fast) の deprecated 通知 | [GitHub Blog Changelog](https://github.blog/changelog/label/copilot/) |

## ハンズオン演習

| リソース | 補足 |
|----------|------|
| [Creating applications with Copilot CLI（GitHub Skills）](https://github.com/skills/create-applications-with-the-copilot-cli) | 公式のガイド付き演習: Issue → アプリ → テスト → PR |

## トーク・デモ

| リソース | 補足 |
|----------|------|
| [GitHub Copilot Anywhere: From Remote Control CLIs to Cloud Sandboxes（DEM305）](https://www.youtube.com/watch?v=JJmmunwXcu8) | Microsoft Developer のデモ。[Copilot Anywhere](../features.md#sandboxing) の説明の元ネタ: CLI のリモートコントロール（prompt mode、ACP、`/delegate`）と、任意のデバイスから再開できるクラウドサンドボックスへの作業オフロード |

## このサイト内の関連資料

| ドキュメント | 関係 |
|--------------|------|
| [Copilot SDK チュートリアル](../../copilot_sdk_tutorial/index.md) | プログラマブルなサーフェス — 同じランタイムをコードに組み込む |
| [Copilot SDK · アーキテクチャ](../../copilot_sdk_tutorial/architecture.md) | SDK・CLI サーバー・Copilot API の相互作用 |
| [Copilot SDK · CLI Server Mode](../../copilot_sdk_tutorial/server_mode.md) | CLI をサーバーとして実行 |

---

## ワークショップの元資料に関する注記

本ワークショップは、参考資料として提供された Microsoft／GitHub 社内のイネーブルメント資料を踏まえています。これらの資料には、将来を見据えた内容やテンプレート的な内容（例: 推測的な将来のモデル名、日付付きのコンテキストウィンドウ値）が含まれており、ここでは **意図的に再現していません**。本ワークショップのすべての事実記述は、代わりに上記の GitHub 一次情報に結び付けています。提供された参考ファイルのうち 3 つは権利保護（暗号化）されており開けませんでした。それらの内容はここには反映されていません。
