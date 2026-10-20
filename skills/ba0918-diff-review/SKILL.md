---
name: ba0918-diff-review
description: "Presenting a set of changes for human review — grouping them by the intent behind them rather than by file, carrying the reason and the points that need judgment with each group, explaining what each change does with diagrams, pseudocode, and examples so it can be judged without reading every line, rendering them where differences are legible instead of pasting them into the conversation, and naming the reviewed bytes as the approval target. Use when asking a person to review, approve, or reject changes, whether a working diff, a draft awaiting approval, or a proposed revision. 日本語キーワード: 差分 diff レビュー 提示 承認 変更点 変更意図 レビュー依頼 草稿 見せ方 まとめ方 説明 図解 疑似コード 仕様 計画"
metadata:
  ba0918-routing: required:diff-review
---

# Presenting Changes for Review

## Scope

Apply this rule whenever a person is asked to look at a set of changes and decide: approving a
draft, accepting a revision, reviewing work before it is committed or published. It governs how
the changes reach the reviewer and what accompanies them. Whether the change is correct, whether
a human decision is required at all, and how the surrounding prose reads are left to the rules
responsible for those judgments.

It does not apply to a change small enough to read where it is discussed. Two or three lines
belong inline; building a review surface for them adds ceremony without adding understanding.

## Rules

- Group changes by the intent behind them, not by the file they landed in. One group is one
  reason to change something, even when that reason touched several files, and a file touched
  for two reasons appears in two groups.
- Give every group the reason the change was made, not a restatement of what the lines show.
  The diff already shows which lines changed; only the author knows why.
- Explain what every group does — the behaviour, mechanism, or model it introduces — well enough
  that the reviewer can judge it without reading every line. Show structure and flow with a
  diagram, logic with pseudocode, and behaviour with concrete before-and-after examples, and define
  each term coined during the work before using it.
- Scale the explanation to the consequence, not to the size of the diff. A specification or a
  plan is reviewed once and decides what gets built: give it the fullest explanation, even when
  that makes the presentation long.
- Name, per group, what the reviewer should actually judge: a decision that could have gone
  another way, a value chosen without evidence, a name or number the author invented, a
  consequence the reviewer may not want.
- Mark what the author added on their own authority, separately from what was agreed. An
  assumption presented as an agreement cannot be reviewed.
- Order groups by consequence — what changes meaning first, what changes wording last — not by
  filename or by the order the edits happened.
- Render changes where they can be read as changes: removed and added lines distinguishable at a
  glance, enough surrounding context to place them, long lines scrolling inside their own
  container rather than forcing the whole surface sideways. Both light and dark viewing must be
  legible.
- Keep the rendering faithful. Never silently reorder, reword, or elide diff content; when
  something is omitted, say what and why, and point to where the complete version is.
- Check the explanation against the bytes before handing it over, unless the change has no
  structure or logic to show and the explanation is a sentence or two. Have a reader who has not
  seen the work restate the change from the explanation alone, then compare it with the diff:
  fix every misreading, every claim the diff does not support, and every change the explanation
  leaves out. When no such reader is available, say so.
- Do not paste a full diff into the conversation as the review surface, and never offer a summary
  as the thing being approved. The summary orients; the bytes are what is accepted.
- State the approval target explicitly: the path of each file and the content identity of the
  exact bytes being approved, so that what was read and what is accepted are provably the same.
- Prefer a surface the reviewer can open with their own tools and keep — a self-contained file
  that needs no network and no particular vendor. Publishing or hosting it is a separate,
  optional act that needs the reviewer's consent, never a precondition for reviewing.
- Ask for a decision once, for the whole set. Splitting one coherent change into a sequence of
  separate approvals produces assent by fatigue, not review.

## Judgment

**Grouping by file describes the edit; grouping by intent describes the change.** A reviewer
deciding whether to accept something needs to see each decision once, whole, with everything it
touched — not the same decision scattered across four files, nor four unrelated decisions
collapsed into one file's diff. When one group cannot be given a single reason, it is two
groups.

**The purpose of the surface is that disagreement remains possible.** A reviewer who cannot see
what was decided, or who is shown so much undifferentiated material that reading it is
impractical, has only one available answer. Approval obtained that way records nothing. Judge a
presentation by whether a reviewer could still reject one part of it for a stated reason.

