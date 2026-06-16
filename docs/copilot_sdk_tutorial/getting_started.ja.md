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
