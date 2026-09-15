"""
Ports the `/platform/v1/test*` and `/platform/v1/invite*` public-API endpoints exercised under
tests/public_apis/invite/ in https://github.com/doselect/do-api-automation.git. Query strings
that were baked into the f-string paths there (e.g. `?suppress_email=true`) are passed as
`query_params` at call time instead, per this framework's RequestSpec convention.
"""
from __future__ import annotations

from src.core.do_api_config import BASE_URL

TEST_LIST = "/platform/v1/test"
TEST_DETAIL = "/platform/v1/test/{testSlug}"
TEST_CANDIDATES = "/platform/v1/test/{testSlug}/candidates"
TEST_CANDIDATES_BULK = "/platform/v1/test/{testSlug}/candidates/bulk/"
TEST_CANDIDATE_DETAIL = "/platform/v1/test/{testSlug}/candidates/{candidateEmail}"
TEST_CANDIDATE_RETAKE = "/platform/v1/test/{testSlug}/candidates/{candidateEmail}/retake"
TEST_CANDIDATE_EXTEND_DURATION = "/platform/v1/test/{testSlug}/candidates/{candidateEmail}/extend_duration"
TEST_CANDIDATE_PAST_REPORTS = "/platform/v1/test/{testSlug}/candidates/{candidateEmail}/past_reports"
TEST_CANDIDATE_REPORT = "/platform/v1/test/{testSlug}/candidates/{candidateEmail}/report"
INVITE_LIST = "/platform/v1/invite/"


def set_base_url() -> str:
    """Mirrors utils.config.BASE_URL (env var `BASE_URL`)."""
    return BASE_URL
