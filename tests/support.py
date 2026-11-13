"""Paths and helpers shared by the skill tests."""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")

# Skill scripts promise Python 3.9+ and the standard library only. CI points
# SKILL_PYTHON at a bare interpreter of the oldest supported version; locally
# they run with the interpreter that runs pytest.
SCRIPT_PYTHON = os.environ.get("SKILL_PYTHON") or sys.executable


def skill_dirs():
    return sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))


def run(script, *args, check=True, **kwargs):
    """Run a skill script with SCRIPT_PYTHON; raise with its output on failure."""
    result = subprocess.run(
        [SCRIPT_PYTHON, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
        **kwargs,
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result
