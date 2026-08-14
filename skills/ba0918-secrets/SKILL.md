---
name: ba0918-secrets
description: "Handling credentials in a working repository — recognising keys, tokens and environment files, keeping them out of staged changes, keeping them out of logs, prompts and commit messages, and the first moves when one leaks. Use when touching configuration or environment files, staging changes, pasting output, writing a commit message, or responding to a suspected credential leak. 日本語キーワード: 機密情報 シークレット 認証情報 APIキー トークン 環境変数 .env 漏洩 露出 失効 ローテーション"
metadata:
  ba0918-routing: always
---

# Secret Handling

## Scope

Applies to credentials that pass through a working repository or an agent session: API keys,
access tokens, private keys, passwords, connection strings, session cookies, and the environment
files that hold them.

It covers four things: recognising a credential, keeping it out of version control, keeping it
out of anything that gets recorded or transmitted, and the first moves after a leak.

It does not cover secret storage systems, key management design, or access control policy.

## Recognising a credential

| Signal | Examples |
|---|---|
| Environment files | `.env`, `.env.local`, `.env.production`, `credentials`, `secrets.yaml` |
| Key material | `id_rsa`, `*.pem`, `*.key`, `*.p12`, `*.keystore` |
| Provider token shapes | a fixed vendor prefix followed by a long random tail |
| High-entropy assignment | a name containing `key`, `token`, `secret`, `password`, or `credential` assigned a long opaque literal |
| Connection strings | a URL carrying a username and password in its authority section |

Treat a value as a credential when it grants access on presentation. Length and randomness are
hints, not the test.

## Rules

- Never stage a credential. Never commit one.
- Never add an environment or key file to version control; add it to the ignore file instead.
- Stage files individually and read what you are staging before committing.
- Keep the real value out of commit messages, branch names, and pull request text.
- Keep the real value out of logs, error messages, and anything printed to a terminal.
- Keep the real value out of prompts, issue reports, and pasted output; replace it with a placeholder.
- Reference a credential by the name of its variable, never by its value.
- Use an obviously fake placeholder in documentation and tests, never a real value that is "expired".
- Report a suspected leak as the first, blocking task — before any fix, and never quietly.
- While approval for the response is pending, stop external operations that involve the affected
  credential.
- Revoke first, clean history second. Urge revocation as the first move; a human executes it, or
  the agent does only under explicit approval.

## Judgment

**Revocation is the only action that actually stops a leak.** Rewriting history removes the value
from the current branch, but the value may already exist in a clone, a fork, a CI log, a
notification, or a build cache. Until it is revoked and replaced, assume it is live. History
cleanup matters, but it is the second step, not the first.

**Revocation is irreversible in the same way rewriting shared history is.** A revoked credential
cannot be un-revoked, and cutting it can break running services far beyond the current session.
So the agent's part is to raise the alarm and push for revocation, not to execute it: a human
runs the revocation, or the agent does under explicit approval. Reporting first is not a delay —
it is what makes the exposure known to the people who own the credential, so containment does not
depend on one session quietly handling it.

**Redaction has to happen before the value is recorded, not after.** Once a credential reaches a
log file, a chat transcript, or a model prompt, you no longer control every copy. The moment to
substitute a placeholder is when you first handle the value.

**"It is only a development key" is not a category.** Development credentials routinely reach
shared infrastructure and are rarely scoped as narrowly as assumed. Apply the same rules and
decide the blast radius during revocation, not during staging.

**Bulk staging is the usual cause.** Adding everything at once is how environment files and key
material enter history, and history is expensive to correct once pushed. Individual staging is
the mechanism that makes the rule enforceable.

**A near-miss is worth recording.** When a credential nearly reached a commit, add the path to
the ignore file so the same near-miss cannot recur.

## Examples

A value exposed in a message, and the same fact stated safely:

```
Bad:  fix: API キー <実際のキー文字列を貼り付け> が失効したので差し替え
Good: fix: 決済 API の認証情報を差し替え（旧キーは失効済み）
```

A sample that invites copying, and one that cannot be mistaken for real:

```
Bad:  PAYMENT_API_KEY=<a realistic-looking vendor-prefixed literal>
Good: PAYMENT_API_KEY=<your-secret-key>
```

The Bad line above is written as a description rather than as a literal on purpose: a
documentation sample shaped like a real credential gets copied verbatim, and gets flagged by
every scanner that reads this file.

Staging that leaks, and staging that does not:

```
Bad:  git add -A
Good: git status --short   # read it
      git add src/config/loader.ts
```

## First moves after a leak

1. **Revoke and rotate** the credential at its provider, before any cleanup. Report the leak as
   the first, blocking task and urge immediate revocation; a human executes it, or the agent does
   only under explicit approval. While that approval is pending, stop external operations that
   involve the affected credential.
2. **Determine the exposure**: which commits, branches, remotes, logs, CI runs, and transcripts
   contain it. Assume anything pushed has been fetched.
3. **Remove it from history** and force-update the affected refs, coordinating with anyone who
   has a clone.
4. **Prevent recurrence**: add the path to the ignore file and record what allowed it through.

Executing the revocation in step 1 cuts off a live credential and step 3 rewrites shared
history; both are irreversible — get explicit approval before executing either. Reporting the
leak and urging revocation are not gated on that approval: they come first, precisely so the
approval can be given.

## Evidence

Show these outputs rather than asserting nothing leaked.

- **What is staged**: `git status --short` and `git diff --cached --name-only` before committing,
  containing no environment file, key file, or credential path.
- **Content scan**: a search of the staged diff for credential-shaped assignments
  (for example `git diff --cached | rg -n "(api[_-]?key|secret|token|password)\s*[=:]"`),
  reviewed line by line.
- **Ignore coverage**: `git check-ignore -v` naming the rule that excludes each environment or key
  file present in the working tree.
- **History is clean**: `git log --all --full-history -- <path>` for each credential path,
  returning no commits.
- **Revocation**: the provider's confirmation that the old credential is inactive, dated after the
  exposure.
