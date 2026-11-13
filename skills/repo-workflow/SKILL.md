---
name: repo-workflow
description: Bootstrap and run an evidence-first GitHub repo workflow.
version: 0.1.0
author: Whayn (whayn)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, workflow, contributing, ci, pull-requests, conventions]
    related_skills: [github-pr-workflow, github-code-review, test-driven-development, systematic-debugging, requesting-code-review]
---

# Repo Workflow

An issue → branch → tests-first → verified PR → bot review + CI → owner-merge
workflow for small GitHub projects maintained with coding agents. It ships the
repository files (CONTRIBUTING, AGENTS, PR/issue templates, CI, Dependabot),
a script that applies the matching GitHub settings, and the day-to-day rules
agents follow. It does not choose a license, architecture or test framework.

## When to Use

- Starting a new repository, or adopting this workflow in an existing one.
- Any change in a repository that already uses it (its `CONTRIBUTING.md` ends
  with a pointer to this skill).
- Repository housekeeping: stale `main`, merged worktrees/branches, handoff notes.

Don't use for: one-off scripts without a remote, or repositories whose owners
run a different process (follow theirs).

## Prerequisites

- `gh` authenticated as an account with admin rights on the target repository
  (settings) or write rights (normal changes).
- Python 3.9+ for `scripts/`. No third-party packages.
- `SKILL_DIR` below means this skill's directory (`skill_dir` in `skill_view`).

## Authority

Defaults; a project may tighten them in its `AGENTS.md` "Project specifics".

| Agent may do without asking | Requires the owner's explicit approval |
| --- | --- |
| Create branches/worktrees, commit on feature branches | Merge any PR |
| Push feature branches, open draft or ready PRs | Tags, releases, deployments, package publishing |
| Trigger bot reviews, reply to and resolve its own review threads | Force-push a shared branch; anything on `main` after bootstrap |
| Open issues for follow-up work | Close an issue not resolved by a merged `Fixes #N` |
| | Repository settings, secrets, app installs, visibility |

Finished work is pushed and opened as a PR. Unpublished local commits are not
"done": nobody else can review them and CI never sees them.

## Change Lifecycle

1. **Sync and search.** `git fetch --prune`; fast-forward `main`; search open and
   closed issues/PRs. Done when `main` equals `origin/main` and duplicates are ruled out.
2. **Issue first** for new behavior, formats/schemas, public APIs or anything
   needing a design decision. Small docs fixes and obvious narrow bugs skip this.
   Titles: `bug: ...` / `feat: ...`. Done when scope and acceptance criteria are written.
3. **Branch** `type/short-kebab` or `type/123-short-kebab` from fresh `main`, in its
   own worktree (`.worktrees/<branch>`). Push with `git push -u origin HEAD` and
   confirm `git rev-parse --abbrev-ref @{u}` names the feature branch, not `origin/main`.
4. **Tests first.** Write the behavior test, watch it fail for the right reason,
   then implement. Bugs get a regression test that fails on the base revision.
5. **Commits** `type(scope): imperative description`, ≤72 chars, no trailing period.
   Types: feat fix docs test refactor perf build ci chore revert. `!` plus a
   `BREAKING CHANGE:` footer for incompatible changes. No AI co-author trailers,
   model names, emoji or "verified" badges.
6. **Verify locally** with the project's lint, test and build commands from
   `CONTRIBUTING.md`. Record exact commands and real results, including skips.
   If a failure looks environmental, rerun it on the base revision before blaming
   or excusing the change.
7. **Open the PR** with the template: problem, changes, verification actually run,
   what was not run, risks/rollback. One problem per PR. Draft if incomplete.
   `Refs #N` links; `Fixes #N` only when it fully resolves the issue.
8. **Bot review.** Sourcery reviews automatically. If CodeRabbit has not started,
   comment `@coderabbitai review` (or `@coderabbitai full review` after big changes).
   Comment `@codex review` on substantive code. A request or reaction is not a
   review: read the actual findings. Reproduce each one; fix real defects with a
   test; reject wrong ones with evidence (`path:line`, test name). Resolve threads.
9. **CI** must pass on the final head. Same-head cancellations caused by editing the
   PR title/body are not failures; note them once. Never weaken or skip a test to
   get green.
10. **Hand off.** Report what is verified, what is not, and that the PR is ready;
    the owner merges (squash, PR title as subject). After merge: delete the branch
    and worktree, fast-forward `main`, update local handoff notes, open follow-up
    issues instead of burying them in PR comments.

