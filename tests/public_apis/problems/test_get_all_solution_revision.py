"""Mirrors tests/public_apis/problems/test_get_all_solution_revision.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL, SOLUTION_SLUG
from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_get_all_solution_revision(problems_response_handler: ProblemsResponseHandler, request):
    response = problems_response_handler.get_all_solution_revisions(SOLUTION_SLUG, CANDIDATE_EMAIL)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
