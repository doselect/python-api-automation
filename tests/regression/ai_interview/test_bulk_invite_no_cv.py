"""Mirrors tests/test_regression/test_ai_interview/test_bulk_invite_no_cv.py (do-api-automation)."""
from __future__ import annotations

from time import sleep

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler
from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.regression
@pytest.mark.run(order=4)
@pytest.mark.ai_interview
@pytest.mark.post_bulk_invite_no_cv
def test_post_bulk_invite_no_cv(
    ai_interview_response_handler: AiInterviewResponseHandler, doiq_response_handler: DoiqResponseHandler
):
    slug = ai_interview_response_handler.get_latest_ai_interview()
    ai_interview_response_handler.get_dashboard_analytics()
    doiq_response_handler.get_doiq_clear(context="interview")
    sleep(5)
    doiq_response_handler.get_doiq_init(context="interview")
    ai_interview_response_handler.post_bulk_invite_no_cv(slug)
