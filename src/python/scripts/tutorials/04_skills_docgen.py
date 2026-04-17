#!/usr/bin/env python3
"""Document Generation using GitHub Copilot SDK Skills (SKILL.md).

What you will learn:
    - What Agent Skills are and how to structure a SKILL.md file
    - How to point the Copilot SDK to a local skills directory
    - How to invoke a skill to auto-generate docstrings for Python code

Usage:
    python 04_skills_docgen.py
    python 04_skills_docgen.py --skills-dir ./skills
    python 04_skills_docgen.py --cli-url localhost:3000

Prerequisites:
    pip install github-copilot-sdk

    Start the Copilot CLI server first:
        export COPILOT_GITHUB_TOKEN="<your-github-pat>"
        gh copilot serve --port 3000

Corresponding doc:
    docs/copilot_sdk_tutorial/tutorials/04_skills.md
"""

import argparse
import asyncio
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Sample Python code that needs docstrings generated
# ---------------------------------------------------------------------------

SAMPLE_CODE = '''\
def calculate_discount(price: float, discount_pct: float) -> float:
    if discount_pct < 0 or discount_pct > 100:
        raise ValueError("discount_pct must be between 0 and 100")
    return price * (1 - discount_pct / 100)


def batch_process(items: list[str], handler) -> list[str]:
    results = []
    for item in items:
        try:
            results.append(handler(item))
        except Exception as exc:
            results.append(f"ERROR: {exc}")
    return results
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Document Generation using GitHub Copilot SDK Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--skills-dir",
        "-s",
        default=str(Path(__file__).parent / "skills"),
        help="Path to the skills directory containing SKILL.md files",
    )
    parser.add_argument(
        "--cli-url",
        "-c",
        default="localhost:3000",
        help="Copilot CLI server URL (default: localhost:3000)",
    )
    return parser.parse_args()


async def run(cli_url: str, skills_dir: str) -> None:
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

    skills_path = Path(skills_dir)
    if not skills_path.exists():
        print(
            f"[Warning] Skills directory not found: {skills_dir}. "
            "Running without skills.",
            file=sys.stderr,
        )
        skills_dir_opt = None
    else:
        skills_dir_opt = str(skills_path.resolve())
        print(f"[Info] Loading skills from: {skills_dir_opt}")

    def approve_all(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        return PermissionRequestResult(kind="approved", rules=[])

    client_options: dict = {"cli_url": cli_url}
    if skills_dir_opt:
        client_options["skills_directory"] = skills_dir_opt

    client = CopilotClient(
        options=CopilotClientOptions(**client_options),
    )
    await client.start()

    session = await client.create_session(
        SessionConfig(
            on_permission_request=approve_all,
            tools=[],
            streaming=True,
            system_message=SystemMessageReplaceConfig(
                content=(
                    "You are a Python documentation specialist. "
                    "Generate clear, complete Google-style docstrings for all functions "
                    "in the provided code. Return only the updated code with docstrings added."
                )
            ),
        )
    )

    print("=== Generating Documentation ===\n")

    def on_event(event) -> None:  # noqa: ANN001
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            print(event.data.delta_content, end="", flush=True)
        elif event.type == SessionEventType.TOOL_EXECUTION_START:
            print(f"\n[Skill] Running: {event.data.tool_name}", file=sys.stderr)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"\n[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    prompt = (
        f"Please add Google-style docstrings to all functions in the following code:\n\n"
        f"```python\n{SAMPLE_CODE}\n```"
    )
    await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
    print("\n\n=== Done ===")


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.cli_url, args.skills_dir))
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
