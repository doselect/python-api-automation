"""Mirrors tests/test_regression/test_contest/test_question_name_visibility.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.question_name_visibility
@pytest.mark.regression
@pytest.mark.contest
def test_hide_question_name(contest_response_handler: ContestResponseHandler):
    """Update to hide/show question name."""
    contest_response_handler.patch_question_name_visibility(True)
    contest_response_handler.patch_question_name_visibility(False)
