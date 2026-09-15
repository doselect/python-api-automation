"""
Ports the `/platform/v1/problem*` and `/platform/v1/submission*` public-API endpoints exercised
under tests/public_apis/problems/ in https://github.com/doselect/do-api-automation.git (see that
repo's utils/api_helper.make_request call sites for the real path strings).
"""
from __future__ import annotations

from src.core.do_api_config import BASE_URL

# Real endpoint strings copied from tests/public_apis/problems/*.py (do-api-automation).
PROBLEM_LIST = "/platform/v1/problem/"
PROBLEM_LIST_GET = "/platform/v1/problem"
PROBLEM_DETAIL = "/platform/v1/problem/{problemSlug}"
PROBLEM_LOCK = "/platform/v1/problem/{problemSlug}/lock"
PROBLEM_UNLOCK = "/platform/v1/problem/{problemSlug}/unlock"
PROBLEM_CLONE = "/platform/v1/problem/{problemSlug}/clone"
PROBLEM_TESTCASE_LIST = "/platform/v1/problem/{problemSlug}/testcase"
PROBLEM_TESTCASE_DETAIL = "/platform/v1/problem/{problemSlug}/testcase/{testcaseId}"
PROBLEM_SUBMISSION_LIST = "/platform/v1/problem/{problemSlug}/submission"
PROBLEM_SUBMISSION_BY_USER = "/platform/v1/problem/{problemSlug}/submission/{candidateEmail}/"
LEARN_FEED_ITEM = "/platform/v1/learnfeeditem/"

SUBMISSION_LIST = "/platform/v1/submission/"
SUBMISSION_DETAIL = "/platform/v1/submission/{solutionSlug}"
SUBMISSION_REVISIONS = "/platform/v1/submission/{solutionSlug}/revisions/{candidateEmail}"
SUBMISSION_CODE_REPO = "/platform/v1/submission/{solutionSlug}/code-repo"
SUBMISSION_SUBMIT = "/platform/v1/submission/{solutionSlug}/submit"


def set_base_url() -> str:
    """Mirrors utils.config.BASE_URL (env var `BASE_URL`)."""
    return BASE_URL
