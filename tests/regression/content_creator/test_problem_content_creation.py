"""Mirrors tests/test_regression/test_creator/test_problem_content_creation.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.core.do_api_config import CREATOR_EMAIL, CREATOR_PASSWORD, CREATOR_USERNAME, REVIEWER_EMAIL, REVIEWER_PASSWORD
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler
from src.specs.content_creator_spec_builder import ContentCreatorSpecBuilder


@pytest.mark.regression
def test_content_creation():
    creator_auth = AuthManager(CREATOR_EMAIL, CREATOR_PASSWORD)
    creator_auth.authenticate()
    reviewer_auth = AuthManager(REVIEWER_EMAIL, REVIEWER_PASSWORD)
    reviewer_auth.authenticate()

    handler = ContentCreatorResponseHandler(ContentCreatorSpecBuilder(creator_auth, reviewer_auth))

    handler.get_creator_stats()
    problem_slug = handler.post_create_problem(CREATOR_USERNAME)
    handler.patch_problem_content_creator(problem_slug, CREATOR_USERNAME)
    handler.patch_problem_status_creator(problem_slug, CREATOR_USERNAME)
    handler.patch_problem_reviewer(problem_slug)
    handler.post_set_problem_status_reviewer(problem_slug)
