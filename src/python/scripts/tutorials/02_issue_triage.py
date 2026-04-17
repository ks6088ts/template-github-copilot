#!/usr/bin/env python3
"""Issue Triage Bot using GitHub Copilot SDK Custom Tools (@define_tool).

What you will learn:
    - How to register custom tools with @define_tool
    - How to pass structured input/output via Pydantic models
    - How to build a simple issue-triage agent that classifies and labels issues

Usage:
    python 02_issue_triage.py
    python 02_issue_triage.py --cli-url localhost:3000
    python 02_issue_triage.py --help

Prerequisites:
    pip install github-copilot-sdk pydantic

    Start the Copilot CLI server first:
        export COPILOT_GITHUB_TOKEN="<your-github-pat>"
        gh copilot serve --port 3000

Corresponding doc:
    docs/copilot_sdk_tutorial/tutorials/02_custom_tools.md
"""

import argparse
import asyncio
import json
import sys
from typing import Any, TypedDict

# ---------------------------------------------------------------------------
# Sample issue data (no external API calls needed)
# ---------------------------------------------------------------------------


class _IssueDict(TypedDict):
    id: int
    title: str
    body: str
    labels: list[str]


SAMPLE_ISSUES: list[_IssueDict] = [
    {
        "id": 1,
        "title": "Application crashes when uploading files larger than 100 MB",
        "body": "Steps to reproduce: open the upload dialog, select a file > 100 MB, click Upload. "
        "Expected: file uploads successfully. Actual: the app throws an unhandled exception.",
        "labels": [],
    },
    {
        "id": 2,
        "title": "Add dark mode support",
        "body": "It would be great to have a dark mode option in the settings panel.",
        "labels": [],
    },
    {
        "id": 3,
        "title": "Typo in README: 'recieve' should be 'receive'",
        "body": "Line 42 of README.md contains a typo.",
        "labels": [],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Issue Triage Bot using GitHub Copilot SDK Custom Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--cli-url",
        "-c",
        default="localhost:3000",
        help="Copilot CLI server URL (default: localhost:3000)",
    )
    return parser.parse_args()


async def run(cli_url: str) -> None:
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
    from copilot.tools import define_tool
    from pydantic import BaseModel

    # ------------------------------------------------------------------
    # Custom tool input/output schemas
    # ------------------------------------------------------------------

    class ListIssuesInput(BaseModel):
        pass

    class IssueItem(BaseModel):
        id: int
        title: str
        body: str
        labels: list[str]

    class ListIssuesOutput(BaseModel):
        issues: list[IssueItem]

    class LabelIssueInput(BaseModel):
        issue_id: int
        labels: list[str]

    class LabelIssueOutput(BaseModel):
        success: bool
        issue_id: int
        applied_labels: list[str]

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    triaged: list[dict[str, Any]] = []

    @define_tool(
        name="list_issues",
        description="Return the list of open GitHub issues to triage.",
    )
    def list_issues(_input: ListIssuesInput) -> ListIssuesOutput:  # noqa: ANN001
        return ListIssuesOutput(
            issues=[
                IssueItem(
                    id=issue["id"],
                    title=issue["title"],
                    body=issue["body"],
                    labels=issue["labels"],
                )
                for issue in SAMPLE_ISSUES
            ]
        )

    @define_tool(
        name="label_issue",
        description="Apply one or more labels to a GitHub issue.",
    )
    def label_issue(input: LabelIssueInput) -> LabelIssueOutput:  # noqa: ANN001
        triaged.append({"id": input.issue_id, "labels": input.labels})
        return LabelIssueOutput(
            success=True,
            issue_id=input.issue_id,
            applied_labels=input.labels,
        )

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------

    def approve_all(
        request: PermissionRequest,
        context: dict,
    ) -> PermissionRequestResult:
        return PermissionRequestResult(kind="approved", rules=[])

    client = CopilotClient(
        options=CopilotClientOptions(cli_url=cli_url),
    )
    await client.start()

    session = await client.create_session(
        SessionConfig(
            on_permission_request=approve_all,
            tools=[list_issues, label_issue],
            streaming=False,
            system_message=SystemMessageReplaceConfig(
                mode="replace",
                content=(
                    "You are an expert GitHub issue triage assistant. "
                    "Use list_issues to fetch open issues, classify each one "
                    "as 'bug', 'enhancement', or 'documentation', then call "
                    "label_issue to apply the appropriate label. "
                    "After triaging all issues, summarise your actions."
                ),
            ),
        )
    )

    def on_event(event: Any) -> None:
        if event.type == SessionEventType.TOOL_EXECUTION_START:
            print(f"[Tool] Calling: {event.data.tool_name}", file=sys.stderr)
        elif event.type == SessionEventType.SESSION_ERROR:
            print(f"[Error] {event.data.message}", file=sys.stderr)

    session.on(on_event)

    prompt = "Please triage all open issues and apply the appropriate labels."
    reply = await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
    content = reply.data.content if reply else "(no response)"

    print("=== Triage Summary ===")
    print(content)
    print("\n=== Applied Labels ===")
    print(json.dumps(triaged, indent=2))


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.cli_url))
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
