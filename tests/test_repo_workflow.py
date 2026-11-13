"""Tests for the repo-workflow skill: frontmatter, rendering and the settings plan."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "repo-workflow"
BOOTSTRAP = SKILL / "scripts" / "bootstrap_repo.py"
SETTINGS = SKILL / "scripts" / "apply_github_settings.py"
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")


def run(script, *args, check=True):
    result = subprocess.run(
        [sys.executable, str(script), *args], capture_output=True, text=True, check=False
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


def bootstrap(repo, *extra):
    return run(BOOTSTRAP, str(repo), "--owner", "octo", "--repo", "demo", *extra)


def test_frontmatter_follows_skill_standards():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    meta = yaml.safe_load(text[4:end])
    assert meta["name"] == SKILL.name
    assert len(meta["description"]) <= 60 and meta["description"].endswith(".")
    for key in ("version", "author", "license", "platforms", "metadata"):
        assert key in meta
    assert text[end + 5 :].strip()


def test_skill_files_carry_no_machine_local_paths():
    for path in SKILL.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert "/opt/data" not in text and "/home/" not in text, path


@pytest.mark.parametrize("stack", ["python", "generic"])
def test_bootstrap_renders_complete_valid_files(repo, stack):
    extra = ["--stack", stack]
    if stack == "generic":
        extra += [
            "--install",
            "npm ci",
            "--lint",
            "npm run lint",
            "--test",
            "npm test",
            "--build",
            "npm run build",
        ]
    bootstrap(repo, *extra)
    expected = {
        "CONTRIBUTING.md",
        "AGENTS.md",
        "SECURITY.md",
        ".editorconfig",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS",
        ".github/release.yml",
        ".github/dependabot.yml",
        ".github/workflows/ci.yml",
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/feature.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
    }
    written = {
        p.relative_to(repo).as_posix()
        for p in repo.rglob("*")
        if p.is_file() and ".git/" not in p.as_posix()
    }
    assert written == expected
    for name in expected:
        text = (repo / name).read_text(encoding="utf-8")
        assert not PLACEHOLDER.search(text), name
        if name.endswith(".yml"):
            assert isinstance(yaml.safe_load(text), dict), name
    assert "@octo" in (repo / ".github/CODEOWNERS").read_text(encoding="utf-8")


def test_ci_job_names_match_the_required_checks(repo):
    bootstrap(repo)
    ci = yaml.safe_load((repo / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    names = {job["name"] for job in ci["jobs"].values()}
    sys.path.insert(0, str(SETTINGS.parent))
    try:
        import apply_github_settings
    finally:
        sys.path.pop(0)
    assert names == set(apply_github_settings.DEFAULT_CHECKS)


def test_commands_with_yaml_syntax_stay_single_scalars(repo):
    tricky = 'echo "a: b" # not a comment && true'
    bootstrap(repo, "--lint", tricky)
    ci = yaml.safe_load((repo / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    runs = [step.get("run") for step in ci["jobs"]["quality"]["steps"]]
    assert tricky in runs


def test_empty_optional_command_drops_its_lines(repo):
    bootstrap(repo, "--build", "")
    ci = (repo / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python -m build" not in ci
    steps = yaml.safe_load(ci)["jobs"]["quality"]["steps"]
    assert all(step.get("run") != "" for step in steps)
    assert "python -m build" not in (repo / "CONTRIBUTING.md").read_text(encoding="utf-8")


def test_generic_stack_requires_commands(repo):
    result = run(
        BOOTSTRAP, str(repo), "--owner", "o", "--repo", "r", "--stack", "generic", check=False
    )
    assert result.returncode != 0 and "--install" in result.stderr
    assert not (repo / "CONTRIBUTING.md").exists()


def test_existing_files_are_kept_unless_forced(repo):
    (repo / "AGENTS.md").write_text("mine\n", encoding="utf-8")
    report = json.loads(bootstrap(repo).stdout)
    assert {"path": "AGENTS.md", "action": "skip (exists)"} in report["files"]
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "mine\n"
    bootstrap(repo, "--force")
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") != "mine\n"


def test_dry_run_writes_nothing(repo):
    report = json.loads(bootstrap(repo, "--dry-run", "--local-notebook").stdout)
    assert report["dry_run"] and all(f["action"] != "skip (exists)" for f in report["files"])
    assert [p for p in repo.iterdir() if p.name != ".git"] == []
    assert "/.hermes/" not in (repo / ".git/info/exclude").read_text(encoding="utf-8")


def test_local_notebook_is_git_excluded(repo):
    bootstrap(repo, "--local-notebook")
    bootstrap(repo, "--local-notebook")  # idempotent
    exclude = (repo / ".git/info/exclude").read_text(encoding="utf-8").splitlines()
    for line in ("/HANDOFF.md", "/.hermes/", "/.worktrees/"):
        assert exclude.count(line) == 1
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "HANDOFF.md" not in status and ".hermes" not in status
    assert "CONTRIBUTING.md" in status


def conventions_script(repo):
    ci = yaml.safe_load((repo / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    step = ci["jobs"]["conventions"]["steps"][0]["run"]
    return step.split("<<'PY'\n", 1)[1].rsplit("PY", 1)[0]


@pytest.mark.parametrize(
    "title,branch,author,ok",
    [
        ("feat(engine): add bounded selection", "feat/12-bounded-selection", "octo", True),
        ("fix: handle empty input", "fix/empty-input", "octo", True),
        ("chore(deps): bump ruff from 1 to 2", "dependabot/pip/ruff-2", "dependabot[bot]", True),
        ("Add stuff", "feat/stuff", "octo", False),
        ("feat: add stuff.", "feat/stuff", "octo", False),
        ("feat: " + "x" * 80, "feat/stuff", "octo", False),
        ("feat: add stuff", "my-branch", "octo", False),
        ("feat: add stuff", "feature/stuff", "octo", False),
    ],
)
def test_pr_convention_check_from_rendered_ci(repo, title, branch, author, ok):
    bootstrap(repo)
    env = {**os.environ, "PR_TITLE": title, "PR_BRANCH": branch, "PR_AUTHOR": author}
    result = subprocess.run(
        [sys.executable, "-c", conventions_script(repo)], env=env, capture_output=True, text=True
    )
    assert (result.returncode == 0) == ok, result.stderr


def test_settings_dry_run_never_calls_gh():
    result = run(SETTINGS, "octo/demo", "--gh", "/nonexistent/gh")
    steps = [json.loads(line) for line in result.stdout.splitlines()]
    endpoints = {s["endpoint"] for s in steps}
    assert "repos/octo/demo/branches/main/protection" in endpoints
    protection = next(s for s in steps if s["endpoint"].endswith("/protection"))
    assert protection["body"]["required_status_checks"]["contexts"] == [
        "Quality",
        "Tests",
        "Secrets",
        "PR conventions",
    ]
    assert protection["body"]["enforce_admins"] is True
    merge = steps[0]["body"]
    assert merge["allow_squash_merge"] and not merge["allow_merge_commit"]
    assert not merge["allow_rebase_merge"] and merge["squash_merge_commit_title"] == "PR_TITLE"


def test_settings_custom_checks_and_branch():
    result = run(SETTINGS, "octo/demo", "--branch", "trunk", "--check", "Build", "--check", "Test")
    protection = next(
        json.loads(line) for line in result.stdout.splitlines() if "/protection" in line
    )
    assert protection["endpoint"] == "repos/octo/demo/branches/trunk/protection"
    assert protection["body"]["required_status_checks"]["contexts"] == ["Build", "Test"]


def test_settings_apply_reports_failures_and_continues(tmp_path):
    fake = tmp_path / "gh"
    log = tmp_path / "calls.log"
    fake.write_text(
        "#!/bin/sh\n"
        f'echo "$*" >> "{log}"\n'
        'case "$*" in *protection*) echo "Upgrade to GitHub Pro" >&2; exit 1;; esac\n'
        'case "$*" in *"--method GET repos/octo/demo/rulesets"*) echo "[]";; '
        '*"--method GET repos/octo/demo"*) echo \'{"default_branch":"main"}\';; esac\n'
        'case "$*" in *--input*) cat >/dev/null;; esac\n',
        encoding="utf-8",
    )
    fake.chmod(0o755)
    result = run(SETTINGS, "octo/demo", "--apply", "--gh", str(fake), check=False)
    assert result.returncode == 1
    assert "FAILED  protect main" in result.stdout
    calls = log.read_text(encoding="utf-8")
    assert "--method POST repos/octo/demo/rulesets" in calls  # later steps still ran
    assert "priority%3A%20high" in calls
