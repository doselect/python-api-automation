"""
Ports the header-building side of tests/regression_api_methods/ai_interview/*.py
(do-api-automation): each source function calls
`generate_headers(USER_TYPE_RECRUITER, "default", shared_data)` then `.update(...)` a few
endpoint-specific overrides — mirrored here as one spec-building method per endpoint.
"""
from __future__ import annotations

from src.constants.headers.browser_fingerprint_headers import CHROME_LINUX_FINGERPRINT_HEADERS
from src.constants.paths import ai_interview_api_path, doiq_api_path
from src.core.auth_manager import AuthManager
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.specs.session_auth_headers import default_recruiter_headers


class AiInterviewSpecBuilder:
    """Builds the reusable request specs for the ported `ai_interview` regression endpoints."""

    def __init__(self, auth_manager: AuthManager) -> None:
        self._auth_manager = auth_manager

    def dashboard_analytics_spec(self) -> RequestSpec:
        """Mirrors get_dashboard_analytics's headers (plain default recruiter headers)."""
        return build_request_spec(
            base_url=ai_interview_api_path.set_base_url(), base_path=ai_interview_api_path.DASHBOARD_ANALYTICS,
            headers=default_recruiter_headers(self._auth_manager),
        )

    def latest_ai_interview_spec(self) -> RequestSpec:
        """Mirrors get_latest_ai_interview's headers (default + Linux/Chrome-129 fingerprint override)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-IN,en;q=0.9,kn-IN;q=0.8,kn;q=0.7,en-GB;q=0.6,en-US;q=0.5",
                "dnt": "1",
                "if-none-match": '"ed174471c1b809a64230aa22ca7f69f2;gzip"',
                "priority": "u=1, i",
                "referer": f"{ai_interview_api_path.set_base_url()}/recruit/interviews/ai",
                **CHROME_LINUX_FINGERPRINT_HEADERS,
            }
        )
        return build_request_spec(
            base_url=ai_interview_api_path.set_base_url(), base_path=ai_interview_api_path.PSEARCH, headers=headers
        )

    def bulk_invite_spec(self) -> RequestSpec:
        """Mirrors post_bulk_invite.py's headers (default + referer override only — no fingerprint/content-type overrides)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update({"referer": f"{ai_interview_api_path.set_base_url()}/recruit/interviews/ai"})
        return build_request_spec(
            base_url=ai_interview_api_path.set_base_url(), base_path=ai_interview_api_path.INTERVIEW_AI_INVITE,
            headers=headers,
        )

    def invite_ai_interview_spec(self, slug: str) -> RequestSpec:
        """Mirrors post_invite_ai_interview.py's headers (long accept-language, no cache-control/pragma)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-IN,en;q=0.9,kn-IN;q=0.8,kn;q=0.7,en-GB;q=0.6,en-US;q=0.5",
                "content-type": "application/json",
                "dnt": "1",
                "origin": ai_interview_api_path.set_base_url(),
                "priority": "u=1, i",
                "referer": f"{ai_interview_api_path.set_base_url()}/recruit/assistant/interview-report/{slug}",
                **CHROME_LINUX_FINGERPRINT_HEADERS,
            }
        )
        return build_request_spec(
            base_url=ai_interview_api_path.set_base_url(), base_path=ai_interview_api_path.INTERVIEW_AI_INVITE,
            headers=headers,
        )

    def bulk_invite_no_cv_spec(self, slug: str) -> RequestSpec:
        """Mirrors post_bulk_invite_no_cv.py's headers (short accept-language, adds cache-control/pragma)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-IN,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "dnt": "1",
                "origin": ai_interview_api_path.set_base_url(),
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": f"{ai_interview_api_path.set_base_url()}/recruit/assistant/interview-report/{slug}",
                **CHROME_LINUX_FINGERPRINT_HEADERS,
            }
        )
        return build_request_spec(
            base_url=ai_interview_api_path.set_base_url(), base_path=ai_interview_api_path.INTERVIEW_AI_INVITE,
            headers=headers,
        )

    def doiq_conversation_ai_interview_spec(self) -> RequestSpec:
        """Mirrors get_ai_interview_doiq_conversation.py's headers (default + interview referer)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update({"referer": f"{doiq_api_path.set_base_url()}/recruit/assistant/interview"})
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_CONVERSATION, headers=headers
        )

    def doiq_conversation_report_spec(self, slug: str) -> RequestSpec:
        """Mirrors post_single_invite_no_cv.py's headers (interview-report referer + Linux fingerprint)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-IN,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "dnt": "1",
                "origin": doiq_api_path.set_base_url(),
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": f"{doiq_api_path.set_base_url()}/recruit/assistant/interview-report/{slug}",
                **CHROME_LINUX_FINGERPRINT_HEADERS,
            }
        )
        return build_request_spec(
            base_url=doiq_api_path.set_base_url(), base_path=doiq_api_path.DOIQ_CONVERSATION, headers=headers
        )

    def upload_file_spec(self) -> RequestSpec:
        """Mirrors post_upload_file.py's headers (default + interview referer)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update({"referer": f"{ai_interview_api_path.set_base_url()}/recruit/assistant/interview"})
        return build_request_spec(
            base_url=ai_interview_api_path.set_base_url(), base_path=ai_interview_api_path.RPC_UPLOAD, headers=headers
        )
