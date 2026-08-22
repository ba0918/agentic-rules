# agentic-rules

Normative rules for AI coding agents, packaged as [Agent Skills](https://agentskills.io).

Design principles, test discipline, information placement, human-readable output, commit
conventions and secret handling live here once, and are distributed to many projects and many
agents from this single repository.

This repository holds **domain rules only**. Workflow automation (procedures, orchestration)
belongs elsewhere and must not be depended on from here.

## Skills

| Skill | Scope | Routing |
|---|---|---|
| `ba0918-design` | Design principles, with testability as the supreme goal | `always` |
| `ba0918-placement` | Where each kind of information belongs: code / tests / commit logs / comments | `always` |
| `ba0918-readability` | Human-facing output that explains unfamiliar context without losing technical meaning | `always` |
| `ba0918-secrets` | Handling credentials and confidential material: detection, staging ban, exposure prevention, audience boundary for any wider-audience destination, third-party licence compliance in any destination, incident response | `always` |
| `ba0918-tdd` | Test-first contract (RED → GREEN → REFACTOR) | `required:implement` |
| `ba0918-commit` | Commit splitting and message conventions | `required:commit` |
| `ba0918-release` | Release discipline: canonical version, bump, breaking changes, changelog, tag | `required:release` |
| `ba0918-delegation` | Delegation discipline: orchestrator principle, five role contracts, executor table | `required:delegate` |
| `ba0918-verification` | Verification discipline: evidence demands, worst-of aggregation, hand-off hygiene | `required:review` |
| `ba0918-reuse` | Reuse-before-build: layer decomposition, an eight-rung search ladder, adopt-or-build records | `required:design` |
| `ba0918-testing` | Testing anti-patterns | fires from its description |
| `ba0918-scaffold` | Generates `AGENTS.md` / `PROJECT.md` for a consuming project | invoked explicitly |

Each skill directory is the unit of distribution and is self-contained: it never refers to a
path outside itself. Skills mention each other by name only.

`Routing` is the `metadata.ba0918-routing` field in each `SKILL.md`. `ba0918-scaffold` reads it
to generate a consuming project's routing table. Only two forms are valid: `always` and
`required:<trigger>`.

## Install

Three kinds of route are supported — plugin, package manager and copy. They differ in how
updates reach you, not in what you get. Claude Code, Codex CLI and OpenCode install by the
plugin route, each from the metadata already in this repository; APM installs by the
package-manager route; `gh skill` and `npx skills` install by the copy route.

### Claude Code (plugin marketplace)

Updates arrive when the plugin's version is bumped. The marketplace entry declares
`plugins[0].version`, and an installed copy follows that version rather than the latest commit,
so a change that leaves the version untouched does not reach it. Suited to a personal
environment.

```
/plugin marketplace add ba0918/agentic-rules
/plugin install ba0918-rules@agentic-rules
```

### Codex CLI (plugin marketplace)

Codex reads the same `.claude-plugin/marketplace.json`, and the skills appear to the model
under the plugin name, as `ba0918-rules:ba0918-design` and so on. Updates are bump-driven here
too, since the version is declared in that same manifest.

```
codex plugin marketplace add ba0918/agentic-rules
codex plugin add ba0918-rules@agentic-rules
```

Codex installs from the marketplace manifest alone; `.claude-plugin/plugin.json` is not
required by it. That file is kept because it is where the plugin's own identity — its version,
license and repository — is declared for the agents that read it.

### OpenCode (plugin)

Add the repository to `plugin` in `opencode.json` — either the project's or the global
`~/.config/opencode/opencode.json` — and restart OpenCode.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["agentic-rules@git+https://github.com/ba0918/agentic-rules.git"]
}
```

The repository is public, so the `git+https` form above is expected to work as written.

`.opencode/plugins/agentic-rules.js` registers `skills/` as a skill path and does nothing
else: the skills become loadable through OpenCode's native `skill` tool, and nothing is
injected into the session. `package.json` exists to make this repository installable by that
plugin route. It is a distribution manifest, not a published npm package — `private: true`
keeps it off the registry.

### APM (package manager)

[APM](https://github.com/microsoft/apm) manages skills and configuration for several AI
agents from one manifest, the way npm manages packages: installing adds one dependency line
to the project's `apm.yml`, `apm.lock.yaml` pins the resolved commit, and `apm update` moves
it forward. Suited to a project that provisions more than one agent from the same
declaration.

```
apm install ba0918/agentic-rules --target claude
apm install -g ba0918/agentic-rules
```

The first form installs into the project: for Claude Code the skills land in
`.claude/skills/`, while `--target opencode` and the other cross-tool targets (Copilot,
Cursor, Codex and others) place them in the shared `.agents/skills/`. The second form
installs into the user scope under `~/.apm/`. APM warns when a dependency is unpinned; pin a
commit SHA today, or a release tag (`ba0918/agentic-rules#v{version}`) once releases are
tagged.

This repository carries no APM-specific file: APM resolves a repository holding
`.claude-plugin/plugin.json` as a plugin collection and discovers `skills/` on its own. For
OpenCode alone the plugin route above is enough; APM earns its place when several agents are
managed from one manifest.

### Copy (`gh skill` / `npx skills`)

Skills are copied into the project at install time, and updates are pulled by running the
command again. Because `gh skill` can pin a commit or tag (`@<ref>`), this route suits
projects, teams and CI.

```
gh skill install ba0918/agentic-rules
npx skills add ba0918/agentic-rules
```

Pin a commit SHA when reproducibility matters, or a release tag (`v{version}`) once releases
are tagged. Changes that alter the meaning of a rule are recorded separately in
[CHANGELOG.md](CHANGELOG.md).

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
1024-character description limit, the routing value grammar, and the absence of references
escaping a skill directory. It does not check the marketplace manifest against `skills/`: the
manifest does not list the skills, because a plugin's skills load from the `skills/` directory
under its source by default.

It also checks that the repository names one version. The canonical one is `plugins[0].version`
in `.claude-plugin/marketplace.json`, and `.claude-plugin/plugin.json`, `package.json` and the
newest release heading of [CHANGELOG.md](CHANGELOG.md) are required to agree with it.

It exits 0 when it finds no violation, 1 when it reports at least one, and 2 when the path
given to it is not a directory.

`pytest` is the only development dependency. If it is not installed, `uv run --with pytest --
pytest` runs the suite without installing anything permanently.

CI additionally runs the reference validator from the Agent Skills project,
`npx skills-ref validate`, over every skill. It checks the published specification; the local
validator checks the conventions of this repository. Both must pass.
