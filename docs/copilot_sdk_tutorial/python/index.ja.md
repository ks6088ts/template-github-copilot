# GitHub Copilot SDK チュートリアル（Python）

Python 向け **GitHub Copilot SDK** を使って実際のアプリケーションを構築するためのステップバイステップガイドです。

> SDK が初めての方は、まず言語依存しない
> [概要と概念](../index.md)（*GitHub Copilot SDK とは何か・何でないか*）と、
> Copilot CLI のインストールと GitHub 認証を扱う
> [共通セットアップ](../getting_started.md)をご覧ください。このページは **Python** 版に焦点を当てます。

---

## チュートリアル構成

各チュートリアルは**解説ドキュメント**とそのまま実行できる**独立した CLI スクリプト**をペアで提供します。

| # | チュートリアル | スクリプト | 学べること |
|---|----------------|----------|------------|
| 1 | [CLI チャットボット](tutorials/01_chat_bot.md) | [`01_chat_bot.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/01_chat_bot.py) | CopilotClient、セッション、プロンプト送信、インタラクティブループ |
| 2 | [Issue トリアージボット](tutorials/02_custom_tools.md) | [`02_issue_triage.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/02_issue_triage.py) | `@define_tool` によるカスタムツール、Pydantic I/O |
| 3 | [ストリーミングレビュー](tutorials/03_streaming.md) | [`03_streaming_review.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/03_streaming_review.py) | `ASSISTANT_MESSAGE_DELTA` によるストリーミング |
| 4 | [スキルによるドキュメント生成](tutorials/04_skills.md) | [`04_skills_docgen.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/04_skills_docgen.py) | `SKILL.md` によるエージェントスキル |
| 5 | [監査ログ](tutorials/05_hooks_permissions.md) | [`05_audit_hooks.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/05_audit_hooks.py) | セッションフック、パーミッションハンドラ |
| 6 | [BYOK Azure OpenAI](tutorials/06_byok.md) | [`06_byok_azure_openai.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/06_byok_azure_openai.py) | Azure OpenAI を使った Bring Your Own Key |

> すべてのスクリプトは [`src/python/scripts/tutorials/`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/) にあります。

---

## クイックスタート

まず Copilot CLI がインストール・認証済みであることを確認してください—共通の
[はじめに](../getting_started.md)を参照。その上で:

```bash
# 1. SDK とチュートリアルの依存関係をインストール（src/python/pyproject.toml を利用）
cd src/python
uv sync --all-groups

# 2. チュートリアルスクリプトを実行（SDK がオンデマンドで CLI を起動）
uv run python scripts/tutorials/01_chat_bot.py --prompt "Hello, Copilot!"
```

Python 固有のセットアップについては [はじめに（Python）](getting_started.md) を参照してください。

---

## スコープ

**含めるもの:**

- GitHub Copilot SDK の概念説明（何であるか／何でないか）
- アーキテクチャと動作原理
- Python SDK の API 設計とインタフェース
- 具体的なユースケースに基づくサンプルコードとステップバイステップガイド
- Agent Skills、カスタムツール、セッションフック、パーミッションハンドリング、ストリーミング、BYOK

**含めないもの:**

- TypeScript / .NET SDK の詳細（[参考文献](../appendix/references.md) を参照）
- Copilot CLI 単体の使い方ガイド
- 本番運用・スケーリング・インフラ構築の詳細
- GitHub OAuth App 認証フロー（[CopilotReportForge ドキュメント](../../copilot_report_forge/guide/github_oauth_app.md) を参照）
- `template_github_copilot` パッケージ内部（チュートリアルスクリプトは自己完結）

---

## さらに読む

| ドキュメント | 説明 |
|-------------|------|
| [概要](../index.md) | 言語依存しない概念と言語選択 |
| [アーキテクチャ](../architecture.md) | SDK、CLI サーバー、Copilot API の相互作用 |
| [はじめに（Python）](getting_started.md) | Python 固有のセットアップと最初の実行 |
| [CLI サーバーモード](../server_mode.md) | Copilot CLI を単独 TCP サーバーとして起動する |
| [参考文献](../appendix/references.md) | API リファレンスと外部リンク |
