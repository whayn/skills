"""Tests for the Claude Code plugin marketplace manifest."""

import json

import yaml

from tests.support import ROOT, skill_dirs

MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"


def _skill_meta(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4:end])


def test_marketplace_manifest_covers_all_skills_and_versions():
    assert MANIFEST.is_file(), f"missing {MANIFEST}"
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(data.get("name"), str) and data["name"]
    assert isinstance(data.get("owner", {}).get("name"), str) and data["owner"]["name"]

    plugins = {entry["name"]: entry for entry in data.get("plugins", [])}
    skills = skill_dirs()
    assert set(plugins) == {s.name for s in skills}

    for skill in skills:
        meta = _skill_meta(skill)
        entry = plugins[skill.name]
        assert entry["source"] == f"./skills/{skill.name}"
        assert (ROOT / entry["source"]).is_dir()
        assert entry["version"] == meta["metadata"]["version"]
        assert isinstance(entry.get("description"), str) and entry["description"].strip()
