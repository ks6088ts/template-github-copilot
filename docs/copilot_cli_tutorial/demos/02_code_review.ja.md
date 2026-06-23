# Demo 2 · AI コードレビュー

**テーマ:** 品質。**時間:** 約 20 分。
**機能:** 組み込みの **Code review** エージェント、`@` ファイル参照、ローカル変更とリモート PR のレビュー。

> **これまで:** [Demo 1](01_issue_to_pr.md) で `feature/reset-button` ブランチに **Reset ボタン** を追加する PR を開きました。**このデモ:** 人間が見る前に、その変更をレビューし、テストで堅牢にします。

人間のレビュアーが見る前に、変更に対するレビューを得ます。このワークショップでいう「ノイズが少ない」とは、スタイルの好みを避け、バグの可能性、セキュリティリスク、テスト不足、危険な API 利用に絞るという意味です（[Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)）。

---

## 前提条件

- [Demo 1](01_issue_to_pr.md) の `feature/reset-button` ブランチとその PR（あるいは未コミット／未プッシュの変更がある任意のブランチ）。
- 認証済み CLI。

---

## 手順

### 1. ブランチを `main` と比較してレビューする

フィーチャーブランチにいることを確認してから、クロスチェックを依頼します。ベストプラクティスガイドは複数モデルを要求できることを示しています。モデル名は短期間で変わるため、スライドや古いメモの名前をコピーするのではなく、`/model` で現在使えるモデルを 2 つ選んでください（[Best practices](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices)、[GPT-5.2 and GPT-5.2-Codex deprecated](https://github.blog/changelog/2026-06-05-gpt-5-2-and-gpt-5-2-codex-deprecated)）。

```text
> !git switch feature/reset-button
> /review Use two currently available models from /model to review the changes on this branch against `main`. Focus on real bugs, missing tests, and risky React/telemetry patterns — not style.
```

お使いのビルドで `/review` が使えない場合は、自然言語でエージェントを呼び出します。自動的に Code review エージェントへ委譲されます。

```text
> Review the Reset-button changes on this branch against main. Surface only real bugs, missing tests, and risky patterns. Skip style nitpicks.
```

### 2. レビューを特定のファイルに絞る

`@` でファイルをプロンプトに追加すると、Copilot はその正確な内容に基づいてレビューします（[Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)）。

```text
> Review @src/App.tsx and @src/telemetry/react/hooks.ts for the Reset-button change. Check for missing telemetry properties, unguarded state updates, and an accessible name/label on the new button.
```

### 3. リモートのプルリクエストをレビューする

Copilot は GitHub.com 上の PR の変更を確認し、重大な問題を報告できます（[About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)）。

```text
> Check the changes in my Reset-button PR on <your-username>/template-typescript-react. Report any serious errors you find in these changes.
```

### 4. 指摘を修正に変える

これはエージェントなので、同じセッションでレビュー結果に対処できます。そして、リポジトリ既存の Playwright パターン（`playwright/app.spec.ts`）を使って回帰テストでループを閉じます。

```text
> Fix the highest-severity issue you found. Then add a Playwright assertion in @playwright/app.spec.ts that clicks the Reset button and verifies the counter returns to "Count is 0". Run `pnpm test:e2e:playwright` and show me the diff.
```

### 5. 専用のセキュリティレビューコマンドを使う

セキュリティに絞った確認には、最近の CLI に experimental public preview として `/security-review` が追加されています。ローカル変更を分析し、深刻度と信頼度付きの高確度な指摘を返します。コマンドが見えない場合は experimental mode を有効にします（[Dedicated security review command](https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli)）。

```text
> /experimental on
> /security-review
```

---

## IDE のインラインレビューとの違い

```mermaid
graph LR
    subgraph CLI["Copilot CLI review"]
      A[Agentic: reads whole diff & related files] --> B[Low-noise, severity-ranked]
      B --> C[Can fix + add tests in the same session]
    end
    subgraph IDE["IDE inline review"]
      D[Visual, hunk-level] --> E[Great while authoring]
    end
```

CLI のレビューは **ゲート**（PR 前、または CI 内）として、IDE は **対話的な作成** に使います。両者は補完関係です。[Access Methods](../access_methods.md) を参照してください。

---

## 学んだこと

- Code review エージェントは、バグ、セキュリティ、テスト不足、危険な API 利用に絞るなど、明確なレビュー方針と組み合わせると使いやすい。
- `@` ファイル参照で、Reset 機能が触れたファイルにレビュー範囲を正確に絞れる。
- *リモート PR* をレビューし、その結果に即座に対処し、同じセッションで回帰テストを追加できる。

## さらに進める

- 同じプロンプトを CI の非対話ステップとして組み込み、このアプリへのすべての PR をレビューする（[Demo 4](04_cicd_automation.md) を参照）。
- このレビュー方針を [カスタムエージェント](06_custom_agents_skills.md) に符号化し、すべてのレビューに同じレンズを適用する。
- GitHub は GitHub.com 上の自動 PR レビューも提供しています — [About GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)。

次へ: [Demo 3 · コードベースのオンボーディング](03_onboarding.md)。
