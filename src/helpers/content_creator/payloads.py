"""
Ports payloads/regression/content/*.py from https://github.com/doselect/do-api-automation.git,
plus the `_get_content_creator_username` username-resolution helper from utils/header_generator.py
(needed by post_create_problem_payload.py and the "patch_problem_content_creator"/
"post_create_problem" generate_params cases).
"""
from __future__ import annotations

import random
from typing import Optional

from src.core.do_api_config import CREATOR_EMAIL, CREATOR_USERNAME, MODERATOR_EMAIL, MODERATOR_USERNAME


def resolve_creator_username(
    authenticated_username: Optional[str] = None, authenticated_email: Optional[str] = None
) -> str:
    """
    Mirrors utils.header_generator._get_content_creator_username(shared_data) /
    post_create_problem_payload.py's inline equivalent. The source also checked
    `shared_data.get("creator_email")`/`["moderator_email"]`, but no call site in either repo ever
    sets those keys — every real call sets `authenticated_username` directly (see
    tests/test_regression/test_creator/*.py), so only that branch and the final fallback are kept.
    """
    if authenticated_username:
        return authenticated_username
    if authenticated_email == CREATOR_EMAIL:
        return CREATOR_USERNAME
    if authenticated_email == MODERATOR_EMAIL:
        return MODERATOR_USERNAME
    return CREATOR_USERNAME if CREATOR_USERNAME else MODERATOR_USERNAME


def get_creator_stats_payload() -> dict:
    """Mirrors payloads/regression/content/get_creator_stats_payload.py."""
    return {}


def patch_problem_content_creator_payload(problem_slug: str) -> dict:
    """Mirrors payloads/regression/content/patch_problem_content_creator_payload.py."""
    return {
        "archived": False,
        "attachments": [],
        "category": "MAR",
        "character_limit": None,
        "code_stub_generator": None,
        "default_execution_timelimit": None,
        "description": "<p>What is the capital of France?</p>",
        "editorial": "",
        "eval_mode": "AUT",
        "extra_data": {
            "dexter": {"cache": "", "database": ""},
            "flags": {"ignore_space": False},
            "is_genAI_problem": False,
            "samplecode": {"code": "", "language": ""},
            "seedscript": {"code": "", "language": ""},
            "testcase_runner": "",
        },
        "in_learn_feed": False,
        "insight_tags": ["CAPITAL", "MCQ"],
        "is_active": True,
        "is_locked": False,
        "is_multi_correct": False,
        "is_promoted": False,
        "level": "EAS",
        "max_submissions": 0,
        "mcq_options": [
            {"content": "<p>FRNACE</p>", "id": "1"},
            {"content": "<p>PARIS</p>", "id": "2"},
            {"content": "<p>BERLIN</p>", "id": "3"},
            {"content": "<p>CHINA</p>", "id": "4"},
        ],
        "mcq_options_correct": ["2"],
        "name": "MCQ_api_problem",
        "num_problem_test_cases": 0,
        "pbp_framework_id": None,
        "penalty": 0,
        "primary_technology": None,
        "private_attachments": [],
        "problem_type": "MCQ",
        "recording_url": None,
        "reviewer": None,
        "sample_solutions": {},
        "sample_solutions_technologies": [],
        "sample_test_cases": [],
        "score": 5,
        "skills": [],
        "slug": problem_slug,
        "solving_time": "5",
        "status": "DRA",
        "stubs": {},
        "subtopics": [],
        "tags": ["MCQ", "NEW"],
        "technologies": [],
        "time_limit_secs": None,
        "topics": [],
        "total_sample_testcases": 0,
        "visibility": [],
        "workspace_specs": {},
        "workspace_template": None,
        "workspace_template_status": "DRA",
    }


def patch_problem_reviewer_payload(problem_slug: str) -> dict:
    """Mirrors payloads/regression/content/patch_problem_reviewer_payload.py."""
    return {
        "problem_slug": problem_slug,
        "status": "PUB",  # PUB for published, REJ for rejected
        "editorial": "Problem reviewed and approved by reviewer",
        "is_active": True,
        "visibility": ["PUB"],
    }


def patch_problem_status_creator_payload() -> dict:
    """Mirrors payloads/regression/content/patch_problem_status_creator_payload.py (updates to URE)."""
    return {"status": "URE"}


def create_problem_payload(username: str) -> dict:
    """Mirrors payloads/regression/content/post_create_problem_payload.py::create_problem_payload."""
    return {
        "creator": f"/api/v1/user/{username}",
        "name": f"New-problem-{random.randint(1, 9999)}",
        "problem_type": "MCQ",
        "eval_mode": None,
        "level": "HAR",
    }


def set_problem_status_reviewer_payload(problem_slug: str) -> dict:
    """Mirrors payloads/regression/content/post_set_problem_status_reviewer_payload.py."""
    return {"problem_slug": problem_slug, "status": "PUB"}
