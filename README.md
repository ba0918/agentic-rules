# agentic-rules

English | [日本語](README-ja.md)

Normative rules for AI coding agents, packaged as [Agent Skills](https://agentskills.io).
Each rule is written once here and distributed to many projects and many agents from this
single repository.

This repository holds **domain rules only**. Workflow automation (procedures, orchestration)
belongs elsewhere and must not be depended on from here.

## Install

Pick the route that matches how you want updates to arrive. Every route delivers the same
skills.

| Route | Agents | How updates arrive | Suited to |
|---|---|---|---|
| Plugin | Claude Code, Codex CLI, OpenCode | When the version is bumped (see below) | Following each published release |
| Package manager | APM | `apm update`, from the commit pinned in `apm.lock.yaml` | Several agents provisioned from one manifest |
| Copy | `gh skill`, `npx skills` | Run the install command again | Projects, teams and CI that pin a revision |

An installed plugin follows the version declared in `.claude-plugin/marketplace.json`, not the
latest commit. A change reaches plugin users only in a release that bumps that version.

### Claude Code

```
/plugin marketplace add ba0918/agentic-rules
/plugin install ba0918-rules@agentic-rules
```

### Codex CLI

Codex reads the same marketplace manifest. The skills appear under the plugin name, as
`ba0918-rules:ba0918-design` and so on.

```
codex plugin marketplace add ba0918/agentic-rules
codex plugin add ba0918-rules@agentic-rules
```

### OpenCode

Add the repository to `plugin` in `opencode.json` — the project's or the global
`~/.config/opencode/opencode.json` — and restart OpenCode.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["agentic-rules@git+https://github.com/ba0918/agentic-rules.git"]
}
```

The plugin only registers `skills/` as a skill path. The skills load through OpenCode's own
`skill` tool, and nothing is injected into the session.

### APM

[APM](https://github.com/microsoft/apm) manages skills for several agents from one `apm.yml`,
the way npm manages packages.

```
apm install ba0918/agentic-rules --target claude
apm install -g ba0918/agentic-rules
```

The first form installs into the project: `.claude/skills/` for Claude Code, and the shared
`.agents/skills/` for `--target opencode` and the other cross-tool targets (Copilot, Cursor,
Codex and others). The second installs into the user scope under `~/.apm/`. Pin a release tag
(`ba0918/agentic-rules#v<version>`) or a commit SHA; APM warns about an unpinned dependency.

For OpenCode alone the plugin route is enough. APM earns its place when several agents are
managed from one manifest.

### Copy (`gh skill` / `npx skills`)

The skills are copied into the project at install time.

```
gh skill install ba0918/agentic-rules
npx skills add ba0918/agentic-rules
```

`gh skill` accepts `@<ref>`; pin a release tag (`v<version>`) or a commit SHA when
reproducibility matters.

Changes that alter the meaning of a rule are marked **BREAKING** in
[CHANGELOG.md](CHANGELOG.md).

## Skills

The skills are grouped below by the kind of work they govern. **Loaded by** says how an agent
comes to read each one.

### Always on

| Skill | Scope | Loaded by |
|---|---|---|
| [`ba0918-design`](skills/ba0918-design/SKILL.md) | Design principles, with testability as the supreme goal | `always` |
| [`ba0918-placement`](skills/ba0918-placement/SKILL.md) | Where each kind of information belongs: code, tests, commit logs or comments | `always` |
| [`ba0918-readability`](skills/ba0918-readability/SKILL.md) | Human-facing output that explains unfamiliar context without losing technical meaning | `always` |
| [`ba0918-secrets`](skills/ba0918-secrets/SKILL.md) | Credentials and confidential material: detection, staging ban, audience boundaries, third-party licences, incident response | `always` |

### Writing code

