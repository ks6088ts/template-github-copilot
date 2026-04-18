# Tutorial 4: Skills-Based Documentation Generation

**Script:** [`src/python/scripts/tutorials/04_skills_docgen.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/04_skills_docgen.py)

---

## What You Will Learn

- What Agent Skills are and how they differ from Custom Tools
- How to write a `SKILL.md` file
- How to configure a skills directory in `CopilotClientOptions`
- How to use a skill for automatic docstring generation

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- `github-copilot-sdk` installed

---

## Skills vs Custom Tools

| | Custom Tools (`@define_tool`) | Skills (`SKILL.md`) |
|-|-------------------------------|---------------------|
| Definition | Python function | Markdown document |
| Logic | Code (Python) | Instructions in natural language |
| Input/Output | Pydantic models | Unstructured text |
| Best for | Structured data, API calls, DB queries | Prompt engineering, reusable agent personas |

**Skills** are Markdown files that give the agent **persistent instructions and context**. They are loaded at server startup and available for all sessions on that server.

---

## Step 1 — Write a SKILL.md file

Create `skills/docgen/SKILL.md`:

```markdown
# docgen

You are an expert Python documentation specialist.

## Instructions

When given Python source code, generate complete **Google-style docstrings**
for every function and class that does not already have one.

- Include `Args:`, `Returns:`, and `Raises:` sections where applicable.
- Keep descriptions concise but precise.
- Return the complete updated source file inside a single fenced code block.
```

Key elements of a good SKILL.md:

| Element | Purpose |
|---------|---------|
| **Title** (`# name`) | The skill's identifier |
| **Role statement** | Defines who the agent "is" for this skill |
| **Instructions** | Step-by-step guidance for the agent |
| **Output format** | How the agent should format its response |
| **Example** (optional) | A concrete input/output pair |

---

## Step 2 — Configure the skills directory

Skill directories are attached **per session** via `SessionConfig.skill_directories`:

```python
from copilot import CopilotClient
from copilot.types import SessionConfig

client = CopilotClient()
await client.start()

session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        skill_directories=["/path/to/skills"],   # ← list of directories
        system_message=SystemMessageReplaceConfig(
            mode="replace",
            content="You are a Python documentation specialist.",
        ),
    )
)
```

The expected layout:

```
skills/
├── docgen/
│   └── SKILL.md          # ← each skill in its own subdirectory
└── coding-standards/
    └── SKILL.md
```

---

## Step 3 — Invoke the skill via a prompt

You don't call skills explicitly — you prompt the agent and the Copilot server selects the most appropriate skill based on your request:

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[],
        streaming=True,
        system_message=SystemMessageReplaceConfig(
            mode="replace",
            content=(
                "You are a Python documentation specialist. "
                "Generate Google-style docstrings for all functions."
            ),
        ),
    )
)

prompt = (
    "Please add Google-style docstrings to all functions in the following code:\n\n"
    "```python\n"
    "def calculate_discount(price: float, discount_pct: float) -> float:\n"
    "    if discount_pct < 0 or discount_pct > 100:\n"
    "        raise ValueError('discount_pct must be between 0 and 100')\n"
    "    return price * (1 - discount_pct / 100)\n"
    "```"
)

await session.send_and_wait(MessageOptions(prompt=prompt), timeout=300)
```

---

## Skills Directory in This Repo

This repository includes two example skills:

| Skill | File | Purpose |
|-------|------|---------|
| `docgen` | `skills/docgen/SKILL.md` | Generates Google-style docstrings |
| `coding-standards` | `skills/coding-standards/SKILL.md` | Checks code against team standards |

You can extend this directory with your own skills.

---

## Run the Script

```bash
cd src/python

# Use the default skills directory (./skills)
uv run python scripts/tutorials/04_skills_docgen.py

# Custom skills directory
uv run python scripts/tutorials/04_skills_docgen.py --skills-dir /path/to/my/skills

# Without skills (server-only prompting)
uv run python scripts/tutorials/04_skills_docgen.py --skills-dir /nonexistent
```

---

## Key Takeaways

- Skills are Markdown files (`SKILL.md`) that give the agent persistent instructions
- Each skill lives in its own subdirectory under a configured skill directory
- Configure `SessionConfig(skill_directories=[...])` to load skills for a session
- The agent automatically uses the most relevant skill based on the task
- Skills complement custom tools: skills define **how** to behave, tools provide **what** to call

---

## Next Tutorial

[Tutorial 5: Audit Log with Session Hooks →](05_hooks_permissions.md)
