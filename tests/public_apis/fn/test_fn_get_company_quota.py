"""Mirrors tests/public_apis/fn/test_fn_get_company_quota.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import FN_COMPANY_SLUG
from src.core.response_validator import validate_response_code
from src.responses.fn_response_handler import FnResponseHandler


@pytest.mark.public
@pytest.mark.naukri_campus
def test_fn_get_company_quota(fn_response_handler: FnResponseHandler, request):
    response = fn_response_handler.get_company_quota(FN_COMPANY_SLUG)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
