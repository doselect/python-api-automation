"""Mirrors tests/test_regression/test_recruit/test_creation_assessment.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.regression.recruit._creation_assessment_flow import run_creation_assessment_flow


@pytest.mark.regression
def test_creation_assessment(recruit_response_handler: RecruitResponseHandler):
    run_creation_assessment_flow(recruit_response_handler)
