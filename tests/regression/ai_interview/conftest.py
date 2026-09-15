"""ai_interview-domain fixtures. Reuses `recruiter_auth_manager` from tests/regression/conftest.py."""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.responses.ai_interview_response_handler import AiInterviewResponseHandler
from src.specs.ai_interview_spec_builder import AiInterviewSpecBuilder


@pytest.fixture
def ai_interview_spec_builder(recruiter_auth_manager: AuthManager) -> AiInterviewSpecBuilder:
    return AiInterviewSpecBuilder(recruiter_auth_manager)


@pytest.fixture
def ai_interview_response_handler(
    ai_interview_spec_builder: AiInterviewSpecBuilder,
) -> AiInterviewResponseHandler:
    return AiInterviewResponseHandler(ai_interview_spec_builder)
