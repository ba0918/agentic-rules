---
name: ba0918-documents
description: "Document discipline for a repository's hand-written documents — one tree of document kinds, a search before creating, one topic per file and one home per fact, a lifetime for every kind, and pruning so that stale documents never pass for current fact. Use when creating a document file or deciding whether to create one, moving, renaming or deleting documents, reorganising a docs directory, or auditing documents for stale or leftover ones. 日本語キーワード: ドキュメント 文書 配置 置き場所 docs ディレクトリ構成 仕様 アーキテクチャ ADR 決定記録 実装計画 メモ 剪定 古い情報 棚卸し"
metadata:
  ba0918-routing: required:document
---

# Document Discipline

## Scope

Applies to every hand-written document file a repository tracks, whoever writes it: a person,
an agent asked to, or an agent recording what it found or decided. It covers which kinds of
document exist and where each lives, when a document may be created and how much it holds, how
long each kind lives and how it is pruned, its minimal format, and how readers find it.

It does not cover the conventional files at the repository root (README, CHANGELOG, LICENSE,
CONTRIBUTING, agent instruction files), a package's own README, documents generated from code,
or skill files. How clearly a document reads is the subject of the skill `ba0918-readability`;
what goes in a comment, a test name or a commit message is the subject of the skill
`ba0918-placement`; keeping secrets and machine-specific details out of documents is the subject
of the skill `ba0918-secrets`; skill files are the subject of the skill `ba0918-skill-authoring`.

## Rules

### Kinds and location

Unless the project declares otherwise, documents live in this tree:

```
docs/
  README.md        entry point: the role of each directory, and the documents that are current
  spec/            specification: what the system must do
  architecture/    current structure: overview, data model, API
  decision/
    adr/           settled decisions, one decision per file
    records/       discussions and explorations, one session per file
  plans/           implementation plans, one plan per file
  guides/          how-to guides people follow step by step
  notes/           findings worth sharing that do not yet belong to another kind
.agents/           session-local working notes; ignored, never committed
```

- Put every document in exactly one of these kinds.
- When a document fits none of them, do not create a new directory on your own judgment. Ask.
  If you cannot ask, put it in `notes/` and say so in the report.
- Adding a kind is a project decision. When one is added, describe its role in the entry point.
- When the project's own documentation, or the configuration of a tool that checks or generates
  documents, declares another location for a kind, the declared location wins. The lifetime,
  format and navigation rules below still apply there.
- Create a kind's directory when its first document is written. Do not lay out empty directories
  ahead of need.
- Below a kind, use at most one level of subdirectories, by topic or module.
- Keep structural documents — architecture, table layout, API — in `architecture/`, not in
  `notes/` and not in a root-level architecture file beside it.

### Creating and sizing

- Before creating a document, search for an existing one on the same topic. If one exists,
  extend or rewrite it. Never hold one topic in two documents.
- Give each document one topic: an ADR one decision, a plan one branch of work, a record one
  discussion.
- Do not turn into a document what ends with the conversation: working lists, logs of attempts,
  summaries of the session. Keep them in `.agents/` if the session needs them.
- Do not write in a document what code, tests, a commit message or a comment can carry.
- Do not copy content from another document or from code; link to it. Where a machine-readable
  source exists — a schema, migrations, an API definition file — it is the authority: describe
  the overall shape and the reasons, and link to it.

### Lifetime and pruning

| Lifetime | Kinds | Handling |
|---|---|---|
| Current | spec, architecture, guides, entry point | States present fact only. Rewritten when reality changes. No change-history section; history is in version control |
| Record | adr, records | A record of its time. Its content is never rewritten; when a later decision overturns it, add only its new status and a link to what overturned it |
| Expiring | plans, notes | A plan is deleted once its branch is merged or abandoned. A note is promoted into another kind, or deleted once it has served its purpose |

