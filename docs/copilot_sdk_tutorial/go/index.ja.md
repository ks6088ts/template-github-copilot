# GitHub Copilot SDK チュートリアル (Go)

Go 向け **GitHub Copilot SDK** を使って実際のアプリケーションを構築するためのステップバイステップガイドです。

> SDK が初めての方は、まず言語依存しない
> [概要と概念](../index.md)（*GitHub Copilot SDK とは何か・何でないか*）と、
> Copilot CLI のインストールと GitHub 認証を扱う
> [共通セットアップ](../getting_started.md)をご覧ください。このページは **Go** 版に焦点を当てます。

---

## チュートリアル構成

各チュートリアルは**解説ドキュメント**とそのままビルドして実行できる **CLI サブコマンド**をペアで提供します。

| # | チュートリアル | サブコマンド | ステータス | 学べること |
|---|----------------|--------------|------------|------------|
| 1 | [CLI チャットボット](tutorials/01_chat_bot.md) | `tutorial chat-bot` | 利用可能 | クライアント／セッション作成、プロンプト送信、ストリーミング、インタラクティブループ |
| 2 | [Issue トリアージボット](tutorials/02_issue_triage.md) | `tutorial issue-triage` | 利用可能 | `DefineTool`、型付きツール I/O、ツール呼び出しエージェント |
| 3 | [ストリーミングレビュー](tutorials/03_streaming_review.md) | `tutorial streaming-review` | 利用可能 | ストリーミングデルタ、リアルタイム出力 |
| 4 | [スキルによるドキュメント生成](tutorials/04_skills_docgen.md) | `tutorial skills-docgen` | 利用可能 | `SkillDirectories`、`SKILL.md`、ドキュメント生成 |
| 5 | [監査ログ](tutorials/05_audit_hooks.md) | `tutorial audit-hooks` | 利用可能 | セッションフック、パーミッションハンドラ、監査ログ |
| 6 | [BYOK Azure OpenAI](tutorials/06_byok_azure_openai.md) | `tutorial byok-azure-openai` | 利用可能 | `ProviderConfig`、Azure OpenAI API キー＆Entra ID |

> すべてのサブコマンドは [`src/go/cmd/tutorial/`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/) にあります。

---

## クイックスタート

まず Copilot CLI がインストール・認証済みであることを確認してください—共通の
[はじめに](../getting_started.md)を参照。その上で:

```bash
# 1. CLI をビルド（src/go/Makefile を利用）
cd src/go
make build

# 2. 最初のチュートリアルサブコマンドを実行（SDK がオンデマンドで CLI を起動）
./dist/template-github-copilot-go tutorial chat-bot --prompt "Hello, Copilot!"
```

Go 固有のセットアップについては [はじめに（Go）](getting_started.md) を参照してください。

---

## スコープ

**含めるもの:**

- GitHub Copilot SDK の概念説明（何であるか／何でないか）
- Go SDK の API 設計とインタフェース
- 具体的なユースケースに基づくサンプルコードとステップバイステップガイド
- ストリーミング、インタラクティブセッション、単独 CLI サーバーへの接続

**含めないもの:**

- 他言語の SDK の詳細（[参考文献](../appendix/references.md) を参照）
- Copilot CLI 単体の使い方ガイド
- 本番運用・スケーリング・インフラ構築の詳細
- GitHub OAuth App 認証フロー（[CopilotReportForge ドキュメント](../../copilot_report_forge/guide/github_oauth_app.md) を参照）

---

## さらに読む

| ドキュメント | 説明 |
|-------------|------|
| [概要](../index.md) | 言語依存しない概念と言語選択 |
| [アーキテクチャ](../architecture.md) | SDK、CLI サーバー、Copilot API の相互作用 |
| [はじめに（Go）](getting_started.md) | Go 固有のセットアップ、CLI のビルド、最初の実行 |
| [CLI サーバーモード](../server_mode.md) | Copilot CLI を単独 TCP サーバーとして起動する |
| [参考文献](../appendix/references.md) | API リファレンスと外部リンク |
| [Go SDK リファレンス (pkg.go.dev)](https://pkg.go.dev/github.com/github/copilot-sdk/go) | 自動生成された Go API ドキュメント |
