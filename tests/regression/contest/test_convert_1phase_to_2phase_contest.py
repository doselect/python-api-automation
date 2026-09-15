"""Mirrors tests/test_regression/test_contest/test_convert_1phase_to_2phase_contest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.convert_1phase_to_2phase
@pytest.mark.regression
@pytest.mark.contest
def test_convert_1phase_to_2phase(contest_response_handler: ContestResponseHandler):
    """Convert contest from 1 phase to 2 phases."""
    contest_response_handler.convert_1phase_to_2phase()
