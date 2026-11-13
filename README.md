# Whayn's agent skills

Reusable [Agent Skills](https://agentskills.io): each skill is a folder with a
`SKILL.md` plus optional `scripts/`, `templates/` and `references/`. They follow
the open specification, so they work with Claude Code, Codex, Cursor, Gemini CLI,
GitHub Copilot, OpenCode, Hermes Agent and any other agent that reads `SKILL.md`,
and they remain plain documentation for humans.

| Skill | What it does |
| --- | --- |
| [`repo-workflow`](skills/repo-workflow/SKILL.md) | Bootstrap and run an evidence-first GitHub workflow: issue → branch → tests first → verified PR → bot review + CI → owner merge. Ships CONTRIBUTING/AGENTS/PR/issue/CI templates and a script for the matching GitHub settings. |

## Install

### Any agent, with the `skills` CLI

[`skills`](https://github.com/vercel-labs/skills) (Node.js) copies a skill into
the right folder for each agent it detects:

```bash
npx skills add whayn/skills --skill repo-workflow        # this project
npx skills add whayn/skills --skill repo-workflow -g     # every project
```

### Claude Code plugin marketplace

```text
/plugin marketplace add whayn/skills
/plugin install repo-workflow@whayn-skills
```

### By hand

Copy `skills/repo-workflow/` (the whole folder, not just `SKILL.md`) into your
agent's skills directory, so that `.../skills/repo-workflow/SKILL.md` exists:

| Agent | This project | All projects |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex, Cursor, Gemini CLI, Copilot, OpenCode | `.agents/skills/` | `~/.agents/skills/` (Codex); see your agent's docs |

Paths are taken from each tool's documentation and the `skills` CLI; check your
agent's docs if it does not pick the skill up, and start a new session after
installing.

### Hermes Agent

```bash
hermes skills install whayn/skills/skills/repo-workflow
hermes skills update repo-workflow    # later
```

Hermes scans community skills before installing. This one ships scripts that call
`git` and `gh`, and a CI template that reads PR metadata from environment
variables, so the scan reports `caution` and blocks the install. Read the findings
(`hermes skills inspect whayn/skills/skills/repo-workflow`), then add `--force`.

## Use

Ask your agent, for example: "set up this repository with the repo-workflow
skill". It renders the files (dry run first), then applies the GitHub settings
(dry run first). Or run the scripts yourself:

```bash
python3 skills/repo-workflow/scripts/bootstrap_repo.py PATH --owner OWNER --repo REPO --dry-run
python3 skills/repo-workflow/scripts/apply_github_settings.py OWNER/REPO
```

The generated `AGENTS.md` is the single instruction file for agents; the
generated `CLAUDE.md` only imports it, because Claude Code reads `CLAUDE.md`.

## Contributing

This repository uses its own workflow; see [CONTRIBUTING.md](CONTRIBUTING.md).
Skills must pass `agentskills validate` ([reference validator](https://github.com/agentskills/agentskills)).

## License

[MIT](LICENSE)
