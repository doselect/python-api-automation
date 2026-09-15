"""Mirrors tests/test_regression/test_contest/test_clone_contest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.clone_contest
@pytest.mark.regression
@pytest.mark.contest
def test_clone_contest(contest_response_handler: ContestResponseHandler):
    """Clone contest."""
    contest_response_handler.post_clone_contest()
