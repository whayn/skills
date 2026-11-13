"""Schema checks for manual agent behavior evals under evals/."""

import json

from tests.support import ROOT, skill_dirs

EVALS = ROOT / "evals"


def test_eval_files_have_valid_schema():
    assert EVALS.is_dir(), f"missing {EVALS}"
    eval_files = sorted(EVALS.glob("*.json"))
    assert eval_files, "expected at least one eval suite in evals/"

    known_skills = {s.name for s in skill_dirs()}
    for path in eval_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        skill = data.get("skill")
        assert skill in known_skills, f"{path}: unknown skill {skill!r}"
        cases = data.get("cases", [])
        assert cases, f"{path}: expected at least one eval case"
        seen_ids = set()
        for case in cases:
            case_id = case.get("id")
            assert isinstance(case_id, str) and case_id and case_id not in seen_ids
            seen_ids.add(case_id)
            assert isinstance(case.get("prompt"), str) and case["prompt"].strip()
            assert isinstance(case.get("should_trigger"), bool)
            behaviors = case.get("expected_behaviors")
            assert isinstance(behaviors, list) and behaviors
            assert all(isinstance(b, str) and b.strip() for b in behaviors)
