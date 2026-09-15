"""
Ports the non-`/doiq/*` endpoints exercised under tests/regression_api_methods/ai_interview/ +
tests/test_regression/test_ai_interview/ in https://github.com/doselect/do-api-automation.git.
The `/doiq/conversation` calls in that domain reuse `src/constants/paths/doiq_api_path.py`
(same endpoint, same DOSELECT_PRIMARY_DOMAIN base) rather than duplicating it here.
"""
from __future__ import annotations

from src.core.do_api_config import DOSELECT_PRIMARY_DOMAIN

DASHBOARD_ANALYTICS = "/search/interview-ai/dashboard/analytics"
PSEARCH = "/search/psearch"
INTERVIEW_AI_INVITE = "/interview-ai/api/v1/invite"
RPC_UPLOAD = "/rpc/upload"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`)."""
    return DOSELECT_PRIMARY_DOMAIN
