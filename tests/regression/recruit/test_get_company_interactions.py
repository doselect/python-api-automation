"""Mirrors tests/test_regression/test_recruit/test_get_company_interactions.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler


@pytest.mark.regression
def test_get_company_interactions(recruit_response_handler: RecruitResponseHandler):
    recruit_response_handler.get_company_interactions()
