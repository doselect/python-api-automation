"""
Ports the `/doiq/*` endpoints exercised under tests/regression_api_methods/doiq/ +
tests/test_regression/test_doiq/ in https://github.com/doselect/do-api-automation.git. Unlike
the `public_apis/*` domains (which hit `BASE_URL`), these session-auth endpoints hit
`DOSELECT_PRIMARY_DOMAIN` — the same host AuthManager logs into.
"""
from __future__ import annotations

from src.core.do_api_config import DOSELECT_PRIMARY_DOMAIN

DOIQ_INIT = "/doiq/init"
DOIQ_ROLES = "/doiq/roles"
DOIQ_SKILLS = "/doiq/skills"
DOIQ_RESPONSIBILITIES = "/doiq/responsibilities"
DOIQ_SKILL_TO_SKILL = "/doiq/skill_to_skill/"
DOIQ_CLEAR = "/doiq/clear"
DOIQ_CONVERSATION = "/doiq/conversation"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`)."""
    return DOSELECT_PRIMARY_DOMAIN