| Skill | Scope | Loaded by |
|---|---|---|
| [`ba0918-tdd`](skills/ba0918-tdd/SKILL.md) | Test-first contract (RED → GREEN → REFACTOR) | `required:implement` |
| [`ba0918-reuse`](skills/ba0918-reuse/SKILL.md) | Reuse before build: layer decomposition, an eight-rung search ladder, adopt-or-build records | `required:design` |
| [`ba0918-gui-structure`](skills/ba0918-gui-structure/SKILL.md) | GUI screen structure: components per region, one owner per piece of state, data down and events up, one dialog state | `required:gui` |
| [`ba0918-testing`](skills/ba0918-testing/SKILL.md) | Testing anti-patterns | its description |

### Delivering changes

| Skill | Scope | Loaded by |
|---|---|---|
| [`ba0918-commit`](skills/ba0918-commit/SKILL.md) | Commit splitting and message conventions | `required:commit` |
| [`ba0918-diff-review`](skills/ba0918-diff-review/SKILL.md) | Presenting changes for review: grouped by intent, with reasons and judgment points, the reviewed bytes named as the approval target | `required:diff-review` |
| [`ba0918-release`](skills/ba0918-release/SKILL.md) | Release discipline: canonical version, bump, breaking changes, changelog, tag | `required:release` |

### Working with other agents

| Skill | Scope | Loaded by |
|---|---|---|
| [`ba0918-delegation`](skills/ba0918-delegation/SKILL.md) | Delegation discipline: orchestrator principle, five role contracts, executor table | `required:delegate` |
| [`ba0918-verification`](skills/ba0918-verification/SKILL.md) | Verification discipline: evidence demands, worst-of aggregation, hand-off hygiene | `required:review` |

### Skills and project setup

| Skill | Scope | Loaded by |
|---|---|---|
| [`ba0918-skill-authoring`](skills/ba0918-skill-authoring/SKILL.md) | Writing a skill: scope, reading cost, runtime independence, descriptions that trigger, wording by rule kind | its description |
| [`ba0918-scaffold`](skills/ba0918-scaffold/SKILL.md) | Generates `AGENTS.md` / `PROJECT.md` for a consuming project | explicit request |

### How skills are loaded

`always` and `required:<trigger>` are the value of `metadata.ba0918-routing` in each
`SKILL.md`, and these are its only two valid forms. `ba0918-scaffold` reads them to generate a
consuming project's `AGENTS.md` routing table: `always` rules are read for every task, and a
`required:<trigger>` rule before the work its trigger names.

A skill without that field is not in the routing table. The agent loads it when the skill's
description matches the task, or when a person asks for it by name.

## Developing this repository

### Naming

Skill names are `ba0918-<domain noun>`. `ba0918` is the owner's user ID, used purely to avoid
collisions in a flat global skill namespace, and never changes. The domain noun is one or two
short common words. Names are lowercase alphanumerics and hyphens, at most 64 characters, and
match the directory name.

Each skill directory is the unit of distribution and is self-contained: it never refers to a
path outside itself. Skills mention each other by name only.

### Skill document structure

Every rule skill's `SKILL.md` presents Scope, Rules, Judgment, Examples and Evidence in that
relative order. The conventions governing them are defined in
[docs/spec/repository-design.md](docs/spec/repository-design.md), the authoritative design
spec. Section order is a review concern; the validator does not check it.

### Verification

```
python3 scripts/validate.py              # this repository's conventions
uv run --with pytest -- pytest tests/    # tests for the validator itself
```

`scripts/validate.py` uses the Python standard library only. It checks each skill's
frontmatter, its name, the 500-line limit, the 1024-character description limit and the
routing value, that no reference escapes a skill
directory, and that `.claude-plugin/plugin.json`, `package.json` and the newest release
heading of [CHANGELOG.md](CHANGELOG.md) agree with the canonical version,
`plugins[0].version` in `.claude-plugin/marketplace.json`. It exits 0 when nothing is wrong,
1 on a violation, and 2 when the path given to it is not a directory.

CI also runs the Agent Skills reference validator, `skills-ref validate`, over every skill,
installed from the Agent Skills repository at a pinned commit. It checks the published
specification, while the local validator checks this repository's conventions. Both must
pass.
