# Changelog

All notable changes to `repo-workflow` are documented in this file.

## [0.3.1] - 2026-11-13

- Add per-skill `CHANGELOG.md` and adopt per-skill release tags (`repo-workflow-vX.Y.Z`).

## [0.3.0] - 2026-11-13

- Move the `PR conventions` check to its own `pr-conventions.yml` workflow template so editing a PR title or body does not cancel and restart CI.

## [0.2.1] - 2026-11-13

- Write rendered files with LF line endings on Windows in `bootstrap_repo.py`.

## [0.2.0] - 2026-11-13

- Make the skill agent-neutral and align frontmatter with the Agent Skills specification.
