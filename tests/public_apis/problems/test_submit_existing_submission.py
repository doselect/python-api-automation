"""Mirrors tests/public_apis/problems/test_submit_existing_submission.py (do-api-automation).

Marked `issue` (not `public`) in the source repo — kept as-is, not upgraded to `public`.
"""
from __future__ import annotations

import pytest

from src.core.do_api_config import SOLUTION_SLUG
from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.issue
def test_submit_existing_submission(problems_response_handler: ProblemsResponseHandler, request):
    response = problems_response_handler.submit_existing_submission(SOLUTION_SLUG)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
