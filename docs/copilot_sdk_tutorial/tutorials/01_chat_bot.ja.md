# チュートリアル 1: CLI チャットボット

**スクリプト:** [`src/python/scripts/tutorials/01_chat_bot.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/01_chat_bot.py)

---

## 学べること

- `CopilotClient` を作成して CLI サーバーに接続する方法
- システムメッセージとパーミッションハンドラを含む `SessionConfig` の作成方法
- 単一プロンプトを送信してレスポンスを受信する方法
- `ASSISTANT_MESSAGE_DELTA` を通じてストリーミングトークンを受信する方法
- インタラクティブチャットループの実行方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `github-copilot-sdk` がインストール済み

---

## ステップ 1 — クライアントの作成と起動

`CopilotClient` はメインのエントリーポイントです。デフォルトでは `copilot` バイナリをサブプロセスとして起動し、stdio 経由で通信します。TCP モードで既に Copilot CLI が動く場合に限り `cli_url` を渡します:

```python
from copilot import CopilotClient
from copilot.types import CopilotClientOptions

# デフォルト: SDK が CLI を stdio で起動
client = CopilotClient()

# オプション: 既に起動している CLI サーバーに接続
# client = CopilotClient(options=CopilotClientOptions(cli_url="localhost:3000"))

await client.start()
```

> **注意:** `await client.start()` は JSON-RPC 接続を確立します。セッションを作成する前に呼び出してください。

---

## ステップ 2 — セッションの設定

`SessionConfig` は単一の会話に関連するすべてをグループ化します:

```python
from copilot.types import (
    PermissionRequest,
    PermissionRequestResult,
    SessionConfig,
    SystemMessageAppendConfig,
)

def approve_all(request: PermissionRequest, context: dict) -> PermissionRequestResult:
    return PermissionRequestResult(kind="approved", rules=[])

session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        system_message=SystemMessageAppendConfig(
            content="You are a helpful assistant."
        ),
    )
)
```

**主要フィールド:**

| フィールド | 説明 |
|----------|------|
| `on_permission_request` | 各ツール実行前に呼び出される — `approved` または `denied` を返す |
| `tools` | 登録するカスタムツールのリスト（プレーンチャットセッションの場合は空） |
| `streaming` | トークンを逐次受信するか（`True`）、完全なレスポンスを待つか（`False`） |
| `system_message` | アシスタントのペルソナを設定 |

---

## ステップ 3 — セッションイベントの処理

セッションイベントは `session.on(handler)` を通じてプッシュされます。ここでストリーミング出力やステータス更新が届きます:

```python
from copilot.generated.session_events import SessionEventType

def on_event(event) -> None:
    if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
        print(event.data.delta_content, end="", flush=True)
    elif event.type == SessionEventType.SESSION_ERROR:
        print(f"\n[Error] {event.data.message}")

session.on(on_event)
```

**主なイベントタイプ:**

| イベント | 発火タイミング |
|---------|---------------|
| `ASSISTANT_TURN_START` | Copilot が処理を開始 |
| `ASSISTANT_MESSAGE_DELTA` | ストリーミングトークンが届いた |
| `TOOL_EXECUTION_START` | ツールが実行されようとしている |
| `TOOL_EXECUTION_COMPLETE` | ツールが完了した |
| `ASSISTANT_TURN_END` | 処理が完了した |
| `SESSION_IDLE` | セッションが次のメッセージを受け付ける状態 |
| `SESSION_ERROR` | エラーが発生した |

---

## ステップ 4 — プロンプトの送信

```python
from copilot.types import MessageOptions

reply = await session.send_and_wait(
    MessageOptions(prompt="What is GitHub Copilot?"),
    timeout=300,
)
content = reply.data.content if reply else "(no response)"
print(content)
```

`send_and_wait` はセッションが `SESSION_IDLE` になるまでブロックします。その間、ストリーミングイベントが `on_event` ハンドラに配信されます。

---

## ステップ 5 — インタラクティブチャットループ

マルチターンの会話には、セッションを維持しながら `send_and_wait` をループで呼び出します:

```python
print("Chat with Copilot (Ctrl+C to quit)\n")
while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    print("Copilot: ", end="")
    await session.send_and_wait(MessageOptions(prompt=user_input), timeout=300)
    print()
```

---

## スクリプトの実行

```bash
# 単一プロンプト
python src/python/scripts/tutorials/01_chat_bot.py --prompt "Explain async/await in Python"

# インタラクティブループ
python src/python/scripts/tutorials/01_chat_bot.py --loop

# カスタム CLI サーバー URL（オプション — TCP モードで CLI サーバーが起動している場合のみ）
python src/python/scripts/tutorials/01_chat_bot.py --cli-url localhost:3000 --loop
```

---

## まとめ

- `CopilotClient` → `create_session` → `send_and_wait` が基本パターン
- `SessionConfig` はペルソナ、ツール、ストリーミング、パーミッションを制御する
- `session.on(handler)` はストリーミングデルタを含むすべてのイベントを受信する
- セッションはマルチターンの会話に再利用できる
- `send_and_wait` はレスポンスが完了するまでブロックする

---

## 次のチュートリアル

[チュートリアル 2: カスタムツールによる Issue トリアージボット →](02_custom_tools.md)
