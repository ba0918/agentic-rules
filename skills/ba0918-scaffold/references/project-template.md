# PROJECT.md Skeleton

Generate this file only when the project has none. Emit the headings with brief guidance and
leave the substance for a human to fill in — the generator does not know this project.

Write the generated file in the language the project's own documentation uses.

---

```markdown
# Project Context

## What this is

One paragraph: what the project does and who uses it. Not a feature list.

## Stack and layout

The languages, frameworks and services in use, and where the significant directories are.

## Commands

| Purpose | Command |
|---|---|
| Install | |
| Build | |
| Test | |
| Lint | |
| Run locally | |

## Conventions specific to this project

Only what differs from the general rules referenced in `AGENTS.md`. If a convention would apply
to any project, it does not belong here.

## Constraints

Compatibility requirements, performance budgets, regulatory limits, and anything that makes an
obvious approach wrong here.

## Glossary

Domain terms whose meaning in this project differs from ordinary usage.
```

---

## Constraints

- Leave the sections empty rather than guessing. An invented convention is worse than a blank
  heading, because it is read as decided.
- Keep general engineering rules out of this file; they arrive through the routing table in
  `AGENTS.md`.
