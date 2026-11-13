"""Verify that every modified skill under skills/ bumps metadata.version."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
    )


def _read_skill_version(repo: Path, rev: str, skill: str) -> str | None:
    result = _git(repo, "show", f"{rev}:skills/{skill}/SKILL.md", check=False)
    if result.returncode != 0:
        return None
    text = result.stdout
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError(f"{rev}:skills/{skill}/SKILL.md is missing YAML frontmatter")
    lines = text.splitlines()
    try:
        end_idx = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{rev}:skills/{skill}/SKILL.md has unterminated frontmatter") from exc
    meta = yaml.safe_load("\n".join(lines[1:end_idx])) or {}
    version = str((meta.get("metadata") or {}).get("version", ""))
    if not SEMVER.fullmatch(version):
        raise ValueError(f"{rev}:skills/{skill}/SKILL.md has invalid metadata.version: {version!r}")
    return version


def _parse_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER.fullmatch(version)
    if not match:
        raise ValueError(f"Invalid semver: {version!r}")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def check_versions(repo: Path, base: str, head: str) -> list[str]:
    diff = _git(repo, "diff", "--name-only", base, head).stdout.splitlines()
    changed_skills = sorted(
        {parts[1] for path in diff if len(parts := Path(path).parts) >= 2 and parts[0] == "skills"}
    )
    errors: list[str] = []
    for skill in changed_skills:
        base_version = _read_skill_version(repo, base, skill)
        head_version = _read_skill_version(repo, head, skill)
        if base_version is None or head_version is None:
            continue
        if _parse_semver(head_version) <= _parse_semver(base_version):
            errors.append(
                f"{skill}: files changed under skills/{skill}/ without bumping "
                f"metadata.version ({base_version} -> {head_version})"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()

    errors = check_versions(args.repo, args.base, args.head)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("All changed skills bumped metadata.version.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
