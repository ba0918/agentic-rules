---
name: ba0918-mutation-testing
description: "Running mutation testing — resource bounds that keep a run from freezing the machine, how to make runs faster, which mutants to run where (diff, full, scheduled, release), hooks versus CI, gating on survivors, equivalent mutants, and diagnosing a failed or crashed mutation run. Use when introducing mutation testing to a project, running it locally or in CI, choosing its scope or schedule, investigating survivors or timeouts, or adding an equivalent mutant. 日本語キーワード: 変異テスト ミューテーションテスト mutation testing mutants 見逃し 生存 等価 時間切れ 差分実行 シャード 並列化 メモリ枯渇 cgroup CPU 張り付き WSL クラッシュ CI タイムアウト"
metadata:
  ba0918-routing: required:mutation
---

# Mutation Testing Discipline

## Scope

Applies whenever mutation testing is run or wired into a project: running it by hand, putting it
in a hook, a CI job, a schedule or a release, choosing which mutants run, setting the resource
limits it runs under, and turning its result into a gate. Mutation testing makes one small change
to the code at a time — a mutant — and runs the tests to see whether they notice. A mutant the
tests do not notice is a survivor.

The rules are stated independently of any one tool or operating system. The concrete form is in
reference files:

- Resource limits on Linux, in containers and on WSL: read `references/resource-bounds.md`
  before running mutation tests on a machine or a runner for the first time.
- Rust with cargo-mutants: read `references/cargo-mutants.md` before running or configuring it.

It does not cover how a test should assert (the skill `ba0918-testing`), the order of writing
tests and code (the skill `ba0918-tdd`), how a CI definition is written (the skill `ba0918-ci`),
or whether to adopt a mutation testing tool (the skill `ba0918-reuse`).

## Rules

### Protect the machine

- Run mutation testing inside a boundary that caps memory and CPU for its whole process tree.
  Never start it from an unbounded shell.
- When it shares a machine with other work, lower its CPU and I/O priority.
- Give each mutant a time limit derived from the time of the unmutated baseline run.
- Kill the processes a timed-out mutant leaves behind, and report how many were killed.
- On a virtualised development environment (WSL, a VM), also cap the whole environment from the
  host side.
- Apply the same boundary in CI as on a workstation.

### Get speed in this order

1. Make the test suite itself fast. No test waits on real time — a sleep, a timeout that actually
   elapses, a slow server. Inject durations, and check a specified duration by testing the
   constant.
2. Where the tool supports it, run per mutant only the tests that can observe it — after comparing
   its survivors against the full suite on the same mutants.
3. Split the mutants across separate machines (shards).
4. Raise the number of mutants run at once on one machine last, and only when a measurement on
   the same mutants shows it faster. Keep build jobs × concurrent mutants at or below the cores
   the run may use — the CPU cap when one is set, otherwise the core count.

### Scope the runs in tiers

- Gate merges on the mutants in the diff from the merge base.
- Run the whole code base on a schedule, and record its survivors as issues, not as a gate.
- Gate a release on the diff from the previous release, or the whole code base when there is none.
- On a workstation, run only the function or file whose tests are being written.

### Where it runs and who waits

- Never run mutation testing in a pre-commit or pre-push hook.
- An agent never waits on a mutation run inside its implementation loop. Run it in the background
  and keep working, or leave it to CI.
- Put the gate in the pull request's required checks. Name the required check independently of
  the number of shards.
- Size the CI job's time limit from mutants per shard × (build time + baseline test time), with a
  margin.

### Shape of the gate

- Gate on zero survivors in scope, after declared equivalent mutants. Never on a score threshold.
- Declare an equivalent mutant — one that changes no observable behaviour — in a list, with a
  reason for each entry. Before adding one, try to simplify the code so the mutant no longer
  exists. Have a reviewer in a separate context try to refute it. Print the number excluded on
  every run.
- Do not use in-source skip annotations or the tool's exclusion settings. The gate fails when it
  finds one.
