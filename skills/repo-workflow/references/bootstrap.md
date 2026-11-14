# Bootstrapping a Repository and Applying GitHub Settings

Read this reference when setting up a new repository, adopting `repo-workflow` in an existing one, or changing required checks, branch protection or tag rulesets. `SKILL_DIR` means the directory containing `SKILL.md`.

## Prerequisites

- `gh` authenticated as an account with admin rights on the target repository.
- Python 3.9+ (standard library only). Commands below use `python3`; on Windows use `py -3` or `python` (`python3` may open the Store).

## Bootstrap Steps

1. Create the repository (or clone it) and check out `main`.
2. Render the files, dry run first:
   ```bash
   python3 SKILL_DIR/scripts/bootstrap_repo.py TARGET --owner OWNER --repo REPO --project 'Name' --stack python --dry-run
   ```
   - Use `--stack generic --install ... --lint ... --test ... --build ...` for non-Python projects (pass `""` to omit an optional command), then add the toolchain setup step marked in `.github/workflows/ci.yml`.
   - Add `--local-notebook` to create a git-excluded `HANDOFF.md` and notes directory (`.notes/`; pick another with `--notebook-dir`).
   - Done when the dry run lists every file as `create` and no unresolved placeholder.
3. Rerun without `--dry-run`. Existing files are skipped unless `--force`; when adopting into an existing repo, merge skipped files by hand instead of overwriting with `--force`.
4. Fill the `Project specifics` and `Code Review Rules` sections of `AGENTS.md` (the single agent-instruction file; `CLAUDE.md` only imports it), and the verification commands in `CONTRIBUTING.md` if they differ.
5. Commit `chore(repo): establish contribution workflow` directly to `main` (the only direct commit) and push. Choose and add a `LICENSE` with the owner.
6. Apply GitHub settings, dry run first:
   ```bash
   python3 SKILL_DIR/scripts/apply_github_settings.py OWNER/REPO
   ```
   Show the planned API calls and get the owner's confirmation before running with `--apply`:
   ```bash
   python3 SKILL_DIR/scripts/apply_github_settings.py OWNER/REPO --apply
   ```
   - It configures squash-only merges with PR-title subjects, branch auto-deletion, the label set, `main` protection (required checks, linear history, resolved conversations, no force-push/deletion, admins included), a release tag ruleset, private vulnerability reporting, secret scanning with push protection, and Dependabot security updates.
   - Use repeatable `--check NAME` flags when CI job names differ from the defaults (`Quality`, `Tests`, `Secrets`, `PR conventions`).
   - Use repeatable `--tag-pattern PATTERN` flags when release tags differ from `refs/tags/v*` (for example `--tag-pattern 'refs/tags/*-v*'`).
7. Ask the owner to install the review apps (Sourcery, CodeRabbit, Codex cloud); app installs need their account.
8. Open a trivial PR (e.g. README wording) to prove the gates. Done when all required checks report on it and the PR is mergeable.

## Setup Pitfalls

- **Required check names are job `name:` values.** Renaming a CI job without updating branch protection blocks every merge; rerun `apply_github_settings.py` with matching `--check` values.
- **PR conventions is its own workflow** (`pr-conventions.yml`) because it must rerun when a PR is edited; keep `edited` out of `ci.yml`, or every title edit cancels and restarts the whole CI on the same head.
- **Branch protection on private repos** needs a paid plan; the settings script reports that step as failed and continues.
- **Template placeholders are `{{UPPER_CASE}}`.** GitHub's `${{ expression }}` syntax is left untouched.
- **Pinned action SHAs** in `ci.yml` are deliberate; let Dependabot bump them.

## Bootstrap Verification

- `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `.editorconfig` and `.github/` exist with no `{{...}}` placeholders left.
- `apply_github_settings.py OWNER/REPO` (dry run) shows the intended state, and `gh api repos/OWNER/REPO/branches/main/protection` lists the required checks.
- A test PR shows every required check and bot review on its head.
