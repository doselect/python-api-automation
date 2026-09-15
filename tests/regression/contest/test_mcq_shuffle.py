"""Mirrors tests/test_regression/test_contest/test_mcq_shuffle.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.mcq_shuffle
@pytest.mark.regression
@pytest.mark.contest
def test_mcq_shuffle(contest_response_handler: ContestResponseHandler):
    """Update MCQ option shuffle."""
    contest_response_handler.patch_mcq_shuffle(True)
    contest_response_handler.patch_mcq_shuffle(False)
