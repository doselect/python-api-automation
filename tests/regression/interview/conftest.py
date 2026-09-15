"""interview-domain fixtures. Reuses `recruiter_auth_manager` from tests/regression/conftest.py
(interview management authenticates as the recruiter role — see interview_spec_builder.py's
docstring for the per-file investigation)."""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.responses.interview_response_handler import InterviewResponseHandler
from src.specs.interview_spec_builder import InterviewSpecBuilder


@pytest.fixture
def interview_spec_builder(recruiter_auth_manager: AuthManager) -> InterviewSpecBuilder:
    return InterviewSpecBuilder(recruiter_auth_manager)


@pytest.fixture
def interview_response_handler(interview_spec_builder: InterviewSpecBuilder) -> InterviewResponseHandler:
    return InterviewResponseHandler(interview_spec_builder)
