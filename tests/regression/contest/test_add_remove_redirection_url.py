"""Mirrors tests/test_regression/test_contest/test_add_remove_redirection_url.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.redirection_url
@pytest.mark.regression
@pytest.mark.contest
def test_add_remove_redirection_url(contest_response_handler: ContestResponseHandler):
    """Test PATCH update to add/remove redirection URL in phase settings."""
    contest_response_handler.patch_add_remove_redirection_url(action="add")
    contest_response_handler.patch_add_remove_redirection_url(action="remove")
