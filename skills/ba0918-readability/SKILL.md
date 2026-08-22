---
name: ba0918-readability
description: "Readability rules for every human-facing response, report, document, question, and approval request — preserving technical meaning while explaining unfamiliar terms, references, uncertainty, choices, and long results where people can understand and act on them. Use whenever an AI writes for a person. 日本語キーワード: 可読性 人間向け 説明 報告 質問 選択肢 承認 専門用語 平易な言葉 情報量 提示方法"
metadata:
  ba0918-routing: always
---

# Human-Readable Output

## Scope

Apply this rule to every human-facing response, question, review, report, specification,
plan, explanation, approval request, and delivery choice. Make the content understandable;
leave correctness, evidentiary sufficiency, agreement with the conclusion, and whether a human
decision is required to the rules responsible for those judgments.

## Rules

- Write for an intelligent reader who may be new to the subject; preserve the reasoning, evidence,
  conditions, and uncertainty that let them think for themselves.
- Translate rather than merely shorten when detail matters: connect what happened, its effect, its
  cause, what is confirmed or unconfirmed, and where the evidence can be checked.
- Use established technical terms when their meaning is clear; do not replace an explanation with
  a coined term, abbreviation, project name, code identifier, or context-dependent label.
- State the concrete meaning before naming an internal term, clause, file, symbol, or log; retain
  those references afterward when they make the claim traceable.
- Explain a term once per artifact unless its meaning changes; do not add dictionary definitions
  for familiar terms or repeat the same conclusion in different words.
- Put what must be decided, why it matters, and what each choice changes next to the decision;
  present interdependent choices together instead of as context-free questions.
- Put long results in a surface suited to reading and place important information where it is
  visible at the point of action; do not duplicate the same full result in a narrow chat surface.
- State plainly when the available evidence cannot support a conclusion and why; never fill a gap
  with a fluent guess or hide uncertainty to make the explanation read smoothly.

## Judgment

Treat pasted terminology as evidence of the reader's source material, not proof that the reader
understands it. Treat a term as already known in the current conversation only when the reader uses
it in their own words, explicitly declines explanation, or the same artifact has already established
its meaning.

Choose paragraphs, bullets, headings, and length for the relationships the reader must follow. Do
not require a fixed template. A long explanation can pass when its meaning remains navigable, and a
short one can fail when it leaves only labels or choices without context.

Keep readability separate from truth. An understandable claim can still be wrong, unsupported, or
unacceptable; an accurate claim can still be unreadable. Report each boundary without implying that
one settles the others.

## Examples

Bad:

> Test identity is stored but not re-established, so the GREEN event is accepted.

Good:

> The workflow does not check that the test which passes after the change is the same test that
> failed before it. Someone could replace the failing test with one that always succeeds and the
> change would still be recorded as fixed. The code calls this relationship `test identity`.

## Evidence

Judge the result by observable understanding, not by style proxies alone:

- An independent reader can explain in their own words what happened, why it matters, and what
  remains uncertain.
- Each material statement, condition, and uncertainty still maps to the source rather than
  disappearing during translation.
- A reader can understand the claim from the artifact and then follow its retained references to
  the specification, code, or verification result.
- Missing evidence remains visibly missing instead of becoming a confident comparison or
  conclusion.

Use counts such as words, sentence length, headings, or technical terms only as signals to inspect;
never use those counts alone as the acceptance criterion. Do not turn comprehension into a ritual by
asking every reader to confirm it on every output.
