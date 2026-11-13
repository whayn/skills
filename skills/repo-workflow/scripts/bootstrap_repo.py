#!/usr/bin/env python3
"""Render the repo-workflow templates into a repository.

Writes CONTRIBUTING.md, AGENTS.md (plus a CLAUDE.md that imports it), SECURITY.md,
.editorconfig and .github/ (PR and
issue templates, CODEOWNERS, release notes, Dependabot, CI). Never overwrites an
existing file unless --force. Standard library only.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"
PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")
STACKS = ("python", "generic")
PYTHON_DEFAULTS = {
    "INSTALL_CMD": 'python -m pip install -e ".[dev]"',
    "LINT_CMD": "ruff check . && ruff format --check .",
    "TEST_CMD": "python -m pytest -q",
    "BUILD_CMD": "python -m build",
}


def target_path(relative):
    """templates/repo path -> repository path (dot- prefixes, stack suffixes)."""
    parts = []
    for part in relative.parts:
        if part.startswith("dot-"):
            part = "." + part[4:]
        parts.append(part)
    name = parts[-1]
    for stack in STACKS:
        name = name.replace(f".{stack}.", ".")
    parts[-1] = name
    return Path(*parts)


def stack_of(relative):
    for stack in STACKS:
        if f".{stack}." in relative.name:
            return stack
    return None


def render(text, values, *, yaml_file):
    common = (TEMPLATES / "ci-common-jobs.yml").read_text(encoding="utf-8")
    text = text.replace("  # {{COMMON_JOBS}}\n", common)
    out = []
    for line in text.splitlines(keepends=True):
        keys = PLACEHOLDER.findall(line)
        if keys and all(values.get(k) == "" for k in keys if k in values):
            stripped = PLACEHOLDER.sub("", line).strip()
            if stripped in ("", "- run:", "run:"):
                continue  # an optional command left empty: drop its line

        def sub(match):
            key = match.group(1)
            if key not in values:
                return match.group(0)
            value = values[key]
            # Commands become JSON strings in YAML (valid double-quoted scalars),
            # so ':' or '#' in a command cannot change the document's structure.
            return json.dumps(value) if yaml_file and key.endswith("_CMD") else value

        out.append(PLACEHOLDER.sub(sub, line))
    result = "".join(out)
    leftover = sorted(set(PLACEHOLDER.findall(result)))
    if leftover:
        raise SystemExit(f"unresolved placeholders: {', '.join(leftover)}")
    return result


def plan(args):
    values = {
        "PROJECT": args.project or args.repo,
        "OWNER": args.owner,
        "REPO": args.repo,
        "MAINTAINER": args.maintainer or f"{args.owner} <your verified noreply email>",
        "PYTHON_VERSION": args.python_version,
    }
    defaults = PYTHON_DEFAULTS if args.stack == "python" else {}
    for key, given in (
        ("INSTALL_CMD", args.install),
        ("LINT_CMD", args.lint),
        ("TEST_CMD", args.test),
        ("BUILD_CMD", args.build),
    ):
        value = given if given is not None else defaults.get(key)
        if value is None:
            raise SystemExit(f"--stack {args.stack} needs --{key[:-4].lower()} (use '' to omit)")
        values[key] = value
    if values["TEST_CMD"] == "":
        raise SystemExit("a test command is required")
    files = []
    root = TEMPLATES / "repo"
    for source in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = source.relative_to(root)
        stack = stack_of(relative)
        if stack is not None and stack != args.stack:
            continue
        destination = target_path(relative)
        text = render(
            source.read_text(encoding="utf-8"),
            values,
            yaml_file=destination.suffix in (".yml", ".yaml"),
        )
        files.append((destination, text))
    if args.local_notebook:
        local = TEMPLATES / "local"
        notebook = notebook_dir(args)
        files.append((Path("HANDOFF.md"), (local / "HANDOFF.md").read_text(encoding="utf-8")))
        files.append(
            (notebook / "README.md", (local / "notebook-README.md").read_text(encoding="utf-8"))
        )
    return files


def write_lf(path, text):
    """Write UTF-8 with LF endings on every platform (text mode on Windows adds CRs)."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def notebook_dir(args):
    path = Path(args.notebook_dir)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] == ".git":
        raise SystemExit("--notebook-dir must be a relative path inside the repository")
    return path


def excludes(args):
    return ("/HANDOFF.md", f"/{notebook_dir(args).as_posix()}/", "/.worktrees/")


def git_dir(target):
    try:
        out = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--git-common-dir"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    path = Path(out)
    return path if path.is_absolute() else (target / path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("target", help="repository root to write into")
    parser.add_argument("--owner", required=True, help="GitHub owner (user or org)")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--project", help="display name (default: repo)")
    parser.add_argument("--maintainer", help="'Name <noreply email>' for maintainer commits")
    parser.add_argument("--stack", choices=STACKS, default="python")
    parser.add_argument("--python-version", default="3.14")
    for name in ("install", "lint", "test", "build"):
        parser.add_argument(f"--{name}", help=f"{name} command ('' omits optional steps)")
    parser.add_argument("--local-notebook", action="store_true", help="add git-excluded notes")
    parser.add_argument(
        "--notebook-dir", default=".notes", help="git-excluded notes directory (default: .notes)"
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.is_dir():
        raise SystemExit(f"target is not a directory: {target}")
    report = []
    for relative, text in plan(args):
        path = target / relative
        exists = path.exists()
        action = "overwrite" if exists and args.force else "skip (exists)" if exists else "create"
        report.append({"path": relative.as_posix(), "action": action})
        if args.dry_run or action.startswith("skip"):
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        write_lf(path, text)
    if args.local_notebook:
        gdir = git_dir(target)
        if gdir is None:
            raise SystemExit("--local-notebook needs a git repository (for .git/info/exclude)")
        exclude = gdir / "info" / "exclude"
        current = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
        missing = [line for line in excludes(args) if line not in current.splitlines()]
        report.append({"path": str(exclude), "action": f"exclude {missing}" if missing else "ok"})
        if missing and not args.dry_run:
            exclude.parent.mkdir(parents=True, exist_ok=True)
            sep = "" if not current or current.endswith("\n") else "\n"
            write_lf(exclude, current + sep + "\n".join(missing) + "\n")
    print(json.dumps({"target": str(target), "dry_run": args.dry_run, "files": report}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
