# cargo-mutants (Rust)

How the rules in `SKILL.md` are carried out with cargo-mutants. Behaviour described here was
observed with cargo-mutants 27.1.0; pin that version or re-check these points after an upgrade.

## Pin the version

```bash
cargo install cargo-mutants --version "<version>" --locked
```

Use the same version on workstations and in CI. Exit codes and output files have changed between
versions, and a gate script reads both.

## Rebuild every mutant

On stable cargo, which decides freshness by file modification time, a mutated file was observed
not to be rebuilt. The tests then ran against the unmutated code and reported survivors that did
not exist. Use the nightly toolchain with content-hash freshness:

```bash
CARGO_UNSTABLE_CHECKSUM_FRESHNESS=true cargo +nightly mutants ...
```

## Run the whole workspace's tests

By default only the tests of the crate that contains the mutant run. When a library's behaviour is
tested from another crate — a CLI's integration tests exercising a core crate — nearly every
mutant in the library survives. Pass:

```bash
cargo mutants --workspace --test-workspace=true ...
```

Test selection (only the mutant's own crate) is a speed choice under `SKILL.md`: compare survivors
with and without it on the same mutants before dropping `--test-workspace=true`.

## Scope

| Tier | Arguments |
|---|---|
| Diff from the merge base | `git diff "$(git merge-base origin/main HEAD)"...HEAD > diff.patch` then `--in-diff diff.patch` |
| Whole code base | no scope argument |
| Release | `--in-diff` with the diff from the previous release tag; whole code base when there is none |
| One file on a workstation | `--file <path>` (repeatable) |

When the diff contains no Rust source, cargo-mutants writes no result file and exits 0. Treat that
case as a pass, and every other missing result file as a failure.

## Concurrency and shards

- `-j <n>` runs n mutants at once on one machine, each in its own copy of the tree. Keep it at 1
  until a measurement on the same mutants shows a higher value is faster. Keep
  `CARGO_BUILD_JOBS` × n at or below the core count.
- `--shard k/n` (k from 0) runs one of n disjoint parts. Run each shard as its own CI job, and make
  a single summary job that depends on all of them the required check, so changing n needs no
  change to branch protection.
- Copies are made under `TMPDIR`. Point `TMPDIR` at a directory created for the run, so leftover
  mutated processes of this run can be found by path and killed without touching other runs.

## Timeouts

cargo-mutants sets the per-mutant timeout from the baseline test time (it logs
`Auto-set test timeout to <n>s`). A timed-out mutant can leave child processes running; reap them
as `references/resource-bounds.md` describes.

## No escape hatches

- `#[mutants::skip]` in the sources hides a mutant from the run. The gate script searches the
  sources for it and fails when found.
- `.cargo/mutants.toml` can exclude files, functions and regular expressions. Pass `--no-config`
  so a configuration file cannot narrow the run, and keep equivalent mutants in a reviewed list
  that the gate reads instead.

## Result and exit codes

Write results to a known place and delete them before each run, so a stale result cannot be read:

```bash
rm -rf mutants.out
cargo +nightly mutants -o . ...
# results: mutants.out/outcomes.json
```

Exit codes in 27.1.0, and what they mean for the gate:

| Code | Meaning | Every mutant measured? |
|---|---|---|
| 0 | No survivors, no timeouts | yes |
| 2 | Survivors found | yes |
| 3 | Timeouts found | yes |
| 1 | Usage error | no |
| 4 | Baseline (unmutated) tests failed | no |
| 5, 6 | Diff could not be read or applied | no |
| 70 | Internal error | no |

Accept only 0, 2 and 3 as a finished run, then decide pass or fail from `outcomes.json` after
removing declared equivalents. Any other code — including a run killed by a signal — is a failure
even when a partial `outcomes.json` exists.

## Putting it together

A workstation run of the diff, inside the boundary from `references/resource-bounds.md`:

```bash
rm -rf mutants.out
run_dir="$(mktemp -d)"
git diff "$(git merge-base origin/main HEAD)"...HEAD > "$run_dir/diff.patch"
systemd-run --user --wait --collect --pipe --same-dir \
  -p MemoryMax=12G -p MemorySwapMax=0 -p CPUQuota=400% \
  -p Nice=19 -p IOSchedulingClass=idle \
  --setenv=PATH="$PATH" --setenv=HOME="$HOME" \
  --setenv=CARGO_UNSTABLE_CHECKSUM_FRESHNESS=true \
  --setenv=CARGO_BUILD_JOBS=4 --setenv=TMPDIR="$run_dir" \
  -- cargo +nightly mutants -j 1 --no-config --workspace --test-workspace=true \
     -o . --in-diff "$run_dir/diff.patch"
```

Keep this in a repository script rather than in a hook or a CI step, so the same command runs on a
workstation and in every CI shard.
