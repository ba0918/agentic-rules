---
name: ba0918-delegation
description: "Delegation discipline for agent orchestration — an orchestrator that delegates work instead of performing it, five fixed role contracts (orchestrator, implementer, investigator, reviewer, bulk-executor), self-contained delegation prompts, a take-home contract for results, explicit handling of long-running work, and an executor table that binds roles to executors in the user's own environment. Use when handing work to another agent, composing a delegation prompt, deciding which role performs a task, or receiving a delegate's result. 日本語キーワード: 委譲 委任 オーケストレーション サブエージェント エージェント分担 役割 実行役 委譲プロンプト 並行作業 持ち帰り"
metadata:
  ba0918-routing: required:delegate
---

# Delegation Discipline

## Scope

Applies when one agent hands work to another: the decision to delegate, the roles the
participants hold, the prompt that carries the task, and the way the result comes back.

It fixes the contracts of the roles and the flow of information between them. It does not
choose which model, product or service performs a role — that binding lives in the user's own
environment, in the executor table whose shape this document specifies. The contracts hold with
or without such a binding.

Verifying a returned result — evidence demands, verdict aggregation, hand-off hygiene — is the
subject of the skill `ba0918-verification`. The boundary overlaps on purpose: a rule such as
"a result comes back with evidence" belongs to both sides, and each document states its side
in full so it reads alone.

## Roles

Five roles, a fixed vocabulary. A role is a shape of work, not a property of whoever performs
it: the same runtime can hold different roles in different sessions, and every contract below
applies whether or not the role is bound to a dedicated executor.

| Role | Contract |
|---|---|
| orchestrator | Faces the session. Delegates work instead of performing it; keeps judgments, gates and verdict summaries in its own context, and little else |
| implementer | Produces the change. Never approves its own work |
| investigator | Read-only. Reports findings with their sources; changes nothing |
| reviewer | Judges the work from a context independent of the implementer's |
| bulk-executor | Runs mechanical, fully pre-specified tasks only; stops and returns at the first branch that requires judgment |

There is no dedicated adjudicator role. Settling conflicts — between findings, between
interpretations, before an irreversible step — is part of the orchestrator's own contract,
escalated to a human when it exceeds the orchestrator's mandate.

## Rules

- Delegate the work; keep the decisions. The orchestrator's first duty is preserving its own
  context, and every file it reads and every command it runs in person spends it.
- Apply the role contracts regardless of binding. A role with no entry in the executor table
  degrades to the delegating agent's default mechanism — the separation rules still apply;
  degradation changes who performs the role, never what the role is allowed to do.
- Never let an implementer approve its own work. Acceptance passes through a reviewer or the
  orchestrator's own gate.
- Keep the investigator read-only. A task that needs a file written or a state-changing command
  run is not an investigation.
- Give the bulk-executor only tasks whose every step is already decided, and instruct it to
  stop and return — not improvise — when a step turns out to need judgment.
- Make every delegation prompt self-contained: inline the contracts to follow, the context
  needed, and the exact paths involved. Never assume the delegate has read a rules file, a
  skill, or the conversation that produced the task.
- Require the delegate to write its deliverable durably before reporting completion; the report
  announces the artifact, it does not replace it. Where the delegate cannot write files, say so
  in the delegation prompt and have it return the deliverable in its reply body, which the
  orchestrator transcribes.
- For long-running work, state explicitly that the call runs synchronously and how long it is
  allowed to take — or design the flow so that a result never returned does no harm.
- Keep one executor table per environment, at the user-level instruction location, with the
  columns Role / Executor / Evidence.
- Write each executor as a stable, fully qualified identifier, never an alias whose resolution
  can change underneath the table.
- Update a table row only when a measured failure or a measured improvement demands it — never
  on announcements, benchmarks run elsewhere, or fashion.

## Judgment

**The orchestrator's context is the scarcest resource in the session.** It is the only place
where the whole task, every verdict and every open question coexist, and it cannot be
replenished. Work performed in person floods it with detail that a delegate could have kept;
what must survive in it are the judgments, the gates passed, and the verdicts — the material
the next decision is made from.

**Roles are permanent vocabulary; executors are not.** Which executor is best at a role changes
with every generation of tooling; the shape of the work does not. That is why this document
fixes the role contracts and refuses to name executors: a norm written against a product decays
with the product, a norm written against a role survives it. The executor table is the single
place where the two layers meet.

**An empty or partial executor table is a working configuration, not a broken one.** An
environment running everything on one executor still gains the substance of this document:
separated contexts, no self-approval, read-only investigation, prompts that stand alone. The
table adds routing on top of the separation; it is not a precondition for it.

**A prompt that presumes shared context fails silently.** The delegate does exactly what it was
literally told, in the context it actually has — and returns something plausible that answers a
different question. The cost of inlining the contract and the paths is paid once, at writing
time; the cost of a presumed context is paid after the work is done, when it is most expensive
to notice.

**A completion report without a deliverable is a failed delegation.** "Done" is a claim about
work; the artifact is the work. A delegation whose result exists only inside the delegate's
reply — when it was expected as a file — has lost its result the moment the reply scrolls out
of context, which is why the fallback of returning the deliverable in the body must be agreed
at delegation time, not discovered at reporting time.

**The Evidence column is what keeps the table honest.** A row that cannot cite the observed
failure or measurement that put it there is an opinion in table form. Evidence-bearing rows can
be re-examined when the environment changes; opinions can only be argued about.

## Examples

The shape of an executor table — placeholders, not recommendations; the values are always the
environment's own:

```
| Role | Executor | Evidence |
|---|---|---|
| implementer | <provider>/<model-or-agent-id> | <date>: refactor task, N sessions, chosen executor completed both; prior one stalled twice |
| investigator | <provider>/<model-or-agent-id> | <date>: repo-wide scan stayed read-only and cited sources; default executor edited a file mid-scan |
| reviewer | (unbound — delegating agent's default mechanism) | — |
```

A delegation prompt that presumes context, and one that stands alone:

```
Bad:  Fix the bug we discussed. Follow the usual conventions.
Good: Fix the off-by-one in src/pager.ts (function pageCount) that drops the
      last page when total is an exact multiple of pageSize.
      Contract, inline: test-first; do not touch files outside src/pager.ts
      and its test; commit message in the project's language.
      Write the result summary to reports/pager-fix.md before reporting done.
```

A long-running delegation left ambiguous, and one made explicit:

```
Bad:  Run the full migration and tell me how it went.
Good: Run the full migration synchronously; it may take up to 30 minutes —
      do not report before it exits. If the environment cannot hold the call
      open that long, stop and say so instead of backgrounding it.
```

## Evidence

Show these outputs rather than asserting the delegation was disciplined.

- **The work was delegated**: the session's task list or delegation log, with the orchestrator's
  own actions limited to judgment, gating and transcription.
- **The prompt stands alone**: the delegation prompt as sent, containing the contract, the
  context and the paths inline — readable with the rest of the session deleted.
- **The deliverable exists**: the artifact at its agreed path before or at the completion
  report; or, under the body-return fallback, the orchestrator's transcription of it.
- **Roles were kept**: the acceptance trace showing the implementer's work approved by someone
  other than the implementer, and the investigator's toolset or log showing reads only.
- **The table is one and grounded**: the executor table quoted from its single user-level
  location, each bound row carrying a fully qualified identifier and an Evidence entry.
