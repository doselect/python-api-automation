"""Mirrors tests/test_regression/test_recruit/test_proctoring_report.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler


@pytest.mark.regression
def test_proctoring_report(recruit_response_handler: RecruitResponseHandler):
    recruit_response_handler.get_proctor_verdict()
    recruit_response_handler.get_solutionset()
    recruit_response_handler.get_test_report_comment()
