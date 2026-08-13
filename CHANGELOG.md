# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A change that alters the meaning of a rule — as opposed to rewording, reformatting or adding
examples — is a breaking change and is listed under `Changed` with a **BREAKING** marker.

## [Unreleased]

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
