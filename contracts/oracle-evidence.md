# Oracle evidence conditions

Source: the skill `ba0918-verification` (agentic-rules). This contract carries the conditions
under which an oracle counts as evidence, for the steps that write requirements or plans and
do not read that skill. A copy records the agentic-rules release version it was taken from.

An oracle — a test, a check, or a fixture — counts as evidence only when the condition it
produces has a named operational producer in a supported environment (untrusted input arriving
at a boundary is one), its subject is the
product or a check rather than the oracle itself, the rule it enforces is stated by the
specification, and every wording, file layout, or internal name it pins is declared there as
a contract. An oracle that fails any of these is a cost: do not add it, keep it in a change
under review, or demand it.

A requirement whose only oracle would fail these conditions is not mechanically verifiable:
when it is not code, verify it by a human-run check or by the platform's own checker; when it
is code, drop the requirement and let the failure join a generic error path a reachable
failure already proves — never resolve it by having the implementer build the fixture.
