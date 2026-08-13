---
name: ba0918-alpha
description: "Baseline fixture skill that satisfies every repository convention. Use when exercising the validator against a clean repository. 日本語キーワード: 正常系 サンプル"
metadata:
  ba0918-routing: always
---

# Alpha

## Scope

Applies to nothing real. This document exists so the validator has a conforming skill to read.

## Rules

- Keep the fixture conforming.

## Evidence

- `python3 scripts/validate.py tests/fixtures/valid` exits 0.
