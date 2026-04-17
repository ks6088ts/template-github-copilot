# チュートリアル 3: ストリーミングコードレビュー

**スクリプト:** [`src/python/scripts/tutorials/03_streaming_review.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/03_streaming_review.py)

---

## 学べること

- `SessionConfig` でストリーミングを有効にする方法
- リアルタイム出力のために `ASSISTANT_MESSAGE_DELTA` イベントを受信する方法
- 統合差分（unified diff）をもとにコードレビュープロンプトを構造化する方法
- ストリーミングと非ストリーミングのレスポンスの違い

---

## 前提条件

- `localhost:3000` で実行中の Copilot CLI サーバー
- `github-copilot-sdk` がインストール済み

---

## ストリーミング vs 非ストリーミング

| モード | `streaming=True` | `streaming=False` |
|--------|-----------------|-------------------|
| トークンの到着 | `ASSISTANT_MESSAGE_DELTA` で逐次届く | 完全なレスポンスが生成された後 |
| 最初のバイトのレイテンシ | 低い — すぐに出力が表示される | 高い — 完全な回答を待つ |
| ユースケース | インタラクティブ UI、長いレスポンス、進捗表示 | バッチ処理、構造化出力のパース |

---

## ステップ 1 — SessionConfig でストリーミングを有効にする

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,     # ← ストリーミングを有効化
        system_message=SystemMessageReplaceConfig(
            mode="replace",
            content=(
                "You are a senior software engineer conducting a thorough code review. "
                "For each change in the diff: identify bugs, security issues, and style problems."
            ),
        ),
    )
)
```

---

## ステップ 2 — トークンが届くたびに出力する

各デルタトークンを直接 stdout に出力するイベントハンドラを登録します:

```python
from copilot.generated.session_events import SessionEventType

def on_event(event) -> None:
    if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
        print(event.data.delta_content, end="", flush=True)
    elif event.type == SessionEventType.SESSION_ERROR:
        print(f"\n[Error] {event.data.message}")

session.on(on_event)
```

重要なのは `end=""` と `flush=True` — これによりトークン間に改行が入らず、即座に出力されます。

---

## ステップ 3 — コードレビュープロンプトを送信する

差分をプロンプトに直接埋め込みます:

```python
diff_text = """
diff --git a/src/auth.py b/src/auth.py
...
-    return hashlib.md5(password.encode()).hexdigest()
+    return hashlib.sha256(password.encode()).hexdigest()
"""

prompt = f"Please review the following diff and provide feedback:\n\n```diff\n{diff_text}\n```"

await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
print()  # ストリーミング出力終了後の改行
```

---

## イベントフローの理解

`streaming=True` の場合、イベントはこの順序で届きます:

```
ASSISTANT_TURN_START
ASSISTANT_MESSAGE_DELTA  (トークン 1)
ASSISTANT_MESSAGE_DELTA  (トークン 2)
ASSISTANT_MESSAGE_DELTA  (トークン 3)
...
ASSISTANT_TURN_END
SESSION_IDLE
```

`send_and_wait` は `SESSION_IDLE` の後に返ります。すべてのデルタイベントはその**前に**ハンドラに配信されます。

---

## サンプル出力

組み込みのサンプル差分に対してスクリプトを実行した場合:

```
=== Streaming Code Review ===

### Security Issues

**Line -12:** `hashlib.md5` is a cryptographically broken hash function.
Using it for password hashing exposes users to collision attacks.
✅ The fix to `sha256` is correct, but consider using `bcrypt` or `argon2` for
password storage instead of raw SHA-256.

### Incomplete Implementation

**Line 31:** The `# TODO: add expiry check` comment indicates the token
validation logic is incomplete. This could allow expired tokens to be accepted.

### Critical: Missing Authorization

**Lines 35-37:** `delete_user()` performs a destructive operation with no
authorization check. Any caller can delete any user...
```

---

## スクリプトの実行

```bash
# 組み込みのサンプル差分を使用
python src/python/scripts/tutorials/03_streaming_review.py

# 独自の差分をレビュー
python src/python/scripts/tutorials/03_streaming_review.py --diff path/to/changes.diff

# カスタム CLI サーバー
python src/python/scripts/tutorials/03_streaming_review.py --cli-url localhost:3000
```

---

## まとめ

- `SessionConfig` で `streaming=True` を設定すると逐次トークンを受信できる
- `ASSISTANT_MESSAGE_DELTA` イベントを処理してトークンが届くたびに出力する
- シームレスなストリーミング出力のために `end=""` と `flush=True` を使用する
- `send_and_wait` は完全なレスポンスを待つ — ストリーミングはトークンをいつ取得するかの問題
- 完全なレスポンスは `send_and_wait` の戻り値からも取得できる

---

## 次のチュートリアル

[チュートリアル 4: スキルによるドキュメント生成 →](04_skills.md)
