"""Mirrors tests/test_regression/test_interview/test_get_interview_technologies_list.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.get_interview_technologies_list
def test_get_interview_technology_list(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_interview_technologies_list()
