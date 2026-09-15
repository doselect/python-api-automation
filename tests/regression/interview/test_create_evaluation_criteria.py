"""Mirrors tests/test_regression/test_interview/test_create_evaluation_criteria.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.create_evaluation_criteria
def test_create_evaluation_criteria(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.post_create_evaluation_criteria()
