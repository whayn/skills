# Manual Behavior Evals

This directory holds prompt-and-expectation suites for checking that coding
agents trigger the right skill and follow its safety and workflow rules.

These evals are **run by hand**, not in CI, because executing them requires
live model calls and a disposable repository or sandbox.

## Running an eval

1. Create a fresh disposable git repository (or temporary directory) with the
   skill installed.
2. Start a new agent session and send the `prompt` from a case in
   `evals/<skill>.json`.
3. Verify each item in `expected_behaviors` (and confirm `should_trigger`
   matches whether the skill was activated).
4. Discard the temporary directory when done.
