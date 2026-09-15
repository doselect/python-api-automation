"""Mirrors tests/test_regression/test_doiq/test_doiq_skill.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.regression
def test_doiq_skills(doiq_response_handler: DoiqResponseHandler):
    doiq_response_handler.get_doiq_skills()
