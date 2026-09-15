"""Mirrors tests/test_regression/test_ai_interview/test_ai_get_analytics.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler


@pytest.mark.regression
@pytest.mark.get_dashboard_analytics
@pytest.mark.ai_interview
def test_get_dashboard_analytics(ai_interview_response_handler: AiInterviewResponseHandler):
    ai_interview_response_handler.get_dashboard_analytics()
