# AGENTS.md Skeleton

Copy the structure below. Replace each `{{...}}` marker. Delete nothing else, and add nothing
project-specific — that belongs in `PROJECT.md`.

Write the generated file in the language the project's own documentation uses.

---

```markdown
# Agent Instructions

## Core

- Serve the stated goal; do not widen the requested scope.
- Distinguish what is confirmed from what is inferred and what is unverified.
- After changing something, verify it by a means appropriate to the change.
- Do not perform irreversible, destructive, or externally visible actions without approval.
- Apply the project's own instructions where they are more specific than these.

## Rule Routing

| When | Read |
|---|---|
| Always | {{always_skills}} |
| {{trigger}} | {{required_skills_for_trigger}} |

Refer to each rule by its skill name. Read every rule that applies before starting the work it
governs.

## Project Context

Project-specific context — what this repository is, how to build and test it, and the
conventions that apply only here — lives in `PROJECT.md`. Read it before making changes.
```

---

## Marker reference

| Marker | Filled with |
|---|---|
| `{{always_skills}}` | comma-separated names of every installed skill declaring `ba0918-routing: always` |
| `{{trigger}}` | one trigger name taken from a `required:<trigger>` value |
| `{{required_skills_for_trigger}}` | comma-separated names of the skills requiring that trigger |

Emit one row per distinct trigger. When no skill declares a given form, omit that row rather
than leaving an empty cell.

## Constraints

- Names only. A filesystem path to a skill directory breaks on a different installation.
- No project-specific content in this file.
- Every row must be traceable to an installed skill's frontmatter.
