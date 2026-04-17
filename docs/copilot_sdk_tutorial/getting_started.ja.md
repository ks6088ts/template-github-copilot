# はじめに

このガイドでは、ローカル開発環境のセットアップとチュートリアルスクリプトの実行に必要なすべての手順を説明します。

---

## 前提条件

| 要件 | 最低バージョン | 用途 |
|------|---------------|------|
| Python | 3.11+ | ランタイム |
| pip / uv | 最新版 | パッケージ管理 |
| GitHub CLI（`gh`） | 最新版 | Copilot トークンとサーバー |
| GitHub Copilot サブスクリプション | — | API アクセスに必要 |

---

## インストール

### SDK のインストール

```bash
pip install github-copilot-sdk
```

`src/python` 内で **uv** を使用している場合:

```bash
# uv は pyproject.toml を読み込みます — SDK はすでに依存関係に記載されています
cd src/python
uv sync
```

スクリプト 02 に必要な `pydantic` も含めてインストールする場合:

```bash
pip install github-copilot-sdk pydantic
```

Entra ID 認証を使った BYOK の場合（スクリプト 06）:

```bash
pip install github-copilot-sdk azure-identity
```

---

## GitHub 認証

Copilot CLI サーバーには Copilot アクセス権を持つ GitHub トークンが必要です。

### オプション A: パーソナルアクセストークン（PAT）

1. **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)** に移動
2. `copilot` スコープ（または `read:user` + Copilot 有効な org）でトークンを生成
3. エクスポート:

```bash
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

### オプション B: GitHub CLI 認証

```bash
gh auth login
# Copilot CLI サーバーは gh CLI の認証情報を自動的に使用します
```

---

## Copilot CLI サーバーの起動

SDK は認証と API ルーティングを処理する **Copilot CLI サーバー**と通信します。専用のターミナルで起動してください:

```bash
gh copilot serve --port 3000
```

以下のような出力が表示されるはずです:

```
Copilot CLI server listening on :3000
```

チュートリアルスクリプトを実行している間、このターミナルを開いたままにしておいてください。

---

## 最初のスクリプトを実行する

2 番目のターミナルを開いて実行します:

```bash
python src/python/scripts/tutorials/01_chat_bot.py --prompt "What is GitHub Copilot?"
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

すべてのチュートリアルスクリプトは `--cli-url`（デフォルト: `localhost:3000`）を受け付けます。スクリプト 06 は環境変数から BYOK 設定も読み込みます。

| 変数名 | 用途 | 使用するスクリプト |
|--------|------|------------------|
| `COPILOT_GITHUB_TOKEN` | Copilot CLI サーバー用の GitHub PAT | `gh copilot serve` |
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
