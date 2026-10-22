"""
Ports the `/api/v1/creator/*`, `/api/v1/problem*`, and `/rpc/creator/moderation.*` endpoints
exercised under tests/regression_api_methods/content_creator/ +
tests/test_regression/test_creator/ in https://github.com/doselect/do-api-automation.git.
"""
from __future__ import annotations

from src.core.do_api_config import DOSELECT_PRIMARY_DOMAIN

CREATOR_STATS = "/api/v1/creator/stats"
PROBLEM_LIST = "/api/v1/problem"
PROBLEM_DETAIL = "/api/v1/problem/{problemSlug}"
MODERATION_SET_PROBLEM_STATUS = "/rpc/creator/moderation.set_problem_status"

# Creator problem-page endpoints (captured from the d6 content dashboard).
PROBLEM_COMMENT_LIST = "/api/v1/problemcomment"
PROBLEM_TESTCASE_LIST = "/api/v1/problemtestcase"
PROBLEM_SOLUTION_STATUS = "/rpc/problems.solution_status"
CODE_STUB_CONFIGURATION = "/code-stub-generator/configuration/"
ONLINE_PLAGIARISM_DATA = "/rpc/online_plagiarism_data/{problemSlug}"
PROBLEM_CHECK = "/api/v1/problem/{problemSlug}/problemcheck"
CREATOR_STATS_GETTER = "/rpc/creator/getter.creator_stats"
TAG_SEARCH = "/search/search"
GENERATE_SOLUTION = "/rpc/problems.generate_solution/"
MCQ_UPLOAD_BULK = "/rpc/problems.mcq_upload_bulk/v2"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`)."""
    return DOSELECT_PRIMARY_DOMAIN
