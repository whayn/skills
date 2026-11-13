# Working on Whayn's agent skills

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

- Skills are agent-neutral and follow the [Agent Skills specification](https://agentskills.io/specification):
  frontmatter uses only `name` (equal to the directory), `description`,
  `license`, `compatibility`, `metadata` (string values) and `allowed-tools`;
  `agentskills validate` must pass. Bump `metadata.version` (semver) when
  behavior changes.
- Instructions name plain shell commands, never one agent's tool-call syntax,
  commands or directories. Agent-specific notes belong in the README.
- Scripts are standard-library Python that runs on the oldest version the skill
  declares, on Linux and Windows; templates must render with no leftover
  placeholders and pass `actionlint` when they are workflows.
- Each skill has its tests in `tests/<skill_name>/`; `tests/test_skills.py`
  holds the checks every skill must pass.
- Skills must not contain machine-local paths, credentials or personal data.

## Code Review Rules

- Flag a script that mutates a repository or GitHub settings without a dry-run
  default, or that overwrites existing files without an explicit flag.
- Flag skill instructions that grant agents irreversible actions (merge, release,
  force-push, settings) without the owner's approval.
- Flag template changes not covered by a rendering test.
