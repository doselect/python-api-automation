"""
Mirrors SalaryDataAPITest.beforeMethod() (JUnit's @BeforeEach): provides a fresh
SalariesSpecBuilder + SalariesResponseHandler for every test that requests them.
"""
from __future__ import annotations

import pytest

from src.responses.salaries_response_handler import SalariesResponseHandler
from src.specs.salaries_spec_builder import SalariesSpecBuilder


@pytest.fixture
def salaries_spec_builder() -> SalariesSpecBuilder:
    """Mirrors `specBuilder = new SalariesSpecBuilder(); specBuilder.setupAllSpecs();` (scoped to the Salary Data spec only)."""
    builder = SalariesSpecBuilder()
    builder.setup_salary_data_spec()
    return builder


@pytest.fixture
def salaries_response_handler(salaries_spec_builder: SalariesSpecBuilder) -> SalariesResponseHandler:
    """Mirrors `handler = new SalariesResponseHandler(specBuilder);`."""
    return SalariesResponseHandler(salaries_spec_builder)
