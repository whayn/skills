"""repo-workflow: rendering the repository templates with bootstrap_repo.py."""

import json
import os
import shutil
import subprocess

import pytest
import yaml

from tests.repo_workflow.conftest import BOOTSTRAP, bootstrap, required_checks
from tests.support import PLACEHOLDER, SCRIPT_PYTHON, run

STACK_ARGS = {
    "python": ["--stack", "python"],
    "generic": [
        "--stack",
        "generic",
        "--install",
        "npm ci",
        "--lint",
        "npm run lint",
        "--test",
        "npm test",
        "--build",
        "npm run build",
    ],
}


def read(repo, name):
    return (repo / name).read_text(encoding="utf-8")


def workflow(repo):
    return yaml.safe_load(read(repo, ".github/workflows/ci.yml"))


@pytest.mark.parametrize("stack", STACK_ARGS)
def test_bootstrap_renders_complete_valid_files(repo, stack):
    bootstrap(repo, *STACK_ARGS[stack])
    expected = {
        "CONTRIBUTING.md",
        "AGENTS.md",
        "CLAUDE.md",
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
        if p.is_file() and ".git" not in p.relative_to(repo).parts
    }
    assert written == expected
    for name in expected:
        text = read(repo, name)
        assert not PLACEHOLDER.search(text), name
        if name.endswith(".yml"):
            assert isinstance(yaml.safe_load(text), dict), name
    assert "@octo" in read(repo, ".github/CODEOWNERS")


@pytest.mark.parametrize("stack", STACK_ARGS)
def test_rendered_workflows_pass_actionlint(repo, stack):
    actionlint = shutil.which("actionlint")
    if actionlint is None:
        if os.environ.get("REQUIRE_ACTIONLINT"):
            pytest.fail("REQUIRE_ACTIONLINT is set but actionlint is not on PATH")
        pytest.skip("actionlint is not installed")
    bootstrap(repo, *STACK_ARGS[stack])
    result = subprocess.run([actionlint], cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_ci_job_names_match_the_required_checks(repo):
    bootstrap(repo)
    names = {job["name"] for job in workflow(repo)["jobs"].values()}
    assert names == set(required_checks())


def test_commands_with_yaml_syntax_stay_single_scalars(repo):
    tricky = 'echo "a: b" # not a comment && true'
    bootstrap(repo, "--lint", tricky)
    runs = [step.get("run") for step in workflow(repo)["jobs"]["quality"]["steps"]]
    assert tricky in runs


def test_empty_optional_command_drops_its_lines(repo):
    bootstrap(repo, "--build", "")
    ci = read(repo, ".github/workflows/ci.yml")
    assert "python -m build" not in ci
    steps = yaml.safe_load(ci)["jobs"]["quality"]["steps"]
    assert all(step.get("run") != "" for step in steps)
    assert "python -m build" not in read(repo, "CONTRIBUTING.md")


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
    assert read(repo, "AGENTS.md") == "mine\n"
    bootstrap(repo, "--force")
    assert read(repo, "AGENTS.md") != "mine\n"


def test_dry_run_writes_nothing(repo):
    report = json.loads(bootstrap(repo, "--dry-run", "--local-notebook").stdout)
    assert report["dry_run"] and all(f["action"] != "skip (exists)" for f in report["files"])
    assert [p for p in repo.iterdir() if p.name != ".git"] == []
    assert "/.notes/" not in read(repo, ".git/info/exclude")


def test_local_notebook_is_git_excluded(repo):
    bootstrap(repo, "--local-notebook")
    bootstrap(repo, "--local-notebook")  # idempotent
    exclude = read(repo, ".git/info/exclude").splitlines()
    for line in ("/HANDOFF.md", "/.notes/", "/.worktrees/"):
        assert exclude.count(line) == 1
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "HANDOFF.md" not in status and ".notes" not in status
    assert (repo / ".notes/README.md").is_file()
    assert "CONTRIBUTING.md" in status


def test_rendered_files_use_lf_line_endings(repo):
    """The generated .editorconfig demands LF; Windows text mode must not add CRs."""
    bootstrap(repo, "--local-notebook")
    written = [p for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]
    written.append(repo / ".git/info/exclude")
    for path in written:
        assert b"\r\n" not in path.read_bytes(), path


def test_notebook_directory_is_configurable(repo):
    bootstrap(repo, "--local-notebook", "--notebook-dir", ".hermes")
    assert (repo / ".hermes/README.md").is_file()
    assert "/.hermes/" in read(repo, ".git/info/exclude").splitlines()


def test_claude_md_points_at_agents_md(repo):
    """Claude Code reads CLAUDE.md, not AGENTS.md; one import keeps a single source."""
    bootstrap(repo)
    assert read(repo, "CLAUDE.md").strip().endswith("@AGENTS.md")


def conventions_script(repo):
    step = workflow(repo)["jobs"]["conventions"]["steps"][0]["run"]
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
        [SCRIPT_PYTHON, "-c", conventions_script(repo)], env=env, capture_output=True, text=True
    )
    assert (result.returncode == 0) == ok, result.stderr
