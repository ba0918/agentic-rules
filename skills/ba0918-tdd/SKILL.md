---
name: ba0918-tdd
description: "The test-first contract — no production code without a failing test, and the RED then GREEN then REFACTOR cycle with a shell test run required as the transition evidence for each phase. Use when starting an implementation, adding a behaviour, fixing a bug, or checking whether work in progress still satisfies test-first discipline. 日本語キーワード: TDD テスト駆動 テストファースト レッドグリーン リファクタ 実装 バグ修正"
metadata:
  ba0918-routing: required:implement
---

# Test-First Contract

## Scope

Applies to production code with behaviour: a function, a module, a bug fix, a new branch of
logic. It governs the order of work, not the quality of the resulting tests — that is a testing
concern — and not the structure of the code — that is a design concern.

It does not apply to natural-language artifacts (documentation, prompts, rule documents) or to
pure configuration with no behaviour of its own.

## The iron law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

If code was written before its test, delete it and implement again from the test. Do not keep it
for reference, do not adapt it while writing the test, do not read it.

## Rules

- Write the test before the code that satisfies it.
- Run the test in a shell and read the failure before writing any implementation.
- Confirm the failure is caused by the feature being absent, not by a typo in the test.
- Cover one behaviour per test, and name the test after that behaviour.
- Write only the code needed to pass the current test.
- Run the whole suite after implementing and confirm every test passes.
- Refactor only while the suite is green, and run it again afterwards.
- Do not add new behaviour during refactoring.
- Prefer real collaborators; introduce a test double only where a real one is impractical.
- Never declare a phase complete without the shell output of the run that proves it.

## The cycle

**RED — write a failing test.** One behaviour, named for what it guarantees. Run it. A
compilation error from referring to a type or function that does not exist yet is a valid RED. A
test that passes immediately is testing something that already works — fix the test.

**GREEN — the minimum implementation.** Write the least code that turns the test green. No
speculative abstraction, no implementing the next three requirements, no unrelated tidying along
the way. Run the whole suite; the new test passes and nothing else broke.

**REFACTOR — tidy with the suite green.** Remove duplication, improve names, separate mixed
responsibilities. Run the suite again.

## Judgment

**REFACTOR has an explicit exit for "nothing to change".** When there is no duplication to
remove, no name to improve, and no responsibility to separate, record what you examined and why
no change was warranted, then move on. Rearranging structure merely to have performed a refactor
adds risk for nothing.

**Recording that a phase happened is not recording what happened.** "RED confirmed" and
"REFACTOR done" are not acceptable. RED needs the failure kind and message; REFACTOR needs either
what changed or what made a change unnecessary.

**A test that is hard to write is design feedback.** When the setup dwarfs the assertion, or the
behaviour cannot be reached without a database or a live clock, the problem is the shape of the
code. Change the design rather than growing the harness.

**Detecting the test command is part of the cycle.** Use what the project already uses, taking the
marker file as the signal:

| Marker file | Test command |
|---|---|
| `package.json` with a `test` script | `npm test` (or `npx vitest` / `npx jest`) |
| `Cargo.toml` | `cargo test` |
| `go.mod` | `go test ./...` |
| `pyproject.toml`, `setup.py`, `pytest.ini` | `pytest` |
| `Makefile` with a `test` target | `make test` |

When detection is ambiguous, ask rather than inventing a command.

## Red flags

Each of these means the contract has already been broken:

- Production code changed before the test file did.
- GREEN declared without a test run in the transcript.
- One test asserting several unrelated behaviours.
- Refactoring started while a test is failing.
- "I will add the tests afterwards."
- The mock setup is longer than the logic under test.

## Examples

A RED that proves nothing, and one that proves the feature is absent:

```
Bad:  the new test passes on first run — it exercises behaviour that already existed

Good: FAILED test_rejects_expired_token - AttributeError: module has no attribute 'is_expired'
      (the failure names the missing function, so the test is pinned to the new behaviour)
```

A GREEN that overshoots, and one that stops at the test:

```
Bad:  the test needs expiry checking; the commit adds expiry, refresh, and revocation

Good: the test needs expiry checking; the commit adds expiry checking
```

## Evidence

Each phase transitions on shell output, not on assertion.

- **RED**: the test command output showing the new test failing, with the error kind and message
  quoted (a compile or import error naming the missing symbol counts).
- **GREEN**: the test command output showing 0 failures across the whole suite, not only the new
  test.
- **REFACTOR**: the test command output after the tidy-up, again 0 failures — or, when nothing
  was changed, a written statement of what was examined and why it needed no change.
- **Order**: `git log -p` or the working-tree diff showing the test file present before, or in
  the same commit as, the implementation it drove.
