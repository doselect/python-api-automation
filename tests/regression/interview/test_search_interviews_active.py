"""
Mirrors 'tests/test_regression/test_interview/test_search_interviews active.py' (note the space in
the source filename — normalized to an underscore here; see DO_API_PORT_STATUS.md/the port report
for the reasoning). The source test function is literally named `test_search_expired_interviews`
even in this "active" file (an apparent copy-paste from test_search_interviews_expired.py) —
preserved as-is rather than renamed, since only the `status` argument actually differs.
"""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
def test_search_expired_interviews(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.search_interviews_based_on_status(status="ACTIVE")
