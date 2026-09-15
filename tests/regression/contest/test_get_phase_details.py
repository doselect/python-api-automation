"""Mirrors tests/test_regression/test_contest/test_get_phase_details.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.get_phase_details
@pytest.mark.regression
@pytest.mark.contest
def test_get_phase_details(contest_response_handler: ContestResponseHandler):
    """Get phase details for the latest contest."""
    contest_response_handler.get_phase_details()
