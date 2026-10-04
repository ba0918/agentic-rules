---
name: ba0918-rust
description: "Rust-specific rules — choosing the edition, toolchain and crate versions, workspace manifests, MSRV, rustfmt and clippy gates and lint selection, suppressing lints, error types, unwrap and panic, exhaustive matches, unsafe, ownership and clones, output from libraries, current idioms, dependencies. Use when writing, changing or reviewing Rust code, creating a crate or workspace, editing Cargo.toml, rust-toolchain or lint configuration, raising the edition or MSRV, or adding or upgrading a crate. 日本語キーワード: Rust ラスト Cargo クレート ワークスペース edition MSRV rust-version ツールチェーン clippy rustfmt lint unwrap expect panic エラー型 thiserror anyhow unsafe clone 借用 所有権 依存追加"
metadata:
  ba0918-routing: required:rust
---

# Rust

## Scope

Applies to Rust code and its build configuration: choosing versions, declaring the workspace,
the gates a change must pass, how lints are suppressed, errors and panics, matches, unsafe,
ownership, side effects in libraries, current idioms and dependencies. It states only what is
specific to Rust and what an agent gets wrong without being told; general design and testing
rules apply as they are.

The concrete form is in reference files:

- Workspace manifest, toolchain pin, gate commands, MSRV check, edition migration: read
  `references/project-setup.md` before creating a crate or workspace, or changing its manifest,
  toolchain, edition or CI gate.
- Which lint enforces which rule, and how to add a lint to existing code: read
  `references/lints.md` before changing the lint configuration.
- Older crates and forms that the standard library or the language now covers: read
  `references/modern-idioms.md` before adding a dependency for something small, or when writing
  a form you remember from older code.

It does not cover the design principles these rules apply — errors as values, exhaustive
matches, side effects out of the domain, unit size (the skill `ba0918-design`); how tests are
written (the skill `ba0918-testing`) or ordered (the skill `ba0918-tdd`); mutation testing (the
skill `ba0918-mutation-testing`); how a CI definition is written (the skill `ba0918-ci`); or
whether to adopt a crate at all (the skill `ba0918-reuse`).

## Rules

### Versions come from the source, not from memory

- Give a new crate the latest stable edition. Check which one that is in the official Rust
  documentation before writing it.
- Raise an existing crate's edition with the migration tooling, in a change of its own.
- Add a dependency through the registry so the tool picks its current version. Never write a
  version number from memory.
- Check that an API exists in the version being used — the crate's documentation for that
  version, and for the standard library the declared minimum supported Rust version (MSRV).

### Declare once, inherit

- In a workspace, declare the edition, the MSRV and the lint configuration once at the
  workspace, and have every member inherit them.
- Declare the MSRV, and build with that version in CI so the declaration is checked.
- Pin the toolchain version. Raise it as a deliberate change, and fix the new lint findings in
  that same change.
- Keep the lint configuration in the manifest, not only in command-line flags.

### Gates

- Make these required checks in CI: the formatter's check mode, the linter with warnings as
  errors over the whole workspace and all targets including tests, and the whole workspace's
  tests. Hooks are a convenience; CI is the gate.
- Choose lints one at a time. Never enable the pedantic, nursery or restriction group whole;
  the restriction group contains lints that contradict each other.
- Before adding a lint to existing code, fix the places it reports or replace each with a
  reasoned suppression in the same change. Do not let warnings accumulate.

### Suppressing a lint

- Suppress with the form that warns when it stops being needed (`expect`, not `allow`), and give
  a reason. Enforce both with lints.
- Never suppress a warning to finish a task.

### Errors and panics

- A library returns an error type with a variant for each kind of failure. Do not pass a
  `String` error or a type-erased error across the library's boundary.
- A type-erased or context-carrying error is fine at the top of a binary, where it is displayed.
- Outside tests, do not unwrap. Where an invariant guarantees success, use `expect` with a
  message saying why it cannot fail. Forbid unwrap by lint, allowed in tests.
- A library does not panic on a failure its caller could recover from.

### Exhaustive matches

- Do not write a wildcard arm in a match on an enum the crate owns. List the variants.
- On a foreign enum, a wildcard is acceptable when ignoring the rest is the intended behaviour,
  knowing that a variant added upstream will then be ignored silently.
