---
name: ba0918-placement
description: "Where each kind of information belongs — code carries How, tests carry What, commit logs carry Why, and comments carry Why not. Use when writing or reviewing a comment, naming a test, wording a commit message, or deciding whether an explanation should live in code, in a test, in history, or in a comment at all. 日本語キーワード: 情報配置 コメント 命名 テスト名 コミットメッセージ ドキュメント 四象限 なぜ"
metadata:
  ba0918-routing: always
---

# Information Placement

## Scope

Applies whenever you are about to write prose about code: a comment, a test name, a commit
subject or body, or a docstring. It decides where a given piece of information belongs, not
whether the code itself is well structured.

## The four homes

| Home | Carries | The question it answers |
|---|---|---|
| Code | How | How is this implemented? |
| Tests | What | What does this do? |
| Commit logs | Why | Why was this change needed? |
| Comments | Why not | Why was the obvious alternative rejected? |

Each row is also a diagnostic. If the information cannot be read from its proper home, the home
itself is broken — see Judgment.

## Rules

- Express How in code. Do not restate the code in a comment.
- Name a test after the behaviour it pins down, not after the functions it calls.
- Write the motivation, the context, and the judgment in the commit message. Do not summarise the diff.
- Reserve comments for Why not: the constraint that makes the obvious alternative wrong.
- Delete a comment that says anything a reader would learn by reading the code.
- Do not put a mock name, an internal method name, or a private field name in a test name.
- Do not write `TODO: explain later`. Why not can only be recorded while you still know it.
- When you cannot state why the change was needed, split the commit until each part has one reason.

## Judgment

**A comment you feel compelled to write is usually a naming problem.** Before writing it, try to
make the code read the way the comment would. Only a constraint that code genuinely cannot
express — a rate limit, a compatibility requirement, an ordering dependency — earns a comment.

**A lying comment is worse than no comment.** Comments are not checked by anything, so a
transcription of the code becomes false the moment the code changes. That asymmetry is why the
Why-not quadrant is narrow on purpose.

**Test names that mention implementation break on refactoring.** When behaviour is unchanged but
the test name no longer matches, the name was describing How. Rewrite it as a sentence about
observable behaviour, so that reading the test list reads as a specification.

**A commit body that restates the diff loses the only thing the diff cannot show.** Six months
later, `git blame` answers what changed; nothing but the message answers why it had to change.
If you cannot state the why, the commit is bundling several concerns — split it.

**Comments are the only home Why not has.** A rejected alternative appears nowhere in the code,
the tests, or the diff. Unless the reason is written next to the code, the next reader will
"improve" the workaround back into the bug.

## Examples

A comment transcribing the code, and the name carrying it instead:

```
// Bad
// filter by user ID, then sort
const result = items.filter(i => i.userId === userId).sort(byCreatedAt);

// Good
const userItemsSortedByDate = items.filter(i => i.userId === userId).sort(byCreatedAt);
```

A test name describing How, and the same test describing What:

```
// Bad
test('calls repository.findByUserId and applies sortByCreatedAt', ...)

// Good
test("returns the user's items ordered from newest to oldest", ...)
```

A deliberate workaround with no reason recorded, and with one:

```
// Bad
for (const item of items) { await processOne(item); }

// Good
// Sequential on purpose: parallelising exceeds the external API rate limit of 10 req/s.
for (const item of items) { await processOne(item); }
```

A commit subject summarising the diff, and one carrying the reason:

```
Bad:  fix: change the conditional in validateInput

Good: fix: reject whitespace-only usernames at the boundary

      A username of only full-width spaces passed validation and broke
      rendering downstream. Trim before the emptiness check so the value
      is rejected where it enters the system.
```

## Evidence

Show these outputs rather than asserting the information is well placed.

- **Test names as a specification**: the test runner's verbose list for the changed module
  (for example `pytest -v`, `cargo test -- --list`), readable as behaviour statements without
  opening the test bodies.
- **No implementation leakage in test names**: a search over the changed test files for `mock`
  and for the internal symbol names touched by the change, returning no matches in test names.
- **Why in history**: `git log -1 --format=%B` for the commit, containing the motivation and not
  a restatement of the diff.
- **Comments are Why not only**: `git diff` filtered to added comment lines, each one naming a
  constraint that rejects an alternative.
