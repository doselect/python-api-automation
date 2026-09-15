"""Mirrors tests/test_regression/test_ai_interview/test_ai_doiq_clear.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.regression
@pytest.mark.ai_interview
def test_get_doiq_clear(doiq_response_handler: DoiqResponseHandler):
    doiq_response_handler.get_doiq_clear(context="interview")
