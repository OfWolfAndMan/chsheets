---
title: GitHub Actions
summary: GitHub Actions — workflows, matrix builds, caching, secrets, permissions
tags: [ci, github, automation]
tooling: [github actions, actionlint, yq]
verified_on: 2026-11-10
verified_env: actionlint 1.7.12 against every workflow snippet on this page
status: verified
---

# GitHub Actions

Every YAML block on this page passes `actionlint` 1.7.12. Nothing was executed on
GitHub — there is no runner here — so this sheet is verified for structure and
expression validity, and unverified for runtime behaviour.

```bash
actionlint .github/workflows/*.yml      # local check; worth a pre-commit hook
```

## A minimal workflow

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest -q
```

`permissions` at the top applies to every job. Without it the token carries the
repository's default, which is often write.

## Triggers

```yaml
name: triggers
on:
  push:
    branches: [main]
    paths: ["src/**", "pyproject.toml"]
  pull_request:
    types: [opened, synchronize, reopened]
  schedule:
    - cron: "17 9 * * *"
  workflow_dispatch:
    inputs:
      environment:
        description: target
        required: true
        default: staging
  release:
    types: [published]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ github.event_name }}"
```

`paths` filters are how you avoid running a documentation workflow on every commit —
and how you accidentally skip the one commit that changed both a doc and the code.

## Jobs, needs, matrix

```yaml
on:
  pull_request:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pipx run ruff check .

  test:
    needs: lint
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        python: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -e ".[test]"
      - run: pytest -q
```

`fail-fast: false` lets the whole matrix finish, which is what you want when the
question is "which combination is broken" rather than "is anything broken".

## Caching

```yaml
name: test
on:
  push:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      - run: pip install -r requirements.txt
```

`hashFiles` on the lock file is the key design: the cache invalidates exactly when the
dependencies change. A cache keyed on the workflow name alone serves stale packages
forever and is worse than no cache.

## Artifacts

```yaml
name: test-reports
on:
  push:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest --junitxml=reports/junit.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: reports/
          retention-days: 7
```

`if: always()` is what makes the report exist when the tests failed — the case where
you need it.

## Secrets and variables

```yaml
name: deploy
on:
  workflow_dispatch:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
        env:
          TOKEN: ${{ secrets.DEPLOY_TOKEN }}
          ENVIRONMENT: ${{ vars.ENVIRONMENT }}
```

- `secrets.*` are masked in logs; `vars.*` are plain configuration and shown.
- A secret passed as a command-line argument appears in the process list and often in
  logs. Pass it through the environment and read it in the program.
- Pull requests from forks do not receive secrets. A workflow that "works on branches
  but not on fork PRs" has found this rule, not a bug.

## Permissions

```yaml
name: oidc-deploy
on:
  workflow_dispatch:
permissions:
  contents: read
  pull-requests: write
  id-token: write     # required for OIDC to a cloud provider
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

Least privilege per job, not per repository. `id-token: write` plus a cloud trust
policy removes long-lived cloud keys from the repository entirely — the single biggest
security improvement available in most Action setups.

## Concurrency

```yaml
name: deploy
on:
  push:
    branches: [main]
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

Without this, two pushes to the same branch produce two deploys racing over the same
environment, and the loser usually wins.

## Reusable workflows and composite actions

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest -q
```

```yaml
# caller workflow
on:
  pull_request:
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: "3.13"
```

A reusable workflow takes `inputs` and `secrets`; a composite action
(`action.yml` with `runs: using: composite`) packages steps. Workflows for
orchestration, composite actions for step bundles.

## Expressions and contexts

```yaml
name: release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Only on main
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: ./release.sh
      - name: Skip on docs-only commits
        if: "!contains(github.event.head_commit.message, '[skip ci]')"
        run: make build
```

Quote an expression that starts with `!` — YAML reads a bare `!` as a tag and the
workflow fails to parse with an error that does not mention it.

## Security notes

- Pin third-party actions to a commit SHA, not a tag: a tag is mutable and belongs to
  someone else. `uses: owner/action@<40-char-sha>` with a comment naming the version.
- `pull_request_target` runs with repository secrets and can be triggered by a fork.
  Use it only with extreme care, and never check out the fork's code in it.
- `GITHUB_TOKEN` is scoped to the repository; it is not a substitute for a personal
  token, and it should stay `contents: read` unless a step genuinely writes.

## Traps worth remembering

- A workflow that never runs is usually a `paths` filter or a branch name that no
  longer exists.
- `actions/checkout` is not implied; a job without it has an empty workspace.
- Caches are scoped by branch: a cache created on a PR is not visible to `main`.
- `runs-on: ubuntu-latest` is a moving target — pin `ubuntu-24.04` when reproducibility
  matters more than freshness.
- Job-level `env` does not inherit into `uses:` steps the way you expect; pass values
  explicitly through `with:`.
