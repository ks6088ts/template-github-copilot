# Tutorial 4: Skills Doc Generation

**Subcommand:** `tutorial skills-docgen`
**Source:** [`src/go/cmd/tutorial/skillsdocgen.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/skillsdocgen.go)

---

## What You Will Learn

- What a `SKILL.md` file is and how a skills directory is laid out
- How to load skills with `SessionConfig.SkillDirectories`
- Why skill paths should be resolved to absolute paths before use
- How to observe skill execution through `ToolExecutionStartData` events

---

## Prerequisites

- The `copilot` CLI installed and authenticated (see [Getting Started](../getting_started.md))
- The Go CLI built with `make build` (see [Getting Started](../getting_started.md))

---

## Step 1 — Understand the skills directory

A skill is a folder containing a `SKILL.md` file with reusable instructions Copilot can apply on demand. This tutorial ships two skills under [`src/go/cmd/tutorial/skills/`](https://github.com/ks6088ts/template-github-copilot/tree/main/src/go/cmd/tutorial/skills):

```text
skills/
├── docgen/
│   └── SKILL.md          # godoc-style doc-comment generator
└── coding-standards/
    └── SKILL.md          # Go coding standards checker
```

Each `SKILL.md` starts with a title and describes the persona and instructions for that skill. The runtime loads them and lets Copilot invoke the relevant one when it matches the task.

---

## Step 2 — Resolve the skills directory to an absolute path

The CLI runtime may run with a different working directory, so resolve the path with `filepath.Abs` and confirm it exists before passing it on. When the directory is missing, the subcommand warns and continues without skills:

```go
var skillDirectories []string
if absDir, err := filepath.Abs(skillsDir); err == nil {
    if info, statErr := os.Stat(absDir); statErr == nil && info.IsDir() {
        skillDirectories = []string{absDir}
        fmt.Fprintf(os.Stderr, "[Info] Loading skills from: %s\n", absDir)
    } else {
        fmt.Fprintf(os.Stderr, "[Warning] Skills directory not found: %s. Running without skills.\n", skillsDir)
    }
}
```

---

## Step 3 — Load skills on the session

Pass the resolved directories to `SessionConfig.SkillDirectories`. A `nil` slice simply means no extra skills are loaded:

```go
session, err := client.CreateSession(ctx, &copilot.SessionConfig{
    OnPermissionRequest: copilot.PermissionHandler.ApproveAll,
    Streaming:           copilot.Bool(true),
    SkillDirectories:    skillDirectories,
    SystemMessage: &copilot.SystemMessageConfig{
        Mode: "replace",
        Content: "You are a Go documentation specialist. " +
            "Generate clear, complete godoc-style doc comments for all exported functions " +
            "in the provided code. Return only the updated code with doc comments added.",
    },
})
```

---

## Step 4 — Observe skill execution and stream the result

When Copilot invokes a skill, it surfaces as a `ToolExecutionStartData` event. The generated documentation streams in via `AssistantMessageDeltaData`:

```go
session.On(func(event copilot.SessionEvent) {
    switch data := event.Data.(type) {
    case *copilot.AssistantMessageDeltaData:
        fmt.Print(data.DeltaContent)
    case *copilot.ToolExecutionStartData:
        fmt.Fprintf(os.Stderr, "\n[Skill] Running: %s\n", data.ToolName)
    case *copilot.SessionErrorData:
        fmt.Fprintf(os.Stderr, "\n[Error] %s\n", data.Message)
    }
})

prompt := fmt.Sprintf("Please add godoc-style doc comments to all functions in the following code:\n\n```go\n%s\n```", sampleGoCode)
if _, err := session.SendPromptAndWait(ctx, prompt); err != nil {
    return err
}
```

---

## Run the Subcommand

Run from the `src/go` directory so the default `--skills-dir cmd/tutorial/skills` resolves correctly:

```bash
cd src/go
make build

# Use the bundled skills directory (default)
./dist/template-github-copilot-go tutorial skills-docgen

# Point at a different skills directory
./dist/template-github-copilot-go tutorial skills-docgen --skills-dir /path/to/skills
```

### Flags

| Flag | Shorthand | Default | Description |
|------|-----------|---------|-------------|
| `--skills-dir` | `-s` | `cmd/tutorial/skills` | Path to the skills directory containing `SKILL.md` files (relative to the current directory) |
| `--cli-url` | `-c` | _(empty)_ | Optional Copilot CLI server URL (e.g. `localhost:3000`) |

> The global `--verbose`/`-v` flag lowers the log level to `DEBUG`, surfacing the client connection mode and session lifecycle.

---

## Authoring Your Own Skill

Create a new folder under the skills directory with a `SKILL.md` file:

```text
skills/
└── my-skill/
    └── SKILL.md
```

Describe the persona and instructions in Markdown. Keep the guidance focused: a clear title, a short role statement, and concrete rules or examples. The runtime decides when the skill is relevant to the current task.

---

## Next Steps

- Tutorial 5 — [Audit Log](05_audit_hooks.md): gate tool calls behind a permission policy
- Tutorial 2 — [Issue Triage Bot](02_issue_triage.md): combine skills with custom tools
- Browse the full Go API on [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go)
