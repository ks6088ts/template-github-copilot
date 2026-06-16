# チュートリアル 1: CLI チャットボット

**サブコマンド:** `tutorial chat-bot`
**ソース:** [`src/go/cmd/tutorial/chatbot.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/chatbot.go)

---

## 学べること

- `copilot.Client` を作成して起動する方法
- システムメッセージとパーミッションハンドラを備えたセッションを作成する方法
- 単一のプロンプトを送信してレスポンスを受信する方法
- `AssistantMessageDeltaData` によるストリーミングトークンの受信方法
- `Ctrl+C` でクリーンに終了するインタラクティブなチャットループの実行方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `make build` でビルド済みの Go CLI（[はじめに](../getting_started.md) を参照）

---

## ステップ 1 — クライアントの作成と起動

`copilot.Client` がメインのエントリポイントです。デフォルトでは `copilot` バイナリをサブプロセスとして起動し、stdio 経由で通信します。すでに TCP モードで稼働中の Copilot CLI がある場合のみ `Connection` を渡します。

```go
import (
    "context"

    copilot "github.com/github/copilot-sdk/go"
)

// デフォルト: SDK が CLI を stdio 経由で起動
client := copilot.NewClient(nil)

// オプション: 稼働中の CLI サーバーに接続（TCP モード）
// client := copilot.NewClient(&copilot.ClientOptions{
//     Connection: copilot.URIConnection{URL: "localhost:3000"},
// })

if err := client.Start(ctx); err != nil {
    return fmt.Errorf("failed to start Copilot client: %w", err)
}
defer func() { _ = client.Stop() }()
```

> **注意:** `client.Start(ctx)` は JSON-RPC 接続を確立します。セッションを作成する前に呼び出し、`client.Stop()`（ここでは `defer`）と対にしてサブプロセスを解放します。

---

## ステップ 2 — セッションの設定

`CreateSession` は、1 つの会話に関するすべてをまとめた `*copilot.SessionConfig` を受け取ります。

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true),
    SystemMessage:       &copilot.SystemMessageConfig{Content: "You are a helpful assistant."},
})
if err != nil {
    return fmt.Errorf("failed to create session: %w", err)
}
```

**主なフィールド:**

| フィールド | 説明 |
|------------|------|
| `OnPermissionRequest` | 各ツール実行前に呼び出される。`copilot.PermissionHandler.ApproveAll` はすべての要求を承認する |
| `Streaming` | `copilot.Bool(true)` でトークンを逐次受信。省略（または `false`）で完全なレスポンスを待機する |
| `SystemMessage` | `&copilot.SystemMessageConfig{Content: ...}` でアシスタントのペルソナを設定する |

---

## ステップ 3 — セッションイベントの処理

セッションイベントは `session.On(handler)` で配信されます。Go SDK は各イベントのペイロードを `event.Data` として渡し、型スイッチで判別します。ここでストリーミング出力とエラーを受け取ります。

```go
session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.AssistantMessageDeltaData:
        fmt.Print(data.DeltaContent)
    case *copilot.SessionErrorData:
        fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
    }
})
```

**主なイベントペイロード型:**

| 型 | 発火するタイミング |
|----|--------------------|
| `*copilot.AssistantMessageDeltaData` | ストリーミングトークンが届いたとき |
| `*copilot.AssistantMessageData` | アシスタントメッセージ全体が揃ったとき |
| `*copilot.SessionErrorData` | エラーが発生したとき |

---

## ステップ 4 — プロンプトの送信

```go
reply, err := session.SendPromptAndWait(ctx, prompt)
if err != nil {
    return err
}

var content string
if reply != nil {
    if data, ok := reply.Data.(*copilot.AssistantMessageData); ok {
        content = data.Content
    }
}
```

`SendPromptAndWait` はセッションがアイドルになるまでブロックします。その間、ストリーミングデルタは `session.On` で登録したハンドラに配信されます。返却される `reply` はメッセージ全体を `Data` フィールドに保持します。

---

## ステップ 5 — インタラクティブなチャットループ

複数ターンの会話では、セッションを生かしたまま `SendPromptAndWait` をループで呼び出します。`Ctrl+C`（コンテキストのキャンセル）でブロッキング読み取りを中断できるよう、標準入力は goroutine から読み取ります。

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
defer stop()

lines := make(chan string)
go func() {
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        lines <- scanner.Text()
    }
    close(lines)
}()

for {
    fmt.Print("You: ")
    select {
    case <-ctx.Done():
        return nil
    case line, ok := <-lines:
        if !ok {
            return nil // 標準入力の EOF
        }
        userInput := strings.TrimSpace(line)
        if userInput == "" {
            continue
        }
        fmt.Print("Copilot: ")
        if _, err := session.SendPromptAndWait(ctx, userInput); err != nil {
            return err
        }
        fmt.Println()
    }
}
```

---

## サブコマンドの実行

まず CLI をビルドし、`src/go` ディレクトリから `chat-bot` サブコマンドを実行します。

```bash
cd src/go
make build

# 単一プロンプト
./dist/template-github-copilot-go tutorial chat-bot --prompt "Explain goroutines in Go"

# インタラクティブループ（Ctrl+C または EOF で終了）
./dist/template-github-copilot-go tutorial chat-bot --loop

# カスタム CLI サーバー URL（任意 — CLI サーバーが TCP モードで稼働中の場合のみ）
./dist/template-github-copilot-go tutorial chat-bot --cli-url localhost:3000 --loop
```

### フラグ

| フラグ | 短縮形 | デフォルト | 説明 |
|--------|--------|------------|------|
| `--prompt` | `-p` | `Hello, Copilot! What can you do?` | 送信するプロンプト（単発モード） |
| `--cli-url` | `-c` | _(空)_ | 任意の Copilot CLI サーバー URL（例: `localhost:3000`） |
| `--loop` | `-l` | `false` | インタラクティブなチャットループモードで実行（Ctrl+C で終了） |

> グローバルな `--verbose`/`-v` フラグはログレベルを `DEBUG` に下げ、クライアントの接続モードとセッションのライフサイクルを表示します。

---

## 単独 CLI サーバー（TCP）への接続

デフォルトでは SDK は `copilot` CLI をサブプロセスとして起動し、stdio 経由で通信します。あるいは、CLI を長時間稼働する TCP サーバーとして実行し、`--cli-url` で接続することもできます。これは、認証済みの単一の CLI プロセスを複数の実行で共有したい場合に便利です。

### ステップ 1 — CLI サーバーの起動

別のターミナルで、CLI をサーバーモードで起動します。

```bash
export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
copilot --server --port 3000 --log-level all \
  --allow-all-tools --allow-all-paths --allow-all-urls
```

### ステップ 2 — サブコマンドから接続

別のターミナルで、サブコマンドを稼働中のサーバーに向けます。

```bash
cd src/go
./dist/template-github-copilot-go tutorial chat-bot \
  --cli-url localhost:3000 --prompt "Reply with exactly: connection ok"
```

成功するとアシスタントのレスポンス（例: `connection ok`）が返ります。

---

## 次のステップ

- [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) で Go API 全体を参照する
