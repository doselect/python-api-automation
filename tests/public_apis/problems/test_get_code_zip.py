"""Mirrors tests/public_apis/problems/test_get_code_zip.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import UI_UX_SOLUTION_SLUG
from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_get_code_zip(problems_response_handler: ProblemsResponseHandler, request):
    response = problems_response_handler.get_code_zip(UI_UX_SOLUTION_SLUG)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
