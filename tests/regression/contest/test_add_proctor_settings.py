"""Mirrors tests/test_regression/test_contest/test_add_proctor_settings.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_proctor_settings
@pytest.mark.regression
@pytest.mark.contest
@pytest.mark.parametrize(
    "proctor_enabled,snapshot_enabled,video_enabled,plagiarism_enabled",
    [
        (True, False, False, False),  # Basic
        (True, True, False, False),  # Standard
        (True, False, True, False),  # Advanced
        (True, False, False, True),  # Plagiarism + Basic
        (False, False, False, False),  # Disabled
    ],
)
def test_add_proctor_settings(
    contest_response_handler: ContestResponseHandler,
    proctor_enabled,
    snapshot_enabled,
    video_enabled,
    plagiarism_enabled,
):
    response = contest_response_handler.patch_proctor_settings(
        proctor_enabled=proctor_enabled,
        snapshot_enabled=snapshot_enabled,
        video_enabled=video_enabled,
        plagiarism_enabled=plagiarism_enabled,
    )
    assert response is not None
