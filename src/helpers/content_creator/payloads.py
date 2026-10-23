"""
Ports payloads/regression/content/*.py from https://github.com/doselect/do-api-automation.git,
plus the `_get_content_creator_username` username-resolution helper from utils/header_generator.py
(needed by post_create_problem_payload.py and the "patch_problem_content_creator"/
"post_create_problem" generate_params cases).
"""
from __future__ import annotations

import copy
import csv
import json
import random
from pathlib import Path
from typing import Optional

from src.core.do_api_config import CREATOR_EMAIL, CREATOR_USERNAME, MODERATOR_EMAIL, MODERATOR_USERNAME

CONTENT_CREATOR_DATA_DIR = Path(__file__).resolve().parents[3] / "tests" / "data" / "content_creator"


def _load_data(file_name: str) -> dict:
    with (CONTENT_CREATOR_DATA_DIR / file_name).open(encoding="utf-8") as file:
        return json.load(file)


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


def create_scr_problem_payload(username: str) -> dict:
    """Scripting (SCR) problem-create body, as sent by the d6 content dashboard's "Create problem" modal."""
    return {
        "creator": f"/api/v1/user/{username}",
        "name": f"New-scr-problem-{random.randint(1, 9999)}",
        "problem_type": "SCR",
        "eval_mode": "TXT",
        "level": "MED",
    }


def auto_stub_problem_payloads() -> dict:
    """
    PATCH bodies for the auto-stub problem flow, keyed by step (description, technologies, tags,
    auto_stubs, sample_solution) — captured from the d6 content dashboard. The stub code itself is
    built by the browser, so it is sent as-is rather than generated here.
    """
    return _load_data("auto_stub_problem.json")


def auto_stub_ai_up_payloads() -> dict:
    """
    Bodies for the AI-service-up flow (stubs -> cpp solution -> AI generation -> testcases -> settings ->
    sanity check), captured from the d6 content dashboard where the sanity check passed.
    """
    return _load_data("auto_stub_ai_up.json")


def allowed_languages(payloads: dict) -> set[str]:
    """Language slugs from the `settings.technologies` URIs (e.g. /api/v1/technology/cpp -> cpp)."""
    return {uri.rstrip("/").rsplit("/", 1)[-1] for uri in payloads["settings"]["technologies"]}


def source_language(payloads: dict) -> str:
    """The language of the hand-written sample solution the AI generates from."""
    return next(iter(payloads["sample_solution"]["sample_solutions"]))


def ai_generation_languages(payloads: dict) -> set[str]:
    """The dashboard offers AI generation only for allowed languages that have a generated stub."""
    stubbed = set(payloads["auto_stubs"]["code_stub_generator"]["languages"])
    return (allowed_languages(payloads) & stubbed) - {source_language(payloads)}


def edited_stubs_payload(auto_stubs: dict, languages: list[str]) -> dict:
    """
    Stub edit as the dashboard saves it: every stub is sent, the edited ones with a changed body and the
    User-Modified label, listed in code_stub_generator.modified_stubs (extra_data.code_stub_type -> User-Modified).
    """
    payload = copy.deepcopy(auto_stubs)
    payload["extra_data"]["code_stub_type"] = "User-Modified"
    payload["code_stub_generator"]["modified_stubs"] = list(languages)
    for language in languages:
        payload["stubs"][language]["code"]["body"] += "\nedited by automation\n"
        payload["stubs"][language]["stub_type"] = "User-Modified"
    return payload


def reset_stubs_payload(auto_stubs: dict) -> dict:
    """Reset stubs as the dashboard saves it: the originally generated stubs again, nothing in modified_stubs."""
    generator = {**copy.deepcopy(auto_stubs["code_stub_generator"]), "modified_stubs": []}
    return {"stubs": copy.deepcopy(auto_stubs["stubs"]), "code_stub_generator": generator}


def edited_solutions_payload(sample_solutions: dict, language: str) -> dict:
    """
    Sample solution edit as the dashboard saves it: all current solutions are sent; the edited one gets a changed
    body, the User-Modified label and no sanity_status.
    """
    solutions = copy.deepcopy(sample_solutions)
    solutions[language] = {
        "solution": solutions[language]["solution"] + "\nedited by automation\n", "solution_type": "User-Modified",
    }
    return {"sample_solutions": solutions}


def delete_stub_payload(auto_stubs: dict, language: str) -> dict:
    """Delete one stub as the dashboard saves it: every other stub, with the generator settings unchanged."""
    payload = copy.deepcopy(auto_stubs)
    del payload["stubs"][language]
    payload["code_stub_generator"]["modified_stubs"] = []
    return payload


def delete_all_stubs_payload(auto_stubs: dict) -> dict:
    """
    Delete all stubs as the dashboard saves it: no stubs, the generator reduced to its created/modified dates and
    extra_data without code_stub_type.
    """
    generator = auto_stubs["code_stub_generator"]
    extra_data = {key: value for key, value in auto_stubs["extra_data"].items() if key != "code_stub_type"}
    return {
        "stubs": {}, "extra_data": copy.deepcopy(extra_data),
        "code_stub_generator": {"created": generator["created"], "modified": generator["modified"]},
    }


def delete_solution_payload(sample_solutions: dict, language: str) -> dict:
    """Delete one sample solution as the dashboard saves it: every other current solution, sent unchanged."""
    return {"sample_solutions": {key: value for key, value in sample_solutions.items() if key != language}}


MCQ_BULK_CSV = CONTENT_CREATOR_DATA_DIR / "mcq_bulk.csv"


def mcq_bulk_rows() -> list[dict]:
    """Rows of the bulk MCQ upload CSV (same file the dashboard upload uses), keyed by its column headers."""
    with MCQ_BULK_CSV.open(encoding="utf-8", newline="") as file:
        return [row for row in csv.DictReader(file) if row["Name (min 6 char)"].strip()]


def manual_language_payloads() -> dict:
    """
    Bodies for a V2 problem with only Manual (non auto-generation) languages — Assembler, Bash, Clojure, Swift, Rust:
    Default stubs, an edited Assembler stub, an Assembler sample solution, testcases — captured from d6.
    """
    return _load_data("manual_language_problem.json")


def testcase_payload(testcase: dict, problem_slug: str, username: str) -> dict:
    """POST /api/v1/problemtestcase body: the captured name/input/output/weight/is_sample plus ownership links."""
    return {
        **testcase, "problem": f"/api/v1/problem/{problem_slug}", "creator": f"/api/v1/user/{username}",
        "owner": None,
    }


def set_problem_status_reviewer_payload(problem_slug: str) -> dict:
    """Mirrors payloads/regression/content/post_set_problem_status_reviewer_payload.py."""
    return {"problem_slug": problem_slug, "status": "PUB"}
