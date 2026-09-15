"""
Ports the `api_helper.make_request(...)` call sites in tests/public_apis/fn/*.py
(do-api-automation), mirroring ProblemsResponseHandler's convention.
"""
from __future__ import annotations

from typing import Any

import requests

from src.core.rest_client import execute_request
from src.specs.fn_spec_builder import FnSpecBuilder


class FnResponseHandler:
    """Wraps an FnSpecBuilder to centralize the ported `fn` (FirstNaukri) public API calls."""

    def __init__(self, spec_builder: FnSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def create_invite(self, payload: dict[str, Any], expected_status_code: int = 200) -> requests.Response:
        """Mirrors POST /customapi/fn/v1/invite/create (test_create_invite.py, test_fn_try_this_test.py)."""
        return execute_request(
            self._spec_builder.get_spec("invite_create"), "POST", body=payload,
            expected_status_code=expected_status_code,
        )

    def get_company_quota(self, company_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /customapi/fn/v1/quota/{companySlug} (test_fn_get_company_quota.py)."""
        return execute_request(
            self._spec_builder.get_spec("company_quota"), "GET",
            path_params={"companySlug": company_slug}, expected_status_code=expected_status_code,
        )

    def get_html_report(self, transcript_id: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../report/{transcriptId}/html (test_fn_get_html_report.py)."""
        return execute_request(
            self._spec_builder.get_spec("report_html"), "GET",
            path_params={"transcriptId": transcript_id}, expected_status_code=expected_status_code,
        )

    def get_html_report_summary(self, transcript_id: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../report/{transcriptId}/html/summary (test_fn_get_html_report_summary.py)."""
        return execute_request(
            self._spec_builder.get_spec("report_html_summary"), "GET",
            path_params={"transcriptId": transcript_id}, expected_status_code=expected_status_code,
        )

    def get_pdf_report(self, transcript_id: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../report/{transcriptId}/pdf (test_fn_get_html_report_pdf.py)."""
        return execute_request(
            self._spec_builder.get_spec("report_pdf"), "GET",
            path_params={"transcriptId": transcript_id}, expected_status_code=expected_status_code,
        )

    def get_pdf_report_summary(self, transcript_id: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../report/{transcriptId}/pdf/summary (test_fn_get_html_report__summary_pdf.py)."""
        return execute_request(
            self._spec_builder.get_spec("report_pdf_summary"), "GET",
            path_params={"transcriptId": transcript_id}, expected_status_code=expected_status_code,
        )

    def post_bulk_report(self, transcript_ids: list[str], expected_status_code: int = 200) -> requests.Response:
        """Mirrors POST /customapi/fn/v1/bulk_report (test_fn_post_bulk_report.py)."""
        return execute_request(
            self._spec_builder.get_spec("bulk_report"), "POST",
            body={"fn_transcript_ids": transcript_ids}, expected_status_code=expected_status_code,
        )

    def get_one_test(self, test_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /customapi/fn/v1/test/{testSlug} (test_get_all_one_test.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_detail"), "GET",
            path_params={"testSlug": test_slug}, expected_status_code=expected_status_code,
        )

    def get_all_tests(self, company_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /customapi/fn/v1/tests/{companySlug} (test_get_all_tests.py)."""
        return execute_request(
            self._spec_builder.get_spec("tests_of_company"), "GET",
            path_params={"companySlug": company_slug}, expected_status_code=expected_status_code,
        )
