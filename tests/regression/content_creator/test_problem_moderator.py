"""Mirrors tests/test_regression/test_creator/test_problem_moderator.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.core.do_api_config import MODERATOR_EMAIL, MODERATOR_PASSWORD, MODERATOR_USERNAME
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler
from src.specs.content_creator_spec_builder import ContentCreatorSpecBuilder


@pytest.mark.regression
def test_content_creation():
    # Source logs in as the moderator account for *both* roles (creator-side and reviewer-side).
    auth_manager = AuthManager(MODERATOR_EMAIL, MODERATOR_PASSWORD)
    auth_manager.authenticate()
    reviewer_auth = AuthManager(MODERATOR_EMAIL, MODERATOR_PASSWORD)
    reviewer_auth.authenticate()

    handler = ContentCreatorResponseHandler(ContentCreatorSpecBuilder(auth_manager, reviewer_auth))

    handler.get_creator_stats()
    problem_slug = handler.post_create_problem(MODERATOR_USERNAME)
    handler.patch_problem_content_creator(problem_slug, MODERATOR_USERNAME)
    handler.patch_problem_status_creator(problem_slug, MODERATOR_USERNAME)
    handler.patch_problem_reviewer(problem_slug)
    handler.post_set_problem_status_reviewer(problem_slug)
