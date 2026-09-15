"""Mirrors tests/test_regression/test_interview/test_get_interview_invitation_status.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
@pytest.mark.get_interview_invitation_status
@pytest.mark.interview_get_methods
def test_get_interview_invitation_status(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_interview_invitation_status()
