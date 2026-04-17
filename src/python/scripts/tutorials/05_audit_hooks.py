#!/usr/bin/env python3
"""Audit Logging using GitHub Copilot SDK Session Hooks and Permission Handling.

What you will learn:
    - How to intercept all session events via session.on()
    - How to implement a custom permission handler (approve / deny)
    - How to build a simple structured audit log from event stream

Usage:
    python 05_audit_hooks.py --prompt "List 3 interesting Python tips"
    python 05_audit_hooks.py --deny-tools
    python 05_audit_hooks.py --cli-url localhost:3000

Prerequisites:
    pip install github-copilot-sdk

    Start the Copilot CLI server first:
        export COPILOT_GITHUB_TOKEN="<your-github-pat>"
        gh copilot serve --port 3000

Corresponding doc:
    docs/copilot_sdk_tutorial/tutorials/05_hooks_permissions.md
"""

import argparse
import asyncio
import json
import sys
import time
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Logging using GitHub Copilot SDK Session Hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="What are 3 best practices for writing secure Python code?",
        help="Prompt to send to Copilot",
    )
    parser.add_argument(
        "--cli-url",
        "-c",
        default="localhost:3000",
        help="Copilot CLI server URL (default: localhost:3000)",
    )
    parser.add_argument(
        "--deny-tools",
        action="store_true",
        help="Use a permission handler that denies all tool executions",
    )
    return parser.parse_args()


async def run(cli_url: str, prompt: str, deny_tools: bool) -> None:
    from copilot import CopilotClient
    from copilot.generated.session_events import SessionEventType
    from copilot.types import (
        CopilotClientOptions,
        MessageOptions,
        PermissionRequest,
        PermissionRequestResult,
        SessionConfig,
        SystemMessageAppendConfig,
    )

    audit_log: list[dict[str, Any]] = []
    start_time = time.time()

    def record(event_name: str, detail: str = "") -> None:
        audit_log.append(
            {
                "ts": round(time.time() - start_time, 3),
                "event": event_name,
                "detail": detail,
            }
        )

    # ------------------------------------------------------------------
    # Permission handler — either approve all or deny all tool calls
    # ------------------------------------------------------------------

    def permission_handler(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        tool_name = getattr(request, "tool_name", "unknown")
        if deny_tools:
            record("PERMISSION_DENIED", f"tool={tool_name}")
            print(
                f"[Permission] DENIED tool execution: {tool_name}", file=sys.stderr
            )
            return PermissionRequestResult(kind="denied", rules=[])
        record("PERMISSION_APPROVED", f"tool={tool_name}")
        return PermissionRequestResult(kind="approved", rules=[])

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------

    client = CopilotClient(
        options=CopilotClientOptions(cli_url=cli_url),
    )
    await client.start()

    session = await client.create_session(
        SessionConfig(
            on_permission_request=permission_handler,
            tools=[],
            streaming=False,
            system_message=SystemMessageAppendConfig(
                content="You are a helpful assistant."
            ),
        )
    )

    # ------------------------------------------------------------------
    # Event hook — records every session event
    # ------------------------------------------------------------------

    def on_event(event: Any) -> None:
        et = event.type

        if et == SessionEventType.ASSISTANT_TURN_START:
            record("TURN_START")
        elif et == SessionEventType.ASSISTANT_INTENT:
            record("INTENT", event.data.intent)
        elif et == SessionEventType.TOOL_EXECUTION_START:
            record("TOOL_START", event.data.tool_name)
            print(f"[Tool] Starting: {event.data.tool_name}", file=sys.stderr)
        elif et == SessionEventType.TOOL_EXECUTION_COMPLETE:
            err = getattr(event.data, "error", None)
            record("TOOL_COMPLETE", f"error={err.message if err else None}")
        elif et == SessionEventType.ASSISTANT_TURN_END:
            record("TURN_END")
        elif et == SessionEventType.SESSION_IDLE:
            record("SESSION_IDLE")
        elif et == SessionEventType.SESSION_ERROR:
            record("SESSION_ERROR", event.data.message)
            print(f"[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    record("SEND", prompt[:80])
    reply = await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
    content = reply.data.content if reply else "(no response)"

    print("=== Response ===")
    print(content)
    print("\n=== Audit Log ===")
    print(json.dumps(audit_log, indent=2))


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.cli_url, args.prompt, args.deny_tools))
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
