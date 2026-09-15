"""Mirrors tests/test_regression/test_hacker/test_attempt_coding.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.public_apis.invite.post_invite_candidate import post_invite_candidate


@pytest.mark.regression
@pytest.mark.hacker
def test_attempt_coding(
    request, recruit_response_handler: RecruitResponseHandler, hacker_response_handler: HackerResponseHandler
):
    res0 = recruit_response_handler.post_create_test()
    test_slug = res0["test_slug"]

    res1 = recruit_response_handler.get_test_details(test_slug)
    section_slug = res1["sections"][0]["slug"]

    res2 = recruit_response_handler.get_list_of_problems(test_slug, "MAR", "SCR", 1)
    prob_to_add = res2["prob_to_add"]

    res3 = recruit_response_handler.get_problem_details(prob_to_add[0])
    solution_lang = res3["solution_lang"]
    solution_code = res3["solution_code"]

    recruit_response_handler.post_add_problem(test_slug, section_slug, prob_to_add)

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

    # get_infra_allocate is commented out in the source test too.

    hacker_response_handler.post_test_start(test_id, candidate_username)

    res15 = hacker_response_handler.connect_websocket(candidate_username, solutionset_id, test_id, test_slug)
    sock_id = res15["sock_id"]

    hacker_response_handler.get_technologies()

    res17 = hacker_response_handler.get_sectionwise_problems(test_id, test_slug)
    problem_slug = res17["problem_slug"]
    problem_id = res17["problem_id"]

    res18 = hacker_response_handler.get_assessment_problems(test_id, problem_id, solution_lang)
    problem_stub = res18["problem_stub"]

    res19 = hacker_response_handler.post_create_solution(
        "SCR", candidate_username, problem_slug, test_slug, solutionset_id,
        problem_stub=problem_stub, solution_lang=solution_lang,
    )
    solution_slug = res19["solution_slug"]
    solution_id = res19["solution_id"]

    hacker_response_handler.patch_solution(
        solution_slug, "SCR", test_slug, solution_code=solution_code, solution_lang=solution_lang
    )

    hacker_response_handler.post_submit_solution(solution_id, sock_id, test_slug, solution_slug, candidate_username)

    hacker_response_handler.post_test_submit_all(solutionset_id, candidate_username)
