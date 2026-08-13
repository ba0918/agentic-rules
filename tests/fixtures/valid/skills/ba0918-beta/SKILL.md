---
name: ba0918-beta
description: Baseline fixture skill carrying a trigger-scoped routing value and a skill-internal reference. 日本語キーワード: 正常系 参照あり
metadata:
  ba0918-routing: required:commit
---

# Beta

## Scope

Applies to nothing real. This document exists so the validator has a conforming skill that
also owns a `references/` file.

## Rules

- Reference skill-internal files only, as in [notes.md](references/notes.md).

## Evidence

- `python3 scripts/validate.py tests/fixtures/valid` exits 0.
