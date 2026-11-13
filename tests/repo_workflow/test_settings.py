"""repo-workflow: the GitHub settings plan of apply_github_settings.py."""

import json
import os

from tests.repo_workflow.conftest import SETTINGS
from tests.support import SCRIPT_PYTHON, run

# Stands in for `gh`: logs its arguments, fails branch protection like a free
# private repository does, and answers the two GET requests the script makes.
FAKE_GH = """\
import sys
from pathlib import Path

args = " ".join(sys.argv[1:])
with Path({log!r}).open("a", encoding="utf-8") as log:
    log.write(args + "\\n")
if "protection" in args:
    sys.exit("Upgrade to GitHub Pro")
if "--input" in args:
    sys.stdin.read()
if "--method GET repos/octo/demo/rulesets" in args:
    print("[]")
elif "--method GET repos/octo/demo" in args:
    print('{{"default_branch": "main"}}')
"""


def fake_gh(tmp_path):
    """An executable `gh` on any OS: a shebang script, or a .cmd wrapper on Windows."""
    log = tmp_path / "calls.log"
    script = tmp_path / "fake_gh.py"
    script.write_text(FAKE_GH.format(log=str(log)), encoding="utf-8")
    if os.name == "nt":
        launcher = tmp_path / "gh.cmd"
        launcher.write_text(f'@"{SCRIPT_PYTHON}" "{script}" %*\r\n', encoding="utf-8")
    else:
        launcher = tmp_path / "gh"
        launcher.write_text(f"#!{SCRIPT_PYTHON}\n" + script.read_text(encoding="utf-8"))
        launcher.chmod(0o755)
    return launcher, log


def plan(*args):
    result = run(SETTINGS, "octo/demo", *args)
    return [json.loads(line) for line in result.stdout.splitlines()]


def test_settings_dry_run_never_calls_gh():
    steps = plan("--gh", "/nonexistent/gh")
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
    steps = plan("--branch", "trunk", "--check", "Build", "--check", "Test")
    protection = next(s for s in steps if s["endpoint"].endswith("/protection"))
    assert protection["endpoint"] == "repos/octo/demo/branches/trunk/protection"
    assert protection["body"]["required_status_checks"]["contexts"] == ["Build", "Test"]


def test_settings_apply_reports_failures_and_continues(tmp_path):
    gh, log = fake_gh(tmp_path)
    result = run(SETTINGS, "octo/demo", "--apply", "--gh", str(gh), check=False)
    assert result.returncode == 1, result.stderr
    assert "FAILED  protect main" in result.stdout
    calls = log.read_text(encoding="utf-8")
    assert "--method POST repos/octo/demo/rulesets" in calls  # later steps still ran
    assert "priority%3A%20high" in calls
