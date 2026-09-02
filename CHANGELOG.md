# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A change that alters the meaning of a rule — as opposed to rewording, reformatting or adding
examples — is a breaking change and is listed under `Changed` with a **BREAKING** marker.

## [Unreleased]

## [0.8.0] - 2026-09-03

### Added

- `ba0918-verification` — the four conditions under which an oracle (a test, a check, or a
  fixture) counts as evidence: the condition it produces has a named operational producer in a
  supported environment, its subject is the product or a check rather than the oracle itself,
  the rule it enforces is stated by the specification, and every wording, file layout, or
  internal name it pins is declared there as a contract. Framed as an extension of "a claim is
  not evidence", never as a second principle: an observation made under an unreachable
  condition is not evidence either. A finding that demands a new oracle is complete only when
  it shows the oracle meets those conditions; one that does not becomes a recorded proposal or
  a documented disagreement, never a fix. A requirement whose only oracle would fail them is
  recorded as UNVERIFIED, per requirement, with the reason and a proposed disposition. Judged
  by the conditions, never by size; evidence is scoped to the diff under review.
- `contracts/oracle-evidence.md` — the same conditions in a copyable form for the workflow steps
  that write requirements or plans and do not read the skill. A copy carries the rule name and
  the agentic-rules release version it was taken from, so a copy left behind by a change to the
  source is found by comparing versions.

## [0.7.0] - 2026-09-01

### Added

- `ba0918-design` — a seam gate, framed as a facet of testability rather than a second
  principle: an interface, injection point, registry, or configuration switch is introduced only
  when the same change contains a test that needs it or a second implementation behind it;
  otherwise the concrete thing is called directly. Judged by counting users in the diff, never
  by predicted need; evidence is scoped to the seams the change at hand introduces. The existing
  rule against abstractions justified only by a future replacement stays as its special case.
- `ba0918-diff-review` — a rule for presenting a set of changes to a person for review: grouping
  them by the intent behind each change instead of by file, carrying the reason and the points
  that need judgment with each group, keeping the rendering faithful to the bytes, and naming the
  reviewed paths and content identities as the approval target rather than a summary. It also
  requires a review surface the reviewer can keep and open with their own tools, so that hosting
  it anywhere stays optional and consented to.

## [0.6.0] - 2026-08-23

### Added

- `ba0918-readability` — a rule for translating technical results into human-readable output
  without deleting claims, conditions, uncertainty, or traceable evidence. It also keeps decision
  context near choices and puts long results in a suitable reading surface instead of duplicating
  them into narrow conversations.

### Changed

- The marketplace manifest no longer lists the skills, and `scripts/validate.py` no longer
  checks such a list against `skills/`. A plugin's skills load from the `skills/` directory
  under its source by default, so the list repeated a scan the runtime already performs while
  charging every skill added an edit to a file that decided nothing. What loads, and from
  which paths, is unchanged.

- **BREAKING** — `ba0918-release`: the unreleased changelog section is a delta against the
  latest release, never against the previous commit. A later change to something still
  unreleased amends or removes the pending entry rather than adding another one, a defect no
  release ever shipped gets no fixed entry, and before the first release the section describes
  what that release delivers rather than the history of building it. A project that has been
  logging every unreleased change as its own entry folds those entries together on upgrade.

## [0.5.0] - 2026-08-16

### Added

- `ba0918-secrets` — confidential context and third-party material as a second protected class
  alongside credentials: internal project and product names, internal hostnames, customer
  names and confidential document content are kept out of any destination whose audience is
  wider than the source's — a public repository's code, documentation, commit logs, issues and
  pull request text, and a broader private one alike. The test is the destination's audience,
  not the value's shape; for unlicensed copyrighted works the licence decides instead, in any
  destination, a private one included. The leak-response section gains an information-leak
  variant where containment replaces revocation, taken per exposed surface — history rewritten
  across every affected commit, ref names, discussion titles, bodies and comments with their
  edit histories — each surface re-checked after the cleanup, since cleaning one never clears
  another. That rewrite carries the same explicit approval gate as the credential path. Leaked
  material with no stable identifier (a paraphrased document, copied code) is located from its
  provenance rather than by search, through inventory, prevention and re-check alike. Evidence
  gains four checks that make the new class verifiable rather than asserted: outgoing text
  against a list of private identifiers held outside the working tree, a named source and
  audience comparison for document-derived passages (a paraphrase carries no name for a search
  to find), the licence and its attribution for each copy of third-party material, and a
  post-containment accounting that separates the surfaces the response reached from the ones
  beyond it — fetched clones, forks, caches — recorded as unresolved rather than claimed as a
  purge.

