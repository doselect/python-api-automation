"""Mirrors tests/test_regression/test_ai_interview/test_ai_create_interview.py (do-api-automation)."""
from __future__ import annotations

import time

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler
from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.regression
@pytest.mark.run(order=1)
@pytest.mark.create_new_ai_interview
@pytest.mark.ai_interview
def test_create_new_ai_interview(
    ai_interview_response_handler: AiInterviewResponseHandler, doiq_response_handler: DoiqResponseHandler
):
    ai_interview_response_handler.get_dashboard_analytics()
    doiq_response_handler.get_doiq_clear(context="interview")
    doiq_response_handler.get_doiq_init(context="interview")
    ai_interview_response_handler.post_doiq_conversation_jobdesc()
    time.sleep(15)

    next_payload = ai_interview_response_handler.get_doiq_conversation_ai_interview(
        preset="1.1", filesize=""
    )
    ai_interview_response_handler.post_doiq_conversation_ai_interview(next_payload)
    time.sleep(15)

    doiq_response_handler.get_doiq_conversation(context="interview", preset="2.1", filesize="")
    ai_interview_response_handler.post_doiq_conversation_followup(preset="3")
    time.sleep(15)

    doiq_response_handler.get_doiq_conversation(context="interview", preset="3.1", filesize="")
