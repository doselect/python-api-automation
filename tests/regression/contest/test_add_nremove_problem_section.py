"""Mirrors tests/test_regression/test_contest/test_add_nremove_problem_section.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_problem_section
@pytest.mark.regression
@pytest.mark.contest
def test_add_remove_problem_section(contest_response_handler: ContestResponseHandler):
    """Add/remove problem section to contest."""
    result_add = contest_response_handler.post_add_remove_problem_section(action="add")

    result_delete = contest_response_handler.post_add_remove_problem_section(
        action="delete", section_slug=result_add["section_slug"],
    )
