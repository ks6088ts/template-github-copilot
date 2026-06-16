# はじめに

このガイドでは、すべての SDK 版に共通する**共通セットアップ**（Copilot CLI のインストールと GitHub 認証）を扱います。これらの手順は言語に依存しません。

> このページを完了したら、SDK のインストールと実行手順については各言語版に進んでください。
>
> - **Python** → [Python はじめに](python/getting_started.md)
> - **Go** → [Go はじめに](go/getting_started.md)

---

## 前提条件

| 要件 | 最低バージョン | 用途 |
|------|---------------|------|
| Node.js（`npm`） または GitHub CLI（`gh`） | 最新版 | Copilot CLI のインストール |
| GitHub Copilot サブスクリプション | — | API アクセスに必要 |

> 言語固有の要件（Python + uv、または Go + Make）は各版の「はじめに」に記載しています。

---

## Copilot CLI のインストール

どの SDK 版も **`copilot` CLI** を stdio 経由のサブプロセスとして起動するため、バイナリがマシン上で利用可能である必要があります。次のいずれかでインストールしてください。

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

### Copilot CLI の更新

CLI は npm パッケージ `@github/copilot` として配布されています。最新の SDK 互換機能や修正を取り込むため、常に最新の状態に保ちましょう。

```bash
# 最新バージョンに更新
npm install -g @github/copilot@latest

# 特定のバージョンに固定（@latest を @<version> に置き換える）
npm install -g @github/copilot@0.0.339
```

便利な確認コマンド:

```bash
copilot --version                          # インストール済みのバージョンを表示
npm view @github/copilot versions --json   # 利用可能なバージョン一覧を表示
```

> **ヒント:** CLI の実行中は `/update` スラッシュコマンドでも更新を確認・適用できます。

---

## GitHub で認証する

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

`COPILOT_GITHUB_TOKEN`、`GH_TOKEN`、`GITHUB_TOKEN` はこの優先順位で参照されます。

### オプション C: Fine-grained PAT（CI 向け推奨）

**Copilot Requests** 権限を付与した **fine-grained パーソナルアクセストークン**は、GitHub Actions など非対話環境で認証する際の推奨方法です。

