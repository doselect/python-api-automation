"""Mirrors tests/test_regression/test_contest/test_archive_contest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.archive_contest
@pytest.mark.regression
@pytest.mark.contest
def test_archive_contest(contest_response_handler: ContestResponseHandler):
    """Update to archive contest."""
    contest_response_handler.patch_archive_contest()
