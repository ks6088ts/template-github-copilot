# はじめに（Go）

このガイドでは、**Go 固有** のセットアップ—CLI のビルドとチュートリアルサブコマンドの
実行—を説明します。Copilot CLI のインストールと GitHub 認証—すべての言語版で共通—に
ついては、まず共通の [はじめに](../getting_started.md) ガイドに従ってください。

---

## 前提条件

| 要件 | 最小バージョン | 用途 |
|------|----------------|------|
| [Go](https://go.dev/doc/install) | 1.26+ | ランタイムとビルドツールチェーン |
| [GNU Make](https://www.gnu.org/software/make/) | 最新 | ビルドターゲット |
| Node.js (`npm`) または GitHub CLI (`gh`) | 最新 | Copilot CLI のインストール |
| GitHub Copilot サブスクリプション | — | API アクセスに必須 |

Go ツールチェーンを確認します。

```bash
go version   # go1.26 以降
```

---

## CLI をビルドする

チュートリアルサブコマンドは Go CLI の一部です。プロジェクトの Makefile でビルドします。

```bash
cd src/go

# CLI を ./dist/ にビルド
make build

# 利用可能なチュートリアルサブコマンドを表示
./dist/template-github-copilot-go tutorial --help
```

これらのサブコマンドは別途起動した Copilot CLI サーバーを**必要としません** — SDK が stdio 経由でオンデマンドに起動します。すでに TCP モードで稼働中の Copilot CLI がある場合のみ `--cli-url host:port` を使用します（[CLI サーバーモード](../server_mode.md) を参照）。

---

## 最初のサブコマンドを実行する

```bash
cd src/go
./dist/template-github-copilot-go tutorial chat-bot --prompt "What is GitHub Copilot?"
```

期待される出力（ストリーミング）:

```text
GitHub Copilot is an AI-powered coding assistant developed by GitHub and OpenAI...
```

---

## グローバルフラグ

ルートコマンドはグローバルな `--verbose`/`-v` フラグ（すべてのサブコマンドが継承）を公開します。これはログレベルを `DEBUG` に下げ、Copilot クライアントの接続モードやセッションのライフサイクルといった診断ログを表示します。

```bash
./dist/template-github-copilot-go tutorial chat-bot --verbose --prompt "Hello!"
```

`tutorial` コマンドは、すべてのチュートリアルサブコマンドが継承する
OpenTelemetry 用の persistent flag も公開します。各フラグの既定値は対応する
環境変数から読み込まれ、エンドポイントを指定しない限りテレメトリは無効です。

| フラグ | 環境変数 | 用途 |
|--------|----------|------|
| `--otel-endpoint` | `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP エンドポイント（例: `http://localhost:4318`） |
| `--otel-capture-content` | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | スパンにプロンプトと応答の内容を含めるかを示す任意の `true`/`false` |
| `--otel-bsp-schedule-delay` | `OTEL_BSP_SCHEDULE_DELAY` | スパンのバッチフラッシュ間隔（ミリ秒、任意） |

例:

```bash
./dist/template-github-copilot-go tutorial chat-bot \
  --otel-endpoint http://localhost:4318 \
  --otel-bsp-schedule-delay 500 \
  --prompt "Hello!"
```

---

## プロジェクト構成

```text
src/go/cmd/tutorial/
├── README.md      # サブコマンド一覧（このドキュメントへのポインタ）
├── tutorial.go    # `tutorial` 親コマンドグループ
└── chatbot.go     # チュートリアル 1: CLI チャットボット（chat-bot サブコマンド）
```

---

## 環境変数

Go CLI は、共通の [はじめに](../getting_started.md) で説明している共通の Copilot 変数
（`COPILOT_GITHUB_TOKEN`、`COPILOT_CLI_PATH`、`COPILOT_CLI_URL`）を使用します。加えて、
OpenTelemetry は上記の標準 `OTEL_*` 変数、または同等の `tutorial` フラグで設定できます。

---

## 次のステップ

環境が整ったので、チュートリアルを進めましょう。

1. [CLI チャットボット](tutorials/01_chat_bot.md) — 最初の Copilot 搭載 Go プログラムを構築する
