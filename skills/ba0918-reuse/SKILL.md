---
name: ba0918-reuse
description: "Reuse-before-build discipline — decompose a task into independently decidable layers before choosing an implementation approach, search each layer for an existing solution along a fixed ladder from 'is this layer needed at all' through the codebase, the standard library, the platform, installed dependencies and ecosystem staples down to minimal self-implementation, and record adopt-or-build with a one-line reason per layer; the record is judged, never the verdict. Use before deciding how to implement something new or how to rework an existing part. 日本語キーワード: 車輪の再発明 再利用 既存ライブラリ 探索 依存選定 自作 層分解 設計判断"
metadata:
  ba0918-routing: required:design
---

# Reuse Before Build

## Scope

Applies before deciding how to implement something new or how to rework an existing part —
the moment an implementation approach is about to be chosen. It governs the decision that
precedes construction: for each part of the task, whether an existing solution serves it or
the part is built here.

It does not govern how the code that gets built is structured (the skill `ba0918-design`)
and it does not decide where the resulting records land (the skill `ba0918-placement`); it
defines what must be searched and what must be recorded before building starts.

## The bias this closes

Coding agents adopt existing solutions for the parts a human named, and hand-roll the parts
nobody mentioned — without searching for an existing answer first. A ban on reinventing
wheels cannot close this gap: nobody can prove that a suitable existing solution did not
exist, so the ban is unverifiable. This rule therefore judges only the record. Adopting and
building are both legitimate verdicts once the reason for the choice is written down.

## Rules

- Decompose the task into layers before choosing any implementation approach. A layer is a
  unit whose adopt-or-build decision can be made independently of the other layers.
- Enumerate the layers explicitly, as an artifact a reviewer can point at.
- Do not count the whole task as one layer when its parts have different alternatives.
- Walk the ladder below for each layer, in order, and stop at the first rung that holds.
- Record, for every layer, whether it was adopted or built, plus a one-line reason.
- Record the layers a human suggested a technology for in the same form as the layers
  nobody mentioned. A suggestion is not an exemption from the record.
- Put a short reason in a why-not comment next to the code; put a reason that compares
  candidates in the commit log. The skill `ba0918-placement` states which home is which.
- Bound the search with a time limit set by the project, and when the limit is hit, record
  that as the reason for building.
- When a constraint or policy forces a large self-implementation, present its consequences
  — implementing, maintaining and security-reviewing the code yourself — to a human before
  implementing, not after.

## The ladder

For each layer, take the first rung that holds:

1. **Is the layer needed at all?** Can the goal be met without it?
2. **Already in this codebase.** An existing module, helper or utility.
3. **The language's standard library.**
4. **The platform's built-in facilities.** The runtime, OS or framework already in place.
5. **A dependency already installed.**
6. **An ecosystem staple not yet installed.** The package known in the registry as the
   standard answer for this domain.
7. **A few lines.** The layer is genuinely trivial to write in place.
8. **Minimal self-implementation.**

## Judgment

**This rule judges the record, never the verdict.** "Built it, to avoid adding a
dependency" is a legitimate outcome — dependency budgets are real constraints. Ruling on
the choice itself would require proving what did or did not exist in the ecosystem, which
is exactly the unverifiable claim this rule refuses to make. What it can verify is whether
the enumeration and the reasons exist.

**Rung 6 exists because the staple is usually not installed yet.** A search that stops at
already-installed dependencies falls through to self-implementation in the most common
situation of all: the standard package for the domain is simply not in the manifest yet.
That fall-through is the failure this rule exists to prevent, so the search extends to the
registry before conceding to build.

**A layer is defined by its alternatives.** Parts with different existing candidates are
different layers, because each can independently be adopted or built. A tool made of a web
front, a remote transport, process management and a small result-type utility is four
layers — each has its own set of existing answers, so each needs its own decision.

**The missing enumeration is the detector.** The layer list is an observable artifact, so
its absence is mechanical evidence that no search happened — no judgment about intent is
needed. This is what makes the rule enforceable at review time.

**The time limit exists because search has a cost curve.** In a niche domain the search
often ends with nothing found, and an unbounded search obligation would cost more than the
building it tries to avoid. The project sets the limit; hitting it, recorded, is a valid
reason to build.

**Detection rides the project's existing review process.** This rule adds no lint step, CI
job or other machinery. Whoever reviews the change checks that the enumeration exists and
that every layer carries its reason line.

## Examples

An enumeration that hides the decisions, and one that exposes them:

```
Bad:  "Build the admin tool" — one unit, one hand-rolled codebase

Good: layers: web front / remote transport / process management / result utility
      (four layers, because each has different existing candidates)
```

A record that covers only what a human suggested, and one that covers every layer:

```
Bad:  web front — adopted the framework the reviewer suggested
      (process management: hand-rolled over the low-level API, nothing recorded)

Good: web front         — adopt (rung 6): suggested framework fits; no reason to build
      remote transport  — adopt (rung 6): staple client covers key-based auth
      process management — adopt (rung 6): staple runner; building would re-do
                           escaping, timeouts and error surfacing
      result utility    — build (rung 7): a few lines; a dependency buys nothing
```

## Evidence

Completion of the pre-implementation decision is shown by these artifacts, not asserted.

- **The layer enumeration exists**: the list of layers, written before implementation
  began, in the plan, the task notes or the commit that starts the work.
- **Every layer carries a verdict and a reason**: adopt or build, one line each — including
  the layers a human suggested a technology for.
- **Reasons sit in their homes**: short reasons as why-not comments beside the code,
  candidate comparisons in the commit log.
- **A search cut short is recorded**: where the time limit ended the search, the record
  says so as the reason for building.
- **A forced large self-implementation was escalated**: the consequences were presented to
  a human before implementation, and the record shows it.
