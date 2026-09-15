"""
Mirrors tests/test_regression/test_contest/test_update_abous_us_about_contest.py
(do-api-automation). Source has no `@pytest.mark.contest` on this one — preserved as-is.
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.update_about_us_about_contest
@pytest.mark.regression
def test_patch_update_about_us_about_contest(contest_response_handler: ContestResponseHandler):
    """Updating contest about us and about contest sections."""
    contest_response_handler.patch_update_about_us_about_contest()
