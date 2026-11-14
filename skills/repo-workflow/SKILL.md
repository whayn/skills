---
name: repo-workflow
description: Bootstrap and run an evidence-first GitHub repository workflow (spec/issue, branch, tests first, verified PR, bot review and CI, owner merge). Use when setting up a new repository, adopting the workflow in an existing one, making any change in a repository whose CONTRIBUTING.md points to this skill, or doing repository housekeeping.
license: MIT
compatibility: Any coding agent that can run shell commands. Needs git and Python 3.9+; applying GitHub settings needs the GitHub CLI (gh) with admin rights.
metadata:
  author: whayn
  version: "0.4.0"
  source: https://github.com/whayn/skills
---

# Repo Workflow

An issue/spec → branch → tests-first → verified PR → bot review + CI → owner-merge
workflow for GitHub projects maintained with coding agents.

- **Static project contract (`AGENTS.md`, `CONTRIBUTING.md`):** lives in each repository and defines its exact commands, architecture boundaries and conventions.
- **Operational playbook (this `SKILL.md`):** how to size changes, lock specifications before coding, verify honestly, triage bot reviews and hand off.
- **One-time bootstrap & GitHub settings (`references/bootstrap.md`):** read `references/bootstrap.md` only when scaffolding a repo, adopting this workflow, or updating branch protection / required checks / tag rulesets (`scripts/bootstrap_repo.py` and `scripts/apply_github_settings.py`, both dry-run first).

Don't use for: one-off scripts without a remote, or repositories whose owners run a different process (follow theirs).

## Authority

Defaults; a project may tighten them in its `AGENTS.md` "Project specifics".

| Agent may do without asking | Requires the owner's explicit approval |
| --- | --- |
| Create branches/worktrees, commit on feature branches | Merge any PR (`gh pr merge`) |
| Push feature branches, open draft or ready PRs | Tags, releases, deployments, package publishing |
| Trigger bot reviews, reply to and resolve its own review threads | Force-push a shared branch; anything on `main` after bootstrap |
| Open issues for follow-up work | Close an issue not resolved by a merged `Fixes #N` |
| Run `bootstrap_repo.py --dry-run` or `apply_github_settings.py` (dry run) | Overwrite files (`--force`) or mutate settings (`--apply`), secrets, app installs, visibility |

Finished work is pushed and opened as a PR. Unpublished local commits are not "done": nobody else can review them and CI never sees them.

## Proportional Ceremony

Scale ceremony to the blast radius of the change:

| Tier | Scope | Required Path |
| --- | --- | --- |
| **Fast-path** | Small docs, comments, typos, narrow config | Branch → local verification → PR → CI green → handoff (skip prior issue and `@codex review` on pure prose). |
| **Standard** | Features, bug fixes, refactors, CI/tooling | Spec/issue → worktree branch → failing test first → implementation → local verification → PR + bot reviews + CI → handoff. |
| **High-risk** | Parsers, schemas, state machines, concurrency, auth/security | Standard path + explicit invariants/property tests (or an independent review of the frozen diff) before handoff. |

## Change Lifecycle

1. **Sync and search.** `git fetch --prune`; fast-forward `main`; search open and closed issues/PRs. Done when `main` equals `origin/main` and duplicates are ruled out.
2. **Specify before coding (Input Gate).** For behavioral, schema or public-API changes, clarify ambiguities with the owner and freeze the spec in an issue (`bug: ...` / `feat: ...`) or `.notes/plans/` before writing code: problem, non-goals, inputs/outputs, edge cases and executable acceptance criteria.
3. **Branch** `type/short-kebab` or `type/123-short-kebab` from fresh `main`, in its own worktree (`.worktrees/<branch>`). Push with `git push -u origin HEAD` and confirm `git rev-parse --abbrev-ref @{u}` names the feature branch, not `origin/main`.
4. **Tests first.** Write the behavior or regression test, watch it fail for the expected reason (on the base revision for bugs), then implement. Never weaken assertions or mock the boundary being claimed.
5. **Commits** `type(scope): imperative description`, ≤72 chars, no trailing period (`feat fix docs test refactor perf build ci chore revert`; `!` + `BREAKING CHANGE:` footer for incompatible changes). No AI co-author trailers, model names, emoji or `[verified]` badges.
6. **Verify locally (Pre-PR Gate).** Run the project's lint, test and build commands from `CONTRIBUTING.md` on the clean, committed tree (`git status --porcelain` empty). Record exact commands and real output, including skips. If a failure looks environmental, rerun it on `main` in the same environment before blaming the environment.
7. **Open the PR** with the template: problem, changes, verification actually run, what was **not** run, risks/rollback. One problem per PR. Draft if incomplete. `Refs #N` links; `Fixes #N` only when it fully resolves the issue.
8. **Bot review (Review-Resolution Gate).** Sourcery reviews automatically. If CodeRabbit has not started, comment `@coderabbitai review` (`full review` after big changes). Comment `@codex review` on substantive code. Wait for actual findings (a reaction or request is not a review):
   - **Valid defect:** reproduce with a test, fix, push, and reply with the commit SHA and test name before resolving the thread.
   - **False positive:** verify against the code/tests and reply with concrete evidence (`path:line`, command or test output) before resolving.
9. **CI** must pass on the final head. Editing the PR title or body reruns only `PR conventions`.
10. **Hand off.** Report what is verified, what is not, and that the PR is ready for the owner to squash-merge. After merge: delete the branch and worktree, fast-forward `main`, update `HANDOFF.md` (current state and next acceptance step only), and open follow-up issues instead of burying them in PR comments.

## Evidence Rules

- Distinguish unit tests, synthetic integration, installed-package checks and real external/provider behavior; passing one level does not establish the next.
- Performance claims (`perf`) need before/after measurements from a committed, reproducible benchmark, with dataset sizes and hardware stated.
- Agent, subagent and bot reports, and zero exit codes of piped commands, are claims; verify against the diff, artifacts and real exit codes.
- Never fabricate output. Report blocked checks as blocked in "What was not tested".

## Agent Topology & Inner-Loop Skills

Default to one capable agent per coherent change. Delegate only for independent components, broad parallel exploration, or an independent review of a frozen diff; workers get bounded file ownership and acceptance criteria, and do not commit, push or redesign.

This skill owns the outer repository lifecycle. Developer tooling and inner-loop methodologies (brainstorming/spec design, strict TDD, systematic debugging, property-based testing, code review) live in composable skills installed in the user's agent environment, not hardcoded in `AGENTS.md`:
- When those skills are installed, invoke them at **Step 2** (spec/planning), **Step 4** (TDD), **Step 6** (debugging) and **Step 8** (review).
- Even when no separate skill is installed, the Input Gate, Pre-PR Gate and Review-Resolution Gate above remain mandatory.

## Maintaining This Skill

Source: `https://github.com/whayn/skills` (`skills/repo-workflow`). Rationale and sources: `references/rationale.md`. Bootstrap and settings reference: `references/bootstrap.md`.
