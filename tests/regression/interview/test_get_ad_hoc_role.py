"""Mirrors tests/test_regression/test_interview/test_get_ad_hoc_role.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
def test_get_ad_hoc_role(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_ad_hoc_role()
