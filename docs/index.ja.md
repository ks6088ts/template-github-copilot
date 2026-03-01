# template-github-copilot

template-github-copilot のドキュメントへようこそ。

**GitHub Copilot SDK**、**Azure AI Foundry**、**GitHub Actions** をベースに構築された複数のユースケースのショーケースリポジトリです。

## プロジェクト

- [CopilotReportForge](copilot_report_forge/index.md): アドホックな LLM 操作を、管理された再現可能かつ監査可能なレポート生成パイプラインに変換するオープンソースプラットフォーム。

## インフラストラクチャ（Terraform シナリオ）

| シナリオ | 説明 |
|---|---|
| Azure GitHub OIDC | GitHub Actions 用 OIDC 付き Azure サービスプリンシパルの作成 |
| GitHub Secrets | GitHub リポジトリ環境へのシークレット登録 |
| Azure Microsoft Foundry | Azure 上に Microsoft Foundry（AI Hub + AI Services）をデプロイ |
| Azure Container Apps | モノリスサービス（Copilot CLI + API）を Azure Container App としてデプロイ |

各シナリオの詳細については、[デプロイ](copilot_report_forge/operations/deployment.md) ガイドを参照してください。
