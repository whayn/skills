# Contributing to Whayn's agent skills

Correctness and reviewable changes come before feature count. Read the
[README](README.md) for current behavior and [AGENTS.md](AGENTS.md) for project
contracts that also bind coding agents.

## Before starting

- Search open and closed issues/PRs and read the current implementation.
- Open a feature/design issue before substantial behavior, schema/format or
  public-interface changes. Agree on scope before a large implementation.
- Small documentation fixes and obvious, narrowly scoped bugs need no prior issue.
- One underlying problem per PR. Do not bundle unrelated cleanup.
- Never include credentials, private data or live configuration. Reproduce
  problems with synthetic fixtures.
- Report vulnerabilities privately; see [SECURITY.md](SECURITY.md).

## Branches

Work from an up-to-date `main`; there is no permanent `develop` branch:

```text
type/short-kebab-description
type/123-short-kebab-description
```

Use the types listed below; the issue number is optional. Dependabot's branches
are exempt. Merged branches are deleted. Never force-push `main`; coordinate
before rewriting a shared PR branch.

## Commits and PR titles

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```text
type(scope): short imperative description
```

| Type | Meaning |
| --- | --- |
| `feat` | New behavior |
| `fix` | Correctness or reliability fix |
| `docs` | Documentation only |
| `test` | Tests and fixtures |
| `refactor` | Restructuring without intended behavior change |
| `perf` | Measured performance improvement |
| `build` | Packaging or build tooling |
| `ci` | CI workflows and checks |
| `chore` | Other maintenance |
| `revert` | Revert a previous change |

Subjects are at most 72 characters, without a trailing period. Use `!` before
`:` and a `BREAKING CHANGE:` footer for incompatible changes, with migration
notes. `Refs #123` links work; `Fixes #123` means it is actually resolved.

Do not add `[verified]`, model names, emoji or invented provenance to titles;
evidence belongs in the PR body. PRs are squash-merged, so CI checks PR titles
rather than every intermediate commit. Use your own Git identity with a verified
noreply email. Maintainer work uses `Whayn <64968114+whayn@users.noreply.github.com>`.

## Development and verification

Use a virtual environment with the pinned tools:

```bash
python -m venv .venv            # then activate it
python -m pip install -r requirements-dev.txt
ruff check . && ruff format --check .
python -m pytest -q -rs
for skill in skills/*/; do agentskills validate "$skill"; done
actionlint                      # when workflows or workflow templates change
git diff --check
```

Tests live in `tests/test_skills.py` (checks every skill must pass) and
`tests/<skill_name>/` (one package per skill). Skill scripts must run on the
oldest Python a skill declares with the standard library only: set
`SKILL_PYTHON` to such an interpreter to run them with it while pytest runs on a
current one. With [`actionlint`](https://github.com/rhysd/actionlint) on `PATH`,
the tests also lint the rendered workflow templates; otherwise they are skipped.

Add a regression test for each bug and, where practical, show that it fails on
the base revision and passes on the fix. Record exact commands and actual
results, and say what was not run. Do not weaken or skip a failing test to get
green CI.

Hosted CI runs quality checks (lint, spec validation, actionlint), tests on
Linux and Windows with the scripts on Python 3.9 and 3.14, a history secret
scan and a PR title/branch convention check. All are required before merging;
the `Tests` check summarizes the whole test matrix.

## Pull requests and review

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md). Mark incomplete work as
a draft and disclose missing verification.

- Include tests and documentation with behavior changes.
- Explain compatibility, migration, privacy and performance implications.
- AI-assisted contributions are welcome; the author owns the result. For material
  agent-assisted work, state which checks were actually run. Do not fabricate
  review or testing claims.
- Automated reviewers: Sourcery reviews automatically; comment
  `@coderabbitai review` if CodeRabbit has not started, and `@codex review` on
  substantive code. A request is not a completed review: triage the actual
  findings and request re-review after substantive fixes. Bots complement tests
  and maintainer judgment; they do not certify correctness.
- Maintainers squash-merge to `main` using the PR title. CI must pass and review
  threads must be resolved. No approval count is required on a solo-maintainer
  project.

## Issues and triage

Use the bug or feature forms; titles start with `bug: ` or `feat: `. Bugs need
versions, a minimal synthetic reproduction, expected/actual behavior and
sanitized evidence. Proposals need the use case, alternatives and bounded
acceptance criteria.

New reports get `needs-triage`. Maintainers classify with `bug`, `enhancement`,
`documentation`, `testing`, `ci`, `security`, `breaking-change` or
`dependencies`; `blocked` marks an explicit dependency. Priority labels are
maintainer-set, not response-time promises. Close an issue as completed only when
its acceptance criteria are met; otherwise use duplicate, not planned or
superseded. Do not bury follow-up work in PR comments: open an issue.

## Releases

Keep `main` working. Version tags use `vMAJOR.MINOR.PATCH` and are protected.
Releases are a maintainer action, never part of an ordinary PR.

---

This workflow is the [repo-workflow skill](https://github.com/whayn/skills/tree/main/skills/repo-workflow).
