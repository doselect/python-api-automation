"""
Mirrors tests/test_regression/test_interview/test_job_role_helper.py (do-api-automation) — the
source test function is named/docstring'd around "get the latest job role slug" but actually only
calls `get_all_job_roles`; preserved as-is (not "fixed" into calling `get_latest_job_role_slug`).
"""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
def test_get_latest_job_role_slug(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_all_job_roles()
