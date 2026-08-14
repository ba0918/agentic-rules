---
name: ba0918-scaffold
description: "Generate a project's AGENTS.md routing table and PROJECT.md skeleton from the rule skills actually installed, by reading each skill's ba0918-routing metadata instead of hand-maintaining the list, plus a one-line CLAUDE.md shim so Claude Code reads the router. Use only when the user explicitly requests this setup work itself — setting up agent instructions for a project, refreshing the routing table after installing or removing a rule skill, or splitting an overgrown AGENTS.md into a router plus project context. Never run it as a side effect of another task. 日本語キーワード: AGENTS.md PROJECT.md 生成 雛形 ルーティング表 セットアップ 初期化 スキャフォールド 指示ファイル"
---

# AGENTS.md, PROJECT.md and CLAUDE.md Scaffold

## Scope

Applies when a project needs agent instructions, or when its existing instructions have drifted
from the rule skills that are actually installed.

Runs only when the user explicitly requests this scaffolding work itself, never as a side effect
of another task. Being loaded as a candidate from its description is not permission to write
files. It writes at most three files and nothing else: `AGENTS.md`, a thin router pointing at
rule skills; `PROJECT.md`, the project-specific context that a router must not absorb; and
`CLAUDE.md`, a one-line shim (`@AGENTS.md`) that makes Claude Code read the router.

It does not author rules. Everything it writes about a rule comes from that rule's own metadata.

## Why the table is generated

A hand-written routing table decays silently. A skill gets installed and no row appears; a skill
is removed and a row points at nothing; a routing value changes and the table still shows the old
one. Reading the value from the installed skills makes the table a derived artifact, so drift
becomes impossible rather than merely discouraged.

## Procedure

### 1. Enumerate installed rule skills

List the skill directories your runtime loads from, and select the ones whose directory name
begins with `ba0918-`. Cover both scopes: the personal scope (for Claude Code, `~/.claude/skills/`
and installed plugin skill directories) and the project scope (`.claude/skills/` inside the
repository).

### 2. Read the routing metadata

For each selected skill, read the frontmatter and take `metadata.ba0918-routing`. Exactly three
cases exist:

| Value | Meaning | Row |
|---|---|---|
| `always` | applies regardless of the kind of work | goes in the always row |
| `required:<trigger>` | mandatory for one kind of work | goes in the `<trigger>` row |
| absent | fires from its own description | no row |

A value in any other form is a defect in that skill, not something to interpret. Leave such a
skill out of the table.

### 3. Generate AGENTS.md

Use `references/agents-template.md` as the skeleton. It has four parts in order: a short block of
universal principles, the generated routing table, a pointer to `PROJECT.md`, and nothing else.

Group `required:<trigger>` skills by trigger so each trigger is one row listing every skill it
requires.

### 4. Generate PROJECT.md when absent

If `PROJECT.md` does not exist, write the skeleton from `references/project-template.md` with the
headings present and the content left for a human to fill in. If it already exists, leave it
untouched.

### 5. Generate the CLAUDE.md shim

Claude Code reads `CLAUDE.md`, not `AGENTS.md`, so without a shim the generated router goes
unread there. If `CLAUDE.md` does not exist, write it containing the single line `@AGENTS.md`.
If it already contains an equivalent reference to `AGENTS.md`, do nothing — the step is
idempotent. Never overwrite any other existing `CLAUDE.md`: show the difference and let a human
apply it.

## Rules

- Derive every routing row from installed metadata. Never hand-write a row.
- Refer to skills by name. Never write a path to a skill directory.
- Do not overwrite an existing `AGENTS.md`. Show the difference and let a human apply it.
- Do not overwrite an existing `PROJECT.md`.
- Do not overwrite an existing `CLAUDE.md`. Leave one that already references `AGENTS.md`
  untouched; for any other content, show the difference and let a human apply it.
- Keep project-specific content out of `AGENTS.md`; it belongs in `PROJECT.md`.
- Report a skill whose routing value is malformed instead of guessing what was meant.
- Report which skill locations were searched, so an empty table can be distinguished from a failed search.

## Judgment

**Overwriting is the one irreversible move here.** An existing `AGENTS.md` usually carries
hand-written project decisions that no metadata can reconstruct. Present a diff and let a human
choose; regenerating in place destroys information the generator never had.

**Names travel; paths do not.** A skill directory sits at a different location on every
installation and under every runtime, so a generated file that names a path works only on the
machine that generated it. A name reference also degrades gracefully: where the skill is not
installed, the row simply goes unread instead of pointing at nothing.

**The router stays thin on purpose.** Every project-specific sentence added to `AGENTS.md` is a
sentence that must be re-read on every task and re-merged on every regeneration. `PROJECT.md`
exists so the router can be regenerated freely.

**An empty routing table is ambiguous.** It means either no rule skills are installed or the
search looked in the wrong place. Always state the locations searched so the reader can tell
which.

**The shim is the wiring that makes the router reachable from Claude Code.** Claude Code loads
`CLAUDE.md`, not `AGENTS.md`, so without the shim the generated router silently goes unread — the
scaffold appears to have worked while changing nothing. Asking a human to hand-write that one
line is exactly the manual wiring this skill exists to remove. The shim carries no content of its
own, so a `CLAUDE.md` that already reaches `AGENTS.md` needs nothing, and one carrying anything
else gets the same treatment as an existing `AGENTS.md`: a diff, not an overwrite.

**Skills without routing metadata are not omissions.** A skill that fires from its description is
deliberately outside the table. Adding it as a row would make it mandatory, which is a change of
meaning.

## Examples

Rows derived from metadata, and a row that cannot be:

```
Good: | Always | ba0918-design, ba0918-placement, ba0918-secrets |
      (three installed skills each declaring ba0918-routing: always)

Bad:  | Always | ba0918-design, ba0918-review |
      (ba0918-review is not installed; the row points at nothing)
```

A reference that survives installation, and one that does not:

```
Good: read the skill ba0918-tdd
Bad:  read ~/.claude/skills/ba0918-tdd/SKILL.md
```

## Evidence

Show these outputs rather than asserting the scaffold is correct.

- **Enumeration**: the directory listing of each skill location searched, showing the `ba0918-*`
  directories found.
- **Metadata basis**: for each generated row, the `ba0918-routing` line from that skill's
  frontmatter (for example `rg -n "ba0918-routing" <each skill directory>`).
- **Table agrees with reality**: the set of names in the generated table compared against the set
  of enumerated skills, with no name in one and not the other.
- **Nothing was overwritten**: `git status --short` showing `AGENTS.md` as added, or the diff that
  was presented for a human decision instead of applied.
- **Shim state**: the content of `CLAUDE.md` after the run — the created `@AGENTS.md` line, the
  pre-existing equivalent reference left untouched, or the diff presented instead of an
  overwrite.
