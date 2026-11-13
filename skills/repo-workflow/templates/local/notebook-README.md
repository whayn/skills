# Local project notebook

Git-excluded (`.git/info/exclude`), never pushed. The Git root stays the single
working tree for source; this directory holds what supports the work.

| Location | Purpose |
| --- | --- |
| `../HANDOFF.md` | Current state and next acceptance step (replace, don't append) |
| `plans/` | One active plan per substantial change; older plans marked historical |
| `reviews/` | Saved review results, bound to the revision they reviewed |
| `history/` | Earlier notes, logs and evidence; preserve original contents |
| `../.worktrees/` | One worktree per in-flight branch; remove after merge |

Review history is not approval of newer files: bind acceptance to the current
revision. Keep private evidence here, not in the repository.