1. [Fine-grained personal access tokens](https://github.com/settings/personal-access-tokens/new) を開く。
2. **Resource owner** — **個人アカウント**を選択。**Organization は選ばない**こと: **Copilot Requests** 権限はユーザー所有トークンでのみ利用可能です。
3. **Repository access** — タスクに応じて *Public repositories* / *All repositories* / *Only select repositories* を選択。
4. **Permissions → Account → Add permissions → Copilot Requests**（Read-only — この権限はアクセスレベルが 1 つだけです）。
5. **Generate token** でトークンを生成し、エクスポート:

```bash
export COPILOT_GITHUB_TOKEN="github_pat_xxxxxxxxxxxxxxxxxxxx"
```

> **補足:** CLI を*実行する*だけなら **Copilot Requests** だけで十分です。組み込みの GitHub MCP サーバー経由で Copilot に GitHub.com 上の操作をさせたい場合のみ **Repository** 権限を追加します（後述の「GitHub Actions（CI）で実行する」を参照）。

---

## GitHub Actions（CI）で実行する

ワークフロー内で Copilot CLI を非対話的に実行できます。このリポジトリにはすぐ使えるワークフロー [`.github/workflows/github-copilot-cli.yaml`](https://github.com/ks6088ts/template-github-copilot/blob/main/.github/workflows/github-copilot-cli.yaml) が含まれています。

### 1. トークンを作成する

上記の「オプション C: Fine-grained PAT（CI 向け推奨）」に従います。

> **なぜ `GITHUB_TOKEN` ではダメか?** Actions が自動提供する `secrets.GITHUB_TOKEN` では Copilot CLI を認証**できません**。**Copilot Requests** は*ユーザー所有*の fine-grained PAT でのみ付与できるためです。自分で PAT を作成し、Secret として保存する必要があります。

### 2. 権限を選ぶ

| 目的 | 付与する権限 | レベル |
|------|------------|--------|
| **Copilot CLI の実行**（必須） | Account → **Copilot Requests** | Read-only |
| ファイル読み書き・ブランチ作成・push | Repository → Contents | Read and write |
| Pull request の作成・更新 | Repository → Pull requests | Read and write |
| Issue の作成・更新 | Repository → Issues | Read and write |
| ワークフローファイルの編集 | Repository → Workflows | Read and write |
| （Repository 権限を付けると自動追加） | Repository → Metadata | Read |

> ランナー上にチェックアウトしたワークスペースを編集するプロンプトを実行するだけなら、**Copilot Requests だけで十分**です（Repository 権限は不要）。

### 3. トークンを Secret に保存する

リポジトリ（または Organization）の設定で、トークンを `COPILOT_GITHUB_TOKEN` という名前の Secret として追加します。

### 4. ワークフローから参照する

```yaml
- name: Install GitHub Copilot CLI
  run: |
    curl -fsSL https://gh.io/copilot-install | VERSION="1.0.63" bash
    echo "$HOME/.local/bin" >> "$GITHUB_PATH"

- name: Run GitHub Copilot CLI
  env:
    COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
  run: |
    copilot \
      --prompt "今週のコミットを要約して" \
      --allow-all-tools --allow-all-paths --allow-all-urls \
      --model gpt-5-mini
```

> **セキュリティ:** `--allow-all-tools`、`--allow-all-paths`、`--allow-all-urls` は、Copilot がランナー上で任意のシェルコマンドを承認なしに実行できるようにします。信頼できる CI に限定し、PAT には**必要最小限の権限**だけを与え、対象を **Only select repositories** に絞り、**短い有効期限**を設定してください。

---

## なぜ `GITHUB_TOKEN` や `gh auth login` では動作しないのか

「静的な PAT を使わず、組み込みの `GITHUB_TOKEN`（やそれを使った `gh auth login`）で認証できないか?」というのはよくある疑問です。Copilot CLI/SDK では**これは動作しません**。しかもこれは設定ミスではなく、仕組み上の制約です。

- **`GITHUB_TOKEN` は GitHub App のインストールトークンです。** リポジトリ操作（contents・issues・pull requests）にスコープされており、**ユーザーアカウントに紐づきません**。そのため **Copilot Requests** が表す Copilot のエンタイトルメントを持つことができません。
- **`GITHUB_TOKEN` を使った `gh auth login` でも解決しません。** これは GitHub REST/GraphQL **API** の認証であって、Copilot サブスクリプションの認証ではありません。トークンの背後に課金対象となるユーザー ID が存在しないためです。
- **トークンは読み込まれた上で拒否されます。** Copilot CLI は `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` の順で認証情報を解決します。`GITHUB_TOKEN` を渡すと CLI は*読み込み*ますが、バックエンドが「Copilot へのアクセス権がない」としてリクエストを拒否します。

### 「静的なトークンを使いたくない」場合

気持ちは分かりますが、Copilot CLI/SDK では**ユーザー所有の fine-grained PAT が現時点で唯一サポートされる CI 認証情報**です。静的トークンを完全に排除することはできないため、代わりに影響範囲を最小化します。

- `Copilot Requests` **のみ**を付与する（Repository 権限の追加は最小限に）。
- トークンの対象を **Only select repositories** に絞る。
- **短い有効期限**を設定し、定期的にローテーションする。

> **単に LLM 推論をしたいだけなら?** `copilot` エージェントを動かすのではなく、モデルを呼び出したいだけであれば、[GitHub Models](https://docs.github.com/github-models) はジョブに `permissions: models: read` を追加することで組み込みの `GITHUB_TOKEN` から呼び出せます（静的 PAT 不要）。ただしこれは本チュートリアルが使う Copilot CLI/SDK（`copilot` バイナリを起動する方式）とは**別の API** であり、このリポジトリの構成にそのまま組み込めるものではありません。

---

## 共通の環境変数

これらの変数はすべての版に適用されます。版またはチュートリアル固有の変数（例: BYOK 設定）は各版の「はじめに」に記載しています。

| 変数名 | 用途 |
|--------|------|
| `COPILOT_GITHUB_TOKEN` | Copilot CLI 用の GitHub PAT（`gh auth login` の代替） |
| `COPILOT_CLI_PATH` | `copilot` バイナリの絶対パス（PATH にない場合） |
| `COPILOT_CLI_URL` | TCP モードで起動中の Copilot CLI サーバーのアドレス（例: `127.0.0.1:3000`） |

---

## サーバーを起動する必要はありますか？

いいえ。デフォルトでは SDK が `copilot` CLI を **stdio** 経由で自動起動するため、チュートリアルでは**手動で何かを起動する必要はありません**。

CLI を長時間稼働する **TCP サーバー** として一度だけ起動し、複数のクライアントから接続したい場合は [CLI サーバーモード](server_mode.md) を参照してください。各版は `--cli-url host:port` フラグで接続します。

---

## 次のステップ

共通セットアップは完了です。お好みの言語版に進んでください。

| 版 | はじめに | チュートリアル |
|----|----------|----------------|
| Python | [Python はじめに](python/getting_started.md) | [Python チュートリアル](python/index.md) |
| Go | [Go はじめに](go/getting_started.md) | [Go チュートリアル](go/index.md) |

各要素がどのように組み合わさるかは [アーキテクチャ](architecture.md) を参照してください。
