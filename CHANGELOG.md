# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A change that alters the meaning of a rule — as opposed to rewording, reformatting or adding
examples — is a breaking change and is listed under `Changed` with a **BREAKING** marker.

## [Unreleased]

### Added

- Codex CLI as an install route — `.claude-plugin/plugin.json` declares the plugin's identity,
  and Codex installs from the marketplace manifest this repository already carried.
- OpenCode as an install route — `package.json` and `.opencode/plugins/agentic-rules.js`
  register `skills/` as a skill path. Nothing is injected into a session; the rules that apply
  at all times are delivered by the `AGENTS.md` that `ba0918-scaffold` generates.
- A version-sync check in `scripts/validate.py`. `plugins[0].version` in
  `.claude-plugin/marketplace.json` is the canonical version, and `.claude-plugin/plugin.json`,
  `package.json` and the newest release heading of this file are checked against it.

### Changed

- The version in `.claude-plugin/marketplace.json` moved from `metadata.version` to
  `plugins[0].version`, so the file names the version once.

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
