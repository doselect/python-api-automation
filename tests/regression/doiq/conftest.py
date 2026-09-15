"""
doiq-domain fixtures. `recruiter_auth_manager`/`doiq_spec_builder`/`doiq_response_handler` now
live at tests/regression/conftest.py (shared with ai_interview, which reuses doiq's
response-handler methods directly) — nothing doiq-specific remains here, kept as a placeholder
so the directory stays an explicit test package matching the source's folder-per-domain layout.
"""
from __future__ import annotations
