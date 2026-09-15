"""Mirrors tests/test_regression/test_contest/test_team_contest_creation.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.team_contest_creation
@pytest.mark.regression
@pytest.mark.contest
def test_team_contest_creation(contest_response_handler: ContestResponseHandler):
    """Run the team contest creation test."""
    contest_response_handler.post_create_team_contest()
