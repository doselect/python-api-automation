"""Mirrors tests/test_regression/test_contest/test_convert_2phase_to_1phase.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.convert_2phase_to_1phase
@pytest.mark.regression
@pytest.mark.contest
def test_convert_2phase_to_1phase(contest_response_handler: ContestResponseHandler):
    """Convert contest from 2 phases to 1 phase."""
    contest_response_handler.convert_2phase_to_1phase()
