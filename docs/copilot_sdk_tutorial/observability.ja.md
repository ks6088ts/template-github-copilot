# OpenTelemetry によるオブザーバビリティ

Copilot SDK は、内部で動作する Copilot CLI から
[OpenTelemetry](https://opentelemetry.io/) のトレースを出力できます。本ページ
では、**Go** と **Python** のチュートリアルでトレースを有効化し、最小構成
（2 サービス）の Docker Compose スタックを使って Grafana でスパンを確認する
方法を説明します。

参考:
[OpenTelemetry instrumentation for Copilot SDK](https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry)

---

## 仕組み

```text
Copilot CLI / VS Code Copilot Chat ──OTLP/HTTP :4318──▶ otel-collector ──OTLP/gRPC :4317──▶ grafana-lgtm ──▶ Grafana UI :3000
```

テレメトリは **環境変数によるオプトイン** です。エンドポイントを設定しない限り
チュートリアルの挙動は従来どおり変わりません（VS Code の Copilot Chat は
`.vscode/settings.json` で別途設定します。
[VS Code の Copilot Chat メトリックを可視化する](#vs-code-の-copilot-chat-メトリックを可視化する)
を参照）。

| 変数 | 説明 |
|------|------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP エンドポイント（例: `http://localhost:4318`）。未設定の場合テレメトリは無効。 |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | スパンにプロンプト/応答の内容を含めるか（`true`/`false`、任意）。 |
| `OTEL_BSP_SCHEDULE_DELAY` | スパンのバッチフラッシュ間隔（ms）。低く設定する（例: `500`）。[トラブルシューティング](#トラブルシューティング-スパンが届かない) を参照。 |

`TelemetryConfig` を組み立てる共有ヘルパー:

- **Python** — [`src/python/scripts/tutorials/_telemetry.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/_telemetry.py)（`make_client()`）
- **Go** — [`src/go/cmd/tutorial/telemetry.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/telemetry.go)（`newClientOptions()`）

---

## 1. オブザーバビリティスタックを起動

Docker 関連のファイルはすべて [`docker/`](https://github.com/ks6088ts/template-github-copilot/tree/main/docker) 配下にまとめています。

```bash
# リポジトリのルートで実行
docker compose -f docker/compose.yaml up -d
```

2 つのサービスが起動します:

| サービス | イメージ | 公開ポート |
|----------|----------|------------|
| `otel-collector` | `otel/opentelemetry-collector-contrib` | `4317`（gRPC）, `4318`（HTTP） |
| `grafana-lgtm` | `grafana/otel-lgtm`（Loki + Grafana + Tempo + Prometheus） | `3000`（Grafana UI） |

---

## 2. チュートリアルをコレクターに向ける

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
# スパンを素早くフラッシュ（後述の「トラブルシューティング」参照）
export OTEL_BSP_SCHEDULE_DELAY=500
# 任意:
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

### Python

```bash
cd src/python
uv run python scripts/tutorials/01_chat_bot.py --prompt "Hello, Copilot!"
```

### Go

```bash
cd src/go
make build
./dist/template-github-copilot-go tutorial chat-bot --prompt "Hello, Copilot!"
```

---

## 3. トレースを確認

[http://localhost:3000](http://localhost:3000)（ログイン `admin` / `admin`）で
Grafana を開き、**Explore → Tempo** から直近のトレースを検索します。

コレクターのログからスパンの流れを確認することもできます:

```bash
docker compose -f docker/compose.yaml logs -f otel-collector
```

---

## 4. 後片付け

```bash
docker compose -f docker/compose.yaml down
```

---

## VS Code の Copilot Chat メトリックを可視化する

同じコレクターで、**VS Code 上の GitHub Copilot Chat** が出力する
OpenTelemetry の**トレース・メトリック・ログ**もそのまま受信できます。追加の
サービスや依存関係は不要で、現状の 2 コンテナ構成で充足します。

本リポジトリには、ローカルのコレクターに接続済みの
[`.vscode/settings.json`](https://github.com/ks6088ts/template-github-copilot/blob/main/.vscode/settings.json)
を同梱しています:

```json
{
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "http://localhost:4318",
  "github.copilot.chat.otel.captureContent": false
}
```

手順:

1. スタックを起動: `docker compose -f docker/compose.yaml up -d`
2. このフォルダーを VS Code で開く（上記のワークスペース設定が自動適用されます）。
   既に Copilot が動作中の場合はウィンドウを再読み込みします。
3. いつもどおり Copilot Chat / エージェントを利用すると、VS Code が OTLP を
   コレクターにエクスポートします。
4. Grafana（[http://localhost:3000](http://localhost:3000)、`admin`/`admin`）の
   **Explore** を開きます:
   - **Tempo** データソース → エージェントのトレース（`invoke_agent`、`chat`、
     `execute_tool`）。
   - **Prometheus** データソース → `github_copilot_agent_turn_count` や
     `github_copilot_mcp_server_connection_count_total` などのメトリック。

補足:

- シグナル名は
  [OTel GenAI Semantic Conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/)
  に準拠し、`gen_ai.*` および `github.copilot.*` 名前空間で出力されます。
- コレクターが**起動していない**場合、VS Code のエクスポートは静かに失敗
  （接続拒否）し、Copilot は通常どおり動作します。
- `captureContent` は既定で `false` です。プロンプト・応答・ツール引数の全文を
  記録するため、信頼できる環境でのみ有効化してください。
- **Azure** 構成（OTel Collector → Application Insights → Azure Managed Grafana）
  については
  [Grafana を使用して AI コーディング エージェントを監視する](https://learn.microsoft.com/ja-jp/azure/managed-grafana/grafana-opentelemetry-app-insights)
  を参照してください。

---

## トラブルシューティング: スパンが届かない

SDK が CLI を **stdio** で起動する場合（チュートリアルの既定動作）、単発の
プロンプトが終わると同時に SDK は CLI を `SIGKILL`（`client.Stop()` →
`process.Kill()`）で停止します。CLI はスパンをバッチでフラッシュし、その間隔
の **既定値は 5 秒** です。そのため短いプロンプトでは最初のフラッシュより前に
プロセスが終了し、**スパンが一切送信されません**。

標準の OpenTelemetry のバッチ用環境変数を設定し、CLI が停止される前にフラッシュ
させてください:

```bash
export OTEL_BSP_SCHEDULE_DELAY=500   # ミリ秒
```

または CLI を [サーバーモード](server_mode.md) で起動し、`--cli-url` で接続
します。常駐プロセスは通常の間隔でフラッシュします。直接 `copilot -p "..."`
を実行すると常に動作するのは、そのプロセスが正常終了時にフラッシュするためです。

---

## 応用: 分散トレースのコンテキスト伝播

CLI のスパンを収集するだけなら、上記の `TelemetryConfig` で十分です。アプリ
ケーション側で独自の OpenTelemetry スパンを作成し、それを CLI と **同一の**
分散トレースに連結したい場合は、
[公式ガイド](https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry)
の *Trace context propagation* を参照してください。Python ではこの用途に
`opentelemetry-api` パッケージ（`pip install copilot-sdk[telemetry]`）が必要
です。Go は既に `go.opentelemetry.io/otel` に依存しています。
