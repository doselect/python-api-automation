"""Mirrors tests/test_regression/test_recruit/test_assessment_update.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler


@pytest.mark.regression
def test_assessment_updates(recruit_response_handler: RecruitResponseHandler):
    res1 = recruit_response_handler.post_create_test()
    test_slug = res1["test_slug"]

    recruit_response_handler.get_test_details(test_slug)

    res3 = recruit_response_handler.patch_test_details(test_slug)
    assert res3["status_code"] == 202, f"Expected status code 202, got {res3['status_code']}"

    recruit_response_handler.get_test_details(test_slug)
