# コンテナのローカル実行

---

## 概要

CopilotReportForge は、プラットフォームをローカルのコンテナで実行するための Docker Compose 設定を提供します。イメージソースに応じて 3 つの方法が利用可能です:

| 方法 | Compose ファイル | イメージソース |
|---|---|---|
| ローカルビルド | `compose.yaml` | ソースからビルド |
| Docker Hub | `compose.docker.yaml` | `docker.io` |
| GitHub Packages | `compose.docker.yaml` | `ghcr.io` |

---

## 前提条件

- Docker と Docker Compose がインストール済み
- Copilot GitHub Token（`COPILOT_GITHUB_TOKEN`）
- （GitHub Packages）`read:packages` スコープ付き GitHub Personal Access Token
- （Docker Hub）Docker Hub アカウント

> **注意:** Docker イメージは Copilot CLI バージョン `0.0.418`（compose ファイルと Dockerfile で固定）を使用します。更新するには、compose ファイルと Dockerfile の `COPILOT_CLI_VERSION` を変更してください。

---

## セットアップ

### 1. 環境ファイルの作成

必要な環境変数を含む `.env` ファイルを `src/python/` 配下に作成します。利用可能な変数の完全なリストについては `.env.template` を参照してください:

```bash
cp .env.template .env
# .env を設定に合わせて編集
```

最低限必要なのは:

```bash
COPILOT_GITHUB_TOKEN=your-copilot-token
```

### 2. ローカルビルドで実行

```bash
cd src/python
docker compose up --build
```

### 3. ビルド済みイメージで実行（Docker Hub）

```bash
cd src/python
docker compose -f compose.docker.yaml up
```

### 4. ビルド済みイメージで実行（GitHub Packages）

```bash
# GitHub Container Registry で認証
echo $GITHUB_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# プルして実行
cd src/python
CONTAINER_REGISTRY=ghcr.io docker compose -f compose.docker.yaml up
```

---

## サービス

| サービス | ポート | 説明 | プロファイル |
|---|---|---|---|
| `copilot` | `3000` | Copilot CLI サーバー | default |
| `api` | `8000` | チャットとレポート UI 付き Web アプリケーション | default |
| `monolith` | `3000`, `8000` | supervisord で Copilot CLI と API の両方を実行する単一コンテナ | `monolith` |

> **サービス依存関係:** `api` サービスはヘルスチェック条件（`service_healthy`）付きで `copilot` に依存します。`copilot` サービスはポート 3000 で TCP 接続テストを実行して準備完了を確認してから `api` が起動します。つまり、`api` サービスは Copilot CLI が完全に準備できるまで待機します。

> **モノリスアーキテクチャ:** `monolith` サービスは内部的に [supervisord](http://supervisord.org/) を使用して 2 つのプロセスを管理します: Copilot CLI サーバー（ポート 3000）と API サーバー（ポート 8000）。これは [Azure Container Apps デプロイ](https://github.com/ks6088ts/template-github-copilot/blob/main/infra/scenarios/azure_container_apps/README.md) で使用されるのと同じイメージです。

### モノリスサービスの実行

`monolith` サービスは Copilot CLI と API サーバーの両方を supervisord を使用して単一コンテナにバンドルします。Docker Compose プロファイルで有効化されます:

```bash
# ローカルビルド
cd src/python
docker compose --profile monolith up monolith --build

# ビルド済みイメージ（Docker Hub）
cd src/python
docker compose -f compose.docker.yaml --profile monolith up monolith
```

これは [Azure Container Apps デプロイ](https://github.com/ks6088ts/template-github-copilot/blob/main/infra/scenarios/azure_container_apps/README.md) で使用されるのと同じイメージです。

---

## 一般的な操作

```bash
# すべてのサービスを停止
docker compose down

# コード変更後に再ビルド
docker compose up --build

# バックグラウンドで起動（デタッチモード）
docker compose up --build -d

# ログを表示
docker compose logs -f

# 特定のサービスを実行
docker compose up api
```

同等の Make ターゲットも利用可能です:

| コマンド | 機能 |
|---|---|
| `make compose-build` | Docker Compose サービスをビルド |
| `make compose-up` | すべてのサービスを起動（フォアグラウンド） |
| `make compose-up-d` | すべてのサービスを起動（バックグラウンド） |
| `make compose-down` | サービスを停止 |
| `make compose-logs` | ログを表示 |