## Evidence Rules

- Distinguish unit tests, synthetic integration, installed-package checks and real
  external/provider behavior; one level does not establish the next.
- Performance claims (`perf`) need before/after measurements from a committed,
  reproducible benchmark, with sizes and hardware stated.
- Agent and bot reports, and successful exits of piped commands, are claims; check
  the diff, artifacts and real exit codes.
- Never fabricate output. A blocked check is reported as blocked.

## Agent Topology

Default to one capable agent per coherent change. Delegate only for independent
components, broad parallel exploration, or an independent final review of a frozen
diff. The main agent keeps architecture decisions; workers get bounded scope,
file ownership and acceptance criteria, and do not commit, push or redesign.
Developer tooling and model choices live in skills, not in `AGENTS.md`.

## Bootstrap a Repository

1. Create the repository (or clone it) and check out `main`.
2. Render the files, dry run first:
   `terminal(command="python3 SKILL_DIR/scripts/bootstrap_repo.py TARGET --owner OWNER --repo REPO --project 'Name' --stack python --dry-run")`.
   Use `--stack generic --install ... --lint ... --test ... --build ...` for
   non-Python projects, then add the toolchain setup step marked in `ci.yml`.
   Add `--local-notebook` to create git-excluded `HANDOFF.md` and `.hermes/`.
   Done when the dry run lists every file as `create` and no unresolved placeholder.
3. Rerun without `--dry-run`. Existing files are skipped unless `--force`; when
   adopting into an existing repo, merge skipped files by hand instead.
4. Fill the `Project specifics` and `Code Review Rules` sections of `AGENTS.md`,
   and the verification commands in `CONTRIBUTING.md` if they differ.
5. Commit `chore(repo): establish contribution workflow` directly to `main` (the
   only direct commit) and push. Choose and add a `LICENSE` with the owner.
6. Apply settings, dry run first:
   `terminal(command="python3 SKILL_DIR/scripts/apply_github_settings.py OWNER/REPO")`,
   then the same with `--apply`. It configures squash-only merges with PR-title
   subjects, branch auto-deletion, the label set, `main` protection (required
   checks, linear history, resolved conversations, no force-push/deletion, admins
   included), a `v*` tag ruleset, private vulnerability reporting, secret scanning
   with push protection, and Dependabot security updates.
7. Ask the owner to install the review apps (Sourcery, CodeRabbit, Codex cloud);
   app installs need their account.
8. Open a trivial PR (e.g. README wording) to prove the gates. Done when all
   required checks report on it and the PR is mergeable.

## Housekeeping

At the start of a session and after each merge: fetch/prune, fast-forward
`main`, remove worktrees and remote branches of merged PRs, and make
`HANDOFF.md` describe the current state and the next acceptance step only.

## Pitfalls

- **Required check names are job `name:` values.** Renaming a CI job without
  updating branch protection blocks every merge; rerun the settings script with
  matching `--check` values.
- **The PR conventions job runs on `edited`.** Editing a PR cancels and restarts
  CI on the same head; that is expected.
- **A branch tracking `origin/main`** (created with `git branch x origin/main`)
  can push to the wrong place. Always `push -u origin HEAD` from the branch.
- **Branch protection on private repos** needs a paid plan; the settings script
  reports that step as failed and continues.
- **Template placeholders are `{{UPPER_CASE}}`.** GitHub's `${{ expression }}`
  syntax is left untouched.
- **Pinned action SHAs** in `ci.yml` are deliberate; let Dependabot bump them.
- **Bots are sometimes wrong.** A confident finding still needs a reproduction.
- **Local toolchains differ from CI pins.** Compare a suspicious failure against
  `main` in the same environment before attributing it to the change.

## Verification

- `CONTRIBUTING.md`, `AGENTS.md`, `SECURITY.md`, `.editorconfig` and `.github/`
  exist with no `{{...}}` placeholders left.
- `apply_github_settings.py OWNER/REPO` (dry run) shows the intended state, and
  `gh api repos/OWNER/REPO/branches/main/protection` lists the required checks.
- A test PR shows every required check and bot review on its head.

## Maintaining This Skill

Source: `https://github.com/whayn/skills` (`skills/repo-workflow`). Change it
through that repository's own PR workflow, then `hermes skills update repo-workflow`.
Rationale and sources: `references/rationale.md`.
