"""
Mirrors tests/test_regression/test_recruit/test_assessment_lock_unlock.py (do-api-automation).

The source wraps its `patch_test_details` calls in `try/except AssertionError: pass` and then
asserts on `shared_data["last_status_code"]` (set inside the `except` branch before re-raising, so
it survives the swallowed exception) — see `RecruitResponseHandler.patch_test_details`'s docstring
for why the ported method returns the status code unasserted instead, letting this test assert on
`result["status_code"]` directly without the exception-carried-state indirection.
"""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler


@pytest.mark.regression
def test_assessment_lock_unlock(recruit_response_handler: RecruitResponseHandler):
    res1 = recruit_response_handler.post_create_test()
    test_slug = res1["test_slug"]

    recruit_response_handler.post_create_remove_lock(test_slug, "create")

    res3 = recruit_response_handler.patch_test_details(test_slug)
    assert res3["status_code"] != 202, "Lock creation failed"

    recruit_response_handler.post_create_remove_lock(test_slug, "remove")

    res5 = recruit_response_handler.patch_test_details(test_slug)
    assert res5["status_code"] == 202, "Lock removal failed"
