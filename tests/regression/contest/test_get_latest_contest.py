"""Mirrors tests/test_regression/test_contest/test_get_latest_contest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.get_latest_contest
@pytest.mark.regression
@pytest.mark.contest
def test_get_latest_contest(contest_response_handler: ContestResponseHandler):
    """Getting latest contest."""
    contest_response_handler.get_latest_contest_id()
