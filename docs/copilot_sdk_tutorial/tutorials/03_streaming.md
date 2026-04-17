# Tutorial 3: Streaming Code Review

**Script:** [`src/python/scripts/tutorials/03_streaming_review.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/03_streaming_review.py)

---

## What You Will Learn

- How to enable streaming in a `SessionConfig`
- How to consume `ASSISTANT_MESSAGE_DELTA` events for real-time output
- How to structure a code-review prompt around a unified diff
- The difference between streaming and non-streaming responses

---

## Prerequisites

- Copilot CLI server running on `localhost:3000`
- `github-copilot-sdk` installed

---

## Streaming vs Non-Streaming

| Mode | `streaming=True` | `streaming=False` |
|------|-----------------|-------------------|
| Tokens arrive | Incrementally, via `ASSISTANT_MESSAGE_DELTA` | After the full response is generated |
| First byte latency | Low — you see output immediately | High — you wait for the complete answer |
| Use case | Interactive UIs, long responses, progress display | Batch processing, structured output parsing |

---

## Step 1 — Enable streaming in SessionConfig

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,     # ← enable streaming
        system_message=SystemMessageReplaceConfig(
            content=(
                "You are a senior software engineer conducting a thorough code review. "
                "For each change in the diff: identify bugs, security issues, and style problems."
            )
        ),
    )
)
```

---

## Step 2 — Print tokens as they arrive

Register an event handler that prints each delta token directly to stdout:

```python
from copilot.generated.session_events import SessionEventType

def on_event(event) -> None:
    if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
        print(event.data.delta_content, end="", flush=True)
    elif event.type == SessionEventType.SESSION_ERROR:
        print(f"\n[Error] {event.data.message}")

session.on(on_event)
```

The key is `end=""` and `flush=True` — this prevents line breaks between tokens and ensures immediate output.

---

## Step 3 — Send the code review prompt

Embed the diff directly in the prompt:

```python
diff_text = """
diff --git a/src/auth.py b/src/auth.py
...
-    return hashlib.md5(password.encode()).hexdigest()
+    return hashlib.sha256(password.encode()).hexdigest()
"""

prompt = f"Please review the following diff and provide feedback:\n\n```diff\n{diff_text}\n```"

await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
print()  # Newline after streaming output ends
```

---

## Understanding the Event Flow

When `streaming=True`, events arrive in this order:

```
ASSISTANT_TURN_START
ASSISTANT_MESSAGE_DELTA  (token 1)
ASSISTANT_MESSAGE_DELTA  (token 2)
ASSISTANT_MESSAGE_DELTA  (token 3)
...
ASSISTANT_TURN_END
SESSION_IDLE
```

`send_and_wait` returns after `SESSION_IDLE`. All delta events are delivered to your handler **before** that.

---

## Sample Output

Running the script against the built-in sample diff:

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

## Run the Script

```bash
# Use the built-in sample diff
python src/python/scripts/tutorials/03_streaming_review.py

# Review your own diff
python src/python/scripts/tutorials/03_streaming_review.py --diff path/to/changes.diff

# Custom CLI server
python src/python/scripts/tutorials/03_streaming_review.py --cli-url localhost:3000
```

---

## Key Takeaways

- Set `streaming=True` in `SessionConfig` to receive incremental tokens
- Handle `ASSISTANT_MESSAGE_DELTA` events to print tokens as they arrive
- Use `end=""` and `flush=True` for seamless streaming output
- `send_and_wait` still waits for the full response; streaming is about **when** you get the tokens
- The complete response is also available in the return value of `send_and_wait`

---

## Next Tutorial

[Tutorial 4: Skills-Based Doc Generation →](04_skills.md)
