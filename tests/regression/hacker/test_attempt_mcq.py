"""Mirrors tests/test_regression/test_hacker/test_attempt_mcq.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.public_apis.invite.post_invite_candidate import post_invite_candidate


@pytest.mark.regression
@pytest.mark.hacker
def test_attempt_mcq(
    request,
    recruit_response_handler: RecruitResponseHandler,
    hacker_response_handler: HackerResponseHandler,
    test_type: str = "RECRUIT",
    duration: int = 120,
):
    """
    `test_type`/`duration` are plain defaulted params, not fixtures — mirrors the source's
    `def test_attempt_mcq(request, shared_data, test_type="RECRUIT", duration=120)` (pytest only
    resolves fixtures for parameters *without* a default, so these always run with their literal
    defaults; no call site overrides them).
    """
    res0 = recruit_response_handler.post_create_test(test_type, duration)
    test_slug = res0["test_slug"]

    res1 = recruit_response_handler.get_test_details(test_slug)
    section_slug = res1["sections"][0]["slug"]

    res2 = recruit_response_handler.get_list_of_problems(test_slug, "MAR", "MCQ", 1)
    prob_to_add = res2["prob_to_add"]

    recruit_response_handler.post_add_problem(test_slug, section_slug, prob_to_add)

    res4 = recruit_response_handler.get_problem_details(prob_to_add[0])
    correct_answer = res4["correct_answer"]

    invite_shared_data: dict = {}
    res5 = post_invite_candidate(request, invite_shared_data, test_slug)
    access_code = res5["access_code"]

    hacker_response_handler.get_test_gateway(access_code)
    hacker_response_handler.post_test_gateway(access_code)
    hacker_response_handler.post_test_gateway_submit(access_code)

    hacker_response_handler.get_server_time()

    res10 = hacker_response_handler.get_identity_gateway()
    candidate_username = res10["candidate_username"]
    user_role_id = res10["user_role_id"]

    hacker_response_handler.get_hacker_details(user_role_id, candidate_username)

    res12 = hacker_response_handler.get_test_details(test_slug, candidate_username)
    test_id = res12["test_id"]

    res13 = hacker_response_handler.post_test_init(test_id, candidate_username)
    solutionset_id = res13["solutionset_id"]

    hacker_response_handler.get_infra_allocate(solutionset_id)

    hacker_response_handler.post_test_start(test_id, candidate_username)

    res16 = hacker_response_handler.get_sectionwise_problems(test_id, test_slug)
    problem_slug = res16["problem_slug"]

    res17 = hacker_response_handler.post_create_solution(
        "MCQ", candidate_username, problem_slug, test_slug, solutionset_id, correct_answer=correct_answer
    )
    solution_slug = res17["solution_slug"]

    hacker_response_handler.patch_solution(solution_slug, "MCQ", test_slug, correct_answer=correct_answer)

    hacker_response_handler.post_test_submit_all(solutionset_id, candidate_username)
