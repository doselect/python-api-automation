"""Mirrors tests/test_regression/test_contest/test_patch_delete_custom_form.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.delete_custom_form
@pytest.mark.regression
@pytest.mark.contest
def test_patch_delete_custom_form(contest_response_handler: ContestResponseHandler):
    """Delete custom form fields from participantDataSettings."""
    contest_response_handler.patch_delete_participant_data_settings()
