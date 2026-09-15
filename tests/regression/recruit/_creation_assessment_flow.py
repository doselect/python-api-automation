"""
Reusable step function mirroring tests/test_regression/test_recruit/test_creation_assessment.py's
body (do-api-automation) — not a pytest test itself (that's `test_creation_assessment.py`, which
calls this too), just the sequence several other `recruit` tests need as setup
(test_add_remove_sections.py, test_candidate_list.py, test_post_clone_test.py,
test_reminder_api.py all call `test_creation_assessment(shared_data)` in the source). Returns the
state explicitly instead of mutating `shared_data`, per the ai_interview/contest convention.
"""
from __future__ import annotations

from src.responses.recruit_response_handler import RecruitResponseHandler


def run_creation_assessment_flow(
    recruit_response_handler: RecruitResponseHandler, test_type: str = "RECRUIT", duration: int = 120
) -> dict:
    res1 = recruit_response_handler.post_create_test(test_type, duration)
    test_slug = res1["test_slug"]

    res2 = recruit_response_handler.get_test_details(test_slug)
    sections = res2["sections"]

    recruit_response_handler.get_problem_search(test_slug)

    res4 = recruit_response_handler.get_list_of_problems(test_slug, "MAR", "MCQ", 1)
    prob_to_add = res4["prob_to_add"]

    section_slug = sections[0]["slug"]
    res5 = recruit_response_handler.post_add_problem(test_slug, section_slug, prob_to_add)

    return {
        "test_slug": test_slug,
        "test_id": res1["test_id"],
        "sections": sections,
        "section_slug": section_slug,
        "prob_to_add": prob_to_add,
        "problem_id": res5.get("problem_id"),
    }
