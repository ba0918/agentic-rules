# Lints

Which lint enforces which rule in `SKILL.md`, and how to add one to existing code. Read it before
changing the lint configuration. The manifest form is in `project-setup.md`.

Lint names and groups were checked against clippy 1.97 on 2026-10-04. A lint can move between
groups or be renamed; `cargo clippy --explain <name>` confirms that a name exists.

## Rule to lint

| Rule in SKILL.md | Lint | Group | Where to set it |
|---|---|---|---|
| Suppress with `expect` | `clippy::allow_attributes` (outer attributes only) | restriction | workspace |
| Give a reason | `clippy::allow_attributes_without_reason` | restriction | workspace |
| No unwrap outside tests | `clippy::unwrap_used` + `allow-unwrap-in-tests = true` in `clippy.toml` | restriction | workspace |
| No wildcard on an owned enum | `clippy::wildcard_enum_match_arm` | restriction | workspace, when the crate mostly matches its own enums (see below) |
| Forbid unsafe | `unsafe_code` | rustc | workspace (see below when a crate needs unsafe) |
| A comment on every unsafe block | `clippy::undocumented_unsafe_blocks` | restriction | workspace |
| Unsafe operations in their own block | `unsafe_op_in_unsafe_fn` | rustc, warns by default from edition 2024 | workspace |
| Borrow what is only read | `clippy::needless_pass_by_value` | pedantic | workspace |
| No clone that is never needed | `clippy::redundant_clone` | nursery | optional: nursery lints can report false positives |
| No output from a library | `clippy::print_stdout`, `clippy::print_stderr` | restriction | each library crate's root, as `#![deny(...)]` |
| No unfinished markers | `clippy::todo`, `clippy::unimplemented`, `clippy::dbg_macro` | restriction | workspace |

These gaps stay with review:

- inner `#![allow(...)]` attributes: `allow_attributes` ignores them, so a reasoned inner
  `allow` can pass both suppression lints without detecting a stale suppression; use `expect`
  here too (see the [lint's documented scope](https://rust-lang.github.io/rust-clippy/master/index.html#allow_attributes))
- an error type with a variant per failure, rather than a `String` error
- `expect` messages that say why the call cannot fail
- shared mutable state used where the ownership could be restructured
- dedicated types for values that would break if swapped

## Why not a group

- **restriction** is a catalogue, not a style. It contains lints that contradict each other —
  `mod_module_files` and `self_named_module_files` each forbid what the other requires — so the
  group cannot be enabled as a whole.
- **pedantic** mixes useful lints (`needless_pass_by_value`) with matters of taste. In one code
  base of about 22,000 lines it produced over 800 warnings.
- **nursery** holds lints still being finished, with known false positives.

Pick lints from any group by name. Each one added should answer a rule or a defect actually seen.

## The wildcard lint

`wildcard_enum_match_arm` reports a wildcard on any enum, the crate's own and foreign ones alike.
In a crate that mostly matches a foreign syntax tree or protocol type, enabling it fills the code
with reasoned suppressions for the foreign cases. Count first:

```sh
cargo clippy --workspace -- -A clippy::all -W clippy::wildcard_enum_match_arm
```

When most findings are on the crate's own enums, enable the lint and suppress each foreign case
with `#[expect(clippy::wildcard_enum_match_arm, reason = "...")]`. Otherwise leave it off and
keep the rule in review.

## When a crate needs unsafe

`forbid` cannot be lowered further down, so a workspace-wide `unsafe_code = "forbid"` leaves no
way in for a crate that needs unsafe. In that case:

- set `unsafe_code = "deny"` at the workspace;
- in the one module that holds the unsafe code, write
  `#![expect(unsafe_code, reason = "...")]` at the top, naming what needs it;
- in each crate root that has no unsafe code at all, write `#![forbid(unsafe_code)]`.

The unsafe code stays in the module that declares it, and a new unsafe block anywhere else fails
the gate.

## Adding a lint to existing code

1. Count what it reports, without changing the configuration:

   ```sh
   cargo clippy --workspace --all-targets -- -A clippy::all -W clippy::<lint>
   ```

2. In the same change that adds the lint, fix each finding, or replace it with
   `#[expect(clippy::<lint>, reason = "...")]` where the code is right as it is.
3. Run the gate. It passes with no warnings left over.

When there are too many findings for one change, split the work by crate or by module, and add
the lint where the findings are already gone — never at `warn` across code that still has them.
