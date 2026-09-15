"""Mirrors tests/test_regression/test_ai_interview/test_ai_doiq_jd.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler


@pytest.mark.regression
@pytest.mark.post_doiq_conversation_jobdesc
@pytest.mark.ai_interview
def test_post_doiq_conversation_jobdesc(ai_interview_response_handler: AiInterviewResponseHandler):
    response = ai_interview_response_handler.post_doiq_conversation_jobdesc()
    assert response.status_code
