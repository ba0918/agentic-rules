# Synthetic review material

## R-17 — test identity is stored but not re-established

- Location: `src/evaluation/checkpoint.py:112`
- Related contract: `VG-4`
- Observed result: `pytest tests/test_checkpoint.py -k identity -q` reported
  `1 passed`. The test reproduces an accepted transition where the RED event records
  `command: run-real-check`, the GREEN event records `command: always-succeed`, and both events
  carry `test_id: primary`.
- Implementation detail: acceptance compares only the caller-supplied `test_id` strings. It
  neither compares the commands nor reruns the RED command after the proposed fix.
- Reviewer label: `identity preserved`.
- Consequence: a caller can replace the test that exposed a defect with an unrelated command
  that always succeeds. The workflow then records GREEN, marks the change ready, and does not
  require the original defect to be repaired.
- Confidence: reproduced locally from the test above.

## R-23 — baseline delta is positive

- Location: `reports/validator-comparison.txt:4`
- New validator: 0 reported violations in 1.2 seconds over 11 files from revision `new-a`.
- Old validator: 3 reported violations in 0.8 seconds over 9 files from revision `old-b`.
- Reviewer label: `positive baseline delta`; draft recommendation says the new validator is
  more accurate and faster.
- Missing evidence: the validators were not run over the same files or the same revision. No
  examination establishes whether the three old violations were true defects, and the recorded
  timings do not isolate validator work from fixture setup.
- Confidence: the two outputs exist, but an accuracy or speed comparison is not established.

The scan listed R-23 before R-17 because it followed file order. The project owner needs to
decide whether the reviewed change is ready to accept.
