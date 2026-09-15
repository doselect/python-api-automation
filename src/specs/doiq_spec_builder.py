"""
Ports the header-building side of utils/header_generator.py's `get_doiq_*_headers` functions
(https://github.com/doselect/do-api-automation.git), for the endpoints exercised under
tests/regression_api_methods/doiq/ + tests/test_regression/test_doiq/.

Unlike ProblemsSpecBuilder/InviteSpecBuilder/FnSpecBuilder (static API-key headers, known before
any request), these headers need a *live, authenticated* AuthManager (`x-csrftoken`/`Cookie` come
from its session) — so specs are built lazily per call rather than all at once, since the
csrf/cookie values aren't known until `auth_manager.authenticate()` has run.
"""
from __future__ import annotations

from src.constants.headers.browser_fingerprint_headers import CHROME_WINDOWS_FINGERPRINT_HEADERS
from src.constants.paths import doiq_api_path
from src.core.auth_manager import AuthManager
from src.core.base_spec_builder import RequestSpec, build_request_spec


class DoiqSpecBuilder:
    """Builds the reusable request specs for the ported `doiq` regression endpoints."""

    def __init__(self, auth_manager: AuthManager) -> None:
        self._auth_manager = auth_manager

    def _auth_headers(self, referer_path: str, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "x-csrftoken": self._auth_manager.csrf_token,
            "Cookie": self._auth_manager.cookie,
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=1, i",
            "referer": f"{doiq_api_path.set_base_url()}{referer_path}",
            **CHROME_WINDOWS_FINGERPRINT_HEADERS,
        }
        if extra:
            headers.update(extra)
        return headers

    def doiq_init_spec(self) -> RequestSpec:
        """Mirrors get_doiq_init_headers."""
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_INIT,
            headers=self._auth_headers("/recruit/assistant/assessment"),
        )

    def doiq_roles_spec(self) -> RequestSpec:
        """Mirrors get_doiq_roles_headers (adds `if-none-match`, same as source)."""
        headers = self._auth_headers(
            "/recruit/assistant/assessment", {"if-none-match": '"8ad02222500cba9708f912c1bc1af515;gzip"'}
        )
        return build_request_spec(base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_ROLES, headers=headers)

    def doiq_skills_spec(self) -> RequestSpec:
        """Mirrors get_doiq_skills_headers."""
        headers = self._auth_headers(
            "/recruit/assistant/assessment", {"if-none-match": '"8ad02222500cba9708f912c1bc1af515;gzip"'}
        )
        return build_request_spec(base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_SKILLS, headers=headers)

    def doiq_responsibilities_spec(self) -> RequestSpec:
        """Mirrors get_doiq_responsibilities_headers."""
        headers = self._auth_headers(
            "/recruit/assistant/assessment", {"if-none-match": '"386b0c5dc02d6ce9adb0aab89797e798;gzip"'}
        )
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_RESPONSIBILITIES, headers=headers
        )

    def doiq_skill_to_skill_spec(self) -> RequestSpec:
        """Mirrors get_doiq_skill_to_skill_headers."""
        headers = self._auth_headers(
            "/recruit/assistant/assessment", {"if-none-match": '"209ba4524dcd91907caa613318f59b7f;gzip"'}
        )
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_SKILL_TO_SKILL, headers=headers
        )

    def doiq_clear_spec(self) -> RequestSpec:
        """Mirrors get_doiq_clear_headers."""
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_CLEAR,
            headers=self._auth_headers("/recruit/assistant/assessment"),
        )

    def doiq_conversation_post_spec(self) -> RequestSpec:
        """Mirrors get_doiq_conversation_headers (POST — adds content-type/origin, same as source)."""
        headers = self._auth_headers(
            "/recruit/assistant/assessment",
            {"content-type": "application/json", "origin": doiq_api_path.set_base_url()},
        )
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_CONVERSATION, headers=headers
        )

    def doiq_conversation_get_spec(self, ai_interview: bool = False) -> RequestSpec:
        """Mirrors get_doiq_conversation_get_headers / _ai_interview (referer differs)."""
        referer_path = "/recruit/assistant/interview" if ai_interview else "/recruit/assistant/assessment"
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_CONVERSATION,
            headers=self._auth_headers(referer_path),
        )