**Restating lines and explaining the change are different acts.** A restatement repeats what
the diff already shows and adds nothing. An explanation gives what the diff cannot show at a
glance: the behaviour that results, how the parts fit together, the model behind a rule. A
reviewer handed only reasons and a diff has to rebuild the mechanism alone, and in a
specification or a plan that rebuilding is where a misreading slips through approval and becomes
the wrong thing built. The explanation is where the change is read; the bytes remain the evidence
and the thing accepted. Because the reviewer no longer reads every line, nobody else will notice
when the explanation and the bytes disagree, which is why the author checks them against each
other first.

**Fidelity outranks presentation.** Every improvement to legibility — grouping, ordering,
commentary, collapsing unchanged regions — is permitted only while the changes themselves stay
exactly what they are. A presentation that quietly improves the diff has replaced the artifact
being reviewed with a description of it.

**The reviewer's tools are theirs.** They may want the change in an editor, in a terminal, in a
browser, or beside another version entirely. Produce something that survives leaving the
conversation, and do not make a hosted or vendor-specific view the only way to see the work.

## Examples

Bad — file-shaped, no reason, approval aimed at a summary:

> Changed 3 files (+113 / -41).
>
> - `a.md`: updated sections 2, 5, 9
> - `b.md`: updated section 4
> - `c.py`: updated two functions
>
> Approve this summary and I will apply the changes.

Good — intent-shaped, reason and judgment points carried, bytes named as the target:

> **1. Stop asking for approval where a command decides the result** (+38 / −12, touches `a.md`,
> `b.md`, `c.py`)
> Approvals that carry no judgment train the reviewer to answer without reading, so the
> mechanical cases are removed from the approval path entirely.
> Look at: the retry limit of 3 — chosen with no evidence behind it.
>
> **2. Rename the frozen-test check** (+4 / −4, touches `c.py`) …
>
> Rendered for reading at `<path to the review file>`.
> Approving means accepting these bytes: `a.md` `sha256:…`, `b.md` `sha256:…`, `c.py`
> `sha256:…`.

Bad — a reason and a pointer, the mechanism left for the reviewer to rebuild from the diff:

> **1. Retry failed deliveries with backoff** (touches `delivery.md`)
> Fixed-interval retries overloaded endpoints during outages.
> Look at: the maximum of 8 attempts.

Good — the mechanism shown, so the reviewer can judge it without reading every line:

> **1. Retry failed deliveries with backoff** (touches `delivery.md`)
> Retrying every 60 s overloaded endpoints during outages. Waits now grow — 30 s, 60 s, 120 s, …,
> capped at one hour — and only timeouts, 5xx, 408 and 429 are retried. Anything else goes
> straight to a dead-letter queue, a queue nothing retries automatically.
>
> ```text
> delay(n) = min(30 s × 2^(n−1), 1 h) × jitter(0.8 to 1.2)
> wait     = Retry-After if the response is a 429 carrying it, else delay(n)
> ```
>
> | Response | Before | After |
> |---|---|---|
> | 503 | retried every 60 s, 3 times | backoff, up to 8 attempts |
> | 404 | retried every 60 s, 3 times | dead-letter at once |
>
> Look at: 8 attempts (about an hour of retrying) against 5 (about 8 minutes) — chosen without
> data behind it.

## Evidence

Judge the presentation by what the reviewer can do with it, not by its appearance:

- The reviewer can name which group they object to, and why, without reading every line.
- Each group states a reason that the diff itself does not contain.
- A reader who has not read the diff can say, from the presentation alone, what each group changes
  in behaviour and how; where a group has structure or logic, a diagram, pseudocode, or a concrete
  example shows it.
- The author's own assumptions are visible as assumptions, distinguishable from what was agreed.
- The rendered changes match the underlying bytes exactly; any omission is declared and locatable.
- Unless the change is exempt, a restatement written from the explanation alone and a
  comparison of the explanation with the diff, with the fixes that followed — or a statement that
  no such reader was available.
- What is being approved is identified by path and content identity, and the identity of what was
  read matches the identity of what is accepted.
- The review surface remains usable after the conversation ends, without a specific vendor,
  account, or network service.