### Changed

- `ba0918-secrets` moves its two leak-response procedures and the evidence they owe into
  `references/leak-response.md`, read when a leak is suspected or confirmed. No rule changed
  meaning and nothing left the distribution unit — the skill directory is what ships — so the
  relocation is compatible under the criterion above. `SKILL.md` keeps the part that must not
  wait: suspicion alone is enough to report and to stop what is still moving, and the explicit
  approval gate covers revoking a credential, rewriting shared history and deleting discussion
  revisions. It names the file to read next.
- `ba0918-secrets` states each norm once. The approval gate and the report-first rule each
  stood in five places across rules, judgment and two procedures; `Rules` now covers prevention
  only and a single `After a leak` section covers response. Three bullets keeping a credential
  out of commit messages, out of logs and out of prompts became one bullet naming every
  destination — with an explicit exclusion for presenting the value to the service it
  authenticates against, since the general-principle wording would otherwise widen the ban
  beyond the scope of the previous specific list. `Judgment` took back the rationale that had
  drifted into the evidence checklist, and two sentences that had become hard to parse were
  rewritten.
- The design spec gains a division of labour between `SKILL.md` and `references/`. The 500-line
  cap is a limit, not a budget: what a skill is read for in every session stays in `SKILL.md`,
  what only a specific situation needs moves to `references/`, safety reflexes stay behind
  whatever else moves, and a norm written in three or more places inside one skill is
  consolidated — the accepted duplication between skills is a rule about distribution units,
  not a licence to repeat a norm within one.

## [0.4.0] - 2026-08-16

### Added

- `ba0918-design` — a replaceability lens, framed as a facet of testability rather than a
  second principle: keep representations specific to a dependency or a storage mechanism
  inside their declared boundary; when changing a persisted format, test the chosen change
  path (compatible read, migration, or explicit rejection); never add an abstraction whose
  only justification is a future replacement. Judged by declared contracts and tested change
  paths, never by stated intent; evidence is scoped to the changed public surface of the
  diff at hand.
- `ba0918-reuse` — a conditional addition to the adoption record: when a newly adopted
  dependency fixes a persisted format or a public contract, the record states what it fixes.
  No unconditional boilerplate line; fixation by self-built parts stays with the boundary
  rules of `ba0918-design`.

## [0.3.0] - 2026-08-15

### Added

- `ba0918-reuse` — reuse-before-build discipline: decomposition of a task into
  independently decidable layers before any implementation approach is chosen, an
  eight-rung search ladder per layer — from questioning whether the layer is needed at
  all, through the codebase, the standard library, the platform, installed dependencies
  and not-yet-installed ecosystem staples, through a few lines written in place, down to
  minimal self-implementation — an adopt-or-build record with a one-line reason for
  every layer with no exemption for human-suggested technology, judgment of the record
  rather than the verdict, a project-set time limit on the search, and escalation to a
  human before any forced large self-implementation.

## [0.2.0] - 2026-08-14

### Added

- `ba0918-delegation` — delegation discipline: an orchestrator that delegates work instead of
  performing it, five fixed role contracts (orchestrator / implementer / investigator /
  reviewer / bulk-executor), self-contained delegation prompts, a take-home contract for
  results, and an executor table that binds roles to executors in the user's own environment —
  no model, vendor or price bindings inside the skill itself.
