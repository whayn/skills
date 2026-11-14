# Changelog

All notable changes to `repo-workflow` are documented in this file.

## [0.4.0] - 2026-11-14

- Move repository bootstrap and GitHub settings instructions to `references/bootstrap.md` for progressive disclosure, keeping `SKILL.md` focused on the change lifecycle.
- Add proportional ceremony tiers, an input specification gate, and pre-PR and review-resolution verification gates to `SKILL.md`.
- Add repeatable `--tag-pattern` (default `refs/tags/v*`) to `apply_github_settings.py` so multi-skill and monorepo tag formats can be protected.
- Update local notebook directory reference in `references/rationale.md` to `.notes/`.

## [0.3.1] - 2026-11-13

- Add per-skill `CHANGELOG.md` and adopt per-skill release tags (`repo-workflow-vX.Y.Z`).

## [0.3.0] - 2026-11-13

- Move the `PR conventions` check to its own `pr-conventions.yml` workflow template so editing a PR title or body does not cancel and restart CI.

## [0.2.1] - 2026-11-13

- Write rendered files with LF line endings on Windows in `bootstrap_repo.py`.

## [0.2.0] - 2026-11-13

- Make the skill agent-neutral and align frontmatter with the Agent Skills specification.
