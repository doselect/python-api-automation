"""
Mirrors tests/test_regression/test_contest/test_remove_three_section_theme_prize_eligibility_section.py
(do-api-automation).
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.remove_three_section_theme_prize_eligibility_section
@pytest.mark.regression
@pytest.mark.contest
def test_remove_three_section_theme_prize_eligibility_section(contest_response_handler: ContestResponseHandler):
    """Remove the theme, prize, and eligibilityCriteria sections from the contest landing page."""
    contest_response_handler.patch_remove_three_section_theme_prize_eligibility_section()
