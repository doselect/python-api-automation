"""Mirrors tests/test_regression/test_recruit/test_retakes_flow.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.regression.recruit._mcq_attempt_flow import run_attempt_mcq_flow


@pytest.mark.regression
def test_retakes_flow(
    request, recruit_response_handler: RecruitResponseHandler, hacker_response_handler: HackerResponseHandler
):
    flow = run_attempt_mcq_flow(request, recruit_response_handler, hacker_response_handler, test_type="LEARN")

    res1 = recruit_response_handler.get_test_candidates(flow["test_slug"])
    invite_id = res1["invite_id"]

    recruit_response_handler.post_add_max_retakes(invite_id, retake_count=2)
    recruit_response_handler.post_remove_retakes(invite_id, flow["test_slug"], retake_count=1)
