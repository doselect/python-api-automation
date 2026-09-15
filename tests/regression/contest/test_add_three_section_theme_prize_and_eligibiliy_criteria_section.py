"""
Mirrors tests/test_regression/test_contest/test_add_three_section_theme_prize_and_eligibiliy_criteria_section.py
(do-api-automation).
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_three_section_theme_prize_and_eligibility_criteria_section
@pytest.mark.regression
@pytest.mark.contest
def test_add_three_section_theme_prize_and_eligibility_criteria_section(
    contest_response_handler: ContestResponseHandler,
):
    """Add theme, prize, and eligibilityCriteria sections in the contest landing page."""
    contest_response_handler.patch_add_three_section_theme_prize_and_eligibility_criteria_section()
