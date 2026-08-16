# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A change that alters the meaning of a rule — as opposed to rewording, reformatting or adding
examples — is a breaking change and is listed under `Changed` with a **BREAKING** marker.

## [Unreleased]

### Added

- `ba0918-secrets` — confidential context and third-party material as a second protected class
  alongside credentials: internal project and product names, internal hostnames, customer
  names, confidential document content, and unlicensed copyrighted works are kept out of
  public destinations (code, documentation, commit logs, issues, pull request text). The test
  is the destination's audience, not the value's shape; for third-party material the licence
  decides instead, in any destination. The leak-response section gains an information-leak
  variant where containment replaces revocation, taken per exposed surface — history rewritten
  across every affected commit, ref names, discussion titles, bodies and comments with their
  edit histories — each surface re-checked after the cleanup, since cleaning one never clears
  another. Evidence gains four checks that make the new class verifiable rather than asserted:
  outgoing text against a list of private identifiers held outside the working tree, a named
  source and audience comparison for document-derived passages (a paraphrase carries no name
  for a search to find), the licence and its attribution for each copy of third-party
  material, and the post-containment re-check of every exposed surface.

## [0.4.0] - 2026-08-16

### Added

- `ba0918-design` — a replaceability lens, framed as a facet of testability rather than a
  second principle: keep representations specific to a dependency or a storage mechanism
  inside their declared boundary; when changing a persisted format, test the chosen change
  path (compatible read, migration, or explicit rejection); never add an abstraction whose
  only justification is a future replacement. Judged by declared contracts and tested change
  paths, never by stated intent; evidence is scoped to the changed public surface of the
  diff at hand.
- `ba0918-reuse` — a conditional addition to the adoption record: when a newly adopted
  dependency fixes a persisted format or a public contract, the record states what it fixes.
  No unconditional boilerplate line; fixation by self-built parts stays with the boundary
  rules of `ba0918-design`.

## [0.3.0] - 2026-08-15

### Added

- `ba0918-reuse` — reuse-before-build discipline: decomposition of a task into
  independently decidable layers before any implementation approach is chosen, an
  eight-rung search ladder per layer — from questioning whether the layer is needed at
  all, through the codebase, the standard library, the platform, installed dependencies
  and not-yet-installed ecosystem staples, through a few lines written in place, down to
  minimal self-implementation — an adopt-or-build record with a one-line reason for
  every layer with no exemption for human-suggested technology, judgment of the record
  rather than the verdict, a project-set time limit on the search, and escalation to a
  human before any forced large self-implementation.

## [0.2.0] - 2026-08-14

### Added

- `ba0918-delegation` — delegation discipline: an orchestrator that delegates work instead of
  performing it, five fixed role contracts (orchestrator / implementer / investigator /
  reviewer / bulk-executor), self-contained delegation prompts, a take-home contract for
  results, and an executor table that binds roles to executors in the user's own environment —
  no model, vendor or price bindings inside the skill itself.
- `ba0918-verification` — verification discipline: observable evidence instead of completion
  claims, worst-of aggregation of review verdicts with a missing required reviewer recorded as
  UNVERIFIED, findings treated as data rather than authority, hand-off hygiene toward external
  systems (scoped diff only, credential scan, sealing delimiters), and narrow escalation
  conditions.
- `ba0918-scaffold` now generates a `CLAUDE.md` shim — a single `@AGENTS.md` line — when none
  exists, so the generated router is actually read by Claude Code. An existing equivalent
  reference is left untouched (idempotent), and any other existing `CLAUDE.md` gets a diff
  presented instead of an overwrite, the same gate as `AGENTS.md`.
- `ba0918-release` — release discipline: one canonical version location per project, a bump
  whenever a release carries a user-visible change, a change of meaning recorded as breaking, a
  tag issued for every release — created only after the project's checks pass, and issued with
  the version heading and the comparison link as one operation — and published tags never moved
  or reused: a published release is fixed by releasing a new version.
- APM ([microsoft/apm](https://github.com/microsoft/apm)) as an install route, documented in
  the README — APM resolves the `.claude-plugin/plugin.json` this repository already carries
  as a plugin collection and discovers `skills/` on its own, so no repository-side change was
  needed.
- Codex CLI as an install route — `.claude-plugin/plugin.json` declares the plugin's identity,
  and Codex installs from the marketplace manifest this repository already carried.
- OpenCode as an install route — `package.json` and `.opencode/plugins/agentic-rules.js`
  register `skills/` as a skill path. Nothing is injected into a session; the rules that apply
  at all times are delivered by the `AGENTS.md` that `ba0918-scaffold` generates.
- A version-sync check in `scripts/validate.py`. `plugins[0].version` in
  `.claude-plugin/marketplace.json` is the canonical version, and `.claude-plugin/plugin.json`,
  `package.json` and the newest release heading of this file are checked against it.

### Changed

- **BREAKING** — `ba0918-secrets`: revoking a leaked credential is now executed by a human, or
  by the agent only under explicit approval — the same gate as rewriting shared history.
  Reporting the leak becomes the first, blocking task, and external operations involving the
  affected credential stop while approval is pending. "Revoke first, clean history second"
  keeps its priority; only the actor changed.
- **BREAKING** — `ba0918-scaffold` runs only when the user explicitly requests the scaffolding
  work itself, never as a side effect of another task. Being loaded as a candidate from its
  description is not permission to write files; the description now states the same condition.
- The design spec's shared-source migration trigger became a staged clause: duplication between
  skills is accepted (self-containment outranks deduplication), a validator sync check is added
  only if drift between copies causes real harm, and a shared source is reconsidered only if
  that fails. A new spec section requires file-writing procedural skills to run only on an
  explicit request.
- The version in `.claude-plugin/marketplace.json` moved from `metadata.version` to
  `plugins[0].version`, so the file names the version once. Declaring it there also decides how
  updates reach the plugin routes: an installed copy follows this version instead of the latest
  commit, so a user-visible change ships only once the version is bumped.

## [0.1.0] - 2026-08-13

### Added

- `ba0918-design` — design principles with testability as the supreme goal.
- `ba0918-placement` — the four quadrants of information placement.
- `ba0918-tdd` — the test-first contract.
- `ba0918-testing` — testing anti-patterns.
- `ba0918-commit` — commit splitting and message conventions.
- `ba0918-secrets` — credential detection, staging ban, exposure prevention, incident response.
- `ba0918-scaffold` — generation of `AGENTS.md` and `PROJECT.md` from installed rule skills.
- `scripts/validate.py` — validator for this repository's conventions, standard library only.
- `.claude-plugin/marketplace.json` — distribution metadata for the Claude Code plugin route.
- CI running the validator, the validator's tests, and `npx skills-ref validate`.

[Unreleased]: https://github.com/ba0918/agentic-rules/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/ba0918/agentic-rules/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ba0918/agentic-rules/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ba0918/agentic-rules/releases/tag/v0.2.0
