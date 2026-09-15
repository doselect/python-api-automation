"""
Ports the `api_helper.make_request(...)` call sites in tests/public_apis/problems/*.py
(do-api-automation) into one response handler, mirroring SalariesResponseHandler's convention:
one method per API operation, each executing through src.core.rest_client.execute_request.
"""
from __future__ import annotations

from typing import Any, Optional

import requests

from src.core.rest_client import execute_request
from src.specs.problems_spec_builder import ProblemsSpecBuilder


class ProblemsResponseHandler:
    """Wraps a ProblemsSpecBuilder to centralize the ported `problems` public API calls."""

    def __init__(self, spec_builder: ProblemsSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def create_problem(self, payload: dict[str, Any], expected_status_code: int = 201) -> requests.Response:
        """Mirrors POST /platform/v1/problem/ (test_create_problem.py, conftest.create_problem)."""
        return execute_request(
            self._spec_builder.get_spec("problem_list"), "POST", body=payload,
            expected_status_code=expected_status_code,
        )

    def get_all_problems(self, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /platform/v1/problem (test_get_all_problem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_list_get"), "GET",
            expected_status_code=expected_status_code,
        )

    def get_one_problem(self, problem_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /platform/v1/problem/{problemSlug} (test_get_one_problems.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_detail"), "GET",
            path_params={"problemSlug": problem_slug}, expected_status_code=expected_status_code,
        )

    def update_problem(
        self, problem_slug: str, payload: dict[str, Any], expected_status_code: int = 202
    ) -> requests.Response:
        """Mirrors PATCH /platform/v1/problem/{problemSlug} (test_update_problem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_detail"), "PATCH",
            path_params={"problemSlug": problem_slug}, body=payload,
            expected_status_code=expected_status_code,
        )

    def lock_problem(self, problem_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors POST /platform/v1/problem/{problemSlug}/lock (test_lock_problem.py, conftest.lock_problem)."""
        return execute_request(
            self._spec_builder.get_spec("problem_lock"), "POST",
            path_params={"problemSlug": problem_slug}, body={}, expected_status_code=expected_status_code,
        )

    def unlock_problem(self, problem_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors POST /platform/v1/problem/{problemSlug}/unlock (test_unlock_problem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_unlock"), "POST",
            path_params={"problemSlug": problem_slug}, body={}, expected_status_code=expected_status_code,
        )

    def clone_problem(self, problem_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors POST /platform/v1/problem/{problemSlug}/clone (test_create_clone_of_problem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_clone"), "POST",
            path_params={"problemSlug": problem_slug}, body={}, expected_status_code=expected_status_code,
        )

    def add_testcase(
        self, problem_slug: str, payload: dict[str, Any], expected_status_code: int = 201
    ) -> requests.Response:
        """Mirrors POST .../testcase (test_create_testcase_ofproblem.py, conftest.add_testcase)."""
        return execute_request(
            self._spec_builder.get_spec("problem_testcase_list"), "POST",
            path_params={"problemSlug": problem_slug}, body=payload,
            expected_status_code=expected_status_code,
        )

    def get_all_testcases(self, problem_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../testcase (test_get_all_testcases_ofproblem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_testcase_list"), "GET",
            path_params={"problemSlug": problem_slug}, expected_status_code=expected_status_code,
        )

    def delete_testcase(
        self, problem_slug: str, testcase_id: Any, expected_status_code: int = 204
    ) -> requests.Response:
        """Mirrors DELETE .../testcase/{testcaseId} (test_delete_testcase_ofproblem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_testcase_detail"), "DELETE",
            path_params={"problemSlug": problem_slug, "testcaseId": testcase_id},
            expected_status_code=expected_status_code,
        )

    def get_all_submissions_of_problem(
        self, problem_slug: str, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors GET .../submission (test_get_all_submission_ofproblem.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_submission_list"), "GET",
            path_params={"problemSlug": problem_slug}, expected_status_code=expected_status_code,
        )

    def get_submission_of_problem_by_user(
        self, problem_slug: str, candidate_email: str, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors GET .../submission/{candidateEmail}/ (test_get_submission_ofproblem_byuser.py)."""
        return execute_request(
            self._spec_builder.get_spec("problem_submission_by_user"), "GET",
            path_params={"problemSlug": problem_slug, "candidateEmail": candidate_email},
            expected_status_code=expected_status_code,
        )

    def push_to_learn_feed(
        self, problem_slug: str, expected_status_code: int = 201
    ) -> requests.Response:
        """Mirrors POST /platform/v1/learnfeeditem/ (test_push_to_learn_feed.py)."""
        return execute_request(
            self._spec_builder.get_spec("learn_feed_item"), "POST",
            body={"problem": f"/platform/v1/problem/{problem_slug}"},
            expected_status_code=expected_status_code,
        )

    def create_submission(self, payload: dict[str, Any], expected_status_code: int = 201) -> requests.Response:
        """Mirrors POST /platform/v1/submission/ (test_create_submission.py)."""
        return execute_request(
            self._spec_builder.get_spec("submission_list"), "POST", body=payload,
            expected_status_code=expected_status_code,
        )

    def get_one_submission(self, solution_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /platform/v1/submission/{solutionSlug} (test_get_one_submission.py)."""
        return execute_request(
            self._spec_builder.get_spec("submission_detail"), "GET",
            path_params={"solutionSlug": solution_slug}, expected_status_code=expected_status_code,
        )

    def get_all_solution_revisions(
        self, solution_slug: str, candidate_email: str, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors GET .../revisions/{candidateEmail} (test_get_all_solution_revision.py)."""
        return execute_request(
            self._spec_builder.get_spec("submission_revisions"), "GET",
            path_params={"solutionSlug": solution_slug, "candidateEmail": candidate_email},
            expected_status_code=expected_status_code,
        )

    def get_code_zip(self, solution_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../code-repo (test_get_code_zip.py)."""
        return execute_request(
            self._spec_builder.get_spec("submission_code_repo"), "GET",
            path_params={"solutionSlug": solution_slug}, expected_status_code=expected_status_code,
        )

    def submit_existing_submission(
        self, solution_slug: str, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors POST .../submit (test_submit_existing_submission.py)."""
        return execute_request(
            self._spec_builder.get_spec("submission_submit"), "POST",
            path_params={"solutionSlug": solution_slug}, body={}, expected_status_code=expected_status_code,
        )
