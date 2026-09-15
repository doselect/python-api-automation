"""Mirrors tests/test_regression/test_ai_interview/test_post_doiq_conversation.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler


@pytest.mark.post_doiq_conversation
def test_post_doiq_conversation(ai_interview_response_handler: AiInterviewResponseHandler):
    # Mirrors the source exactly: called standalone, with no preceding GET populating a JD
    # payload, so `next_payload` is None here just as `shared_data["post_extracted_jd_response"]`
    # is unset there.
    ai_interview_response_handler.post_doiq_conversation_ai_interview()
