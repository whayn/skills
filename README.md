# Whayn's agent skills

Reusable [Hermes Agent](https://github.com/NousResearch/hermes-agent) skills.
Each one is a `SKILL.md` plus optional `scripts/`, `templates/` and `references/`,
so it also works as plain documentation for other agents or humans.

| Skill | What it does |
| --- | --- |
| [`repo-workflow`](skills/repo-workflow/SKILL.md) | Bootstrap and run an evidence-first GitHub workflow: issue → branch → tests first → verified PR → bot review + CI → owner merge. Ships CONTRIBUTING/AGENTS/PR/issue/CI templates and a script for the matching GitHub settings. |

## Install

```bash
hermes skills install whayn/skills/skills/repo-workflow
# or add the whole repository as a tap:
hermes skills tap add whayn/skills
```

Hermes scans community skills before installing. This one ships scripts that call
`git` and `gh` and a CI template that reads PR metadata from environment
variables, so the scan reports a `caution` verdict and blocks the install. Read the
findings (`hermes skills inspect whayn/skills/skills/repo-workflow`), then add
`--force` to install it. Update later with `hermes skills update repo-workflow`.

## Use

Ask your agent, for example: "set up this repository with the repo-workflow
skill". It renders the files (dry run first), then applies the GitHub settings
(dry run first). Or run the scripts directly:

```bash
python3 skills/repo-workflow/scripts/bootstrap_repo.py PATH --owner OWNER --repo REPO --dry-run
python3 skills/repo-workflow/scripts/apply_github_settings.py OWNER/REPO
```

## Contributing

This repository uses its own workflow; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
