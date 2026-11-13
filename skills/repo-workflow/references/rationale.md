# Rationale and sources

Why the workflow looks the way it does. Upstream policies were inspected at the
pinned revisions below and may have changed since. We borrow principles, not
project-specific commands or contribution restrictions.

## Sources

- **Hermes Agent** (`d9397d7b559f75e60395af4e5f1a1f593ee8358c`):
  [CONTRIBUTING](https://github.com/NousResearch/hermes-agent/blob/d9397d7b559f75e60395af4e5f1a1f593ee8358c/CONTRIBUTING.md),
  [AGENTS](https://github.com/NousResearch/hermes-agent/blob/d9397d7b559f75e60395af4e5f1a1f593ee8358c/AGENTS.md).
  Conventional titles/branches, search before work, tests with every change.
- **T3 Code** (`ac8dce0cc3abd8a337f2d806b5082a6834b9b81a`):
  [CONTRIBUTING](https://github.com/pingdotgg/t3code/blob/ac8dce0cc3abd8a337f2d806b5082a6834b9b81a/CONTRIBUTING.md),
  [PR template](https://github.com/pingdotgg/t3code/blob/ac8dce0cc3abd8a337f2d806b5082a6834b9b81a/.github/pull_request_template.md).
  One-problem PRs; concrete verification including what was not checked.
- **hermes-lcm** (`a13e709c25476fa9dc145c61f733f1f4a0443a05`):
  [CONTRIBUTING](https://github.com/stephenschoettler/hermes-lcm/blob/a13e709c25476fa9dc145c61f733f1f4a0443a05/CONTRIBUTING.md).
  Lightweight issue-first design discussion and explicit scope limits.
- **Conventional Commits 1.0.0** for subjects; **Anthropic's multi-agent guidance**
  for the single-agent default (delegation pays off for isolated, parallel or
  specialized work; coordination costs tokens).
- The workflow was first run on [hermes-ariadne](https://github.com/whayn/hermes-ariadne).

## Deliberate choices

| Choice | Why |
| --- | --- |
| One `main`, short-lived `type/slug` branches | No integration branch to drift; branch name states intent |
| Squash merges with the PR title as subject | `main` reads as one conventional commit per change; intermediate commits stay free-form |
| CI checks PR titles, not every commit | Matches what lands on `main` |
| Required checks + linear history + resolved threads, admins included | The owner can't bypass the gates by accident either |
| Zero required approvals | A solo maintainer cannot approve their own PR; bots + CI + owner merge replace it |
| Issue first for substantial changes | Scope and acceptance criteria are agreed before code exists |
| Evidence-first PR template with "what was not tested" | Missing verification is visible instead of implied |
| Several bot reviewers, findings triaged by reproduction | Different bots catch different things; none is trusted blindly |
| Agents push and open PRs; only the owner merges/releases | Work becomes reviewable immediately; irreversible actions stay human |
| Pinned action SHAs, checksum-verified Gitleaks | Supply-chain hygiene; Dependabot keeps pins fresh |
| Small label set and two issue forms | Enough to triage, not a bureaucracy |
| Local git-excluded notebook (`HANDOFF.md`, `.hermes/`) | Session continuity without leaking private evidence |
| Developer tooling in skills, not `AGENTS.md` | `AGENTS.md` stays a portable project contract |

## Evidence levels

Each level is separate evidence; passing one does not establish the next.

1. Unit tests of pure logic.
2. Integration tests against real dependencies with synthetic data.
3. The installed/packaged artifact, outside the source checkout.
4. Real external behavior (live services, real models, real users).
