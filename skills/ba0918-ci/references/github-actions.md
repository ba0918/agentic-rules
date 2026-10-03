# GitHub Actions

How the rules of this skill are written in GitHub Actions workflows (`.github/workflows/*.yml`).
The rules themselves are in `SKILL.md`; this file gives their form on this platform.

## Skeleton

A repository with no workflows yet starts from this shape. A repository that already has
workflows follows its own shape first, and this file only where that shape breaks a rule.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

# Read-only by default; a job that must write widens its own permissions.
permissions:
  contents: read

# A newer push to the same branch or pull request supersedes the running check.
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

defaults:
  run:
    shell: bash

jobs:
  test:
    name: Test
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - name: Check out
        uses: actions/checkout@<full commit hash>  # vX.Y.Z
        with:
          persist-credentials: false

      - name: Run tests
        run: scripts/test.sh
```

## Rule by rule

### Pin external code

- `uses:` takes `owner/repo@<40-character commit hash>` with the version as a trailing comment.
  This applies to `actions/*` too, and to `uses:` of a reusable workflow in another repository.
- A local action or workflow in the same repository (`uses: ./...`) is versioned with the
  repository and needs no hash.
- A container image (`container:`, `services:`, `docker://`) is pinned by `@sha256:<digest>`.
- Resolve a tag to its commit with `git ls-remote https://github.com/<owner>/<repo> refs/tags/<tag>`.
  For an annotated tag, take the line ending in `^{}`, which is the commit.
- Keep pins current with Dependabot's `github-actions` ecosystem (`.github/dependabot.yml`) or
  Renovate. Both update the hash and the version comment together. Set a cooldown (Dependabot's
  `cooldown.default-days`, Renovate's `minimumReleaseAge`) so a new release is proposed only after
  it has been public for some days; a compromised release is usually noticed and pulled within that
  window.
- GitHub has published a lockfile for workflow dependencies, transitive ones included
  (`.github/workflows/actions.lock`), and a `gh` extension that generates it. Both are in preview
  before 1.0 and state that the format and commands may change without notice. Adopting it is the
  project's decision. Once adopted, the lockfile is regenerated with its tool, never edited by
  hand, and the tool's own current documentation is the guide — not a copy of its commands kept
  elsewhere.
- An organisation or repository can require full-hash pinning by policy in its Actions settings.
  Where that policy is on, an unpinned reference fails the run.

### Least privilege, stated

- Declare `permissions:` at the top of every workflow: `contents: read`, or `{}` when the workflow
  needs no repository access. A job that writes declares its own `permissions:`; a job-level block
  replaces the workflow-level one for that job, so it lists every scope the job needs.
- OIDC: the job needs `id-token: write`, and the cloud provider's official login action exchanges
  the token. Restrict the trust policy on the provider side to the repository and the branch or
  environment that deploys.
- Pass secrets with `env:` on the step that uses them, not on `jobs.<id>.env` or the workflow's
  top-level `env:`.
- Deployment jobs set `environment:` naming an environment with protection rules.
- `actions/checkout` keeps a credential for later git commands unless `persist-credentials: false`
  is set. Set it on every checkout in a job that does not push.
- Prefer the workflow's `GITHUB_TOKEN` over a personal access token. When another identity is
  needed, prefer a GitHub App installation token, which is scoped and short-lived.

### Untrusted input

- `pull_request_target` and `workflow_run` run with the base repository's secrets and a token that
  can write, even for a pull request from a fork. Under them, never check out or execute the pull
  request's code (`ref: ${{ github.event.pull_request.head.sha }}` or similar). Use `pull_request`
  to build and test contributors' code; it receives no secrets for forks.
- Since 2025-12-08, `pull_request_target` always takes the workflow file from the default branch.
  That stops an outdated workflow on another branch from running; it does not make checking out the
  pull request's code safe.
- Treat as untrusted: `github.event.pull_request.title`, `.body`, `.head.ref`, `github.head_ref`,
  `github.event.issue.title`, `.body`, `github.event.comment.body`, commit messages and author
  names, and `inputs.*` of `workflow_dispatch`. Move each to `env:` and use the variable in `run:`.
  The same holds for the `script:` of `actions/github-script`: read the value from
  `process.env`, not from an expression pasted into the script.
- Write to `$GITHUB_ENV` and `$GITHUB_OUTPUT` only values that are not attacker-controlled; a
  newline in such a value can define further variables.
- Release and deploy workflows do not use `actions/cache` or a setup action's `cache:` option.
- Public repositories do not run pull request jobs on self-hosted runners.

### Bounded, predictable runs

- `timeout-minutes:` on every job. The default is 360 minutes.
- `concurrency:` with `cancel-in-progress: true` for checks; for deployments, a fixed group per
  environment with `cancel-in-progress: false`.
- Use the setup action's built-in cache (`cache:` on `actions/setup-node`, `actions/setup-python`
  and similar), which keys on the lockfile. With `actions/cache`, key on
  `hashFiles('<lockfile>')`.
- `defaults.run.shell: bash` runs steps with `bash --noprofile --norc -eo pipefail`. The implicit
  default shell on Linux omits `-o pipefail`.
- `runs-on: ubuntu-latest` moves to a new image without notice; a versioned label such as
  `ubuntu-24.04` moves only when changed.

### Structure

- `name:` on the workflow, every job and every step.
- A required check is matched by the job's name as it appears in the check list. Renaming the job
  leaves the old required check waiting.
- A workflow-level `paths:` filter that skips the run leaves a required check from that workflow
  pending. Either do not make that job required, or filter inside the job instead.
- Reuse: a reusable workflow (`on: workflow_call`) for whole jobs; a composite action
  (`action.yml` with `runs.using: composite`) for a sequence of steps.

## Evidence on this platform

- **actionlint**: `actionlint` run in the repository (it finds `.github/workflows/` itself),
  showing no findings. It also runs shellcheck on `run:` scripts where shellcheck is installed.
- **zizmor**: `zizmor .github/workflows/` showing no findings, or each remaining finding named
  with the reason it stays. It checks pinning, permissions, credential persistence, template
  injection and dangerous triggers.
- **Pins**: a search of the changed workflows for `uses:` lines whose reference is not a
  40-character hash, excluding local `./` references, finding nothing.
- **It ran**: the run's URL on the Actions tab and its conclusion.
