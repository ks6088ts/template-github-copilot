# はじめに（Python）

このガイドでは、チュートリアルスクリプトを実行するための **Python 固有** のセットアップを
説明します。Copilot CLI のインストールと GitHub 認証—すべての言語版で共通—については、
まず共通の [はじめに](../getting_started.md) ガイドに従ってください。

---

## 前提条件

| 要件 | 最低バージョン | 用途 |
|------|---------------|------|
| Python | 3.13+ | ランタイム |
| [uv](https://docs.astral.sh/uv/) | 最新版 | パッケージ管理 |
| Node.js（`npm`） または GitHub CLI（`gh`） | 最新版 | Copilot CLI のインストール |
| GitHub Copilot サブスクリプション | — | API アクセスに必要 |

---

## インストール

### SDK とチュートリアルの依存関係をインストール

チュートリアルスクリプトで使用するすべてのパッケージ（`github-copilot-sdk`、`pydantic`、`azure-identity` など）は [`src/python/pyproject.toml`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/pyproject.toml) に宣言されています。`uv sync` コマンド一つでまとめてインストールできます。

```bash
cd src/python
uv sync --all-groups
```

> `uv sync` は `.venv/` に仮想環境を作成し、`uv.lock` に固定された依存関係をすべてインストールします。仮想環境を手動でアクティブ化する代わりに `uv run <command>` を使うと、その環境内でツールを実行できます。

> **ランタイムのダウンロード（SDK v1.0.4 以降）:** Python パッケージは Copilot CLI ランタイムを wheel に同梱しなくなり、初回利用時に固定バージョンのランタイムをダウンロードします。`uv run python -m copilot download-runtime` で事前にキャッシュするか、`COPILOT_CLI_PATH` で既存の `copilot` バイナリを再利用してください。自動ダウンロードのフォールバックを無効化するには `COPILOT_SKIP_CLI_DOWNLOAD=1` を設定します（[Copilot SDK v1.0.4](https://github.com/github/copilot-sdk/releases/tag/v1.0.4)）。

> **CLI・認証・サーバーモードについて:** `copilot` CLI のインストール、`gh auth login`
> または `COPILOT_GITHUB_TOKEN` でのサインイン、CLI を TCP サーバーとして起動する方法は、
> 共通の [はじめに](../getting_started.md) と [CLI サーバーモード](../server_mode.md) ガイドに
> 一度だけまとめています。SDK が stdio 経由で CLI を起動するため、チュートリアルの
> 実行にサーバーは不要です。

---

## 最初のスクリプトを実行する

チュートリアルスクリプトは `src/python` ディレクトリから `uv run python` で実行すると、管理された仮想環境内で動作します。

```bash
cd src/python
uv run python scripts/tutorials/01_chat_bot.py --prompt "What is GitHub Copilot?"
```

期待される出力（ストリーミング）:

```
GitHub Copilot is an AI-powered coding assistant developed by GitHub and OpenAI...
```

---

## オブザーバビリティオプション

すべてのチュートリアルスクリプトは、同じ任意の OpenTelemetry オプションを公開します。
各オプションの既定値は対応する環境変数から読み込まれ、エンドポイントを指定しない限り
テレメトリは無効です。

| オプション | 環境変数 | 用途 |
|------------|----------|------|
| `--otel-endpoint` | `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP エンドポイント（例: `http://localhost:4318`） |
| `--otel-capture-content` | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | スパンにプロンプトと応答の内容を含めるかを示す任意の `true`/`false` |
| `--otel-bsp-schedule-delay` | `OTEL_BSP_SCHEDULE_DELAY` | スパンのバッチフラッシュ間隔（ミリ秒、任意） |

例:

```bash
uv run python scripts/tutorials/01_chat_bot.py \
    --otel-endpoint http://localhost:4318 \
    --otel-bsp-schedule-delay 500 \
    --prompt "Hello!"
```

---

## プロジェクト構成

```
src/python/scripts/tutorials/
├── README.md                   # スクリプト一覧と実行手順
├── 01_chat_bot.py              # チュートリアル 1: CLI チャットボット
├── 02_issue_triage.py          # チュートリアル 2: カスタムツールによる Issue トリアージ
├── 03_streaming_review.py      # チュートリアル 3: ストリーミングコードレビュー
├── 04_skills_docgen.py         # チュートリアル 4: スキルによるドキュメント生成
├── 05_audit_hooks.py           # チュートリアル 5: セッションフックによる監査ログ
├── 06_byok_azure_openai.py     # チュートリアル 6: Azure OpenAI を使った BYOK
└── skills/
    ├── docgen/SKILL.md
    └── coding-standards/SKILL.md
```

---

## 環境変数

すべてのチュートリアルスクリプトは `--cli-url`（デフォルト: *stdio*）を受け付けます。共通の CLI
変数（`COPILOT_GITHUB_TOKEN`、`COPILOT_CLI_PATH`、`COPILOT_CLI_URL`）は共通の
[はじめに](../getting_started.md) で説明しています。加えて、OpenTelemetry は上記の
標準 `OTEL_*` 変数、または同等のスクリプトオプションで設定できます。スクリプト 06 は
さらに次の BYOK 設定も読み込みます。

| 変数名 | 用途 | 使用するスクリプト |
|--------|------|------------------|
| `BYOK_BASE_URL` | Azure OpenAI デプロイのベース URL | スクリプト 06 |
| `BYOK_API_KEY` | Azure OpenAI API キー | スクリプト 06（api-key 認証） |
| `BYOK_MODEL` | モデル/デプロイ名 | スクリプト 06 |

---

## 次のステップ

環境の準備ができたら、チュートリアルを順番に進めてください:

1. [CLI チャットボット](tutorials/01_chat_bot.md) — Copilot を使った最初のスクリプトを作成
2. [カスタムツール](tutorials/02_custom_tools.md) — 独自のツールでエージェントを拡張
3. [ストリーミング](tutorials/03_streaming.md) — リアルタイムでトークンを受信
4. [スキル](tutorials/04_skills.md) — SKILL.md で再利用可能なエージェント動作を定義
5. [フックとパーミッション](tutorials/05_hooks_permissions.md) — すべてのアクションを観察・制御
6. [BYOK](tutorials/06_byok.md) — Azure OpenAI を LLM バックエンドとして利用
