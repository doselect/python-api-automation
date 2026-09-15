"""Mirrors tests/test_regression/test_recruit/test_post_clone_test.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler
from tests.regression.recruit._creation_assessment_flow import run_creation_assessment_flow


@pytest.mark.regression
def test_post_clone_test(recruit_response_handler: RecruitResponseHandler):
    flow = run_creation_assessment_flow(recruit_response_handler)
    recruit_response_handler.post_clone_test(flow["test_slug"])
