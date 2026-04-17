# チュートリアル 4: スキルによるドキュメント生成

**スクリプト:** [`src/python/scripts/tutorials/04_skills_docgen.py`](https://github.com/ks6088ts/template-github-copilot/blob/main/src/python/scripts/tutorials/04_skills_docgen.py)

---

## 学べること

- エージェントスキルとは何か、カスタムツールとの違い
- `SKILL.md` ファイルの書き方
- `CopilotClientOptions` でスキルディレクトリを設定する方法
- スキルを使って docstring を自動生成する方法

---

## 前提条件

- `localhost:3000` で実行中の Copilot CLI サーバー
- `github-copilot-sdk` がインストール済み

---

## スキル vs カスタムツール

| | カスタムツール（`@define_tool`） | スキル（`SKILL.md`） |
|-|--------------------------------|---------------------|
| 定義 | Python 関数 | Markdown ドキュメント |
| ロジック | コード（Python） | 自然言語での指示 |
| 入出力 | Pydantic モデル | 非構造化テキスト |
| 適したユースケース | 構造化データ、API 呼び出し、DB クエリ | プロンプトエンジニアリング、再利用可能なエージェントペルソナ |

**スキル**はエージェントに**永続的な指示とコンテキスト**を与える Markdown ファイルです。サーバー起動時に読み込まれ、そのサーバー上のすべてのセッションで利用可能です。

---

## ステップ 1 — SKILL.md ファイルを書く

`skills/docgen/SKILL.md` を作成します:

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

良い SKILL.md の主要要素:

| 要素 | 目的 |
|------|------|
| **タイトル**（`# name`） | スキルの識別子 |
| **役割の説明** | エージェントがこのスキルで「誰」であるかを定義 |
| **指示** | エージェントへのステップバイステップのガイダンス |
| **出力フォーマット** | エージェントがレスポンスをフォーマットする方法 |
| **例**（オプション） | 具体的な入出力ペア |

---

## ステップ 2 — スキルディレクトリを設定する

スキルフォルダを含むディレクトリを `CopilotClientOptions` に渡します:

```python
from copilot import CopilotClient
from copilot.types import CopilotClientOptions

client = CopilotClient(
    options=CopilotClientOptions(
        cli_url="localhost:3000",
        skills_directory="/path/to/skills",
    )
)
await client.start()
```

期待されるレイアウト:

```
skills/
├── docgen/
│   └── SKILL.md          # ← 各スキルは独自のサブディレクトリに
└── coding-standards/
    └── SKILL.md
```

---

## ステップ 3 — プロンプトを通じてスキルを呼び出す

スキルを明示的に呼び出す必要はありません — エージェントにプロンプトを送ると、Copilot サーバーがリクエストに基づいて最も適切なスキルを選択します:

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

## このリポジトリのスキルディレクトリ

このリポジトリには 2 つのサンプルスキルが含まれています:

| スキル | ファイル | 目的 |
|--------|---------|------|
| `docgen` | `skills/docgen/SKILL.md` | Google スタイルの docstring を生成 |
| `coding-standards` | `skills/coding-standards/SKILL.md` | コードをチームの標準に照らしてチェック |

このディレクトリに独自のスキルを追加できます。

---

## スクリプトの実行

```bash
# デフォルトのスキルディレクトリ（./skills）を使用
python src/python/scripts/tutorials/04_skills_docgen.py

# カスタムスキルディレクトリ
python src/python/scripts/tutorials/04_skills_docgen.py --skills-dir /path/to/my/skills

# スキルなし（サーバーのみのプロンプティング）
python src/python/scripts/tutorials/04_skills_docgen.py --skills-dir /nonexistent
```

---

## まとめ

- スキルはエージェントに永続的な指示を与える Markdown ファイル（`SKILL.md`）
- 各スキルは `skills_directory` 配下の独自のサブディレクトリに配置される
- 起動時にスキルを読み込むために `CopilotClientOptions(skills_directory=...)` を設定する
- エージェントはタスクに基づいて最も関連するスキルを自動的に使用する
- スキルはカスタムツールを補完する — スキルは**どのように**振る舞うかを定義し、ツールは**何を**呼び出すかを提供する

---

## 次のチュートリアル

[チュートリアル 5: セッションフックによる監査ログ →](05_hooks_permissions.md)
