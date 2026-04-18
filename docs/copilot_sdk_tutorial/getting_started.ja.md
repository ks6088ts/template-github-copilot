# はじめに

このガイドでは、ローカル開発環境のセットアップとチュートリアルスクリプトの実行に必要なすべての手順を説明します。

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

---

## GitHub 認証

Copilot CLI は Copilot アクセス権を持つ GitHub アカウントが必要です。

### オプション A: GitHub CLI 認証（推奨）

```bash
gh auth login
# Copilot CLI は gh CLI の認証情報を自動的に利用します。
```

### オプション B: パーソナルアクセストークン（PAT）

1. **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)** に移動
2. `copilot` スコープ（または `read:user` + Copilot 有効な org）でトークンを生成
3. エクスポート:

```bash
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

---

## Copilot CLI のインストール

SDK は **`copilot` CLI** を stdio 経由のサブプロセスとして起動します。このためバイナリがマシン上で利用可能である必要があります。次のいずれかでインストールしてください。

```bash
# オプション A: npm（`copilot` コマンドを PATH にインストール）
npm install -g @github/copilot

# オプション B: gh copilot（バイナリをダウンロード・管理）
gh copilot   # 初回実行時に ~/.local/share/gh/copilot に CLI をダウンロード
```

実行可能か確認:

```bash
copilot --version
# または gh copilot でインストールした場合:
gh copilot -- --version
```

> **ヒント:** `copilot` が PATH 上にない場合は、SDK にバイナリの場所を伝えます:
>
> ```bash
> export COPILOT_CLI_PATH="/absolute/path/to/copilot"
> ```

チュートリアルスクリプトは独立した Copilot CLI サーバーを起動する**必要はありません** — SDK が stdio 経由でオンデマンドに起動します。既に TCP モードで動く Copilot CLI がある場合は、オプションとして `--cli-url host:port` フラグを使えます。

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

すべてのチュートリアルスクリプトは `--cli-url`（デフォルト: *stdio*）を受け付けます。スクリプト 06 は環境変数から BYOK 設定も読み込みます。

| 変数名 | 用途 | 使用するスクリプト |
|--------|------|------------------|
| `COPILOT_GITHUB_TOKEN` | Copilot CLI 用の GitHub PAT（`gh auth login` の代替） | Copilot CLI サブプロセス |
| `COPILOT_CLI_PATH` | `copilot` バイナリの絶対パス（PATH にない場合） | SDK のサブプロセスランチャー |
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
