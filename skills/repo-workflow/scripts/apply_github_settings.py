#!/usr/bin/env python3
"""Plan, and with --apply set, the repo-workflow GitHub settings via `gh api`.

Dry run by default: prints every request it would make. With --apply it runs them
in order, continues past failures and exits nonzero if any step failed.
"""

import argparse
import json
import subprocess
import sys
from urllib.parse import quote

DEFAULT_CHECKS = ("Quality", "Tests", "Secrets", "PR conventions")
LABELS = (
    ("bug", "D73A4A", "Reproducible defect or behavior regression"),
    ("enhancement", "A2EEEF", "Feature or design proposal"),
    ("documentation", "0075CA", "Documentation changes"),
    ("needs-triage", "D4C5F9", "New report awaiting maintainer triage"),
    ("testing", "5319E7", "Tests, fixtures and verification"),
    ("ci", "1D76DB", "Continuous integration and checks"),
    ("security", "B60205", "Security hardening; report vulnerabilities privately"),
    ("breaking-change", "B60205", "Incompatible public interface, configuration or data change"),
    ("dependencies", "0366D6", "Dependency updates"),
    ("blocked", "FBCA04", "Blocked by an explicit dependency"),
    ("priority: high", "D93F0B", "High priority; no response-time guarantee"),
    ("priority: normal", "FEF2C0", "Normal priority"),
    ("priority: low", "C2E0C6", "Low priority"),
    ("skip-changelog", "EDEDED", "Exclude maintenance-only work from release notes"),
)
TAG_RULESET = {
    "name": "Protect release tags",
    "target": "tag",
    "enforcement": "active",
    "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
    "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}, {"type": "update"}],
}


def steps(repo, branch, checks):
    """Ordered (description, method, endpoint, body) requests."""
    r = f"repos/{repo}"
    out = [
        (
            "merge settings: squash only, PR title subject, delete merged branches",
            "PATCH",
            r,
            {
                "allow_squash_merge": True,
                "allow_merge_commit": False,
                "allow_rebase_merge": False,
                "squash_merge_commit_title": "PR_TITLE",
                "squash_merge_commit_message": "COMMIT_MESSAGES",
                "delete_branch_on_merge": True,
                "allow_update_branch": True,
                "allow_auto_merge": True,
                "has_wiki": False,
                "has_projects": False,
            },
        )
    ]
    for name, color, description in LABELS:
        out.append(
            (
                f"label {name!r}",
                "LABEL",
                f"{r}/labels",
                {"name": name, "color": color, "description": description},
            )
        )
    out += [
        (
            f"protect {branch}: required checks {list(checks)}, linear history, "
            "resolved conversations, admins included",
            "PUT",
            f"{r}/branches/{branch}/protection",
            {
                "required_status_checks": {"strict": True, "contexts": list(checks)},
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": False,
                    "required_approving_review_count": 0,
                },
                "restrictions": None,
                "required_linear_history": True,
                "allow_force_pushes": False,
                "allow_deletions": False,
                "required_conversation_resolution": True,
            },
        ),
        ("protect v* release tags", "RULESET", f"{r}/rulesets", TAG_RULESET),
        ("private vulnerability reporting", "PUT", f"{r}/private-vulnerability-reporting", None),
        ("Dependabot alerts", "PUT", f"{r}/vulnerability-alerts", None),
        ("Dependabot security updates", "PUT", f"{r}/automated-security-fixes", None),
        (
            "secret scanning with push protection",
            "PATCH",
            r,
            {
                "security_and_analysis": {
                    "secret_scanning": {"status": "enabled"},
                    "secret_scanning_push_protection": {"status": "enabled"},
                }
            },
        ),
    ]
    return out


def gh(gh_path, method, endpoint, body=None):
    command = [gh_path, "api", "--method", method, endpoint]
    if body is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command,
        input=None if body is None else json.dumps(body),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip()[:500])
    return json.loads(result.stdout) if result.stdout.strip() else None


def run_step(gh_path, method, endpoint, body):
    if method == "LABEL":
        # Upsert: update an existing label, else create it.
        name = body["name"]
        try:
            gh(gh_path, "PATCH", f"{endpoint}/{quote(name, safe='')}", body)
        except RuntimeError:
            gh(gh_path, "POST", endpoint, body)
        return
    if method == "RULESET":
        existing = gh(gh_path, "GET", endpoint) or []
        match = [rs for rs in existing if rs.get("name") == body["name"]]
        if match:
            gh(gh_path, "PUT", f"{endpoint}/{match[0]['id']}", body)
        else:
            gh(gh_path, "POST", endpoint, body)
        return
    gh(gh_path, method, endpoint, body)


def main(argv=None):
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("repo", help="OWNER/REPO")
    parser.add_argument("--branch", help="protected branch (default: the repo's default branch)")
    parser.add_argument(
        "--check",
        action="append",
        dest="checks",
        help=f"required status check (repeatable; default: {', '.join(DEFAULT_CHECKS)})",
    )
    parser.add_argument("--gh", default="gh", help="gh executable")
    parser.add_argument("--apply", action="store_true", help="make the changes")
    args = parser.parse_args(argv)
    if args.repo.count("/") != 1:
        raise SystemExit("repo must be OWNER/REPO")
    branch = args.branch
    if branch is None:
        if args.apply:
            branch = (gh(args.gh, "GET", f"repos/{args.repo}") or {}).get("default_branch", "main")
        else:
            branch = "main"
    planned = steps(args.repo, branch, tuple(args.checks or DEFAULT_CHECKS))
    if not args.apply:
        for description, method, endpoint, body in planned:
            print(
                json.dumps(
                    {"step": description, "method": method, "endpoint": endpoint, "body": body}
                )
            )
        print(f"dry run: {len(planned)} steps; rerun with --apply", file=sys.stderr)
        return 0
    failures = 0
    for description, method, endpoint, body in planned:
        try:
            run_step(args.gh, method, endpoint, body)
            print(f"ok      {description}")
        except (RuntimeError, OSError) as exc:
            failures += 1
            print(f"FAILED  {description}: {exc}")
    print(f"{len(planned) - failures}/{len(planned)} steps applied")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
