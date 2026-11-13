# Working on {{PROJECT}}

Read `CONTRIBUTING.md` and `README.md` before changing behavior. This file holds
stable project contracts for every contributor and coding agent. Personal
developer tooling, model routing and orchestration preferences do not belong here.

- Keep changes small, source-backed and tested. Discuss substantial behavior,
  format or interface changes in an issue first; use a focused branch and PR.
- Use `type(scope): description` subjects and `type/kebab-description` branches.
  Do not add verification badges or AI co-author identities. Use the configured
  contributor identity; do not alter global Git settings.
- Write a failing behavior test before a fix, then run the focused and full
  checks. Do not weaken assertions, skip failures or mock the boundary being claimed.
- Report actual command output, including failures and skips. Never present
  inferred or generated results as executed ones. Distinguish unit tests,
  integration tests and real external behavior.
- Treat agent, bot and tool reports as claims to verify against the diff, the
  artifacts and real exit codes.
- Never commit credentials, private data or live configuration. Use synthetic
  fixtures and disposable directories.
- Push finished feature branches and open PRs. Do not merge, tag, release,
  deploy, force-push shared branches or change repository settings without the
  maintainer's explicit approval. Do not rewrite published `main` history.
- Keep attribution and license notices when porting code.

## Project specifics

<!-- Architecture boundaries, invariants that must never break, data that must be
preserved, environments that must not be touched, and anything that tightens the
defaults above. Keep it short and stable. -->

## Code Review Rules

<!-- Reviewers (including @codex) read this section. List what should block a PR
in this project, e.g. lost data, unbounded resource use, unsafe defaults,
behavior claimed without a test. -->
