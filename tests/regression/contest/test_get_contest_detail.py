"""Mirrors tests/test_regression/test_contest/test_get_contest_detail.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.get_contest_details
@pytest.mark.regression
@pytest.mark.contest
def test_get_contest_details(contest_response_handler: ContestResponseHandler):
    """Getting contest details."""
    contest_response_handler.get_contest_details()
