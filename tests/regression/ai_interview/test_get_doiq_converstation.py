"""
Mirrors tests/test_regression/test_ai_interview/test_get_doiq_converstation.py (do-api-automation),
plus setup the source implicitly relied on. The source calls this GET bare, with no clear/init/
post-jobdesc of its own — it only passed there because it ran, in a fixed suite order, right after
another test had posted a job description into the same account's conversation and nothing had
cleared it since. That's not a guarantee this framework's per-test fixtures provide (each test gets
its own auth session and marker-based ordering only pins two ai_interview tests), so this primes
its own state the same way test_ai_create_interview.py does, deviating from the source rather than
being order-dependently flaky.
"""
from __future__ import annotations

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler
from src.responses.doiq_response_handler import DoiqResponseHandler


@pytest.mark.get_doiq_conversation
def test_get_doiq_conversation(
    ai_interview_response_handler: AiInterviewResponseHandler, doiq_response_handler: DoiqResponseHandler
):
    doiq_response_handler.get_doiq_clear(context="interview")
    doiq_response_handler.get_doiq_init(context="interview")
    ai_interview_response_handler.post_doiq_conversation_jobdesc()
    ai_interview_response_handler.get_doiq_conversation_ai_interview(preset="1.1", filesize="")
