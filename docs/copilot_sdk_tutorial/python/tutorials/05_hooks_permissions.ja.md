# チュートリアル 5: セッションフックと Permission Handling による監査ログ

**スクリプト:** [`src/python/scripts/tutorials/05_audit_hooks.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/05_audit_hooks.py)

---

## 学べること

- `session.on()` を通じてすべてのセッションイベントをインターセプトする方法
- カスタム `on_permission_request` ハンドラの実装方法
- 特定のツール実行を承認または拒否する方法
- セッションがツールを登録したときにのみパーミッションハンドラが発火する理由
- イベントストリームから構造化された監査ログを構築する方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `github-copilot-sdk` がインストール済み

---

## セッションフック

`session.on(handler)` はセッションで起きるすべてを観察する主要な方法です。ターン開始からツール呼び出し、エラーまで、すべてのイベントがハンドラを通過します。

これにより `session.on` は以下に最適です:

- **監査ログ** — 誰が何をいつ呼び出したかを記録
- **モニタリング** — ツール使用状況、レイテンシ、エラーの追跡
- **進捗表示** — エージェントが何をしているかをリアルタイムで表示
- **テスト** — 特定のイベントが正しい順序で発生したことをアサート

---

## ステップ 1 — セッションイベントで監査ログを構築する

```python
import time
import json
from typing import Any
from copilot.generated.session_events import SessionEventType

audit_log: list[dict[str, Any]] = []
start_time = time.time()

def record(event_name: str, detail: str = "") -> None:
    audit_log.append({
        "ts": round(time.time() - start_time, 3),
        "event": event_name,
        "detail": detail,
    })

def on_event(event: Any) -> None:
    et = event.type
    if et == SessionEventType.ASSISTANT_TURN_START:
        record("TURN_START")
    elif et == SessionEventType.ASSISTANT_INTENT:
        record("INTENT", event.data.intent)
    elif et == SessionEventType.TOOL_EXECUTION_START:
        record("TOOL_START", event.data.tool_name)
    elif et == SessionEventType.TOOL_EXECUTION_COMPLETE:
        err = getattr(event.data, "error", None)
        record("TOOL_COMPLETE", f"error={err.message if err else None}")
    elif et == SessionEventType.ASSISTANT_TURN_END:
        record("TURN_END")
    elif et == SessionEventType.SESSION_IDLE:
        record("SESSION_IDLE")
    elif et == SessionEventType.SESSION_ERROR:
        record("SESSION_ERROR", event.data.message)

session.on(on_event)
```

---

## ステップ 2 — ツールとパーミッションハンドラを登録する

`on_permission_request` コールバックは**すべてのツール実行前**に呼び出されます — したがってセッションがツールを一つも登録していなければハンドラは一度も発火しません。このチュートリアルでは、監査ポリシーがブロックしたい破壊的なアクションをモデル化した `delete_record` ツールを登録します:

```python
from copilot.tools import define_tool
from pydantic import BaseModel


class DeleteRecordInput(BaseModel):
    record_id: int


class DeleteRecordOutput(BaseModel):
    success: bool
    record_id: int
    message: str


deleted_records: list[int] = []


@define_tool(
    name="delete_record",
    description="Permanently delete a customer record by its numeric ID.",
)
def delete_record(input: DeleteRecordInput) -> DeleteRecordOutput:
    deleted_records.append(input.record_id)
    return DeleteRecordOutput(
        success=True,
        record_id=input.record_id,
        message=f"Record {input.record_id} permanently deleted.",
    )
```

ハンドラは呼び出しを許可する場合は `PermissionDecisionApproveOnce()` を、ブロックする場合は `PermissionDecisionReject(feedback=...)` を返します。後で確認できるように決定を監査ログに記録します:

```python
from copilot.generated.rpc import (
    PermissionDecisionApproveOnce,
    PermissionDecisionReject,
)
from copilot.generated.session_events import PermissionRequest
from copilot.session import PermissionRequestResult

def permission_handler(
    request: PermissionRequest,
    context: dict,
) -> PermissionRequestResult:
    tool_name = getattr(request, "tool_name", "unknown")

    # 例: すべてのツール呼び出しを拒否（読み取り専用の監査に有用）
    if deny_tools:
        record("PERMISSION_DENIED", f"tool={tool_name}")
        print(f"[Permission] DENIED: {tool_name}")
        return PermissionDecisionReject(feedback="Tool execution denied by audit policy")

    record("PERMISSION_APPROVED", f"tool={tool_name}")
    print(f"[Permission] APPROVED: {tool_name}")
    return PermissionDecisionApproveOnce()
```

セッション作成時にツールとハンドラを登録します:

```python
session = await client.create_session(
    on_permission_request=permission_handler,
    tools=[delete_record],
    streaming=False,
    system_message=SystemMessageReplaceConfig(
        mode="replace",
        content="You are an operations assistant with access to a delete_record tool.",
    ),
)
```

---

## ステップ 3 — 実行して監査ログを確認する

```python
reply = await session.send_and_wait(prompt, timeout=300)
content = getattr(reply.data, "content", None) if reply else "(no response)"
print(content)

print("\n=== Audit Log ===")
print(json.dumps(audit_log, indent=2))
```

サンプルの監査ログ出力（デフォルト — ポリシーが `delete_record` 呼び出しを**承認**）:

```json
[
  {"ts": 1.584, "event": "SEND", "detail": "Delete the customer record with ID 42..."},
  {"ts": 4.085, "event": "TURN_START", "detail": ""},
  {"ts": 6.8, "event": "TOOL_START", "detail": "delete_record"},
  {"ts": 6.8, "event": "PERMISSION_APPROVED", "detail": "tool=delete_record"},
  {"ts": 6.82, "event": "TOOL_COMPLETE", "detail": "error=None"},
  {"ts": 6.82, "event": "TURN_END", "detail": ""},
  {"ts": 9.615, "event": "SESSION_IDLE", "detail": ""}
]
```

`--deny-tools` を指定するとハンドラは `PermissionDecisionReject(...)` を返します。`delete_record` の実装は一度も実行されず、監査ログには `PERMISSION_DENIED` が記録され、アシスタントはアクションがポリシーでブロックされたことを報告します。

---

## パーミッションハンドラのパターン

| パターン | ユースケース |
|---------|------------|
| すべて `PermissionDecisionApproveOnce()` | 開発 / 信頼された環境 |
| すべて `PermissionDecisionReject(...)` | 読み取り専用の監査モード — 副作用なし |
| ツール名で承認 | 安全なツールのみ許可、リスクのあるものは拒否 |
| ユーザーに確認 | 機密アクションへのインタラクティブな承認 |
| ログ後に承認 | すべてのツール呼び出しをブロックせずに記録 |

---

## スクリプトの実行

```bash
cd src/python

# delete_record ツールを承認（デフォルト） — レコードが削除される
uv run python scripts/tutorials/05_audit_hooks.py

# すべてのツール呼び出しを拒否 — delete_record 呼び出しがブロックされ、実行されない
uv run python scripts/tutorials/05_audit_hooks.py --deny-tools

# 独自のプロンプトを送信
uv run python scripts/tutorials/05_audit_hooks.py \
    --prompt "Delete the customer record with ID 7 using the delete_record tool."

# カスタム CLI サーバー（オプション）
uv run python scripts/tutorials/05_audit_hooks.py --cli-url localhost:3000
```

---

## まとめ

- `session.on(handler)` はすべてのセッションイベントをインターセプト — ログ、モニタリング、テストに使用
- `on_permission_request` はすべてのツール実行前に呼び出され、実行するかどうかを制御する
- ハンドラはセッションがツールを登録したときにのみ発火する — `tools=[]` の場合は一度も呼び出されない
- 両方のフックはリッチなイベントデータ（ツール名、インテント、エラー詳細など）を受け取る
- タイムスタンプ付きの監査ログを構築してセッション全体のエージェントの動作を追跡する
- `PermissionDecisionReject(...)` レスポンスはツールをブロックするが、セッションは継続させる

---

## 次のチュートリアル

[チュートリアル 6: Azure OpenAI を使った BYOK →](06_byok.md)
