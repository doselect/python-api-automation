"""Mirrors tests/test_regression/test_contest/test_add_custom_form.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_participant_data_settings
@pytest.mark.regression
@pytest.mark.contest
def test_add_participant_data_settings(contest_response_handler: ContestResponseHandler):
    """Updating contest participant data settings."""
    contest_response_handler.patch_add_participant_data_settings()
