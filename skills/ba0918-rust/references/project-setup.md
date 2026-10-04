# Project setup

The concrete form of the version, workspace and gate rules in `SKILL.md`. Read it before creating
a crate or workspace, or changing its manifest, toolchain, edition or CI gate.

## Versions as of the last check

Checked on 2026-10-04. Check again before relying on these; they change every six weeks.

| What | Value | Where to check |
|---|---|---|
| Latest stable Rust | 1.99.0 (released 2026-10-01) | <https://blog.rust-lang.org/releases/>, or `rustup check` |
| Latest stable edition | 2024 (stable since 1.85.0) | <https://doc.rust-lang.org/edition-guide/> |
| Resolver | `"3"`, the default under edition 2024 (chooses dependency versions compatible with `rust-version`) | <https://doc.rust-lang.org/cargo/reference/resolver.html> |

When the check finds a newer edition or toolchain, use it, and update this table and its date
in the same change.

## Workspace manifest

Declare the shared values once, at the workspace:

```toml
[workspace]
members = ["crates/app-core", "crates/app-cli"]
resolver = "3"

[workspace.package]
edition = "2024"            # the latest stable edition on the day — see the table above
rust-version = "1.85"       # the oldest toolchain the project promises to build on
license = "MIT"

[workspace.lints.rust]
unsafe_code = "forbid"      # see lints.md here when a crate needs unsafe
unsafe_op_in_unsafe_fn = "deny"

[workspace.lints.clippy]
# the lints chosen one at a time — see lints.md here
unwrap_used = "warn"
allow_attributes = "warn"
allow_attributes_without_reason = "warn"
undocumented_unsafe_blocks = "warn"
todo = "warn"
unimplemented = "warn"
dbg_macro = "warn"
```

Each member inherits them:

```toml
[package]
name = "app-core"
version = "0.1.0"
edition.workspace = true
rust-version.workspace = true
license.workspace = true

[lints]
workspace = true
```

A member that writes `[lints] workspace = true` cannot add its own lint keys beside it. A lint
only one crate needs — the output lints on a library, for one — goes in that crate's root as an
inner attribute (`#![deny(clippy::print_stdout, clippy::print_stderr)]` in `lib.rs`).

The lints are set to `warn` in the manifest, and the gate turns warnings into errors. A local
build then still runs while a warning is being fixed, and nothing reaches the main branch with
one.

For a single crate without a workspace, put the same keys under `[package]` and `[lints.rust]` /
`[lints.clippy]`.

## Linter configuration file

`clippy.toml` beside the workspace manifest:

```toml
allow-unwrap-in-tests = true
```

The linter reads the MSRV from `rust-version`, so it does not suggest an API newer than the
declared version; do not repeat it here.

## Toolchain pin

`rust-toolchain.toml` at the repository root:

```toml
[toolchain]
channel = "1.99.0"          # raise deliberately; fix new lint findings in the same change
components = ["rustfmt", "clippy"]
```

rustup reads this file wherever cargo runs, so a workstation and a CI job that installs the
toolchain through rustup build with the same version. A CI step that installs "stable" ignores
the pin; install the pinned version instead.

## Formatting

Run the formatter through cargo (`cargo fmt`), which reads the edition from the manifest. The
`rustfmt` binary called directly does not, and formats with an older edition's style unless
given `--edition`. A hook that formats only the staged files has to pass it.

## Gate commands

```sh
cargo fmt --all --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
```

`--all-targets` puts tests, examples and benchmarks under the linter too. `--locked` fails when
the lockfile would change, so CI builds exactly what was committed.

## Checking the MSRV

A CI job that installs the toolchain named in `rust-version` and builds with it:

```sh
rustup toolchain install 1.85.0 --profile minimal
cargo +1.85.0 check --workspace --locked
```

Check the libraries and binaries; development dependencies often need a newer toolchain than
the product, so leave `--all-targets` out of this job unless the tests are also promised to
build on the MSRV.

## Adding a dependency

```sh
cargo add serde --features derive
cargo add rustls --no-default-features --features std,ring
```

`cargo add` asks the registry for the current version and writes it, so no number comes from
memory. Under resolver 3 it also prefers a version whose own `rust-version` fits the project's.
Read the API on docs.rs for the version that was written, not from memory of an older one.

## Raising the edition

On a clean working tree, in a change of its own:

1. `cargo fix --edition --workspace --all-targets` — rewrites the code that the new edition
   would reject, while the manifest still names the old edition.
2. Change `edition` in the workspace manifest.
3. `cargo fmt --all` — the edition also selects the formatting style.
4. Run the gate commands above and fix what the migration could not.

Changes in the 2024 edition that the migration does not always settle by itself:

- `std::env::set_var` and `std::env::remove_var` are unsafe functions.
- `extern` blocks are written `unsafe extern`.
- An unsafe operation inside an `unsafe fn` needs its own `unsafe` block
  (`unsafe_op_in_unsafe_fn` warns by default).
- `gen` is a reserved keyword.
- `impl Trait` in return position captures all lifetimes in scope; add `use<..>` to narrow it.
- Temporaries in a block's tail expression are dropped before the block's locals.

The full list is in the edition guide linked in the table above.
