---
name: ba0918-skill-authoring
description: "Skill authoring norms — scope and boundaries of a skill, reading cost and references, independence from any one runtime, structure that survives change, descriptions that trigger, and wording chosen by rule kind. Use when writing a new skill, revising an existing SKILL.md or its references, or splitting or merging skills. Not for merely using a skill, and not for auditing or evaluating one. 日本語キーワード: スキル作成 スキル執筆 スキルの書き方 SKILL.md references description 発火 スキル改修 スキル分割 スキル統合 読み込みコスト"
---

# Skill Authoring

## Scope

Applies when writing an Agent Skill — a skill directory with its `SKILL.md`, its `references/`
and any scripts bundled with it — whether creating a new one, revising an existing one, or
splitting or merging skills. Other instruction documents, such as a project's agent
instructions file or slash commands, are outside this rule.

It covers both kinds of skill: a rule skill, which states norms for some kind of work, and a
procedural skill, which carries out a procedure with side effects such as writing files. A norm
below that applies to only one kind says which.

When revising part of an existing skill, apply these norms to the part being changed. Bringing
the whole skill into line is separate work, not a precondition of the edit.

It does not govern how code is designed (the skill `ba0918-design`), how prose for a human reader
is made understandable (the skill `ba0918-readability`), or which kind of information belongs in
code, tests, commit logs or comments (the skill `ba0918-placement`). Measuring or evaluating how
well a skill works is outside this rule too: this rule states how a skill is written.

## Rules

### Scope and boundaries

- Give one skill one domain.
- Open the body with a scope section stating what the skill governs and what it does not.
  Where a neighbouring skill governs the excluded part, name that skill.
- Split off a separate skill when a part belongs to a different domain, or is read for a
  different kind of work.
- Keep a part that belongs to the same domain but is needed only in a specific situation in the
  same skill, under `references/` as the reading-cost rules below describe.

### Reading cost

- Treat size as cost per read: what a skill costs is how often it is read times how much is read.
- Put in `SKILL.md` only what every reading of the skill needs.
- Move content needed only in a specific situation to `references/`, and state in `SKILL.md`
  the situation and the file to read when it arises.
- Keep safety reflexes in `SKILL.md` even when their procedure moves out — "report first",
  "get approval before an irreversible step" and the like.

### Independence from any one runtime

- Do not write the body so that it depends on one particular tool, model or runtime command.
- Refer to other skills by name, never by path.
- Do not reference any path outside the skill's own directory. Relative references into the
  skill's own `references/` are fine.
- A frontmatter field that only one runtime understands may be used, provided the skill still
  works correctly where that field is ignored and the body never relies on its effect.
- For bundled scripts, state in `SKILL.md` the runtime and commands they require.

### Structure that survives change

- Handle a new situation by adding a section or a reference file, not by rewriting existing
  rules.
- When a change alters what an existing rule means, say that it changes the meaning. Do not let
  it pass as rewording.
- Do not rename headings or identifiers that other skills or documents may refer to — the skill
  name, section names — without a reason that outweighs breaking those references.
- Duplication of a rule across skills is acceptable.
- Within one skill, merge a norm once it is written in three or more places. Stating a rule, its
  reason and its procedure are different roles and may each mention it; copying the rule
  verbatim is not a different role.

### Descriptions that trigger

- Write in the description only what an agent needs to decide whether to load the skill: its
  domain, the work and situations it is for, and the words users actually say when they want it.
- Keep the contents of the rules — their conditions and procedures — out of the description.
  A list of domain keywords is fine; it is a cue for triggering, not a rule.
- Exception (procedural skills): state the conditions under which the side effects may run in
  the description, as part of when the skill is for.
- Do not fix the description's language by rule; the words users actually say decide it.

### Wording by rule kind

- Do not shorten everything uniformly. Choose the form by the kind of rule: one line, one
  command for a prohibition or a requirement; the reason and the conditions of application for a
  judgment that depends on the situation; a contrasting pair of examples for a boundary that is
  easily misread.
- Convey importance through the reason and the conditions of application, not through capitals,
  "never ever", or repeating the same instruction.
- Write a completion or confirmation condition as a demand for observable evidence — command
  output, a diff, a file that exists — not as a self-check question.
- Rule skills: the recommended order of the body is scope, rules, judgment and exceptions,
  examples, evidence of completion.
- Procedural skills: put the scope section first; the rest of the order is free.
- Procedural skills: state the conditions under which the side effects may run in both the body
  and the description.
- Procedural skills: run the side effects only when that work itself was explicitly requested,
  never as a by-product of other work.

## Judgment

**Only what outlasts a model generation belongs here.** Advice tuned to how one model or one
runtime behaves today ages as soon as the next one ships. The norms above are the part of
skill-writing practice that holds regardless of which agent reads the skill, which is also why
they are stated in their own words rather than borrowed from any one vendor's guide.

