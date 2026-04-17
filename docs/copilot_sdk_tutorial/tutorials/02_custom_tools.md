# Tutorial 2: Issue Triage Bot with Custom Tools

**Script:** [`src/python/scripts/tutorials/02_issue_triage.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/02_issue_triage.py)

---

## What You Will Learn

- How to define custom tools with the `@define_tool` decorator
- How to use Pydantic models for tool input and output schemas
- How to build a tool-calling agent that classifies and labels GitHub issues

---

## Prerequisites

- Copilot CLI server running on `localhost:3000`
- `github-copilot-sdk` and `pydantic` installed

---

## What Are Custom Tools?

Custom tools let you give the Copilot agent access to your own functions. The agent decides **when** to call them based on their descriptions. You define:

1. The tool's **name** and **description** (used by the LLM to decide when to call it)
2. The **input schema** (a Pydantic `BaseModel`)
3. The **output schema** (another Pydantic `BaseModel`)
4. The **implementation** (a regular Python function)

---

## Step 1 — Define Input/Output schemas

```python
from pydantic import BaseModel

class ListIssuesInput(BaseModel):
    pass  # No parameters needed

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
```

Clear, typed schemas help the LLM understand what data to pass and what to expect back.

---

## Step 2 — Implement the tools with `@define_tool`

```python
from copilot.tools import define_tool

@define_tool(
    name="list_issues",
    description="Return the list of open GitHub issues to triage.",
)
def list_issues(_input: ListIssuesInput) -> ListIssuesOutput:
    return ListIssuesOutput(
        issues=[IssueItem(**issue) for issue in SAMPLE_ISSUES]
    )

@define_tool(
    name="label_issue",
    description="Apply one or more labels to a GitHub issue.",
)
def label_issue(input: LabelIssueInput) -> LabelIssueOutput:
    # In a real scenario, call the GitHub API here
    return LabelIssueOutput(
        success=True,
        issue_id=input.issue_id,
        applied_labels=input.labels,
    )
```

> **Tip:** Write descriptive `description` strings. The LLM uses them to decide when to invoke each tool.

---

## Step 3 — Register tools in the session

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[list_issues, label_issue],  # ← register here
        streaming=False,
        system_message=SystemMessageReplaceConfig(
            mode="replace",
            content=(
                "You are an expert GitHub issue triage assistant. "
                "Use list_issues to fetch open issues, classify each one "
                "as 'bug', 'enhancement', or 'documentation', then call "
                "label_issue to apply the appropriate label."
            ),
        ),
    )
)
```

Note `SystemMessageReplaceConfig` — this **replaces** the default system message entirely, giving the agent a focused persona.

---

## Step 4 — Send the task prompt

```python
reply = await session.send_and_wait(
    MessageOptions(prompt="Please triage all open issues and apply the appropriate labels."),
    timeout=300,
)
print(reply.data.content)
```

The agent will:

1. Call `list_issues()` to fetch the issues
2. Analyse each issue
3. Call `label_issue()` for each one with the appropriate label
4. Return a summary

---

## Run the Script

```bash
python src/python/scripts/tutorials/02_issue_triage.py
python src/python/scripts/tutorials/02_issue_triage.py --cli-url localhost:3000
```

Expected output:

```
[Tool] Calling: list_issues
[Tool] Calling: label_issue
[Tool] Calling: label_issue
[Tool] Calling: label_issue
=== Triage Summary ===
I've triaged all 3 open issues...

=== Applied Labels ===
[
  {"id": 1, "labels": ["bug"]},
  {"id": 2, "labels": ["enhancement"]},
  {"id": 3, "labels": ["documentation"]}
]
```

---

## Key Takeaways

- `@define_tool(name, description)` registers a function as a callable tool
- Pydantic `BaseModel` defines strongly-typed input/output contracts
- Tools are registered per-session in `SessionConfig(tools=[...])`
- The LLM decides **when** to call tools based on the task and the description strings
- `SystemMessageReplaceConfig` gives the agent a dedicated persona for the task

---

## Next Tutorial

[Tutorial 3: Streaming Code Review →](03_streaming.md)
