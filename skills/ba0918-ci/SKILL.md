---
name: ba0918-ci
description: "CI/CD pipeline definitions — GitHub Actions workflows and other CI configuration: following the repository's existing workflows, pinning actions, images and reusable workflows, lockfiles for actions, token permissions, secrets and OIDC in pipelines, untrusted input from pull requests, timeouts, concurrency and caching, keeping logic in scripts, linting workflows. Use when writing or changing a workflow file or CI configuration, adding a job, step or third-party action, setting up CI for a project, or reviewing or auditing CI definitions. 日本語キーワード: CI CD GitHub Actions ワークフロー パイプライン ジョブ ステップ アクション 自動テスト SHA 固定 ピン留め ロックファイル 権限 permissions pull_request_target シークレット OIDC タイムアウト 並行実行 キャッシュ actionlint zizmor"
metadata:
  ba0918-routing: required:ci
---

# CI Pipeline Discipline

## Scope

Applies to every CI/CD pipeline definition kept in a repository — the configuration files that
run jobs on a hosted runner when code is pushed, a pull request is opened, a tag is created, a
run is started by hand, or a schedule fires — whether a person asks for it or an agent adds it
alongside other work. It covers how a definition is shaped: what it runs from outside the
repository, which permissions and secrets reach which step, what it does with input it cannot
trust, how its runs are bounded, and where its logic lives.

The rules are stated independently of any one CI platform. How to write them on a particular
platform is in a reference file for that platform:

- GitHub Actions: read `references/github-actions.md` before writing or changing a workflow.

It does not cover building or administering runners, organisation-wide policy settings,
deployment strategy, the build or tests a pipeline invokes, or the project's own dependencies
managed through its manifest and lockfile. Recognising credentials, keeping them out of staged
changes and responding to a leak are the subject of the skill `ba0918-secrets`; versions, tags
and changelogs are the subject of the skill `ba0918-release`; how a pipeline's behaviour is
verified is the subject of the skill `ba0918-verification`; whether to adopt an outside component
or write one is the subject of the skill `ba0918-reuse`.

## Rules

### Follow the existing shape

- Before writing a new pipeline definition, read the repository's existing ones and follow their
  layout, naming and conventions.
- Where an existing definition breaks a rule here, follow the rule. Do not copy the breach into
  the new definition.

### Pin external code

- Refer to everything the pipeline fetches and runs from outside the repository — actions,
  reusable workflows from other repositories, container images, tools downloaded by a script —
  by an immutable reference: a full commit hash, an image digest, or a version together with a
  checksum. Never by a tag or a branch name.
- Keep the human-readable version as a comment beside each pinned reference.
- Transitive dependencies count too. Where the platform offers a lock mechanism for them and the
  project has adopted it, the lockfile is the source of truth: regenerate it with its own tool and
  never edit it by hand.
- Keep pins current with an automated dependency-update tool configured for the platform. Never
  update by removing the pin.

### Least privilege, stated

- Declare the permissions of the pipeline's token at the top of every definition, with read-only
  access — or none — as the default. Widen them only on the job that needs it.
- Comment every widened permission with the reason it is needed.
- Authenticate to cloud and other external services with short-lived federated credentials
  (OIDC) where the service supports them. Do not store long-lived keys for them.
- Pass a secret only to the step that uses it. Never to the whole pipeline or the whole job.
- Put deployment credentials behind a protected environment: required reviewers, restricted
  branches.
- In a job that does not push, do not leave the checkout's credential available to later steps.

### Untrusted input

- Never run code from an untrusted contributor — a pull request from a fork, for one — in a
  context that holds secrets or write permission.
- Never place event data — pull request titles and bodies, branch names, commit messages, the
  inputs of a manual run — into the text of a script. Pass it as an environment variable and
  quote it in the shell.
- Do not restore caches in a job that releases, publishes or deploys.
- Do not run jobs for untrusted pull requests on reused runners, such as persistent self-hosted
  machines.

### Bounded, predictable runs

