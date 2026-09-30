---
name: ba0918-worktree
description: "Worktree discipline for version-control worktrees shared by people, agents and tools — one declared location per repository, names that map to a branch and a task, one writer per working tree, and a lifecycle that ends with the work delivered and the worktree removed. Use when creating a worktree, deciding whether to create one, assigning working directories to parallel writers or agents, entering an existing worktree, or cleaning up or auditing leftover worktrees. 日本語キーワード: ワークツリー worktree git worktree 作業ツリー 並行作業 並列エージェント 作業場所 置き場所 後片付け 削除 棚卸し"
metadata:
  ba0918-routing: required:worktree
---

# Worktree Discipline

## Scope

Applies to every version-control worktree — a separate working directory attached to the same
repository on its own branch — whoever creates it: a person asking an agent, an agent on its own
initiative, or a tool that creates one automatically to run work in parallel. It covers where a
worktree lives, how it is named and based, what it isolates, and how it ends.

It does not cover how to configure a particular tool, nor scripts or hooks that automate
creating and removing worktrees. How commits inside a worktree are split and worded is the
subject of the skill `ba0918-commit`; how work is handed to another agent is the subject of the
skill `ba0918-delegation`; keeping machine-specific paths and neighbouring clones out of shared
text is the subject of the skill `ba0918-secrets`.

## Rules

### Location

- Keep all worktrees of a repository in one directory.
- Use `.agents/worktrees/` at the repository root unless the project's own documentation
  declares another location; a declared location wins.
- Exclude that directory in the repository's ignore file. Do not widen the exclusion to the
  whole `.agents/` directory for its sake — tools may keep tracked files elsewhere under
  `.agents/`. A project that already ignores all of `.agents/` on purpose is covered as it is.
- Exclude it as well from tools that do not read the ignore file: type checkers, test runners,
  file watchers.
- When a tool's default location differs, configure the tool to use the declared one. A
  worktree created where the tool cannot be configured still follows every other rule here.
- Never create a worktree inside another worktree.

### Name and base

- Tie each worktree to one branch and one task.
- Derive the worktree's directory name from its branch name, so that one maps to the other by
  replacing separators alone.
- Name the task. Do not keep a name a tool generated — random words, a counter, a bare tool
  prefix. The branch naming scheme itself is the project's convention.
- Choose the base explicitly. By default, branch from the remote base branch as freshly fetched.
  When branching from unpushed work instead, say so in the report.
- Do not reuse a finished task's worktree for a new task; create a new one.

### Isolation

- Give each concurrent writer its own working tree. The main checkout counts as one.
- Never let two writers write in the same worktree at the same time.
- From a worktree, do not modify files in the main checkout or in another worktree.
- Do not create a worktree for read-only investigation.
- Treat a worktree as a fresh checkout: install dependencies inside it, copy in only the ignored
  configuration files it needs, and share no written resource — build output directory, local
  database, listening port — with another worktree.
- Never release a lock on a worktree that another party placed.

### Ending

- Deliver the work out of the worktree before finishing: commit it and push it to the remote.
  If it is not pushed, report why and name the branch. Work that exists only inside a worktree
  is not complete.
- Remove a worktree once its branch is merged or abandoned.
- Remove it with the version control's own worktree removal, not by deleting the directory.
  If a directory was deleted directly, clean up the registration it left behind the same way.
- Never force-remove a worktree holding uncommitted changes or unpushed commits without
  approval, and never delete an unmerged branch without approval. Neither can be undone.
- Treat the version control's worktree list as the ledger: every entry corresponds to a task in
  progress. Remove an entry with no such task by the steps above, or ask its owner.

### Referring to a worktree

- Refer to a worktree by its path relative to the repository root, or by its branch name. Keep
  its absolute path out of tracked files, commit messages and outward-bound text.

## Judgment

**A worktree is for parallel work, not an end in itself.** When one writer works alone, the main
checkout is the working tree and no worktree is needed. The rules exist so that writers who do
run side by side cannot trample each other and leave nothing behind.

**An environment that already isolates each session needs no second layer.** When the runtime
hands every session a disposable clone of its own, that clone is already the unit of isolation.
Create worktrees inside it only when it in turn needs parallel writers.

**A tool's automation does not change the ending.** Where a tool creates and removes worktrees
on its own, meet the location and naming rules as far as its configuration allows. Delivering
the work before finishing, and not force-removing unpushed work without approval, hold whether
a person, an agent or the tool performs the removal.

**One location is what makes the rest checkable.** Scattered worktrees cannot be audited: no one
can tell which exist, which are live, or which hold the only copy of some work. A single declared
directory, together with the worktree list as ledger, turns "is anything left behind" into a
listing anyone can read.

**Inside the repository, under a tool-neutral name.** A location named after one tool is
arbitrary for every agent that does not use that tool. A location beside the repository fills the
parent directory with branch names indistinguishable from other clones, and a listing of that
parent is itself something that should not be copied into shared text. Inside the repository the
worktrees are found with it and removed with it; the price is excluding them from tools that
ignore the ignore file, which is why that exclusion is a rule.

**Deleting the directory is not removal.** The version control keeps its own record of every
worktree. A directory deleted underneath it leaves a registration that points nowhere and still
blocks its branch from being checked out elsewhere.

## Examples

Where a worktree goes:

```
Bad:  myrepo-fix-login next to myrepo   (beside the repository, in its parent)
Bad:  <tool-specific-dir>/worktrees/bright-running-fox
Good: .agents/worktrees/fix-login    (branch fix/login)
```

Ignoring the location:

```
Bad:  .agents/
Good: .agents/worktrees/
```

Sharing state between worktrees:

```
Bad:  link the worktree's dependency directory to the main checkout's copy
      (an install in one silently changes the other)
Good: install dependencies inside the worktree
```

Ending a task:

```
Bad:  delete the worktree directory; report "done"
Good: push the branch; after the merge, remove the worktree with the version
      control's removal and confirm it no longer appears in the worktree list
```

## Evidence

Show these outputs rather than asserting the worktrees are in order.

- **The ledger**: the version control's worktree list before creating and after removing, every
  entry under the declared location and tied to a live task.
- **The location is ignored**: the ignore check naming the rule that excludes the worktree
  directory.
- **Nothing lost on removal**: before removing, the worktree's status showing no uncommitted
  changes and its branch showing no commits missing from the remote.
- **The work left the worktree**: the pushed branch on the remote, or the report naming the
  branch and why it was not pushed.