- When a change makes a document false, correct or delete that document in the same change.
  Before the change, search the documents for the behaviour, names and structure it alters.
- When recording a new decision, search for older records of the same decision or mechanism, and
  in the same change mark each one it overturns, with a link to the new one.
- Do not read records — ADRs, discussion records — as evidence of current behaviour. Current fact
  is in the code, the tests and the current documents; where a record and a current document
  disagree, the current document wins.
- Delete a retired document; do not move it into an archive directory (`archive/`, `old/`,
  `deprecated/`). Version-control history is the archive, and an archived file is still found by
  every search.
- When a document you are reading disagrees with reality, do not rely on it. Fix it if that is
  within your task; otherwise report which document, which passage, and what it contradicts.
- Keep every expiring document tied to work in progress. An audit lists each plan and note with
  no such work, and deletes it or asks its owner.

### Format

- For a kind whose format a tool defines, follow the tool's format. Add nothing on top of it.
- Otherwise, open with a heading that names the document, followed by one or two sentences
  stating what it is.
- Name files in lowercase words joined by hyphens, after their topic. Prefix the date as
  `YYYY-MM-DD-` only for kinds where the date means something, such as discussion records;
  prefix a sequence number for numbered kinds such as ADRs.
- Write in the language the project uses for its documents.
- Do not put a "last updated" line or a "previously, …" passage in a current document.
- Do not put implementation-status notes — "implemented", "not yet", "planned" — in a current
  document. Status changes and the note does not; the code and the plans carry status.

### Navigation

- Make `docs/README.md` the entry point: the role of each directory and the documents that are
  current.
- When a directory is added, or a document the entry point lists is added or removed, update the
  entry point in the same change.
- Link documents to each other with relative links: an ADR to the record it came from, a plan to
  the specification it implements.
- Make the entry point reachable in one step from the project context agents always read.

## Judgment

**A wrong document is worse than none.** Nothing checks a document against the code. A stale one
is read later as present fact, and the reader — person or agent — builds on a premise that is no
longer true. Pruning exists to keep what remains true; a single tree and a lifetime per kind are
what make that pruning possible to check.

**Documents go stale when code changes, not when documents are written.** That is why pruning is
part of the change that alters behaviour, and why a record is never read as the current state.

**Do not scaffold a whole tree for a small project.** Each kind's directory appears with its
first document. A project with two documents has two directories at most.

**Pruning keeps documents correct; it is not a deletion drive.** Do not delete a document that is
correct and still read just because it is old.

**Outside your task, report rather than delete.** Deletion can be undone in version control, but
deleting another person's document outside the task can break their work in progress. Report a
stale document you come across outside your task. When you are asked for an audit, the audit is
the task.

## Examples

A new directory for each session's findings, and the same findings placed by kind:

```
Bad:   docs/investigation/cache.md
       docs/memo-2026-10/cache-notes.md
       docs/cache-notes-v2.md

Good:  docs/notes/cache-eviction.md            (one topic, extended in place)
```

An API reference copied into a document, and the document pointing at its source:

```
Bad:   architecture/api.md restates every endpoint, parameter and status code from the
       API definition file, and drifts from it after the next change.

Good:  architecture/api.md describes how the API is grouped and why, and links to the
       API definition file for every endpoint.
```

A finished plan kept, and a finished plan removed:

```
Bad:   git mv docs/plans/cache-eviction.md docs/plans/done/

Good:  git rm docs/plans/cache-eviction.md     (in the change that completes the work)
```

## Evidence

Show these outputs rather than asserting the documents are in order.

- **Placement**: `git status` showing each created or moved document inside the tree or the
  declared location.
- **Search before creating**: the search command run for the topic and its result.
- **Pruning in the change**: for a change that alters behaviour, names or structure, the search
  of the documents for what it alters, and the diff of each document corrected or deleted — or the
  search result showing none.
- **Navigation**: the diff of the entry point whenever a directory was added.
