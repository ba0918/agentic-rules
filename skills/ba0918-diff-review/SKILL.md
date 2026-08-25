---
name: ba0918-diff-review
description: "Presenting a set of changes for human review — grouping them by the intent behind them rather than by file, carrying the reason and the points that need judgment with each group, rendering them where differences are legible instead of pasting them into the conversation, and naming the reviewed bytes as the approval target. Use when asking a person to review, approve, or reject changes, whether a working diff, a draft awaiting approval, or a proposed revision. 日本語キーワード: 差分 diff レビュー 提示 承認 変更点 変更意図 レビュー依頼 草稿 見せ方 まとめ方"
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
  The diff already says what changed; only the author knows why.
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

## Evidence

Judge the presentation by what the reviewer can do with it, not by its appearance:

- The reviewer can name which group they object to, and why, without reading every line.
- Each group states a reason that the diff itself does not contain.
- The author's own assumptions are visible as assumptions, distinguishable from what was agreed.
- The rendered changes match the underlying bytes exactly; any omission is declared and locatable.
- What is being approved is identified by path and content identity, and the identity of what was
  read matches the identity of what is accepted.
- The review surface remains usable after the conversation ends, without a specific vendor,
  account, or network service.
