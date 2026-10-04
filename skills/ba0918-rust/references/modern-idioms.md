# Current idioms

Older crates and forms that the standard library or the language now covers. Read it before
adding a dependency for something small, or when writing a form remembered from older code.

Use the right-hand column only when the project's MSRV is at least the version in the last
column. Below that version, the older form is the correct one. Versions were checked on
2026-10-04 against the Rust release notes.

| Older | Current | Stable since |
|---|---|---|
| `lazy_static!`, `once_cell::sync::Lazy` | `std::sync::LazyLock` | 1.80 |
| `once_cell::sync::OnceCell` | `std::sync::OnceLock` | 1.70 |
| `once_cell::unsync::Lazy` | `std::cell::LazyCell` | 1.80 |
| `atty` crate | `std::io::IsTerminal` | 1.70 |
| `#[async_trait]` on a trait never used as `dyn` | `async fn` in the trait | 1.75 |
| `match` / `if let` with an early return in the `else` arm | `let ... else` | 1.65 |
| `#[allow(lint)]` | `#[expect(lint, reason = "...")]` | 1.81 |
| `Option::map_or(false, ...)` | `Option::is_some_and` | 1.70 |
| `Option::map_or(true, ...)` | `Option::is_none_or` | 1.82 |
| `extern crate foo;` | a `use` of the crate (edition 2018 and later) | edition 2018 |
| `try!(...)` | `?` | 1.13 |
| `"{}", x` in a format string | `"{x}"` (inline argument) | 1.58 |

`async_trait` is still needed when the trait is used as `dyn Trait`: an `async fn` in a trait is
not object-safe.

When a new row is added, check its version in the release notes, and keep the table to forms
an agent actually writes.
