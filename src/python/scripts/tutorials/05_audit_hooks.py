#!/usr/bin/env python3
"""Audit Logging using GitHub Copilot SDK Session Hooks and Permission Handling.

A custom ``delete_record`` tool models a destructive operation that an audit
policy may want to block. Run with ``--deny-tools`` to see the permission
handler reject the call — the tool implementation never runs and the audit log
records the denial.

See the tutorial for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/tutorials/05_hooks_permissions.md     (English)
    docs/copilot_sdk_tutorial/tutorials/05_hooks_permissions.ja.md  (日本語)
"""

import argparse
import asyncio
import json
import sys
import time
from typing import Any

from copilot import (
    CopilotClient,
    RuntimeConnection,
)
from copilot.generated.rpc import (
    PermissionDecisionApproveOnce,
    PermissionDecisionReject,
)
from copilot.generated.session_events import (
    SessionEventType,
    PermissionRequest,
)
from copilot.session import (
    PermissionRequestResult,
    SystemMessageReplaceConfig,
)
from copilot.tools import define_tool
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Custom tool — a destructive action an audit policy may want to block
# ---------------------------------------------------------------------------


class DeleteRecordInput(BaseModel):
    record_id: int


class DeleteRecordOutput(BaseModel):
    success: bool
    record_id: int
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Logging using GitHub Copilot SDK Session Hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="Delete the customer record with ID 42 using the delete_record tool, then confirm what happened.",
        help="Prompt to send to Copilot",
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
    parser.add_argument(
        "--deny-tools",
        action="store_true",
        help="Use a permission handler that denies all tool executions",
    )
    return parser.parse_args()


async def run(cli_url: str | None, prompt: str, deny_tools: bool) -> None:
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
    # Custom tool — records which records were actually deleted so the
    # caller can observe whether the permission handler allowed the call
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Permission handler — either approve all or deny all tool calls.
    # This fires because the session registers a custom tool below; with
    # no tools the handler would never be invoked.
    # ------------------------------------------------------------------

    def permission_handler(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        tool_name = getattr(request, "tool_name", "unknown")
        if deny_tools:
            record("PERMISSION_DENIED", f"tool={tool_name}")
            print(f"[Permission] DENIED tool execution: {tool_name}", file=sys.stderr)
            return PermissionDecisionReject(
                feedback="Tool execution denied by audit policy"
            )
        record("PERMISSION_APPROVED", f"tool={tool_name}")
        print(f"[Permission] APPROVED tool execution: {tool_name}", file=sys.stderr)
        return PermissionDecisionApproveOnce()

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------

    client = (
        CopilotClient(connection=RuntimeConnection.for_uri(cli_url))
        if cli_url
        else CopilotClient()
    )
    await client.start()

    session = await client.create_session(
        on_permission_request=permission_handler,
        tools=[delete_record],
        streaming=False,
        system_message=SystemMessageReplaceConfig(
            mode="replace",
            content=(
                "You are an operations assistant with access to a delete_record tool. "
                "When asked to delete a record, call the delete_record tool. "
                "If a tool call is denied, clearly state that the action was blocked "
                "by policy and do not retry."
            ),
        ),
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
    reply = await session.send_and_wait(prompt, timeout=300)
    content = getattr(reply.data, "content", None) if reply else "(no response)"

    print("=== Response ===")
    print(content)
    print("\n=== Deleted Records ===")
    print(deleted_records if deleted_records else "(none — tool was not executed)")
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
