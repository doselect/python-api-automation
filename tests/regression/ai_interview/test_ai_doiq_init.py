"""Mirrors tests/test_regression/test_ai_interview/test_ai_doiq_init.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.regression
@pytest.mark.ai_interview
def test_get_doiq_init(doiq_response_handler: DoiqResponseHandler):
    doiq_response_handler.get_doiq_init(context="interview")