- `ba0918-verification` — verification discipline: observable evidence instead of completion
  claims, worst-of aggregation of review verdicts with a missing required reviewer recorded as
  UNVERIFIED, findings treated as data rather than authority, hand-off hygiene toward external
  systems (scoped diff only, credential scan, sealing delimiters), and narrow escalation
  conditions.
- `ba0918-scaffold` now generates a `CLAUDE.md` shim — a single `@AGENTS.md` line — when none
  exists, so the generated router is actually read by Claude Code. An existing equivalent
  reference is left untouched (idempotent), and any other existing `CLAUDE.md` gets a diff
  presented instead of an overwrite, the same gate as `AGENTS.md`.
- `ba0918-release` — release discipline: one canonical version location per project, a bump
  whenever a release carries a user-visible change, a change of meaning recorded as breaking, a
  tag issued for every release — created only after the project's checks pass, and issued with
  the version heading and the comparison link as one operation — and published tags never moved
  or reused: a published release is fixed by releasing a new version.
- APM ([microsoft/apm](https://github.com/microsoft/apm)) as an install route, documented in
  the README — APM resolves the `.claude-plugin/plugin.json` this repository already carries
  as a plugin collection and discovers `skills/` on its own, so no repository-side change was
  needed.
- Codex CLI as an install route — `.claude-plugin/plugin.json` declares the plugin's identity,
  and Codex installs from the marketplace manifest this repository already carried.
- OpenCode as an install route — `package.json` and `.opencode/plugins/agentic-rules.js`
  register `skills/` as a skill path. Nothing is injected into a session; the rules that apply
  at all times are delivered by the `AGENTS.md` that `ba0918-scaffold` generates.
- A version-sync check in `scripts/validate.py`. `plugins[0].version` in
  `.claude-plugin/marketplace.json` is the canonical version, and `.claude-plugin/plugin.json`,
  `package.json` and the newest release heading of this file are checked against it.

### Changed

- **BREAKING** — `ba0918-secrets`: revoking a leaked credential is now executed by a human, or
  by the agent only under explicit approval — the same gate as rewriting shared history.
  Reporting the leak becomes the first, blocking task, and external operations involving the
  affected credential stop while approval is pending. "Revoke first, clean history second"
  keeps its priority; only the actor changed.
- **BREAKING** — `ba0918-scaffold` runs only when the user explicitly requests the scaffolding
  work itself, never as a side effect of another task. Being loaded as a candidate from its
  description is not permission to write files; the description now states the same condition.
- The design spec's shared-source migration trigger became a staged clause: duplication between
  skills is accepted (self-containment outranks deduplication), a validator sync check is added
  only if drift between copies causes real harm, and a shared source is reconsidered only if
  that fails. A new spec section requires file-writing procedural skills to run only on an
  explicit request.
- The version in `.claude-plugin/marketplace.json` moved from `metadata.version` to
  `plugins[0].version`, so the file names the version once. Declaring it there also decides how
  updates reach the plugin routes: an installed copy follows this version instead of the latest
  commit, so a user-visible change ships only once the version is bumped.

## [0.1.0] - 2026-08-13

### Added

- `ba0918-design` — design principles with testability as the supreme goal.
- `ba0918-placement` — the four quadrants of information placement.
- `ba0918-tdd` — the test-first contract.
- `ba0918-testing` — testing anti-patterns.
- `ba0918-commit` — commit splitting and message conventions.
- `ba0918-secrets` — credential detection, staging ban, exposure prevention, incident response.
- `ba0918-scaffold` — generation of `AGENTS.md` and `PROJECT.md` from installed rule skills.
- `scripts/validate.py` — validator for this repository's conventions, standard library only.
- `.claude-plugin/marketplace.json` — distribution metadata for the Claude Code plugin route.
- CI running the validator, the validator's tests, and `npx skills-ref validate`.

[Unreleased]: https://github.com/ba0918/agentic-rules/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/ba0918/agentic-rules/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/ba0918/agentic-rules/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/ba0918/agentic-rules/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/ba0918/agentic-rules/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ba0918/agentic-rules/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ba0918/agentic-rules/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ba0918/agentic-rules/releases/tag/v0.2.0
