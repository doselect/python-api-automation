"""
Ports the request-building side of tests/public_apis/fn/*.py (do-api-automation) — same
DoSelect-Api-Key/Secret header *names* as `problems`/`invite`, but sourced from the separate
FN_API_KEY/FN_API_SECRET env vars (a distinct FirstNaukri credential pair per utils/config.py).
"""
from __future__ import annotations

from src.constants.headers.header_constants import HeaderConstants
from src.constants.paths import fn_api_path
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.core.do_api_config import FN_API_KEY, FN_API_SECRET


def get_fn_headers() -> dict[str, str]:
    """Mirrors the inline `headers = {"DoSelect-Api-Key": config.FN_API_KEY, ...}` dict."""
    return {
        HeaderConstants.DOSELECT_API_KEY_HEADER: FN_API_KEY,
        HeaderConstants.DOSELECT_API_SECRET_HEADER: FN_API_SECRET,
    }


class FnSpecBuilder:
    """Builds and holds the reusable request specs for the ported `fn` public API tests."""

    def __init__(self) -> None:
        self._specs: dict[str, RequestSpec] = {}

    def _spec_for(self, key: str, base_path: str) -> RequestSpec:
        if key not in self._specs:
            self._specs[key] = build_request_spec(
                base_url=fn_api_path.set_base_url(),
                base_path=base_path,
                headers=get_fn_headers(),
            )
        return self._specs[key]

    def setup_all_specs(self) -> None:
        """Builds every spec up front, mirroring `specBuilder.setupAllSpecs()`."""
        for key, base_path in (
            ("invite_create", fn_api_path.INVITE_CREATE),
            ("company_quota", fn_api_path.COMPANY_QUOTA),
            ("report_html", fn_api_path.REPORT_HTML),
            ("report_html_summary", fn_api_path.REPORT_HTML_SUMMARY),
            ("report_pdf", fn_api_path.REPORT_PDF),
            ("report_pdf_summary", fn_api_path.REPORT_PDF_SUMMARY),
            ("bulk_report", fn_api_path.BULK_REPORT),
            ("test_detail", fn_api_path.TEST_DETAIL),
            ("tests_of_company", fn_api_path.TESTS_OF_COMPANY),
        ):
            self._spec_for(key, base_path)

    def get_spec(self, key: str) -> RequestSpec:
        return self._specs.get(key) or self._spec_for(key, getattr(fn_api_path, key.upper()))
