"""
Ports utils/failure_tracker.py from https://github.com/doselect/do-api-automation.git: a small
SQLite-backed flaky/recurring-failure counter, plus a Teams webhook alert for cases that stay
above a threshold. Only exercised by response_validator.validate_response_code when
do_api_config.ENVIRONMENT == "PRODUCTION" — same gating as the source repo.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import requests

from src.core.do_api_config import TEAMS_WEBHOOK_URL

# python-api-automation/src/core/failure_tracker.py -> repo root is 2 parents up from this file's dir.
DB_FILE = Path(__file__).resolve().parents[2] / "tests" / "data" / "do_api_automation" / "failures.db"
COUNTER_INCREMENT = 4
COUNTER_DECREMENT = 2


def init_db() -> None:
    """Initialize the database and create the table if not exists."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS failures (
                test_case TEXT PRIMARY KEY,
                failure_count INTEGER
            )
            """
        )
        conn.commit()


def log_failure(case_name: str) -> None:
    """Increment failure count for a test case."""
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT failure_count FROM failures WHERE test_case = ?", (case_name,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE failures SET failure_count = failure_count + ? WHERE test_case = ?",
                (COUNTER_INCREMENT, case_name),
            )
        else:
            cursor.execute(
                "INSERT INTO failures (test_case, failure_count) VALUES (?, ?)",
                (case_name, COUNTER_INCREMENT),
            )
        conn.commit()


def log_success(case_name: str) -> None:
    """Decrement failure count for a test case, remove it if it reaches 0."""
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT failure_count FROM failures WHERE test_case = ?", (case_name,))
        row = cursor.fetchone()
        if row:
            new_count = row[0] - COUNTER_DECREMENT
            if new_count <= 0:
                cursor.execute("DELETE FROM failures WHERE test_case = ?", (case_name,))
            else:
                cursor.execute(
                    "UPDATE failures SET failure_count = ? WHERE test_case = ?", (new_count, case_name)
                )
        conn.commit()


def fetch_high_priority_failures(current_failures: list[str]) -> list[tuple[str, int]]:
    """Fetch test cases failing in the current run & have failure count > 12."""
    if not current_failures:
        return []
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in current_failures)
        query = (
            f"SELECT test_case, failure_count FROM failures "
            f"WHERE test_case IN ({placeholders}) AND failure_count > 12"
        )
        cursor.execute(query, tuple(current_failures))
        return cursor.fetchall()


def send_teams_alert(failed_cases: list[tuple[str, int]]) -> None:
    """Send a Teams alert only once at the end. No-op if TEAMS_WEBHOOK_URL isn't configured."""
    if not failed_cases or not TEAMS_WEBHOOK_URL:
        return

    message = "** API Test Failures Detected! **\n\n"
    message += "The following APIs failed in the current run and have a failure count > 12:\n\n"
    for case, count in failed_cases:
        message += f"- **{case}** (Failures: {count})\n"

    requests.post(TEAMS_WEBHOOK_URL, json={"text": message}, headers={"Content-Type": "application/json"})


def trigger_alert_on_failures(current_failures: list[str]) -> None:
    """Check failure conditions and trigger an alert if needed."""
    send_teams_alert(fetch_high_priority_failures(current_failures))
