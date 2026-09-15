"""Mirrors tests/test_regression/test_recruit/test_candidate_report_flow.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.regression.recruit._mcq_attempt_flow import run_attempt_mcq_flow


@pytest.mark.regression
def test_candidate_report_flow(
    request, recruit_response_handler: RecruitResponseHandler, hacker_response_handler: HackerResponseHandler
):
    flow = run_attempt_mcq_flow(request, recruit_response_handler, hacker_response_handler)

    recruit_response_handler.get_solution(
        flow["test_slug"], flow["candidate_username"], flow["problem_slug"],
    )
    recruit_response_handler.get_solution_revisions(
        flow["test_slug"], flow["candidate_username"], flow["problem_slug"],
    )
    recruit_response_handler.patch_solution_review(
        flow["test_slug"], flow["candidate_username"], flow["problem_slug"],
    )
    recruit_response_handler.post_direct_pdf(
        flow["solutionset_id"], flow["test_slug"], flow["candidate_username"], flow["problem_slug"],
    )
    recruit_response_handler.get_direct_pdf_status(
        flow["test_slug"], flow["candidate_username"], flow["problem_slug"],
    )
