#!/usr/bin/env python3
"""Streaming Code Review using GitHub Copilot SDK.

What you will learn:
    - How to enable streaming and consume ASSISTANT_MESSAGE_DELTA events
    - How to structure a code-review prompt around a unified diff
    - How real-time output differs from waiting for the full response

Usage (run from ``src/python``):
    uv run python scripts/tutorials/03_streaming_review.py
    uv run python scripts/tutorials/03_streaming_review.py --diff path/to/changes.diff
    uv run python scripts/tutorials/03_streaming_review.py --cli-url localhost:3000

Prerequisites:
    uv sync   # installs github-copilot-sdk (declared in pyproject.toml)

    Install and authenticate the GitHub Copilot CLI so the SDK can launch it:
        npm install -g @github/copilot            # or: gh copilot (downloads on first run)
        gh auth login                             # or: export COPILOT_GITHUB_TOKEN=...

Corresponding doc:
    docs/copilot_sdk_tutorial/tutorials/03_streaming.md
"""

import argparse
import asyncio
import sys
from pathlib import Path

from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from copilot.types import (
    CopilotClientOptions,
    MessageOptions,
    PermissionRequest,
    PermissionRequestResult,
    SessionConfig,
    SystemMessageReplaceConfig,
)

# ---------------------------------------------------------------------------
# Sample diff (embedded so the script runs without external files)
# ---------------------------------------------------------------------------

SAMPLE_DIFF = """\
diff --git a/src/auth.py b/src/auth.py
index 1a2b3c4..5d6e7f8 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -12,7 +12,7 @@ import hashlib
 def hash_password(password: str) -> str:
-    return hashlib.md5(password.encode()).hexdigest()
+    return hashlib.sha256(password.encode()).hexdigest()

@@ -28,6 +28,12 @@ def verify_token(token: str) -> bool:
     if not token:
         return False
+    # TODO: add expiry check
     return token in _valid_tokens

+def delete_user(user_id: int) -> None:
+    # WARNING: no authorization check
+    db.execute("DELETE FROM users WHERE id = %s" % user_id)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Streaming Code Review using the GitHub Copilot SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--diff",
        "-d",
        default=None,
        help="Path to a unified diff file (uses built-in sample if not provided)",
    )
    parser.add_argument(
        "--cli-url",
        "-c",
        default=None,
        help=(
            "Optional Copilot CLI server URL (e.g. localhost:3000). "
            "When omitted, the SDK launches the copilot CLI over stdio."
        ),
    )
    return parser.parse_args()


async def run(cli_url: str | None, diff_text: str) -> None:
    def approve_all(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        return PermissionRequestResult(kind="approved", rules=[])

    client_options: CopilotClientOptions = (
        CopilotClientOptions(cli_url=cli_url) if cli_url else CopilotClientOptions()
    )
    client = CopilotClient(options=client_options)
    await client.start()

    session = await client.create_session(
        SessionConfig(
            on_permission_request=approve_all,
            tools=[],
            streaming=True,  # ← streaming enabled
            system_message=SystemMessageReplaceConfig(
                mode="replace",
                content=(
                    "You are a senior software engineer conducting a thorough code review. "
                    "For each change in the diff: identify bugs, security issues, and style problems. "
                    "Be concise but precise. Use Markdown formatting."
                ),
            ),
        )
    )

    # Stream tokens to stdout as they arrive
    print("=== Streaming Code Review ===\n")

    def on_event(event) -> None:  # noqa: ANN001
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            print(event.data.delta_content, end="", flush=True)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"\n[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    prompt = f"Please review the following diff and provide feedback:\n\n```diff\n{diff_text}\n```"
    await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
    print("\n\n=== Review Complete ===")


def main() -> None:
    args = parse_args()

    if args.diff:
        diff_path = Path(args.diff)
        if not diff_path.exists():
            print(f"Error: diff file not found: {args.diff}", file=sys.stderr)
            sys.exit(1)
        diff_text = diff_path.read_text()
    else:
        diff_text = SAMPLE_DIFF
        print(
            "[Info] Using built-in sample diff. Pass --diff <path> to use your own.\n"
        )

    try:
        asyncio.run(run(args.cli_url, diff_text))
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
