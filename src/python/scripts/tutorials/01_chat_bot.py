#!/usr/bin/env python3
"""CLI Chatbot using the GitHub Copilot SDK.

What you will learn:
    - How to create a CopilotClient and start a session
    - How to send a single prompt and receive a response
    - How to run an interactive chat loop
    - How to handle session events

Usage:
    # Single prompt (SDK auto-launches the copilot CLI via stdio)
    python 01_chat_bot.py --prompt "What is GitHub Copilot?"

    # Interactive loop
    python 01_chat_bot.py --loop

    # Connect to an externally running CLI server over TCP
    python 01_chat_bot.py --cli-url localhost:3000 --loop

Prerequisites:
    pip install github-copilot-sdk

    Install and authenticate the GitHub Copilot CLI so the SDK can launch it:
        npm install -g @github/copilot            # or: gh copilot (downloads on first run)
        gh auth login                             # or: export COPILOT_GITHUB_TOKEN=...

    If the copilot binary is not on PATH, set:
        export COPILOT_CLI_PATH=/path/to/copilot

Corresponding doc:
    docs/copilot_sdk_tutorial/tutorials/01_chat_bot.md
"""

import argparse
import asyncio
import sys


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
            streaming=True,
            system_message=SystemMessageAppendConfig(
                content="You are a helpful assistant."
            ),
        )
    )

    def on_event(event) -> None:  # noqa: ANN001
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            print(event.data.delta_content, end="", flush=True)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"\n[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    reply = await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
    content = reply.data.content if reply else None
    # Ensure a newline after streaming output
    print()
    if not content:
        print("(no response)", file=sys.stderr)


async def run_loop(cli_url: str | None) -> None:
    """Run an interactive chat loop."""
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
            streaming=True,
            system_message=SystemMessageAppendConfig(
                content="You are a helpful assistant."
            ),
        )
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
        await session.send_and_wait(MessageOptions(prompt=user_input), timeout=300)
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
