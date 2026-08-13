---
name: ba0918-design
description: "Design principles that keep code mechanically verifiable — composing small parts, keeping logic out of glue code, unidirectional layering, pure domain boundaries, dependency injection, extension by addition, type-level verification, immutability, and security as structure. Use when designing a module, choosing an architecture, deciding where a responsibility belongs, or judging whether code can be tested at all. 日本語キーワード: 設計原則 設計 アーキテクチャ 責務分離 レイヤ 依存注入 純粋関数 不変 テスタビリティ リファクタリング"
metadata:
  ba0918-routing: always
---

# Design Principles

## Scope

Applies to every decision about structure: where a responsibility lives, what depends on what,
what a function takes and returns, and whether a change is made by adding or by editing.

It does not cover how tests are written (the skill `ba0918-testing`) or where a given piece of
information is recorded (the skill `ba0918-placement`).

## The one goal these rules serve

Testability. A single instruction now produces more code than human review can absorb, so the
only safety net that scales is mechanically verifiable correctness. Every rule below exists
because it makes something testable that would otherwise not be.

## Rules

- Compose small focused units into larger ones. Do not build a large unit directly.
- Keep business logic out of orchestrators, handlers, routers, and controllers. They delegate; they do not compute.
- Depend in one direction only: domain, then service, then handler or adapter, then presentation.
- Do not depend upward, and do not depend sideways on a sibling module in the same layer.
- Give the domain layer zero framework and zero infrastructure dependencies.
- Express domain logic as pure functions: same input, same output, no hidden state.
- Put anything with a side effect in the service or infrastructure layer, never in the domain.
- Inject every external dependency — clock, randomness, filesystem, network, database, third-party API.
- Inject the abstraction (interface, trait, protocol), not the concrete implementation.
- Add a new variant by adding a module. Do not modify existing modules to accommodate it.
- Model expected failures as return values (a result or union type), not as thrown exceptions.
- Make pattern matches exhaustive so the compiler reports a missing case.
- Validate untrusted input at the system boundary; trust the types inside the boundary.
- Do not reach for type escape hatches such as `any` or an unchecked cast.
- Default to immutable data. Produce a new value instead of mutating an existing one.
- Grant the least privilege and expose the smallest surface that works.
- Route every boundary through one canonical validator rather than repeating ad-hoc checks.

## Judgment

**Module size is a signal, not a limit.** Around 200 lines is where you should stop and look, not
where you must split. A module with one genuine responsibility may be longer. The target is
preventing mixed responsibilities; shrinking line counts by scattering a single responsibility
across files makes the code harder to test, not easier.

**"Can I test this in isolation" is the deciding question.** When a module cannot be tested
without a running database, a live clock, or a network call, the design is wrong and the fix is
to abstract the dependency — not to add a heavier test harness.

**Mutation needs a stated reason.** Immutability is the default because it removes a whole class
of bugs and because it makes state transitions testable directly: given state A and event X,
expect state B. Update by producing a copy with the changed fields. Mutating in place is allowed
when a measured constraint demands it — record the constraint next to the code, because the next
reader will otherwise convert it back.

**Extension by addition has a mechanism and a diagnostic.** The mechanism is a contract plus one
implementation per variant — an interface with a strategy or a registry — so that adding a
variant leaves existing code and existing tests untouched. The diagnostic is the inverse: if
adding one feature requires touching many existing files, the abstraction boundary is in the
wrong place. Move the boundary before adding the feature.

**Security is structural.** Path traversal defence, input sanitisation, and prototype pollution
defence belong in the shape of the system — one validator at one boundary — not sprinkled as
later patches. A rule enforced in one place can be tested in one place.

## Examples

Business logic living in glue code, and the same logic moved down:

```
// Bad: the handler computes, so testing the rule requires an HTTP request
function handler(req) {
  const total = req.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  return { total: total > 10000 ? total * 0.9 : total };
}

// Good: the handler delegates, so the rule is tested as a pure function
function handler(req) {
  return { total: priceWithVolumeDiscount(req.items) };
}
```

A hidden dependency, and the same dependency injected:

```
// Bad: the result depends on the wall clock, so the test cannot pin it down
function isExpired(token) {
  return token.expiresAt < Date.now();
}

// Good: time is an argument, so expiry is testable at any instant
function isExpired(token, now) {
  return token.expiresAt < now;
}
```

## Evidence

Show these outputs rather than asserting the design is sound.

- **Isolation**: the domain module's test command run with no database and no network reachable,
  showing 0 failures.
- **No logic in glue code**: the orchestrator's test asserting delegation only, plus the domain
  test asserting the computation — two separate runs, both passing.
- **Layer direction**: a search for imports of an upper or sibling layer from inside the domain
  layer that returns no matches (for example `rg -n "service|handler|controller" src/domain`,
  reviewed for import lines).
- **Extension by addition**: `git diff --stat` for the change adding a variant, showing new files
  added and existing modules untouched.
- **Type-level verification**: the type checker or compiler run, exit code 0, with no suppressed
  errors introduced by the change.
