"""Mirrors tests/test_regression/test_recruit/test_reminder_api.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL
from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.regression.recruit._creation_assessment_flow import run_creation_assessment_flow


@pytest.mark.regression
def test_reminder_api(recruit_response_handler: RecruitResponseHandler):
    flow = run_creation_assessment_flow(recruit_response_handler)

    recruit_response_handler.post_create_invite(CANDIDATE_EMAIL, test_slug=flow["test_slug"])

    res1 = recruit_response_handler.get_test_candidates(flow["test_slug"])
    invite_id = res1["invite_id"]

    recruit_response_handler.post_send_reminder(invite_id, flow["test_slug"])
    recruit_response_handler.get_bulk_reminder_status(flow["test_slug"])
    recruit_response_handler.post_clear_bulk_reminder(flow["test_slug"])
