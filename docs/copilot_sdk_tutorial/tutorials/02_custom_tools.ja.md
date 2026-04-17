# チュートリアル 2: カスタムツールによる Issue トリアージボット

**スクリプト:** [`src/python/scripts/tutorials/02_issue_triage.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/02_issue_triage.py)

---

## 学べること

- `@define_tool` デコレータでカスタムツールを定義する方法
- Pydantic モデルをツールの入出力スキーマとして使う方法
- GitHub Issue を分類・ラベル付けするツール呼び出しエージェントの構築方法

---

## 前提条件

- `localhost:3000` で実行中の Copilot CLI サーバー
- `github-copilot-sdk` と `pydantic` がインストール済み

---

## カスタムツールとは？

カスタムツールを使うと、Copilot エージェントに独自の関数へのアクセスを与えられます。エージェントはツールの説明に基づいて、**いつ**呼び出すかを判断します。定義するもの:

1. ツールの**名前**と**説明**（LLM がいつ呼び出すかを判断するために使用）
2. **入力スキーマ**（Pydantic の `BaseModel`）
3. **出力スキーマ**（別の Pydantic の `BaseModel`）
4. **実装**（通常の Python 関数）

---

## ステップ 1 — 入出力スキーマの定義

```python
from pydantic import BaseModel

class ListIssuesInput(BaseModel):
    pass  # パラメータ不要

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

明確で型付けされたスキーマにより、LLM はどのデータを渡し、何を期待すればよいかを理解できます。

---

## ステップ 2 — `@define_tool` でツールを実装する

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
    # 実際のシナリオでは、ここで GitHub API を呼び出す
    return LabelIssueOutput(
        success=True,
        issue_id=input.issue_id,
        applied_labels=input.labels,
    )
```

> **ヒント:** 説明文字列は詳しく書きましょう。LLM はこれを基に各ツールをいつ呼び出すかを判断します。

---

## ステップ 3 — セッションにツールを登録する

```python
session = await client.create_session(
    SessionConfig(
        on_permission_request=approve_all,
        tools=[list_issues, label_issue],  # ← ここで登録
        streaming=False,
        system_message=SystemMessageReplaceConfig(
            content=(
                "You are an expert GitHub issue triage assistant. "
                "Use list_issues to fetch open issues, classify each one "
                "as 'bug', 'enhancement', or 'documentation', then call "
                "label_issue to apply the appropriate label."
            )
        ),
    )
)
```

`SystemMessageReplaceConfig` を使うと、デフォルトのシステムメッセージを**完全に置き換え**、エージェントに集中したペルソナを与えられます。

---

## ステップ 4 — タスクプロンプトを送信する

```python
reply = await session.send_and_wait(
    MessageOptions(prompt="Please triage all open issues and apply the appropriate labels."),
    timeout=300,
)
print(reply.data.content)
```

エージェントは以下を実行します:

1. `list_issues()` を呼び出して Issue を取得
2. 各 Issue を分析
3. 各 Issue に対して適切なラベルで `label_issue()` を呼び出す
4. サマリーを返す

---

## スクリプトの実行

```bash
python src/python/scripts/tutorials/02_issue_triage.py
python src/python/scripts/tutorials/02_issue_triage.py --cli-url localhost:3000
```

期待される出力:

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

## まとめ

- `@define_tool(name, description)` は関数を呼び出し可能なツールとして登録する
- Pydantic の `BaseModel` は強く型付けされた入出力コントラクトを定義する
- ツールは `SessionConfig(tools=[...])` でセッションごとに登録される
- LLM はタスクと説明文字列に基づいて**いつ**ツールを呼び出すかを判断する
- `SystemMessageReplaceConfig` はエージェントにタスク専用のペルソナを与える

---

## 次のチュートリアル

[チュートリアル 3: ストリーミングコードレビュー →](03_streaming.md)
