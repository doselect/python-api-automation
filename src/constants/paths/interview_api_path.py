"""
Ports the endpoints exercised under tests/regression_api_methods/interview/ +
tests/test_regression/test_interview/ in https://github.com/doselect/do-api-automation.git.

Unlike the single-domain doiq/ai_interview/content_creator ports, `interview` genuinely spans
three different hosts (confirmed by reading every source file, not assumed):
  - `DOSELECT_PRIMARY_DOMAIN` — almost everything (`/interview-service/api/v1/*`,
    `/rpc/invite.interviewer_invite`, `/api/v1/company/doselect-problemsetters`).
  - `DOLORES_BASE_URL` — `get_active_interviewers.py`'s `/search/interviewers` call.
  - `DO_INTERVIEW_INTERFACE_DOMAIN` — `get_interview_gateway.py`'s unauthenticated
    page-navigation-style `/gateway/{token}` GET.
"""
from __future__ import annotations

from src.core.do_api_config import DO_INTERVIEW_INTERFACE_DOMAIN, DOLORES_BASE_URL, DOSELECT_PRIMARY_DOMAIN

INTERVIEW_DETAIL = "/interview-service/api/v1/interviews/{interviewSlug}/"
RPC_INTERVIEWER_INVITE = "/rpc/invite.interviewer_invite"
ROLE_RECOMMEND_PROBLEM_DETAIL = "/interview-service/api/v1/roles/{jobRoleSlug}/recommend/{problemSlug}/"
ROLE_AD_HOC = "/interview-service/api/v1/roles/{jobRoleSlug}/ad_hoc/"
SEARCH_ROLE = "/interview-service/api/v1/search/role/"
SEARCH_INTERVIEWERS = "/search/interviewers"
GATEWAY = "/gateway/{gatewayToken}"
INTERVIEW_INVITATION_STATUS = "/interview-service/api/v1/interviews/{interviewSlug}/interview_invitation_status/"
INTERVIEW_META = "/interview-service/api/v1/interviews/{interviewToken}/meta/"
INTERVIEW_QUESTIONS = "/interview-service/api/v1/interviews/{interviewSlug}/questions/"
INTERVIEW_REPORT = "/interview-service/api/v1/interviews/{interviewSlug}/report/"
INTERVIEW_STATUS = "/interview-service/api/v1/interviews/{interviewSlug}/status/"
INTERVIEW_TECHNOLOGY_LIST = "/interview-service/api/v1/interviews/technology/list/"
INTERVIEW_INTERVIEWER_FEEDBACK = "/interview-service/api/v1/interviews/{interviewSlug}/interviewer_feedback/"
INTERVIEW_INTERVIEWER_FEEDBACK_DETAIL = (
    "/interview-service/api/v1/interviews/{interviewSlug}/interviewer_feedback/{feedbackSlug}/"
)
ROLE_DETAIL = "/interview-service/api/v1/roles/{jobRoleSlug}/"
COMPANY_PROBLEMSETTERS = "/api/v1/company/doselect-problemsetters"
INTERVIEW_PARTICIPANTS = "/interview-service/api/v1/interviews/{interviewSlug}/participants/"
INTERVIEW_RECORDING_SIGNED_URL = "/interview-service/api/v1/interviews/{interviewSlug}/recording_signed_url/"
SEARCH_INTERVIEW = "/interview-service/api/v1/search/interview/"
SEARCH_PROBLEM = "/interview-service/api/v1/interviews/search/problem/"
INTERVIEW_FINAL_STATUS = "/interview-service/api/v1/interviews/{interviewSlug}/final_status/"
ROLE_ARCHIVE = "/interview-service/api/v1/roles/{jobRoleSlug}/archive/"
INTERVIEW_ASK_FEEDBACK = "/interview-service/api/v1/interviews/{interviewSlug}/report/ask_feedback/"
ROLE_CANCEL_INTERVIEW = "/interview-service/api/v1/roles/{jobRoleSlug}/cancel_interview/"
ROLE_CLONE = "/interview-service/api/v1/roles/{jobRoleSlug}/clone/"
ROLE_CRITERIA = "/interview-service/api/v1/roles/{jobRoleSlug}/criteria/"
ROLE_LIST = "/interview-service/api/v1/roles/"
INTERVIEW_JOIN = "/interview-service/api/v1/interviews/{interviewSlug}/join/"
INTERVIEW_LEAVE_ALL = "/interview-service/api/v1/interviews/{interviewSlug}/leave_all/"
# Was "/recommend_problem/" — genuinely 404s on the server (verified live against PLT); the real
# route shares the "/recommend/" prefix with ROLE_RECOMMEND_PROBLEM_DETAIL's DELETE
# ("/recommend/{problemSlug}/") just above.
ROLE_RECOMMEND_PROBLEM = "/interview-service/api/v1/roles/{jobRoleSlug}/recommend/"
ROLE_SCHEDULE_INTERVIEW = "/interview-service/api/v1/roles/{jobRoleSlug}/schedule_interview/"
SEND_OTP = "/interview-service/api/v1/send_otp/"
INTERVIEW_START = "/interview-service/api/v1/interviews/{interviewSlug}/start/"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`) — the base
    host for every interview-service/rpc/company endpoint above."""
    return DOSELECT_PRIMARY_DOMAIN


def dolores_base_url() -> str:
    """Mirrors utils.config.DOLORES_BASE_URL (env var `DOLORES_BASE_URL`) — used only by
    get_active_interviewers.py's `/search/interviewers` call."""
    return DOLORES_BASE_URL


def gateway_base_url() -> str:
    """Mirrors utils.config.DO_INTERVIEW_INTERFACE_DOMAIN (env var `DO_INTERVIEW_INTERFACE_DOMAIN`)
    — used only by get_interview_gateway.py's `/gateway/{token}` call."""
    return DO_INTERVIEW_INTERFACE_DOMAIN
