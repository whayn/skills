"""Tests for the CI per-skill version-bump check."""

import subprocess
import sys
from pathlib import Path

from tests.support import ROOT

SCRIPT = ROOT / ".github" / "scripts" / "check_skill_versions.py"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    _write_skill(repo, "alpha", "0.1.0", "initial")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "init")
    return repo


def _write_skill(repo: Path, name: str, version: str, body: str) -> None:
    skill_dir = repo / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f'---\nname: {name}\ndescription: test\nmetadata:\n  version: "{version}"\n---\n\n{body}\n',
        encoding="utf-8",
    )


def _run_check(repo: Path, base: str = "HEAD~1", head: str = "HEAD") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), "--base", base, "--head", head],
        capture_output=True,
        text=True,
        check=False,
    )


def test_non_skill_change_passes(tmp_path):
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("docs\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "docs")
    result = _run_check(repo)
    assert result.returncode == 0, result.stderr


def test_modified_skill_without_version_bump_fails(tmp_path):
    repo = _init_repo(tmp_path)
    _write_skill(repo, "alpha", "0.1.0", "updated body")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "edit without bump")
    result = _run_check(repo)
    assert result.returncode != 0
    assert "alpha" in (result.stdout + result.stderr)


def test_modified_skill_with_downgraded_version_fails(tmp_path):
    repo = _init_repo(tmp_path)
    _write_skill(repo, "alpha", "0.0.9", "downgraded")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "downgrade")
    result = _run_check(repo)
    assert result.returncode != 0
    assert "alpha" in (result.stdout + result.stderr)


def test_modified_skill_with_version_bump_passes(tmp_path):
    repo = _init_repo(tmp_path)
    _write_skill(repo, "alpha", "0.1.1", "updated body")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "bump")
    result = _run_check(repo)
    assert result.returncode == 0, result.stderr


def test_new_skill_passes_without_prior_version(tmp_path):
    repo = _init_repo(tmp_path)
    _write_skill(repo, "beta", "0.1.0", "brand new")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "add beta")
    result = _run_check(repo)
    assert result.returncode == 0, result.stderr


def test_deleted_skill_passes(tmp_path):
    repo = _init_repo(tmp_path)
    _git(repo, "rm", "-rq", "skills/alpha")
    _git(repo, "commit", "-q", "-m", "remove alpha")
    result = _run_check(repo)
    assert result.returncode == 0, result.stderr
