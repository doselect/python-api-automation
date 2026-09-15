"""
Mirrors specs.SalariesSpecBuilder (Java) — only the Salary Data API spec is ported (SalariesSpecBuilder
in Java owns ~30 specs for endpoints out of scope for this first pass; see project README).
"""
from __future__ import annotations

from typing import Optional

from src.constants.paths import salaries_api_path
from src.core.base_spec_builder import RequestSpec, build_request_spec, get_default_headers


class SalariesSpecBuilder:
    """Builds and holds the reusable request spec(s) for the ported Salary Data API."""

    def __init__(self) -> None:
        self._salary_data_spec: Optional[RequestSpec] = None

    def setup_salary_data_spec(self) -> None:
        """Mirrors SalariesSpecBuilder.setupSalaryDataSpec()."""
        self._salary_data_spec = build_request_spec(
            base_url=salaries_api_path.set_base_url(),
            base_path=salaries_api_path.SALARY_DATA,
            query_params=None,
            headers=get_default_headers(),
            path_params=None,
            body=None,
        )

    def get_salary_data_spec(self) -> RequestSpec:
        """Mirrors SalariesSpecBuilder.getSalaryDataSpec()."""
        if self._salary_data_spec is None:
            self.setup_salary_data_spec()
        return self._salary_data_spec
