# チュートリアル 5: 監査ログ

**サブコマンド:** `tutorial audit-hooks`
**ソース:** [`src/go/cmd/tutorial/audithooks.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/audithooks.go)

---

## 学べること

- ツール呼び出しを承認または拒否するカスタムパーミッションハンドラの書き方
- `PermissionRequest` インターフェース値からツール名を読み取る方法
- `rpc.PermissionDecisionApproveOnce` または `rpc.PermissionDecisionReject` を返す方法
- すべてのセッションイベントをタイムスタンプ付きの監査ログに記録する方法
- 拒否されたツール呼び出しがツール実装に到達しない仕組み

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `make build` でビルド済みの Go CLI（[はじめに](../getting_started.md) を参照）

---

## ステップ 1 — 破壊的な操作をツールとしてモデル化する

`delete_record` は、監査ポリシーがブロックしたくなるような不可逆な操作を表します。実際に削除された ID を記録するため、パーミッションハンドラが呼び出しを通したかどうかを観測できます。

```go
type deleteRecordInput struct {
    RecordID int `json:"record_id" jsonschema:"numeric ID of the customer record to delete"`
}

type deleteRecordOutput struct {
    Success  bool   `json:"success"`
    RecordID int    `json:"record_id"`
    Message  string `json:"message"`
}

deleteRecord := copilot.DefineTool(
    "delete_record",
    "Permanently delete a customer record by its numeric ID.",
    func(in deleteRecordInput, _ copilot.ToolInvocation) (deleteRecordOutput, error) {
        mu.Lock()
        deleted = append(deleted, in.RecordID)
        mu.Unlock()
        return deleteRecordOutput{
            Success:  true,
            RecordID: in.RecordID,
            Message:  fmt.Sprintf("Record %d permanently deleted.", in.RecordID),
        }, nil
    },
)
```

---

## ステップ 2 — カスタムパーミッションハンドラを書く

パーミッションハンドラはリクエストを受け取り `rpc.PermissionDecision` を返します。`PermissionRequest` はインターフェースなので、`*copilot.PermissionRequestCustomTool` に型スイッチしてツール名を読み取ります。`*rpc.PermissionDecisionReject` を返すと呼び出しがブロックされ、ツール実装は決して実行されません。

```go
import "github.com/github/copilot-sdk/go/rpc"

permissionHandler := func(request copilot.PermissionRequest, _ copilot.PermissionInvocation) (rpc.PermissionDecision, error) {
    toolName := "unknown"
    if ct, ok := request.(*copilot.PermissionRequestCustomTool); ok {
        toolName = ct.ToolName
    }
    if denyTools {
        record("PERMISSION_DENIED", "tool="+toolName)
        feedback := "Tool execution denied by audit policy"
        return &rpc.PermissionDecisionReject{Feedback: &feedback}, nil
    }
    record("PERMISSION_APPROVED", "tool="+toolName)
    return &rpc.PermissionDecisionApproveOnce{}, nil
}
```

> **注意:** このハンドラはセッションがカスタムツールを登録している場合にのみ発火します。ツールがなければパーミッションリクエストも発生しません。

---

## ステップ 3 — すべてのセッションイベントを記録する

`record` はミューテックスで保護されたタイムスタンプ付きエントリを追加します。イベントハンドラが各イベントのペイロードを監査エントリにマッピングし、エージェントのターンの時系列の証跡を構築します。

```go
record := func(event, detail string) {
    mu.Lock()
    auditLog = append(auditLog, auditEntry{
        TS:     math.Round(time.Since(start).Seconds()*1000) / 1000,
        Event:  event,
        Detail: detail,
    })
    mu.Unlock()
}

session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.AssistantTurnStartData:
        record("TURN_START", "")
    case *copilot.AssistantIntentData:
        record("INTENT", data.Intent)
    case *copilot.ToolExecutionStartData:
        record("TOOL_START", data.ToolName)
    case *copilot.ToolExecutionCompleteData:
        detail := "error=<nil>"
        if data.Error != nil {
            detail = "error=" + data.Error.Message
        }
        record("TOOL_COMPLETE", detail)
    case *copilot.AssistantTurnEndData:
        record("TURN_END", "")
    case *copilot.SessionIdleData:
        record("SESSION_IDLE", "")
    case *copilot.SessionErrorData:
        record("SESSION_ERROR", data.Message)
    }
})
```

---

## ステップ 4 — ターンを実行して監査ログを出力する

ターン完了後、レスポンス、実際に削除されたレコード、監査ログ全体を JSON で出力します。

```go
reply, err := session.SendPromptAndWait(ctx, prompt)
// ... reply.Data から content を取り出す ...

logJSON, _ := json.MarshalIndent(auditLog, "", "  ")
fmt.Println("=== Deleted Records ===")
if len(deleted) == 0 {
    fmt.Println("(none — tool was not executed)")
} else {
    fmt.Println(deleted)
}
fmt.Println("\n=== Audit Log ===")
fmt.Println(string(logJSON))
```

`--deny-tools` を渡すと、削除レコードのリストは空のままになります。パーミッションハンドラが `delete_record` の実行前に呼び出しを拒否し、監査ログには `PERMISSION_DENIED` エントリが記録されます。

---

## サブコマンドの実行

まず CLI をビルドし、`src/go` ディレクトリから `audit-hooks` サブコマンドを実行します。

```bash
cd src/go
make build

# デフォルト: 監査ポリシーが delete_record の呼び出しを承認
./dist/template-github-copilot-go tutorial audit-hooks

# --deny-tools: 監査ポリシーが呼び出しを拒否（ツールは実行されない）
./dist/template-github-copilot-go tutorial audit-hooks --deny-tools
```

### フラグ

| フラグ | 短縮形 | デフォルト | 説明 |
|--------|--------|------------|------|
| `--prompt` | `-p` | `Delete the customer record with ID 42 …` | Copilot に送るプロンプト |
| `--cli-url` | `-c` | _(空)_ | 任意の Copilot CLI サーバー URL（例: `localhost:3000`） |
| `--deny-tools` | | `false` | すべてのツール実行を拒否するパーミッションハンドラを使用 |

> グローバルな `--verbose`/`-v` フラグはログレベルを `DEBUG` に下げ、クライアント接続モードとセッションのライフサイクルを表示します。

---

## 次のステップ

- チュートリアル 6 — [BYOK Azure OpenAI](06_byok_azure_openai.md): セッションを独自のモデルプロバイダー経由でルーティングする
- チュートリアル 2 — [Issue トリアージボット](02_issue_triage.md): パーミッションポリシーなしのツール呼び出しの基礎
- [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) で Go API 全体を参照
