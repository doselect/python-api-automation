"""Mirrors tests/test_regression/test_contest/test_get_all_contest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.regression
@pytest.mark.get_all_contests
@pytest.mark.contest
def test_get_all_contests(contest_response_handler: ContestResponseHandler):
    """Get all contests."""
    contest_response_handler.get_all_contests()
