"""
Mirrors tests/test_regression/test_interview/test_delete_invite_interviewer.py (do-api-automation),
plus setup the source implicitly relied on. `delete_invite_interviewer()` with no `email` sends no
body, and the server 400s a bodyless DELETE ("This field may not be null.", verified live against
PLT) — the source's own NameError bug (see delete_invite_interviewer's docstring) meant it never
ran clean there either. Invites a real interviewer first so there's something valid to delete.
"""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.delete_invite_interviewer
def test_delete_invite_interviewer(interview_response_handler: InterviewResponseHandler):
    email, _full_name = interview_response_handler.post_invite_interviewer()
    result = interview_response_handler.delete_invite_interviewer(email)
    assert result.status_code in (200, 204)
