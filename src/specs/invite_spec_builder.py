"""
Ports the request-building side of tests/public_apis/invite/*.py (do-api-automation) — same
DoSelect-Api-Key/Secret header auth as the `problems` domain, different base paths.
"""
from __future__ import annotations

from src.constants.headers.header_constants import HeaderConstants
from src.constants.paths import invite_api_path
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.core.do_api_config import DOSELECT_API_KEY, DOSELECT_API_SECRET


def get_invite_headers() -> dict[str, str]:
    """Mirrors the inline `headers = {"DoSelect-Api-Key": ..., "DoSelect-Api-Secret": ...}` dict."""
    return {
        HeaderConstants.DOSELECT_API_KEY_HEADER: DOSELECT_API_KEY,
        HeaderConstants.DOSELECT_API_SECRET_HEADER: DOSELECT_API_SECRET,
    }


class InviteSpecBuilder:
    """Builds and holds the reusable request specs for the ported `invite` public API tests."""

    def __init__(self) -> None:
        self._specs: dict[str, RequestSpec] = {}

    def _spec_for(self, key: str, base_path: str) -> RequestSpec:
        if key not in self._specs:
            self._specs[key] = build_request_spec(
                base_url=invite_api_path.set_base_url(),
                base_path=base_path,
                headers=get_invite_headers(),
            )
        return self._specs[key]

    def setup_all_specs(self) -> None:
        """Builds every spec up front, mirroring `specBuilder.setupAllSpecs()`."""
        for key, base_path in (
            ("test_list", invite_api_path.TEST_LIST),
            ("test_detail", invite_api_path.TEST_DETAIL),
            ("test_candidates", invite_api_path.TEST_CANDIDATES),
            ("test_candidates_bulk", invite_api_path.TEST_CANDIDATES_BULK),
            ("test_candidate_detail", invite_api_path.TEST_CANDIDATE_DETAIL),
            ("test_candidate_retake", invite_api_path.TEST_CANDIDATE_RETAKE),
            ("test_candidate_extend_duration", invite_api_path.TEST_CANDIDATE_EXTEND_DURATION),
            ("test_candidate_past_reports", invite_api_path.TEST_CANDIDATE_PAST_REPORTS),
            ("test_candidate_report", invite_api_path.TEST_CANDIDATE_REPORT),
            ("invite_list", invite_api_path.INVITE_LIST),
        ):
            self._spec_for(key, base_path)

    def get_spec(self, key: str) -> RequestSpec:
        return self._specs.get(key) or self._spec_for(key, getattr(invite_api_path, key.upper()))
