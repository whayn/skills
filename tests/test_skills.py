"""Checks every skill must pass: the Agent Skills spec, neutrality and privacy."""

import re

import pytest
import yaml
from skills_ref.validator import validate

from tests.support import skill_dirs

SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SKILLS = pytest.mark.parametrize("skill", skill_dirs(), ids=lambda p: p.name)


def frontmatter(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4:end]), text[end + 5 :]


def text_files(skill):
    for path in sorted(skill.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            yield path, path.read_text(encoding="utf-8")


def test_there_are_skills():
    assert skill_dirs()


@SKILLS
def test_frontmatter_follows_the_agent_skills_spec(skill):
    """https://agentskills.io/specification: only portable fields, so any agent loads it."""
    meta, body = frontmatter(skill)
    assert set(meta) <= SPEC_FIELDS, set(meta) - SPEC_FIELDS
    assert meta["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["name"]) and len(meta["name"]) <= 64
    assert 0 < len(meta["description"]) <= 1024
    assert len(meta.get("compatibility", "")) <= 500
    metadata = meta.get("metadata", {})
    assert all(type(k) is str and type(v) is str for k, v in metadata.items())
    assert re.fullmatch(r"\d+\.\d+\.\d+", metadata.get("version", "")), "metadata.version"
    assert body.strip()


@SKILLS
def test_reference_validator_accepts_the_skill(skill):
    assert validate(skill) == []


@SKILLS
def test_skill_text_is_agent_neutral(skill):
    """No one agent's tool-call syntax, commands or directories in the instructions."""
    _, body = frontmatter(skill)
    for marker in ("terminal(", "skill_view", "hermes skills", ".hermes/", "delegate_task"):
        assert marker not in body, marker


@SKILLS
def test_skill_files_carry_no_machine_local_paths(skill):
    for path, text in text_files(skill):
        for marker in ("/opt/data", "/home/", "/Users/", "C:\\Users", "C:/Users"):
            assert marker not in text, (path, marker)


@SKILLS
def test_skill_changelog_records_current_version(skill):
    changelog = skill / "CHANGELOG.md"
    assert changelog.is_file(), f"missing {changelog}"
    meta, _ = frontmatter(skill)
    version = meta["metadata"]["version"]
    pattern = re.compile(rf"^## \[?{re.escape(version)}\]?(?:\s|$)", re.MULTILINE)
    assert pattern.search(changelog.read_text(encoding="utf-8")), (
        f"{changelog} does not record current version {version}"
    )