- Give every job a time limit.
- Cancel a superseded run for the same branch or pull request when a new one starts. Serialise
  deployments and never cancel one mid-run.
- Derive cache keys from the content of the dependency lockfile.
- Run shell steps so that they stop at the first failure, including a failure inside a pipe.
- Choose runner images and language runtime versions deliberately. Use a name that tracks
  "latest" only when its changing underneath the pipeline is acceptable.

### Structure

- Put logic that branches or decides into a script in the repository, and have the step call it.
  Keep what is written inline in a step to a few lines of invocation.
- Give every pipeline, job and step a name that says what it does.
- Do not rename a job registered as a required check except as one change together with the
  required-check setting.
- Move a sequence repeated across pipelines into the platform's reuse mechanism — a reusable
  workflow, a composite action or its equivalent — instead of copying it.
- Trigger only on the events the pipeline needs. Where a path filter meets a required check,
  confirm that a run skipped by the filter does not leave the check pending forever.

## Judgment

**A pipeline is privileged code that runs other people's code.** It holds secrets and write
access, and it executes actions and images fetched at run time. A tag can be moved to point at
different code without any change in the repository that uses it; a commit hash cannot. That is
why pinning applies to every external reference, including those published by the platform
itself: an official publisher's tags are no less movable.

**Each outside action is a supply-chain entry point.** Before adding one, consider whether a few
lines of script would do. Every action added is one more thing to pin, update and trust with
whatever the job can reach. Whether to adopt or write is decided as the skill `ba0918-reuse`
describes; in a pipeline, add to that judgment the fact that the component runs next to secrets.

**Untrusted data is code once it is pasted into a script.** The platform expands event data into
the script text before the shell runs it, so a branch name containing shell syntax executes.
An environment variable reaches the shell as data. The same holds for fork code run under a
trigger that grants secrets: the trigger decides the privilege, the checkout decides whose code
runs with it.

**Logic in scripts can be run where it is written.** A script can be executed locally, tested,
and kept when the CI platform changes. Logic inside the pipeline definition can be tried only by
pushing, and is locked to the platform. Testing then targets the script, not the definition's
text, as the skill `ba0918-verification` describes.

**Where this rule is silent, the repository's existing shape decides.** File names, how jobs are
split and their order are left to the project. A repository with no pipelines yet follows the
skeleton in the platform's reference file. Uniformity across one repository's pipelines is what
lets a reader move between them without re-learning each.

**Prefer what the platform enforces to what a rule asks.** Where the platform can enforce a rule
here — an organisation policy requiring pinned actions, a protected environment, a lockfile the
runner verifies — that enforcement is stronger than this text. Adopting a platform mechanism
that is still in preview is the project's decision.

## Examples

Shown in GitHub Actions syntax; the contrast is the same on any platform.

Referring to an external action:

```
Bad:  uses: some-org/some-action@v3
Good: uses: some-org/some-action@<full commit hash>  # v3.2.1
```

Using event data in a script:

```
Bad:  run: echo "Checking ${{ github.event.pull_request.title }}"
Good: env:
        PR_TITLE: ${{ github.event.pull_request.title }}
      run: echo "Checking $PR_TITLE"
```

Permissions:

```
Bad:  (no permissions declared; the job gets whatever the repository default grants)
Good: permissions:
        contents: read      # at the top; a release job alone widens to contents: write
```

Where the logic lives:

```
Bad:  a 40-line inline shell step that decides which packages to publish
Good: run: scripts/publish-changed-packages.sh   (tested like any other script)
```

## Evidence

Show these outputs rather than asserting the pipeline is sound.

- **The definition passes its checker**: the platform's workflow linter run on every changed
  definition, with no findings.
- **The security audit is clean**: a static security analyser for the platform run on every
  changed definition, with no findings, or each remaining finding named with the reason it stays.
- **The pins are pins**: a search of the changed definitions for external references showing none
  by tag or branch.
- **It ran**: the result of an actual run of the changed pipeline — its link and conclusion. Where
  the change cannot be pushed from the current environment, say so and name what is unconfirmed.
