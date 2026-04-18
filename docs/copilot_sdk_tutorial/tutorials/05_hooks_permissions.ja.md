# チュートリアル 5: セッションフックと Permission Handling による監査ログ

**スクリプト:** [`src/python/scripts/tutorials/05_audit_hooks.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/05_audit_hooks.py)

---

## 学べること

- `session.on()` を通じてすべてのセッションイベントをインターセプトする方法
- カスタム `on_permission_request` ハンドラの実装方法
- 特定のツール実行を承認または拒否する方法
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

## ステップ 2 — パーミッションハンドラを実装する

`on_permission_request` コールバックは**すべての**ツール実行前に呼び出されます。ポリシーに基づいて `approved` または `denied` を返します:

```python
from copilot.types import PermissionRequest, PermissionRequestResult

def permission_handler(
    request: PermissionRequest,
    context: dict,
) -> PermissionRequestResult:
    tool_name = getattr(request, "tool_name", "unknown")

    # 例: すべてのツール呼び出しを拒否（読み取り専用の監査に有用）
    if should_deny(tool_name):
        print(f"[Permission] DENIED: {tool_name}")
        return PermissionRequestResult(kind="denied-interactively-by-user", rules=[])

    print(f"[Permission] APPROVED: {tool_name}")
    return PermissionRequestResult(kind="approved", rules=[])
```

セッション設定に登録します:

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=permission_handler,
        ...
    )
)
```

---

## ステップ 3 — 実行して監査ログを確認する

```python
reply = await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
print(reply.data.content)

print("\n=== Audit Log ===")
print(json.dumps(audit_log, indent=2))
```

サンプルの監査ログ出力:

```json
[
  {"ts": 0.001, "event": "SEND", "detail": "What are 3 best practices..."},
  {"ts": 0.012, "event": "TURN_START", "detail": ""},
  {"ts": 0.015, "event": "INTENT", "detail": "answer_question"},
  {"ts": 2.341, "event": "TURN_END", "detail": ""},
  {"ts": 2.342, "event": "SESSION_IDLE", "detail": ""}
]
```

---

## パーミッションハンドラのパターン

| パターン | ユースケース |
|---------|------------|
| すべて `approved` | 開発 / 信頼された環境 |
| すべて `denied` | 読み取り専用の監査モード — 副作用なし |
| ツール名で承認 | 安全なツールのみ許可、リスクのあるものは拒否 |
| ユーザーに確認 | 機密アクションへのインタラクティブな承認 |
| ログ後に承認 | すべてのツール呼び出しをブロックせずに記録 |

---

## スクリプトの実行

```bash
cd src/python

# すべてのツールを承認（デフォルト）
uv run python scripts/tutorials/05_audit_hooks.py \
    --prompt "What are best practices for Python error handling?"

# すべてのツール呼び出しを拒否
uv run python scripts/tutorials/05_audit_hooks.py --deny-tools

# カスタム CLI サーバー（オプション）
uv run python scripts/tutorials/05_audit_hooks.py --cli-url localhost:3000
```

---

## まとめ

- `session.on(handler)` はすべてのセッションイベントをインターセプト — ログ、モニタリング、テストに使用
- `on_permission_request` はすべてのツール実行前に呼び出され、実行するかどうかを制御する
- 両方のフックはリッチなイベントデータ（ツール名、インテント、エラー詳細など）を受け取る
- タイムスタンプ付きの監査ログを構築してセッション全体のエージェントの動作を追跡する
- パーミッションハンドラからの `denied` レスポンスはセッションの継続を妨げない

---

## 次のチュートリアル

[チュートリアル 6: Azure OpenAI を使った BYOK →](06_byok.md)
