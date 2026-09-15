"""
Reusable step function mirroring tests/regression/hacker/test_attempt_mcq.py's body (itself a port
of tests/test_regression/test_hacker/test_attempt_mcq.py, do-api-automation) — re-implemented here
rather than imported, since several `recruit` source tests (test_candidate_report_flow.py,
test_extend_test_time.py, test_retakes_flow.py, test_solutionset_reset_flow.py) call
`test_attempt_mcq(request, shared_data)` purely as a setup step and then read state it populated
into `shared_data` (test_slug, candidate_username, solutionset_id, problem_slug, ...) — state this
port's `test_attempt_mcq` doesn't return (see that file: it has no `return`, matching the source's
implicit `None`, since nothing in the already-completed `hacker` domain needed its output). Rather
than modify that already-merged file, this duplicates its exact call sequence and returns the state
explicitly, per the ai_interview/contest convention — same requests, same assertions, same payloads
(delegates to the very same `recruit_response_handler`/`hacker_response_handler` methods).
"""
from __future__ import annotations

from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.public_apis.invite.post_invite_candidate import post_invite_candidate


def run_attempt_mcq_flow(
    request,
    recruit_response_handler: RecruitResponseHandler,
    hacker_response_handler: HackerResponseHandler,
    test_type: str = "RECRUIT",
    duration: int = 120,
) -> dict:
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

    return {
        "test_slug": test_slug,
        "section_slug": section_slug,
        "test_id": test_id,
        "candidate_username": candidate_username,
        "solutionset_id": solutionset_id,
        "problem_slug": problem_slug,
        "solution_slug": solution_slug,
        "access_code": access_code,
    }
