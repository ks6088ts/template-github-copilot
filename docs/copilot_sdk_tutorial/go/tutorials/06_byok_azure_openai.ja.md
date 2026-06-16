# チュートリアル 6: BYOK Azure OpenAI

**サブコマンド:** `tutorial byok-azure-openai`
**ソース:** [`src/go/cmd/tutorial/byokazureopenai.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/byokazureopenai.go)

---

## 学べること

- `SessionConfig.Provider` でセッションを独自のモデルプロバイダー経由でルーティングする方法
- Azure OpenAI 向けに `copilot.ProviderConfig` を構成する方法
- API キーまたは Entra ID ベアラートークンで認証する方法
- `DefaultAzureCredential` で Entra ID トークンを取得する方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `make build` でビルド済みの Go CLI（[はじめに](../getting_started.md) を参照）
- Azure OpenAI のデプロイメント、および API キーまたは Entra ID 認証用の RBAC アクセス権

---

## ステップ 1 — Azure ProviderConfig を構築する

`copilot.ProviderConfig` は Bring Your Own Key（BYOK）プロバイダーを記述します。Azure では `Type: "azure"` とデプロイメントの `BaseURL` を設定します。API キーは `APIKey` で、Entra ID トークンは `BearerToken` で渡します。両方を設定した場合は `BearerToken` が優先されます。

```go
provider := &copilot.ProviderConfig{
    Type:    "azure",
    BaseURL: baseURL,
}
switch auth {
case "api-key":
    provider.APIKey = apiKey
case "entra":
    bearerToken, err := buildEntraBearerToken(ctx)
    if err != nil {
        return err
    }
    provider.BearerToken = bearerToken
}
```

---

## ステップ 2 — Entra ID ベアラートークンを取得する

キーレス認証では、`DefaultAzureCredential` が環境変数、マネージド ID、Azure CLI などから資格情報を解決します。Cognitive Services のスコープに対してトークンを要求します。

```go
import (
    "github.com/Azure/azure-sdk-for-go/sdk/azcore/policy"
    "github.com/Azure/azure-sdk-for-go/sdk/azidentity"
)

func buildEntraBearerToken(ctx context.Context) (string, error) {
    credential, err := azidentity.NewDefaultAzureCredential(nil)
    if err != nil {
        return "", fmt.Errorf("failed to create Azure credential: %w", err)
    }
    token, err := credential.GetToken(ctx, policy.TokenRequestOptions{
        Scopes: []string{"https://cognitiveservices.azure.com/.default"},
    })
    if err != nil {
        return "", fmt.Errorf("failed to acquire Entra ID token: %w", err)
    }
    return token.Token, nil
}
```

> **注意:** Entra ID 認証では、`az login` でサインイン（またはマネージド ID を構成）し、Azure OpenAI リソースに対してプリンシパルに **Cognitive Services OpenAI User** ロールを付与します。

---

## ステップ 3 — プロバイダーをセッションに割り当てる

プロバイダーとモデル（デプロイメント）名を `CreateSession` に渡します。ここではシステムメッセージに append モード（デフォルト）を使うため、SDK の基盤が保持され、その上に指示が追加されます。

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true),
    Model:               model,
    Provider:            provider,
    SystemMessage:       &copilot.SystemMessageConfig{Content: "You are a helpful assistant powered by Azure OpenAI."},
})
```

> **注意:** カスタムプロバイダーを構成すると、GitHub 側のセッションテレメトリは自動的に無効化されます。リクエストは直接 Azure OpenAI デプロイメントへ送られます。

---

## ステップ 4 — レスポンスをストリーミングする

ストリーミングを有効にして、デルタトークンを届いた順に出力します。

```go
fmt.Printf("\nYou: %s\nCopilot: ", prompt)

session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.AssistantMessageDeltaData:
        fmt.Print(data.DeltaContent)
    case *copilot.SessionErrorData:
        fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
    }
})

if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
    return err
}
```

---

## サブコマンドの実行

Azure OpenAI の情報を環境変数で設定（または対応するフラグで渡）し、`src/go` ディレクトリから実行します。

```bash
cd src/go
make build

# API キー認証（デフォルト）
export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deployment>"
export BYOK_API_KEY="<your-api-key>"
export BYOK_MODEL="gpt-4o"
./dist/template-github-copilot-go tutorial byok-azure-openai

# Entra ID 認証（キーレス）
az login
export BYOK_BASE_URL="https://<resource>.openai.azure.com/openai/deployments/<deployment>"
export BYOK_MODEL="gpt-4o"
./dist/template-github-copilot-go tutorial byok-azure-openai --auth entra
```

### フラグ

| フラグ | 短縮形 | デフォルト | 説明 |
|--------|--------|------------|------|
| `--prompt` | `-p` | `Briefly explain what BYOK means …` | 送信するプロンプト |
| `--auth` | | `api-key` | 認証方式: `api-key` または `entra` |
| `--base-url` | | `$BYOK_BASE_URL` | Azure OpenAI デプロイメントのベース URL |
| `--api-key` | | `$BYOK_API_KEY` | Azure OpenAI API キー（api-key 認証） |
| `--model` | | `$BYOK_MODEL` または `gpt-4o` | モデル/デプロイメント名 |
| `--cli-url` | `-c` | _(空)_ | 任意の Copilot CLI サーバー URL（例: `localhost:3000`） |

### 環境変数

| 変数 | 説明 |
|------|------|
| `BYOK_BASE_URL` | Azure OpenAI デプロイメントのベース URL（必須） |
| `BYOK_API_KEY` | Azure OpenAI API キー（`api-key` 認証で必須） |
| `BYOK_MODEL` | モデル/デプロイメント名（デフォルトは `gpt-4o`） |

> グローバルな `--verbose`/`-v` フラグはログレベルを `DEBUG` に下げ、クライアント接続モードとセッションのライフサイクルを表示します。

---

## 次のステップ

- チュートリアル 1 — [CLI チャットボット](01_chat_bot.md): GitHub ホストモデルでの同じストリーミングフロー
- [アーキテクチャ](../../architecture.md): SDK、CLI、プロバイダーがどのように連携するか
- [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) で Go API 全体を参照
