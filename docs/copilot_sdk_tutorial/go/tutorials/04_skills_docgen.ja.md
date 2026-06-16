# チュートリアル 4: スキルによるドキュメント生成

**サブコマンド:** `tutorial skills-docgen`
**ソース:** [`src/go/cmd/tutorial/skillsdocgen.go`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/go/cmd/tutorial/skillsdocgen.go)

---

## 学べること

- `SKILL.md` ファイルとは何か、スキルディレクトリの構成
- `SessionConfig.SkillDirectories` でスキルを読み込む方法
- スキルのパスを使用前に絶対パスへ解決すべき理由
- `ToolExecutionStartData` イベントでスキルの実行を観測する方法

---

## 前提条件

- `copilot` CLI がインストール済みかつ認証済み（[はじめに](../getting_started.md) を参照）
- `make build` でビルド済みの Go CLI（[はじめに](../getting_started.md) を参照）

---

## ステップ 1 — スキルディレクトリを理解する

スキルとは、Copilot が必要に応じて適用できる再利用可能な指示を記述した `SKILL.md` ファイルを含むフォルダです。このチュートリアルでは [`src/go/cmd/tutorial/skills/`](https://github.com/ks6088ts/template-github-copilot/tree/main/src/go/cmd/tutorial/skills) に 2 つのスキルを同梱しています。

```text
skills/
├── docgen/
│   └── SKILL.md          # godoc スタイルのドキュメントコメント生成
└── coding-standards/
    └── SKILL.md          # Go コーディング規約チェッカー
```

各 `SKILL.md` はタイトルで始まり、そのスキルのペルソナと指示を記述します。ランタイムがこれらを読み込み、タスクに合致したときに Copilot が該当スキルを呼び出します。

---

## ステップ 2 — スキルディレクトリを絶対パスへ解決する

CLI ランタイムは異なる作業ディレクトリで動作する可能性があるため、`filepath.Abs` でパスを解決し、渡す前に存在を確認します。ディレクトリが見つからない場合、サブコマンドは警告を出してスキルなしで続行します。

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

## ステップ 3 — セッションにスキルを読み込む

解決したディレクトリを `SessionConfig.SkillDirectories` に渡します。`nil` スライスは単に追加スキルを読み込まないことを意味します。

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

## ステップ 4 — スキルの実行を観測し結果をストリーミングする

Copilot がスキルを呼び出すと `ToolExecutionStartData` イベントとして現れます。生成されたドキュメントは `AssistantMessageDeltaData` でストリーミングされます。

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

## サブコマンドの実行

デフォルトの `--skills-dir cmd/tutorial/skills` が正しく解決されるよう、`src/go` ディレクトリから実行します。

```bash
cd src/go
make build

# 同梱のスキルディレクトリを使用（デフォルト）
./dist/template-github-copilot-go tutorial skills-docgen

# 別のスキルディレクトリを指定
./dist/template-github-copilot-go tutorial skills-docgen --skills-dir /path/to/skills
```

### フラグ

| フラグ | 短縮形 | デフォルト | 説明 |
|--------|--------|------------|------|
| `--skills-dir` | `-s` | `cmd/tutorial/skills` | `SKILL.md` ファイルを含むスキルディレクトリのパス（カレントディレクトリ基準） |
| `--cli-url` | `-c` | _(空)_ | 任意の Copilot CLI サーバー URL（例: `localhost:3000`） |

> グローバルな `--verbose`/`-v` フラグはログレベルを `DEBUG` に下げ、クライアント接続モードとセッションのライフサイクルを表示します。

---

## 独自スキルの作成

スキルディレクトリの下に `SKILL.md` ファイルを持つ新しいフォルダを作成します。

```text
skills/
└── my-skill/
    └── SKILL.md
```

ペルソナと指示を Markdown で記述します。明確なタイトル、短い役割の説明、具体的なルールや例に絞って簡潔に保ちます。スキルが現在のタスクに関連するかどうかはランタイムが判断します。

---

## 次のステップ

- チュートリアル 5 — [監査ログ](05_audit_hooks.md): パーミッションポリシーでツール呼び出しを制御する
- チュートリアル 2 — [Issue トリアージボット](02_issue_triage.md): スキルとカスタムツールを組み合わせる
- [pkg.go.dev](https://pkg.go.dev/github.com/github/copilot-sdk/go) で Go API 全体を参照