- Treat a run that did not finish — interrupted, a failing baseline, an internal tool error — as a
  failure, never as a partial pass. Regenerate the result file on every run. A successful run
  with no result file passes only with evidence of zero candidates in the same scope and shard.
- Pin the tool's version.
- Require a passing baseline and no flaky tests before gating.
- Report timeouts separately from survivors.

## Judgment

**Cost is mutants × suite time.** Every second the suite takes is paid once per mutant, and a
large diff has hundreds or thousands of mutants. That is why a faster suite comes before any
parallelism: it is the only change that shrinks every run, everywhere. A location that keeps
timing out usually means a test is waiting on real time; fix the test.

**The boundary is there for the rest of the machine.** A mutant can allocate without end, spin a
loop, or start a server that outlives its test. Without a boundary, one run has pinned the CPU at
100 %, stopped other sessions, crashed WSL and frozen the host. A memory cap alone does not stop
CPU starvation. A limit inside a virtual environment protects that environment; only a limit set
from the host protects the host, so both are needed. On a CI runner the missing boundary shows up
differently: the runner dies, and the job reports a lost runner instead of a result.

**The size of the boundary is the project's choice.** How much memory and what share of the CPU
depend on the machine and on what else runs on it, so no number here is a rule. The reference file
gives starting values only.

**Running fewer tests per mutant is a trade, not a default.** Selecting only the tests that can
observe a mutant is fast, but tests far from the change — an end-to-end test catching a library
mutant — are what it drops. Compare survivors with and without selection on the same mutants
before adopting it.

**Waiting is the most expensive failure.** When an agent implements a little and then waits two
hours for mutants, most of the session is waiting. Running mutants in a pre-push hook does the
same to people. The gate belongs where nobody blocks on it — a required check before merge.

**Parallelism on one machine often loses.** Each mutant rebuilds a copy of the project, and the
builds compete for the same cores and cache. In one measurement the same 44 mutants took 312 s one
at a time, 348 s three at a time (with a false timeout) and 380 s four at a time. Separate machines
do not compete.

**A diff gate cannot see what was never changed.** Deleting or weakening a test creates survivors
in code the diff does not touch. The scheduled whole run is what finds them.

**Zero survivors names the work; a score hides it.** A score threshold can be met by adding weak
tests elsewhere. A list of survivors in the diff says exactly which behaviour is untested. The
cost of that strictness is the equivalent mutant, which a machine cannot judge — hence the
layered checks on every declaration.

**Diagnose a failed run before moving it.** A red mutation job is one of three things: survivors
(the gate working), a lost runner (no resource boundary), or the job time limit (shards sized too
small). Each has a different fix, and none of them is to stop running the gate in CI.

## Examples

Running on a workstation:

```
Bad:  the tool started from a plain shell with as many concurrent mutants as there are cores
Good: the tool started inside a memory- and CPU-capped boundary at low priority, one mutant at a
      time unless a measurement says otherwise, in the background
```

Where the gate sits:

```
Bad:  pre-push hook runs the diff's mutants; every push waits an hour
Good: the pull request's required check runs the diff's mutants in shards; a schedule runs the
      whole code base and files issues
```

Removing a survivor:

```
Bad:  add a skip annotation on the function, or a score threshold the survivor fits under
Good: add a test that observes the behaviour; or, when the mutant is truly equivalent, simplify
      the code away or declare it with a reason a second reviewer could not refute
```

## Evidence

Show these outputs rather than asserting the run is sound.

- **The boundary is real**: output from inside the run showing its process group and the memory
  and CPU limits applied to it.
- **The speed choice was measured**: when concurrency or test selection changed, the timings and
  survivor counts of the same mutants under each setting.
- **The gate ran**: the run's result — survivors, timeouts and the number excluded as equivalent —
  and, for CI, the run's link and conclusion.
- **No escape hatch**: a search of the sources and tool configuration for skip annotations and
  exclusion settings, showing none.
