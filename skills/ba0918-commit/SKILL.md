---
name: ba0918-commit
description: "Commit conventions — splitting changes into one-concern units, staging files individually rather than adding everything, never staging secrets or scratch files, and writing a Conventional Commits message that reads as a standalone historical record without the conversation that produced it. Use when committing, staging, splitting a large change, or wording a commit subject or body. 日本語キーワード: コミット ステージング コミットメッセージ git add 分割 履歴 Conventional Commits"
metadata:
  ba0918-routing: required:commit
---

# Commit Conventions

## Scope

Applies to every commit, including ones you initiate yourself in the middle of other work — not
only when someone asks you to commit. It covers what goes into a commit and how the message is
worded.

What information belongs in a commit message versus a comment or a test name is covered by the
skill `ba0918-placement`; this document assumes that division and specifies the form.

## Rules

- Split a change into logical units. One concern per commit.
- Stage files individually. Do not run `git add -A` or `git add .`.
- Never stage secrets: environment files, keys, tokens, credentials.
- Never stage artifacts that are not the work product: logs, temporary files, caches, build output.
- Use the form `<type>: <subject>` with a Conventional Commits type.
- Add a body only when the reason needs explaining. Omit the footer by default.
- Write the message in the language the repository's history already uses; default to Japanese.
- Describe the resulting change and why it was needed.
- Do not describe the workflow that produced the change.

## Judgment

**The message is read without any of the context you have now.** No conversation, no plan
document, no agent session. Everything needed to understand the change has to be inside the
message or reachable from a stable reference.

**"Standalone" rules out four specific things**, each of which is invisible to a future reader:

- Phase or step labels from a process — a reader has no phase list.
- Agent or review chronology — "found during a review sweep", "per feedback" describe how the
  change was discovered, not what it is.
- References needing local or ephemeral context — gitignored paths, bare identifiers from a
  session. Spell the content out, or cite a stable reference such as an issue or PR number, a
  specification name, or an architectural concept.
- Generic subjects — "address feedback", "apply remaining changes" identify nothing.

**Being unable to state the why means the commit is not one concern.** When the reason comes out
as a list of unrelated motivations, split the commit until each part has a single one.

**Staging individually is a safety property, not a style preference.** Adding everything is how
credentials and scratch files reach history, and history is hard to correct after a push.

## Examples

A subject that summarises the diff, and one that carries the change:

```
Bad:  fix: change the conditional in validateInput
Good: fix: 空白のみのユーザー名を境界で弾く
```

A body describing the workflow, and one describing the reason:

```
Bad:  レビュー指摘 A8 に対応。第 2 期-3 の残作業。

Good: 全角スペースだけのユーザー名が検証を通過し、表示が崩れていた。
      入力の受け口で trim してから空判定するようにして、値が系に入る
      前に落とす。
```

Staging that risks history, and staging that does not:

```
Bad:  git add -A
Good: git add src/validators/username.ts tests/validators/username.test.ts
```

## Evidence

Show these outputs rather than asserting the commit is clean.

- **What is staged**: `git status --short` before committing, listing only the intended files.
- **Nothing unintended**: `git diff --cached --stat` showing no environment file, key, log, cache,
  or build artifact.
- **One concern**: `git diff --cached` reviewed as a whole, expressible as a single reason in one
  sentence.
- **The recorded message**: `git log -1 --format=%B` after committing, readable by someone who
  has never seen this session.
