"""Mirrors tests/public_apis/fn/test_fn_get_html_report__summary_pdf.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import FN_HTML_REPORT_TRANSCRIPT_ID
from src.core.response_validator import validate_response_code
from src.responses.fn_response_handler import FnResponseHandler


@pytest.mark.public
@pytest.mark.naukri_campus
def test_fn_get_html_report__summary_pdf(fn_response_handler: FnResponseHandler, request):
    response = fn_response_handler.get_pdf_report_summary(FN_HTML_REPORT_TRANSCRIPT_ID)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
