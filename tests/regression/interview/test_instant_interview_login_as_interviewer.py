"""
Mirrors tests/test_regression/test_interview/test_instant_interview_login_as_interviewer.py
(do-api-automation). `session_interview_token` is captured once from `get_or_create_fresh_token`
and threaded explicitly to every later call needing it (source stashed the same value once in
`shared_data["session_interview_token"]`); `interview_feedback_slug` is likewise captured once
from `post_interviewer_feedback` and reused for both `patch_interviewer_feedback` calls, matching
the source's `shared_data["interview_feedback_slug"]` reuse. `post_update_final_status`/
`get_recording_signed_url` are commented out in the source — omitted here too.
"""
from __future__ import annotations

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL_INTERVIEW
from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.join_interview_as_interviewer
def test_instant_interview_login_and_join_workflow(interview_response_handler: InterviewResponseHandler):
    session_interview_token = interview_response_handler.get_or_create_fresh_token(force_refresh=True)
    interview_slug = interview_response_handler.post_instant_interview_login_as_interviewer(session_interview_token)

    interview_response_handler.post_join_interview(interview_slug, "INTERVIEWER")
    interview_response_handler.post_start_interview_as_interviewer(interview_slug)
    interview_response_handler.get_interview_status(interview_slug)

    interview_response_handler.join_interview_as_candidate_using_otp(
        participant_email=CANDIDATE_EMAIL_INTERVIEW, session_interview_token=session_interview_token,
        max_otp_retries=2,
    )
    interview_response_handler.get_participants(interview_slug)

    interview_response_handler.get_interviewer_feedback(interview_slug)
    interview_feedback_slug = interview_response_handler.post_interviewer_feedback(interview_slug)
    interview_response_handler.patch_interviewer_feedback(interview_slug, interview_feedback_slug, rating=5)
    interview_response_handler.post_leave_all(interview_slug)

    # Get interview report to extract job_role_slug if needed
    interview_response_handler.get_interview_report(interview_slug)

    interview_response_handler.post_ask_feedback(interview_slug)
    interview_response_handler.get_interviewer_feedback(interview_slug)
    interview_response_handler.patch_interviewer_feedback(interview_slug, interview_feedback_slug, rating=4)
