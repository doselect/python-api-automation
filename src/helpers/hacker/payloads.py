"""
Ports payloads/regression/hacker/*.py (4 files) from
https://github.com/doselect/do-api-automation.git. Source functions read everything off a
`shared_data` dict; ported here as explicit parameters instead (matching this repo's existing
ai_interview/doiq payload-module convention), one function/dispatcher per source file.
"""
from __future__ import annotations

from typing import Any, Optional


# -- payloads/regression/hacker/code_run.py --------------------------------------------------

def code_run_payload(
    solution_lang: Optional[str],
    solution_code: Optional[str],
    problem_id: Optional[str],
    solution_id: Optional[str],
    sock_id: Optional[str],
    candidate_username: Optional[str],
) -> dict[str, Any]:
    """Mirrors payloads/regression/hacker/code_run.py::code_run_payload(shared_data)."""
    return {
        "technology": solution_lang,
        "code": solution_code,
        "input": "",
        "problem_id": problem_id,
        "solution_id": solution_id,
        "sockmeta": {"connid": "123456789", "wid": "nimbus", "sockid": sock_id},
        "username": candidate_username,
    }


# -- payloads/regression/hacker/create_solution.py --------------------------------------------

def _base_solution_payload(
    candidate_username: str, problem_slug: str, test_slug: Optional[str], solutionset_id: str
) -> dict[str, Any]:
    """
    Mirrors create_solution.py::get_base_payload(shared_data). The "solution_type" field there is
    `shared_data.get("solution_type", "MCQ")` — a *different* key from the `solution_type` argument
    that selects which payload builder runs below, and no ported call site ever sets
    `shared_data["solution_type"]` — so it is always the "MCQ" literal fallback, preserved as-is.
    """
    return {
        "creator": f"/api/v1/user/{candidate_username}",
        "problem": f"/api/v1/problem/{problem_slug}",
        "solution_type": "MCQ",
        "test": f"/api/v1/test/{test_slug}",
        "test_solution_set": f"api/v1/testsolutionset/{solutionset_id}",
        "test_slug": test_slug,
    }


def _generate_mcq_payload(candidate_username, problem_slug, test_slug, solutionset_id, correct_answer):
    """Mirrors create_solution.py::generate_mcq_payload."""
    return {"choice": correct_answer, **_base_solution_payload(candidate_username, problem_slug, test_slug, solutionset_id)}


def _generate_fib_payload(candidate_username, problem_slug, test_slug, solutionset_id, correct_answer):
    """Mirrors create_solution.py::generate_fib_payload."""
    return {"choice": correct_answer, **_base_solution_payload(candidate_username, problem_slug, test_slug, solutionset_id)}


def _generate_coding_payload(candidate_username, problem_slug, test_slug, solutionset_id, problem_stub, solution_lang):
    """Mirrors create_solution.py::generate_coding_payload."""
    head = (problem_stub.get("head", "") or "").strip()
    body = (problem_stub.get("body", "") or "").strip()
    tail = (problem_stub.get("tail", "") or "").strip()

    final_code = f"{head}\n\n{body}\n\n{tail}"

    head_lines = head.count("\n") + 1 if head else 0
    body_lines = body.count("\n") + 1 if body else 0
    tail_lines = tail.count("\n") + 1 if tail else 0

    stub_length = {
        "head": head_lines if head_lines > 0 else None,
        "tail": tail_lines if tail_lines > 0 else None,
    }

    lock_range: dict[str, Optional[str]] = {}
    lock_range["head"] = f"1-{head_lines}" if head_lines > 0 else None
    lock_range["tail"] = (
        f"{head_lines + body_lines + 1}-{head_lines + body_lines + tail_lines}" if tail_lines > 0 else None
    )

    return {
        "code": final_code,
        "extra_data": {"code": {"stub_length": stub_length, "lock_range": lock_range}},
        "technology": f"/api/v1/technology/{solution_lang}",
        **_base_solution_payload(candidate_username, problem_slug, test_slug, solutionset_id),
    }


def _generate_subjective_payload(candidate_username, problem_slug, test_slug, solutionset_id):
    """Mirrors create_solution.py::generate_subjective_payload."""
    return {
        "answer": "Hi this is a automated answer using API automation",
        **_base_solution_payload(candidate_username, problem_slug, test_slug, solutionset_id),
    }


def get_solution_payload(
    solution_type: str,
    candidate_username: str,
    problem_slug: str,
    test_slug: Optional[str],
    solutionset_id: str,
    correct_answer: Optional[list] = None,
    problem_stub: Optional[dict] = None,
    solution_lang: Optional[str] = None,
) -> dict[str, Any]:
    """Mirrors create_solution.py::get_solution_payload(shared_data, solution_type)."""
    if solution_type == "MCQ":
        return _generate_mcq_payload(candidate_username, problem_slug, test_slug, solutionset_id, correct_answer)
    if solution_type == "FIB":
        return _generate_fib_payload(candidate_username, problem_slug, test_slug, solutionset_id, correct_answer)
    if solution_type in ("SCR", "DBA"):  # DBA payload is same as coding, per source
        return _generate_coding_payload(
            candidate_username, problem_slug, test_slug, solutionset_id, problem_stub, solution_lang
        )
    if solution_type == "SUB":
        return _generate_subjective_payload(candidate_username, problem_slug, test_slug, solutionset_id)
    raise ValueError(f"Payload not found for : {solution_type}")


# -- payloads/regression/hacker/patch_solution.py ----------------------------------------------

def get_patch_payload(
    solution_type: str,
    test_slug: str,
    correct_answer: Optional[list] = None,
    solution_code: Optional[str] = None,
    solution_lang: Optional[str] = None,
) -> dict[str, Any]:
    """Mirrors patch_solution.py::get_patch_payload(shared_data, solution_type)."""
    if solution_type in ("MCQ", "FIB"):
        return {"choice": correct_answer, "test_slug": test_slug}
    if solution_type in ("SCR", "DBA"):  # DBA payload is same as coding, per source
        return {
            "code": solution_code,
            "technology": f"/api/v1/technology/{solution_lang}",
            "test_slug": test_slug,
        }
    if solution_type == "SUB":
        return {
            "answer": "Hi this is a automated answer using API automation and is a PATCH call",
            "test_slug": test_slug,
        }
    raise ValueError(f"Patch Payload not found for : {solution_type}")


# -- payloads/regression/hacker/solutions_submit.py ----------------------------------------------

def get_submit_solution_payload(
    solution_id: Optional[str], sock_id: Optional[str], test_slug: Optional[str], solution_slug: Optional[str]
) -> dict[str, Any]:
    """Mirrors solutions_submit.py::get_submit_solution_payload(shared_data)."""
    return {
        "solution_id": solution_id,
        "sockmeta": {"connid": "123456789", "wid": "nimbus", "sockid": sock_id},
        "test_slug": test_slug,
        "solution_slug": solution_slug,
    }
