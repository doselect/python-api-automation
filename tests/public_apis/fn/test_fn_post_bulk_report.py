"""Mirrors tests/public_apis/fn/test_fn_post_bulk_report.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import FN_BULK_HTML_TRANSCRIPT_ID, FN_HTML_REPORT_TRANSCRIPT_ID
from src.core.response_validator import validate_response_code
from src.responses.fn_response_handler import FnResponseHandler


@pytest.mark.public
@pytest.mark.naukri_campus
def test_fn_post_bulk_report(fn_response_handler: FnResponseHandler, request):
    response = fn_response_handler.post_bulk_report(
        [FN_HTML_REPORT_TRANSCRIPT_ID, FN_BULK_HTML_TRANSCRIPT_ID]
    )
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
