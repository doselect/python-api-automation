"""Mirrors tests/test_regression/test_interview/test_invite_interviewer.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
def test_post_invite_interviewer(interview_response_handler: InterviewResponseHandler):
    email, _full_name = interview_response_handler.post_invite_interviewer()
    interview_response_handler.delete_invite_interviewer(email)
