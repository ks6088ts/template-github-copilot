# チュートリアル 2: Issue トリアージボット

**サブコマンド:** `tutorial issue-triage`
**ソース:** [`src/go/cmd/tutorial/issuetriage.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/issuetriage.go)

---

## 学べること

- 構造体タグで型付きのツール入出力を宣言する方法
- 型から JSON スキーマを生成する `copilot.DefineTool` でツールを作成する方法
- `SessionConfig.Tools` でセッションにツールを登録する方法
- 1 つのプロンプトから複数のツール呼び出しを駆動するツール呼び出しエージェントループの仕組み
- `ToolExecutionStartData` イベントでツール呼び出しを観測する方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `make build` でビルド済みの Go CLI（[はじめに](../getting_started.md) を参照）

---

## ステップ 1 — 型付きのツール入出力を宣言する

`copilot.DefineTool` は Go の関数をツールに変換します。引数と戻り値の型がツールの JSON スキーマになり、Copilot は呼び出し方を理解します。`jsonschema` 構造体タグはモデルに見せるフィールドの説明を提供し、`json` タグはワイヤフォーマットを制御します。

```go
// list_issues は引数を取りません。
type listIssuesInput struct{}

type issueItem struct {
    ID     int      `json:"id"`
    Title  string   `json:"title"`
    Body   string   `json:"body"`
    Labels []string `json:"labels"`
}

type listIssuesOutput struct {
    Issues []issueItem `json:"issues"`
}

type labelIssueInput struct {
    IssueID int      `json:"issue_id" jsonschema:"numeric ID of the issue to label"`
    Labels  []string `json:"labels" jsonschema:"labels to apply (e.g. bug, enhancement, documentation)"`
}

type labelIssueOutput struct {
    Success       bool     `json:"success"`
    IssueID       int      `json:"issue_id"`
    AppliedLabels []string `json:"applied_labels"`
}
```

---

## ステップ 2 — DefineTool でツールを作成する

`copilot.DefineTool[T, U](name, description, handler)` は入力型 `T` と出力型 `U` のジェネリックです。ハンドラはデコード済みの引数と `copilot.ToolInvocation` を受け取り、型付きの結果を返します。文字列以外の結果は自動的に JSON シリアライズされます。

```go
var (
    mu      sync.Mutex
    triaged []triageRecord
)

listIssues := copilot.DefineTool(
    "list_issues",
    "Return the list of open GitHub issues to triage.",
    func(_ listIssuesInput, _ copilot.ToolInvocation) (listIssuesOutput, error) {
        return listIssuesOutput{Issues: sampleIssues}, nil
    },
)

labelIssue := copilot.DefineTool(
    "label_issue",
    "Apply one or more labels to a GitHub issue.",
    func(in labelIssueInput, _ copilot.ToolInvocation) (labelIssueOutput, error) {
        mu.Lock()
        triaged = append(triaged, triageRecord{ID: in.IssueID, Labels: in.Labels})
        mu.Unlock()
        return labelIssueOutput{Success: true, IssueID: in.IssueID, AppliedLabels: in.Labels}, nil
    },
)
```

> **注意:** ツールハンドラは異なるゴルーチンから呼び出される可能性があるため、共有状態（ここでは `triaged` スライス）は `sync.Mutex` で保護してください。

---

## ステップ 3 — セッションにツールを登録する

ツールを `SessionConfig.Tools` に渡します。システムメッセージで Copilot に使い方を伝えます。この実行では最終的な要約だけが必要で逐次トークンは不要なため、`Streaming: copilot.Bool(false)` を使います。

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Tools:               []copilot.Tool{listIssues, labelIssue},
    Streaming:           copilot.Bool(false),
    SystemMessage: &copilot.SystemMessageConfig{
        Mode: "replace",
        Content: "You are an expert GitHub issue triage assistant. " +
            "Use list_issues to fetch open issues, classify each one as 'bug', " +
            "'enhancement', or 'documentation', then call label_issue to apply the " +
            "appropriate label. After triaging all issues, summarise your actions.",
    },
})
```

> **注意:** `Mode: "replace"` はシステムメッセージを完全に差し替えます。カスタムツールが登録されているため、各ツール実行の前に `OnPermissionRequest` が発火します。`ApproveAll` はすべての呼び出しを通します。

---

## ステップ 4 — イベントでツール呼び出しを観測する

イベントハンドラを登録してエージェントの動作を監視します。`ToolExecutionStartData` は Copilot がツールを呼び出すたびに発火します。

```go
session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.ToolExecutionStartData:
        fmt.Fprintf(os.Stderr, "[Tool] Calling: %s\n", data.ToolName)
    case *copilot.SessionErrorData:
        fmt.Fprintf(os.Stderr, "[Error] %s\n", data.Message)
    }
})
```

---

## ステップ 5 — トリアージのターンを実行して結果を集める

1 つのプロンプトがエージェントループを開始します。Copilot は `list_issues` を呼び、各項目を分類し、それぞれに `label_issue` を呼び、最後に要約を返します。`SendPromptAndWait` はセッションがアイドルになるまでブロックします。

```go
reply, err := session.SendPromptAndWait(ctx, "Please triage all open issues and apply the appropriate labels.")
if err != nil {
    return err
}

content := "(no response)"
if reply != nil {
    if data, ok := reply.Data.(*copilot.AssistantMessageData); ok {
        content = data.Content
    }
}

mu.Lock()
applied := triaged
mu.Unlock()

labelsJSON, _ := json.MarshalIndent(applied, "", "  ")
fmt.Println("=== Triage Summary ===")
fmt.Println(content)
fmt.Println("\n=== Applied Labels ===")
fmt.Println(string(labelsJSON))
```

---

## サブコマンドの実行

まず CLI をビルドし、`src/go` ディレクトリから `issue-triage` サブコマンドを実行します。

```bash
cd src/go
make build

# 組み込みのサンプル Issue をトリアージ
./dist/template-github-copilot-go tutorial issue-triage

# スタンドアロンの CLI サーバーに接続（任意 — TCP モードで稼働中の場合のみ）
./dist/template-github-copilot-go tutorial issue-triage --cli-url localhost:3000
```

### フラグ

| フラグ | 短縮形 | デフォルト | 説明 |
|--------|--------|------------|------|
| `--cli-url` | `-c` | _(空)_ | 任意の Copilot CLI サーバー URL（例: `localhost:3000`） |

> グローバルな `--verbose`/`-v` フラグはログレベルを `DEBUG` に下げ、クライアント接続モードとセッションのライフサイクルを表示します。

---

## 次のステップ

- チュートリアル 3 — [ストリーミングレビュー](03_streaming_review.md): レスポンスをトークンごとにストリーミングする
- チュートリアル 5 — [監査ログ](05_audit_hooks.md): カスタムパーミッションハンドラでツール呼び出しを拒否する
- [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) で Go API 全体を参照
