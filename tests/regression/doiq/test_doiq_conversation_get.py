"""Mirrors tests/test_regression/test_doiq/test_doiq_conversation_get.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.regression
def test_doiq_conversation_get(doiq_response_handler: DoiqResponseHandler):
    response = doiq_response_handler.get_doiq_conversation(context="assessment", preset="1.1", filesize="")

    # Mirrors the source: only asserts 201 when no "interview.summary" item was found in the
    # response (an interview_name/slug already being present means the conversation already
    # progressed, so a fresh 201 isn't expected).
    parsed = doiq_response_handler.get_all_doiq_conversation_response(response)
    if not parsed["interview_name"]:
        assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
