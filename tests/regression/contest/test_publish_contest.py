"""Mirrors tests/test_regression/test_contest/test_publish_contest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.publish_contest
@pytest.mark.regression
@pytest.mark.contest
def test_publish_contest(contest_response_handler: ContestResponseHandler):
    """Update to publish contest."""
    contest_response_handler.patch_publish_contest()
