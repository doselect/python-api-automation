"""Mirrors tests/test_regression/test_recruit/test_patch_company_details.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler


@pytest.mark.regression
def test_patch_company_details(recruit_response_handler: RecruitResponseHandler):
    res1 = recruit_response_handler.get_company_details()

    recruit_response_handler.patch_company_details(res1["company_details"])

    recruit_response_handler.get_company_details()
