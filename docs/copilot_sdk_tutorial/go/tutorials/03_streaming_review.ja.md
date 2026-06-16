# チュートリアル 3: ストリーミングレビュー

**サブコマンド:** `tutorial streaming-review`
**ソース:** [`src/go/cmd/tutorial/streamingreview.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/streamingreview.go)

---

## 学べること

- `Streaming: copilot.Bool(true)` でストリーミングを有効化する方法
- `AssistantMessageDeltaData` でストリーミングトークンを受信する方法
- レスポンスを生成されるそばから逐次出力する方法
- ファイルまたは組み込みサンプルから読み込んだ統合 diff をモデルに渡す方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `make build` でビルド済みの Go CLI（[はじめに](../getting_started.md) を参照）

---

## ステップ 1 — セッションでストリーミングを有効にする

ストリーミングはセッションレベルの設定です。`Streaming: copilot.Bool(true)` を指定すると、ランタイムはレスポンスをまとめて返す代わりに、生成しながら `assistant.message_delta` イベントを発行します。

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true), // ← ストリーミングを有効化
    SystemMessage: &copilot.SystemMessageConfig{
        Mode: "replace",
        Content: "You are a senior software engineer conducting a thorough code review. " +
            "For each change in the diff: identify bugs, security issues, and style problems. " +
            "Be concise but precise. Use Markdown formatting.",
    },
})
```

---

## ステップ 2 — デルタトークンを届いた順に出力する

各 `AssistantMessageDeltaData` イベントは `DeltaContent` の断片を保持します。出力が連続したテキストとして読めるよう、末尾の改行なしで表示します。

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

> **注意:** ストリーミングを有効にしても、ターンの終わりにはメッセージ全体が `AssistantMessageData` として届きます。ライブ出力にはデルタを、最終テキストを 1 つにまとめて扱いたい場合はメッセージ全体を使います。

---

## ステップ 3 — diff を送信して完了を待つ

diff はフェンス付きコードブロックに入れてプロンプトに埋め込みます。`SendPromptAndWait` はセッションがアイドルになるまでブロックし、その頃にはすべてのデルタがハンドラによって出力済みです。

```go
prompt := fmt.Sprintf("Please review the following diff and provide feedback:\n\n```diff\n%s\n```", diffText)
if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
    return err
}
fmt.Println("\n\n=== Review Complete ===")
```

このサブコマンドはデフォルトで組み込みのサンプル diff をレビューします。`--diff <path>` を渡すと独自の統合 diff をレビューでき、ファイルはセッション開始前に `os.ReadFile` で読み込まれます。

---

## サブコマンドの実行

まず CLI をビルドし、`src/go` ディレクトリから `streaming-review` サブコマンドを実行します。

```bash
cd src/go
make build

# 組み込みのサンプル diff をレビュー
./dist/template-github-copilot-go tutorial streaming-review

# 独自の統合 diff をレビュー
git diff > /tmp/changes.diff
./dist/template-github-copilot-go tutorial streaming-review --diff /tmp/changes.diff
```

### フラグ

| フラグ | 短縮形 | デフォルト | 説明 |
|--------|--------|------------|------|
| `--diff` | `-d` | _(空)_ | 統合 diff ファイルのパス（未指定なら組み込みサンプルを使用） |
| `--cli-url` | `-c` | _(空)_ | 任意の Copilot CLI サーバー URL（例: `localhost:3000`） |

> グローバルな `--verbose`/`-v` フラグはログレベルを `DEBUG` に下げ、クライアント接続モードとセッションのライフサイクルを表示します。

---

## 次のステップ

- チュートリアル 4 — [スキルによるドキュメント生成](04_skills_docgen.md): `SKILL.md` ファイルから再利用可能な指示を読み込む
- チュートリアル 1 — [CLI チャットボット](01_chat_bot.md): インタラクティブループでのストリーミングの基礎
- [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) で Go API 全体を参照
