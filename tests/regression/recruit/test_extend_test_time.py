"""
Mirrors tests/test_regression/test_recruit/test_extend_test_time.py (do-api-automation). The
source's retry loop calls `get_solutionset(shared_data)` with one positional arg after first
calling it correctly as `get_solutionset(auth_manager, shared_data)` — a latent `TypeError` in the
source, moot here since `RecruitResponseHandler.get_solutionset` takes no live-flow args at all
(see that method's docstring) — both calls below are simply `recruit_response_handler.get_solutionset()`.
"""
from __future__ import annotations

from time import sleep

import pytest

from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.regression.recruit._mcq_attempt_flow import run_attempt_mcq_flow


@pytest.mark.regression
def test_extend_test_time(
    request, recruit_response_handler: RecruitResponseHandler, hacker_response_handler: HackerResponseHandler
):
    flow = run_attempt_mcq_flow(request, recruit_response_handler, hacker_response_handler)

    res1 = recruit_response_handler.get_test_candidates(flow["test_slug"])
    invite_id = res1["invite_id"]

    res2 = recruit_response_handler.get_solutionset()
    count = 0
    while res2.get("solutionset_status") in ("CTK", "RGP") and count < 3:
        res2 = recruit_response_handler.get_solutionset()
        sleep(10)
        count += 1

    recruit_response_handler.post_increase_test_duration([], invite_id, flow["test_slug"])
