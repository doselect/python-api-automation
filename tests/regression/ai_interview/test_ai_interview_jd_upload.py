"""
Mirrors tests/test_regression/test_ai_interview/test_ai_interview_jd_upload.py (do-api-automation).

The referenced fixture file (resources/data/SDET.pdf, relative to the source test file) does not
exist in the source repo either — `os.path.exists(file_path)` would already fail there before any
request is made. Preserved as-is rather than fabricating a PDF fixture; see DO_API_PORT_STATUS.md.
"""
from __future__ import annotations

import os

import pytest

from src.responses.ai_interview_response_handler import AiInterviewResponseHandler


@pytest.mark.post_upload_file
def test_post_upload_file(ai_interview_response_handler: AiInterviewResponseHandler):
    file_path = os.path.join(os.path.dirname(__file__), "../../data/do_api_automation/SDET.pdf")
    assert os.path.exists(file_path), f"Test file not found: {file_path}"
    ai_interview_response_handler.post_upload_file(file_path)
