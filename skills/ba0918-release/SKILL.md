---
name: ba0918-release
description: "Release discipline — keeping the version in exactly one canonical location, bumping it whenever a release carries a user-visible change, marking a change of meaning as breaking, writing changelog entries that read without the session behind them, and issuing the tag, the version heading and the comparison link as one operation. Use when bumping a version, preparing or cutting a release, deciding whether a change is breaking, or adding a changelog entry. 日本語キーワード: リリース bump バージョン 版 タグ changelog 変更履歴 破壊的変更 配信"
metadata:
  ba0918-routing: required:release
---

# Release Discipline

## Scope

Applies to a release: choosing the next version, recording what changed, tagging it, and making
the change reach anyone who has already installed the project. It states the invariants a release
has to satisfy, whatever tool performs it.

It does not cover the command sequence of a particular package manager, registry or release tool.
Those are procedure and differ per project; this document specifies what has to be true before
the procedure runs and what has to be true after it.

Changelog entries and commit messages share one requirement — being readable without the session
that produced them. The skill `ba0918-commit` states it for commit messages, and the same standard
applies to every entry written here.

## Rules

- Keep the version in exactly one canonical location per project.
- Record where that location is in the project's specification or `PROJECT.md`. When no such
  record exists, decide the location and record it before releasing anything.
- Treat every other declaration of the project's own current version as a follower of the
  canonical one, and check their agreement mechanically.
- Where no mechanical version check exists, add one before relying on the declarations agreeing.
- Bump the canonical version in any release carrying a user-visible change: a rule, a feature, an
  install procedure, or the composition of what is distributed. Do not ship such a change with
  the version left standing.
- In the changelog, record a change that alters meaning separately from a compatible one, and
  mark it as breaking.
- Write the changelog entry when the change is made, under an unreleased section.
- Promote the unreleased section to a version heading at release time, and make that heading match
  the canonical version exactly.
- Write each entry so it reads without the conversation, the plan or the session behind it: what
  changed, and what that does to someone who has installed the project.
- Whatever a release issues — a tag, the version heading, a comparison link — issue them as one
  operation, leaving no state where one exists without the others.
- Never silence a version mismatch by deleting a declaration, loosening the check, or excluding a
  file from it.

## Judgment

**"User-visible" is about what the consumer receives, not about how much code moved.** A one-word
edit that changes what a rule instructs is visible. A test added for internal tooling is not. A
change to the install procedure is visible even when nothing inside the distributed artifact
changed. When it is unclear, ask whether someone holding only the distributed artifact could
notice the difference.

**Leaving the version standing is a decision not to ship.** Where a channel resolves an installed
copy by declared version rather than by latest commit, the bump is the delivery condition, not a
label attached after delivery. A change merged without a bump exists in the repository and nowhere
else. Treat the choice as what it is, and make it deliberately: either bump, or state that this
change is deliberately not being delivered yet.

**Exactly one canonical location is a design property, not a formatting preference.** If cutting a
release means editing the same number by hand in several files, the mismatch is already latent —
the manual step gets skipped in one of them eventually, and the release then declares two
different versions of itself. Declare it once, derive or verify the rest.

**For a rule aimed at an agent, a change of meaning is a change of instructed behaviour.**
Rewording, reformatting and adding an example leave the instruction intact. A change that makes an
agent act differently from before does not, however small the diff. That distinction, not the size
of the change, decides how far the version moves, in whatever scheme the project follows.

**Split the release when the unreleased entries span unrelated concerns.** A version heading is
the unit a consumer reads to decide whether to upgrade and what to re-check. When it mixes an
unrelated set of changes, that decision gets harder to make from the heading alone, and a later
revert of one part has to take the unrelated part with it.

**A failing version check reports the state of the repository; it is not an obstacle inside it.**
There are two honest ways out: correct the versions so the declarations agree, or reconsider the
change. Removing the declaration, loosening the check or excluding the file removes the report and
keeps the mismatch, and the next release then ships from a state nothing is checking.

## Examples

Version declarations kept in step by hand, and declarations that cannot drift apart:

```
Bad:  manifest A: version 1.4.0    # edited by hand
      manifest B: version 1.3.0    # the same edit, forgotten
Good: manifest A: version 1.4.0    # canonical, recorded in the project spec
      manifest B: follows the canonical value; a check fails on disagreement
```

An entry that needs the session to be understood, and one that stands alone:

```
Bad:  - Fixed the point raised in review and updated the rule.
Good: - **BREAKING** The naming rule now rejects an empty value instead of
        substituting a default. A project relying on the substitution has to
        supply the value explicitly before upgrading.
```

A release left half-issued, and a release issued as one operation:

```
Bad:  tag v<N> pushed; the changelog still says Unreleased; no comparison link
Good: one commit promoting the unreleased section to the v<N> heading and adding
      the v<N> comparison link, with the tag pointing at that commit
```

## Evidence

Show these outputs rather than asserting the release is consistent.

- **The canonical location is recorded**: the line of the project's specification or `PROJECT.md`
  that names it, quoted.
- **The bump happened**: `git show <the bump commit> -- <the canonical file>`, with the old and
  the new value both visible. Where the version is derived from the tag rather than declared,
  the tag creation itself is that evidence.
- **Every declaration agrees**: the project's version check, run after the bump, reporting no
  mismatch.
- **The release is one operation**: `git show <tag>`, containing the version heading and the
  comparison link in the commit the tag points at.
- **The entry stands alone**: the released section as it reads at the tag
  (`git show <tag>:<the changelog file>`), each line naming what changed and what it does to a
  project that has installed this one.
