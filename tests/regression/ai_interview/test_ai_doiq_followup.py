"""Mirrors tests/test_regression/test_ai_interview/test_ai_doiq_followup.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler


@pytest.mark.post_doiq_conversation_followup
def test_post_doiq_conversation_followup(ai_interview_response_handler: AiInterviewResponseHandler):
    ai_interview_response_handler.post_doiq_conversation_followup(preset="3")
