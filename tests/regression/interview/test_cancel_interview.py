"""
Mirrors tests/test_regression/test_interview/test_cancel_interview.py (do-api-automation), plus
setup the source implicitly relied on. `post_cancel_interview` cancels the first UPCOMING interview
for the latest job role — the source test ran standalone banking on one already existing; this
schedules one first so the test doesn't depend on leftover state from another test/run.
"""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.cancel_interview
def test_cancel_interview(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.post_schedule_interview()
    interview_response_handler.post_cancel_interview()
