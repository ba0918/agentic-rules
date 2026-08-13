---
name: ba0918-testing
description: "Testing anti-patterns and how to escape them — asserting on mocks instead of behaviour, test-only methods leaking into production classes, mocking a dependency whose side effects the test relies on, partial mocks that hide the real response shape, and tests written after the fact. Use when writing a test, reviewing a test suite, deciding whether to mock something, or diagnosing a test that passes while the feature is broken. 日本語キーワード: テスト アンチパターン モック レビュー テスト設計 スタブ 偽陽性 テスト品質"
---

# Testing Anti-Patterns

## Scope

Applies to the tests themselves: what they assert, what they replace with doubles, and whether
they would notice a real defect. It does not govern the order of writing test and code (the skill
`ba0918-tdd`) nor the structure of the code under test (the skill `ba0918-design`).

Because testability is the point of the design rules, a broken test is a broken safety net. These
anti-patterns all produce tests that pass while the system is wrong.

## The iron laws

```
1. Never assert on the behaviour of a mock
2. Never put a test-only method in production code
3. Never mock a dependency you do not understand
4. Never build a partial mock
5. Never write the tests after the fact
```

## Rules

- Assert on behaviour the user or caller can observe, not on the presence of a test double.
- Query rendered output the way a consumer would (by role, by visible text, by return value).
- Put cleanup and setup helpers in test utilities, not on the production class.
- Before mocking anything, state what side effects the real thing has.
- Do not mock away a side effect the test under construction depends on.
- Mock at the lowest level that removes the real problem — the slow or external call, not its caller.
- Give a mocked response every field the real response has.
- Delete an assertion you cannot explain the purpose of.

## Judgment

**Asserting a mock exists proves the mock exists.** It says nothing about the component. The
question to ask before an assertion is whether it would still hold if the real implementation
were substituted; if not, either test the real thing or drop the assertion.

**A method only tests call belongs to the tests.** Putting it on the production class pollutes
the class, mixes responsibilities, and risks being called for real. Ask whether the class owns
the lifecycle of the resource; when it does not, the method belongs elsewhere.

**Over-mocking destroys the behaviour under test.** Mocking "to be safe" or "because it might be
slow" is how a duplicate-detection test ends up erasing the write that makes duplicates
detectable. When you do not yet understand the dependency chain, run against the real
implementation first, observe what actually needs replacing, then replace only that.

**A partial mock is a hidden assumption.** It encodes the fields you happened to remember. The
test passes and integration breaks on the field you forgot. Reproduce the documented response
shape in full; when uncertain, include everything the documentation lists.

**Complex mock setup is a signal to change level.** When the setup is more than half the test,
the unit boundary is wrong — write an integration test instead, or move the boundary.

**A test that breaks when a mock is removed is testing the mock.** A test should break when the
implementation is wrong, not when its scaffolding changes.

## Examples

Asserting on the double, and asserting on behaviour:

```
// Bad
render(<Page />);
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();

// Good
render(<Page />);
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

A test-only method on a production class, and the same helper in test utilities:

```
// Bad: destroy() is called from nowhere but tests
class Session { async destroy() { await this.workspaceManager?.destroy(this.id); } }

// Good: test-utils/session-cleanup.ts
export async function cleanupSession(session) { ... }
```

Mocking away the side effect the test needs, and mocking the right level:

```
// Bad: the duplicate check depends on the write that the mock erased
vi.mock('ToolCatalog', () => ({ discoverAndCacheTools: vi.fn() }));

// Good: only the slow external call is replaced; the write still happens
vi.mock('SlowExternalService');
```

A partial mock, and the full response shape:

```
// Bad
{ status: 'success', data: { userId: '123', name: 'Alice' } }

// Good
{ status: 'success', data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 } }
```

## Quick reference

| Symptom | Fix |
|---|---|
| Assertion on a `*-mock` identifier | Test the real component, or stop mocking |
| Method called only from tests | Move it to a test utility |
| Mock added "to be safe" | Understand the dependency, then mock the narrowest thing |
| Response mock missing fields | Reproduce the documented schema in full |
| Tests written after the code | Write the test first next time |
| Mock setup dominates the test | Raise the level: write an integration test |

## Evidence

Show these outputs rather than asserting the tests are sound.

- **Defect detection**: break the behaviour under test on purpose, run the suite, and show the
  test failing; then restore and show it passing. A test that stays green through both is not
  testing the behaviour.
- **No mock assertions**: a search over the changed tests for `-mock`, `Mock`, and `getByTestId`
  returning no matches in assertion positions.
- **No test-only production methods**: a search for each method added to a production class
  showing at least one non-test caller.
- **Mock completeness**: the real response sample or API documentation alongside the mock, with
  the field sets matching.
- **Suite health**: the full test command output with 0 failures, from the current working tree.
