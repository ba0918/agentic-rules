# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A change that alters the meaning of a rule — as opposed to rewording, reformatting or adding
examples — is a breaking change and is listed under `Changed` with a **BREAKING** marker.

## [Unreleased]

### Added

- `ba0918-scaffold` now generates a `CLAUDE.md` shim — a single `@AGENTS.md` line — when none
  exists, so the generated router is actually read by Claude Code. An existing equivalent
  reference is left untouched (idempotent), and any other existing `CLAUDE.md` gets a diff
  presented instead of an overwrite, the same gate as `AGENTS.md`.
- `ba0918-release` — release discipline: one canonical version location per project, a bump
  whenever a release carries a user-visible change, a change of meaning recorded as breaking, and
  the tag, the version heading and the comparison link issued as one operation.
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