**Split by domain or by work, not by size alone.** A skill grows either because its domain
genuinely has more to say, or because something from another domain crept in. The first calls
for `references/`, the second for a separate skill. Asking which domain a part belongs to, and
during which kind of work it is read, tells the two apart; a line count does not.

**Size is a cost paid on every read.** A skill read on every task pays for every line on every
task; a skill read once a month can afford more. That is why the measure is frequency times
volume, and why a fixed line budget is not the rule: the right size shifts with the model and
with how often the skill fires.

**A safety reflex has to be where the reading happens.** Moving an incident procedure to
`references/` is sound, but an agent that has not yet recognised the incident will not open that
file. The first move — report, or stop for approval — stays in the text that is always read.

**A name survives where a path breaks.** Skills are installed one by one, so a neighbour may
simply be absent. A reference by name then degrades to a skill that is not read; a path, or a
step that leans on one runtime's command or frontmatter field, breaks the skill outright in the
environments that lack it. Stating a bundled script's requirements is the same courtesy: the
reader learns what must exist before the first run fails.

**Other text points at a skill's words.** Headings, the skill name and the meaning of a rule are
what other skills, documents and users' habits refer to. Adding a section leaves every existing
reference true; rewriting a rule in place silently changes what those references mean, which is
why a meaning change is declared rather than passed off as rewording.

**Duplication across skills beats a shared source.** A skill directory is installed on its own.
A rule pulled out into one shared document makes every skill depend on it, and one edit there
changes all of them without anyone reviewing each. Within a single skill, duplication has no such
excuse, so it is merged.

**Triggering is not permission.** A description is read to decide whether to load a skill.
Loading a procedural skill as a candidate is not a request to run its side effects, which is why
the conditions for running them are written in both places and why a by-product run is excluded.

**A description full of rules crowds out the triggers.** Rule contents in the description are
read on every triggering decision, add nothing to that decision, and push aside the words that
would have matched the user's request.

**Emphasis stops working; reasons do not.** Capitals and repetition are read differently by
different models, and a model that takes them literally over-applies the rule. A stated reason
lets the reader apply the rule where it fits and nowhere else.

## Examples

Where a part of a growing skill belongs:

```
Bad:  a commit-conventions skill with a section on tagging releases
      (different work: releasing, so a separate skill)
Bad:  a commit-conventions skill carrying a references file on responding to a leaked secret
      (it happens during a commit, but its domain is secret handling: it belongs in the
      references of the secret-handling skill)
Good: the secret-handling skill keeps its leak-response procedure under references/, with
      "report first" and the name of that file in SKILL.md
```

A description that carries the rules, and one that carries the triggers:

```
Bad:  "... walk each layer through a fixed ladder, stop at the first rung that holds, and record
      a one-line reason ..."
Good: "Reuse before build: layer decomposition, search ladder, adopt-or-build records. Use before
      deciding how to implement something new ..."
```

Relying on one runtime's frontmatter, and not relying on it:

```
Bad:  "Writes are blocked by the tool restriction in the frontmatter, so no write check is needed."
Good: "Do not write files in this skill." — with the frontmatter restriction as an extra guard
```

Removing duplication by creating a shared source, and accepting it:

```
Bad:  two skills state the same rule, so it is moved into one shared document both read
      (one edit there now changes both skills unreviewed)
Good: each skill states the rule in full
```

A confirmation gate as a question, and as evidence:

```
Bad:  "Have you confirmed the tests pass?"
Good: "Show the test run output, with the pass count."
```

## Evidence

Show these in the skill as written, rather than asserting it follows this rule.

- **Scope comes first**: the first section of the body states what the skill governs and what it
  does not, naming the neighbouring skills for the excluded parts.
- **The description triggers**: it names the domain, the work and situations, and the users'
  words, and it contains no rule procedure or condition — except, for a procedural skill, the
  conditions for running its side effects.
- **Situational content is routed**: every file under `references/` is named in `SKILL.md`
  together with the situation in which to read it, and safety reflexes remain in `SKILL.md`.
- **Nothing escapes the directory**: a search of the skill for parent-directory references and
  for other skills' paths finds nothing; other skills appear by name only.
- **Runtime requirements are stated**: every bundled script has its runtime and commands listed
  in `SKILL.md`.
- **Kind-specific norms are labelled**: each norm that applies to only one kind of skill says
  which kind.
- **Procedural conditions appear twice**: for a procedural skill, the conditions for running its
  side effects appear in both the body and the description.
- **A partial revision stays partial**: the diff of a revision touches the part being changed;
  a meaning change in it is declared as one in the change's description.
