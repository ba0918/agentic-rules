# agentic-rules

Normative rules for AI coding agents, packaged as [Agent Skills](https://agentskills.io).

Design principles, test discipline, information placement, commit conventions and secret
handling live here once, and are distributed to many projects and many agents from this
single repository.

This repository holds **domain rules only**. Workflow automation (procedures, orchestration)
belongs elsewhere and must not be depended on from here.

## Skills

| Skill | Scope | Routing |
|---|---|---|
| `ba0918-design` | Design principles, with testability as the supreme goal | `always` |
| `ba0918-placement` | Where each kind of information belongs: code / tests / commit logs / comments | `always` |
| `ba0918-secrets` | Handling credentials: detection, staging ban, exposure prevention, incident response | `always` |
| `ba0918-tdd` | Test-first contract (RED → GREEN → REFACTOR) | `required:implement` |
| `ba0918-commit` | Commit splitting and message conventions | `required:commit` |
| `ba0918-testing` | Testing anti-patterns | fires from its description |
| `ba0918-scaffold` | Generates `AGENTS.md` / `PROJECT.md` for a consuming project | invoked explicitly |

Each skill directory is the unit of distribution and is self-contained: it never refers to a
path outside itself. Skills mention each other by name only.

`Routing` is the `metadata.ba0918-routing` field in each `SKILL.md`. `ba0918-scaffold` reads it
to generate a consuming project's routing table. Only two forms are valid: `always` and
`required:<trigger>`.

## Install

Two routes are supported. They differ in how updates reach you, not in what you get.

### Marketplace (Claude Code plugin)

Updates arrive automatically. Suited to a personal environment.

```
/plugin marketplace add ba0918/agentic-rules
/plugin install ba0918-rules@agentic-rules
```

### Copy (`gh skill` / `npx skills`)

Skills are copied into the project at install time, and updates are pulled by running the
command again. Because a tag can be pinned, this route suits projects, teams and CI.

```
gh skill install ba0918/agentic-rules
npx skills add ba0918/agentic-rules
```

Pin a release tag when reproducibility matters. Releases are tagged, and changes that alter
the meaning of a rule are recorded separately in [CHANGELOG.md](CHANGELOG.md).

## Naming

Skill names are `ba0918-<domain noun>`. `ba0918` is the owner's user ID, used purely to avoid
collisions in a flat global skill namespace, and never changes. The domain noun is one or two
short common words. Names are lowercase alphanumerics and hyphens, at most 64 characters, and
match the directory name.

## Skill document structure

Every `SKILL.md` presents Scope, Rules, Judgment, Examples and Evidence in that relative order,
and the conventions governing them are defined in
[docs/spec/repository-design.md](docs/spec/repository-design.md). Section order is a review
concern; the validator does not check it.

## Verification

```
python3 scripts/validate.py          # repository-specific rules
pytest                               # tests for the validator itself
```

`scripts/validate.py` uses the Python 3 standard library only — there is nothing to install to
run it. It checks frontmatter completeness, the naming convention, the 500-line limit, the
1024-character description limit, the routing value grammar, the absence of references escaping
a skill directory, and agreement between `.claude-plugin/marketplace.json` and the actual
contents of `skills/`.

It exits 0 when it finds no violation, 1 when it reports at least one, and 2 when the path
given to it is not a directory.

`pytest` is the only development dependency. If it is not installed, `uv run --with pytest --
pytest` runs the suite without installing anything permanently.

CI additionally runs the reference validator from the Agent Skills project,
`npx skills-ref validate`, over every skill. It checks the published specification; the local
validator checks the conventions of this repository. Both must pass.
