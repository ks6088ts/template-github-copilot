#!/usr/bin/env python3
"""CLI Chatbot using the GitHub Copilot SDK.

See the tutorial for learning goals, prerequisites, and usage:
    docs/copilot_sdk_tutorial/tutorials/01_chat_bot.md     (English)
    docs/copilot_sdk_tutorial/tutorials/01_chat_bot.ja.md  (日本語)
"""

import argparse
import asyncio
import sys

from copilot import (
    CopilotClient,
    RuntimeConnection,
)
from copilot.generated.rpc import PermissionDecisionApproveOnce
from copilot.generated.session_events import (
    SessionEventType,
    PermissionRequest,
)
from copilot.session import (
    PermissionRequestResult,
    SystemMessageAppendConfig,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI Chatbot using the GitHub Copilot SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="Hello, Copilot! What can you do?",
        help="Prompt to send (single-shot mode)",
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
        "--loop",
        "-l",
        action="store_true",
        help="Run in interactive chat loop mode (Ctrl+C to exit)",
    )
    return parser.parse_args()


async def run_single(cli_url: str | None, prompt: str) -> None:
    """Send a single prompt and print the response."""

    def approve_all(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        return PermissionDecisionApproveOnce()

    client = (
        CopilotClient(connection=RuntimeConnection.for_uri(cli_url))
        if cli_url
        else CopilotClient()
    )
    await client.start()

    session = await client.create_session(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        system_message=SystemMessageAppendConfig(
            content="You are a helpful assistant."
        ),
    )

    def on_event(event) -> None:  # noqa: ANN001
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            print(event.data.delta_content, end="", flush=True)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"\n[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    reply = await session.send_and_wait(prompt, timeout=300)
    content = getattr(reply.data, "content", None) if reply else None
    # Ensure a newline after streaming output
    print()
    if not content:
        print("(no response)", file=sys.stderr)


async def run_loop(cli_url: str | None) -> None:
    """Run an interactive chat loop."""

    def approve_all(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        return PermissionDecisionApproveOnce()

    client = (
        CopilotClient(connection=RuntimeConnection.for_uri(cli_url))
        if cli_url
        else CopilotClient()
    )
    await client.start()

    session = await client.create_session(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        system_message=SystemMessageAppendConfig(
            content="You are a helpful assistant."
        ),
    )

    def on_event(event) -> None:  # noqa: ANN001
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            print(event.data.delta_content, end="", flush=True)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"\n[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    print("Chat with Copilot — type your message and press Enter (Ctrl+C to quit)\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        if not user_input:
            continue
        print("Copilot: ", end="")
        await session.send_and_wait(user_input, timeout=300)
        print()


def main() -> None:
    args = parse_args()
    try:
        if args.loop:
            asyncio.run(run_loop(args.cli_url))
        else:
            asyncio.run(run_single(args.cli_url, args.prompt))
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
