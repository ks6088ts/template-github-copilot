# 参考文献

GitHub Copilot SDK に関する外部リンクとさらなる参考情報です。

---

## GitHub Copilot SDK

| リソース | リンク |
|---------|-------|
| GitHub リポジトリ（モノレポ） | [github/copilot-sdk](https://github.com/github/copilot-sdk) |
| 変更履歴 | リポジトリの GitHub リリースを参照 |

### 言語別の SDK パッケージ

| 言語 | パッケージ | リンク |
|------|-----------|-------|
| Python | `github-copilot-sdk` | [PyPI](https://pypi.org/project/github-copilot-sdk/) |
| Go | `github.com/github/copilot-sdk/go` | [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) |
| TypeScript | `@github/copilot-sdk` | [npm](https://www.npmjs.com/package/@github/copilot-sdk) |

---

## GitHub Copilot ドキュメント

| リソース | リンク |
|---------|-------|
| GitHub Copilot 概要 | [docs.github.com/copilot](https://docs.github.com/copilot) |
| CLI での GitHub Copilot | [docs.github.com/copilot/github-copilot-in-the-cli](https://docs.github.com/copilot/github-copilot-in-the-cli/about-github-copilot-in-the-cli) |
| Copilot API リファレンス | [docs.github.com/rest/copilot](https://docs.github.com/rest/copilot) |
| パーソナルアクセストークン | [docs.github.com/authentication](https://docs.github.com/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) |

---

## Azure OpenAI（BYOK 用）

| リソース | リンク |
|---------|-------|
| Azure OpenAI Service | [learn.microsoft.com/azure/ai-services/openai](https://learn.microsoft.com/azure/ai-services/openai/) |
| Azure Identity ライブラリ | [learn.microsoft.com/python/api/azure-identity](https://learn.microsoft.com/python/api/azure-identity/) |
| DefaultAzureCredential | [DefaultAzureCredential リファレンス](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential) |

---

## 言語別のチュートリアルライブラリ

**Python**

| ライブラリ | 用途 | リンク |
|-----------|------|-------|
| `github-copilot-sdk` | Python 向け Copilot SDK | [PyPI](https://pypi.org/project/github-copilot-sdk/) |
| `pydantic` | データバリデーションとツールスキーマ | [pydantic.dev](https://docs.pydantic.dev/) |
| `azure-identity` | Entra ID 認証（BYOK） | [PyPI](https://pypi.org/project/azure-identity/) |

**Go**

| ライブラリ | 用途 | リンク |
|-----------|------|-------|
| `github.com/github/copilot-sdk/go` | Go 向け Copilot SDK | [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) |
| `github.com/spf13/cobra` | CLI コマンドフレームワーク | [pkg.go.dev](https://pkg.go.dev/github.com/spf13/cobra) |
| `github.com/spf13/viper` | 設定・環境変数バインディング | [pkg.go.dev](https://pkg.go.dev/github.com/spf13/viper) |

---

## SDK のソースとリリース

| リソース | リンク |
|---------|-------|
| モノレポの Issue・Discussion | [github/copilot-sdk/issues](https://github.com/github/copilot-sdk/issues) |
| リリース | [github/copilot-sdk/releases](https://github.com/github/copilot-sdk/releases) |

---

## 変更ウォッチリスト { #change-watchlist }

各ワークショップの実施前に、以下の情報源を確認してください。SDK と、それが依存する Copilot CLI は頻繁に更新されるため、このチュートリアルは契約ではなくスナップショットとして扱ってください。ページ内に固定されたバージョンよりも、パッケージレジストリやリリースノートを優先してください。

| 監視対象 | 一次情報源 | 重要な理由 |
|---------|-----------|----------|
| SDK のリリースと API 変更 | [`github/copilot-sdk` のリリース](https://github.com/github/copilot-sdk/releases) | 各言語の SDK バージョンと、クライアント・セッション・イベント・ツール・スキル・フック・権限 API の変更を追跡します |
| Python パッケージのバージョン | [PyPI の `github-copilot-sdk`](https://pypi.org/project/github-copilot-sdk/) | Python チュートリアルがインストール・固定するバージョン |
| Go パッケージのバージョン | [pkg.go.dev の Go SDK](https://pkg.go.dev/github.com/github/copilot-sdk/go) | Go チュートリアルがビルド対象とするバージョン |
| SDK のハウツーとリファレンス | [GitHub Copilot SDK ハウツー](https://docs.github.com/en/copilot/how-tos/copilot-sdk) | サーバーモード・認証・BYOK に関するドキュメント化されたワークフロー |
| CLI サーバーの挙動 | [`github/copilot-cli` の changelog](https://github.com/github/copilot-cli/blob/main/changelog.md) | SDK は Copilot CLI サーバーを起動または接続するため、CLI のフラグや挙動の変更は [はじめに](../getting_started.md) と [CLI サーバーモード](../server_mode.md) に影響します |

## このチュートリアルに反映済みの最近の変更

| 日付 | 変更内容 | 出典 |
|------|---------|------|
| 2026-06-19 | Python・Go の SDK チュートリアルを、当時の最新 SDK パッケージと Copilot CLI サーバーモードに合わせて整備 | [github/copilot-sdk releases](https://github.com/github/copilot-sdk/releases) |
| 2026-06-18 | SDK v1.0.2: 作成・再開時のオプトインなセッションメモリ、ツール検索向けのツール `defer` オプション、`otlpProtocol` テレメトリトランスポート（`http/json` \| `http/protobuf`）、`ModelBilling.tokenPrices`、クライアント停止時の確定的なテレメトリフラッシュ | [Copilot SDK v1.0.2](https://github.com/github/copilot-sdk/releases/tag/v1.0.2) |

---

## このリポジトリ内の関連プロジェクト

| ドキュメント | 説明 |
|------------|------|
| [CopilotReportForge](../../copilot_report_forge/index.md) | この SDK を使ったエンタープライズ向けマルチペルソナレポート生成プラットフォーム |
| [はじめに](../getting_started.md) | チュートリアルの環境設定 |