- Mark a public enum non-exhaustive if variants will be added to it.

### Unsafe

- Forbid unsafe code in every crate that does not need it.
- Where it is needed, keep it in a small module and give every unsafe block a comment saying
  why it is sound. Detect a missing comment by lint.
- Inside an unsafe function, wrap each unsafe operation in its own unsafe block.

### Ownership and types

- Borrow where a borrow does. A clone added to satisfy the borrow checker is a sign the ownership
  design needs another look.
- Take a parameter as the general borrowed form (`&str`, `&[T]`) when it is only read. Take
  ownership only when the function stores or consumes the value.
- Use shared mutable state (`Rc<RefCell<T>>`, `Arc<Mutex<T>>`) only after confirming the
  ownership cannot be restructured instead.
- Give a dedicated type to values that cross a boundary or would break if swapped, instead of a
  bare string or integer; use an enum instead of a boolean parameter.

### Side effects in libraries

- Library code does not write to standard output or standard error and does not exit the
  process. It returns values; the binary displays them and sets the exit code. Enable the output
  lints on library crates.

### Current idioms

- Do not add a crate or an older form for what the standard library or the language now does.
  Check the version it became stable in against the MSRV first, and preserve the API guarantees
  the callers need when replacing an older form.

### Dependencies

- Commit the lockfile, and have CI resolve exactly what it records.
- When only part of a crate is used, turn off its default features and enable only what is used.

### Unfinished work

- Never report a change as done while it contains `todo!()`, `unimplemented!()` or `dbg!()`.
  Detect them by lint.

## Judgment

**Enforce by lint what a lint can enforce.** A rule that relies on attention ends up kept in some
places and not in others: a project with a habit of writing safety comments on unsafe blocks
still had more blocks without one than with. Pair each rule with its lint; leave to review only
what no lint detects.

**One lint at a time, never a group.** The pedantic group mixes useful lints with matters of
taste, and the restriction group contradicts itself. Enabling a group on an existing code base
produced hundreds of warnings in one measurement; fixing them crowds out the real work until the
gate is removed altogether.

**The wildcard lint cannot tell owned enums from foreign ones.** It reports both. In a crate that
mostly matches its own enums, enable it and suppress the foreign cases with reasons; in a crate
that mostly matches a foreign syntax tree or protocol, keep the rule by review instead.

**Dedicated types where a mix-up is possible.** Wrapping every value adds code that only wraps
and unwraps. The rule pays off at boundaries and between values of the same primitive type that
mean different things.

**Version numbers belong in the references, with a date.** A model writes the edition and the
crate versions most common in its training data. A rule that names today's number repeats the
same mistake once the next edition ships, so the rule says where to look and the reference file
records what was found and when.

## Examples

Choosing an edition:

```
Bad:  edition = "2021" in a new crate, because it is the one most often seen
Good: the latest stable edition, confirmed in the official documentation on the day, declared
      once in the workspace and inherited by every member
```

Errors in a library:

```
Bad:  pub fn parse(s: &str) -> Result<Config, String>
Good: pub fn parse(s: &str) -> Result<Config, ParseError>
      where ParseError has one variant per way parsing can fail
```

A match on the crate's own enum:

```
Bad:  match shape { Shape::Circle(c) => draw(c), _ => {} }
Good: match shape { Shape::Circle(c) => draw(c), Shape::Square(_) | Shape::Line(_) => {} }
      (adding a variant now fails to compile until each match decides what to do with it)
```

Silencing a finding:

```
Bad:  #[allow(dead_code)] added so the build is clean
Good: the dead code removed; or #[expect(dead_code, reason = "...")] when it is kept on purpose
```

An invariant that cannot fail:

```
Bad:  serde_json::to_string(&report).unwrap()
Good: serde_json::to_string(&report)
          .expect("Report holds only strings and integers, which always serialise")
```

## Evidence

Show these outputs rather than asserting the change follows this rule.

- **The gates pass**: the output of the formatter's check, the linter with warnings as errors
  over all targets, and the whole workspace's tests, from the current working tree.
- **Versions were checked**: for each edition, toolchain or crate version chosen, the source it
  was confirmed in and the date.
- **Every exception is reasoned**: a list of the suppressions, unsafe blocks and `expect` calls
  the change adds, each with its reason.
