"""Allure reporting helpers: `log_test_summary` attaches an aligned per-scenario result table to a test."""
from __future__ import annotations

from typing import Any

import allure

SUMMARY_COLUMNS = ("input", "expected_status", "actual_status", "field_check", "result")


def summary_row(input_: str, expected_status: int, response: Any, field_check: str) -> dict[str, Any]:
    """Builds one `log_test_summary` row for a call that has already passed its assertions."""
    return {
        "input": input_, "expected_status": expected_status, "actual_status": response.status_code,
        "field_check": field_check, "result": "PASS",
    }


def log_test_summary(title: str, rows: list[dict[str, Any]]) -> None:
    """Attaches `rows` (one dict per scenario, keyed by SUMMARY_COLUMNS) to Allure as an aligned text table."""
    table = [SUMMARY_COLUMNS] + [tuple(str(row.get(col, "")) for col in SUMMARY_COLUMNS) for row in rows]
    widths = [max(len(line[i]) for line in table) for i in range(len(SUMMARY_COLUMNS))]
    lines = [" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(line)) for line in table]
    lines.insert(1, "-+-".join("-" * width for width in widths))
    allure.attach("\n".join(lines), name=title, attachment_type=allure.attachment_type.TEXT)
