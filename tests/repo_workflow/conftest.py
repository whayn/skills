"""Fixtures and helpers for the repo-workflow tests."""

import ast
import subprocess

import pytest

from tests.support import SKILLS, run

SKILL = SKILLS / "repo-workflow"
BOOTSTRAP = SKILL / "scripts" / "bootstrap_repo.py"
SETTINGS = SKILL / "scripts" / "apply_github_settings.py"


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


def bootstrap(repo, *extra):
    return run(BOOTSTRAP, str(repo), "--owner", "octo", "--repo", "demo", *extra)


def required_checks():
    """DEFAULT_CHECKS from the settings script, read without importing it."""
    tree = ast.parse(SETTINGS.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "DEFAULT_CHECKS" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("DEFAULT_CHECKS not found")
