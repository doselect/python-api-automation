"""
Ports the `/customapi/fn/v1/*` (FirstNaukri) public-API endpoints exercised under
tests/public_apis/fn/ in https://github.com/doselect/do-api-automation.git.
"""
from __future__ import annotations

from src.core.do_api_config import BASE_URL

INVITE_CREATE = "/customapi/fn/v1/invite/create"
COMPANY_QUOTA = "/customapi/fn/v1/quota/{companySlug}"
REPORT_HTML = "/customapi/fn/v1/report/{transcriptId}/html"
REPORT_HTML_SUMMARY = "/customapi/fn/v1/report/{transcriptId}/html/summary"
REPORT_PDF = "/customapi/fn/v1/report/{transcriptId}/pdf"
REPORT_PDF_SUMMARY = "/customapi/fn/v1/report/{transcriptId}/pdf/summary"
BULK_REPORT = "/customapi/fn/v1/bulk_report"
TEST_DETAIL = "/customapi/fn/v1/test/{testSlug}"
TESTS_OF_COMPANY = "/customapi/fn/v1/tests/{companySlug}"


def set_base_url() -> str:
    """Mirrors utils.config.BASE_URL (env var `BASE_URL`)."""
    return BASE_URL
