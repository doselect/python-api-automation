# python-api-automation

A pytest-based Python port of the separate
**[doselect/do-api-automation](https://github.com/doselect/do-api-automation)** suite (DoSelect
Recruit/Interview/Hacker/Contest/DOIQ/public APIs) into a layered spec-builder/response-handler/
model/test framework — see [do-api-automation port](#do-api-automation-port) below.

This is a first-pass port, scoped deliberately narrow. It sits as a sibling of the existing Java
project and does not touch it.

## Framework building blocks

| Java (`src/test/java/...`)                          | Python (`python-api-automation/...`)                              |
|-------------------------------------------------------|---------------------------------------------------------------------|
| `specs/BaseSpecBuilder`                                | `src/core/base_spec_builder.py`                                     |
| `testutils/core/RestClient`                            | `src/core/rest_client.py`                                           |
| `constants/headers/HeaderConstants`                     | `src/constants/headers/header_constants.py`                         |
| `.agent/rules/serenity-api-automation-rules.md`         | `.agent/rules/python-api-automation-rules.md`                       |

Reporting: Serenity's `Serenity.recordReportData()` tabular summary convention is mirrored via
`src/reports/report_utils.py`'s `log_test_summary(title, rows)`, which attaches an aligned text
table (`Input | Expected Status | Actual Status | Field Check | Result`) to the Allure report.

## How to run

```bash
cd python-api-automation
pip install -e .
pytest --alluredir=allure-results
```

To view the Allure report (requires the Allure command-line tool, installed separately — not a
Python package):

```bash
allure serve allure-results
```

If the Allure CLI/Java aren't available, generate a self-contained HTML report instead (no extra
tooling beyond `pytest-html`, already in `dependencies`):

```bash
pytest --html=report.html --self-contained-html
```

Open `report.html` directly in a browser.

## do-api-automation port

The whole of [doselect/do-api-automation](https://github.com/doselect/do-api-automation) (a flat,
procedural pytest suite for DoSelect's Recruit/Interview/Hacker/Contest/DOIQ/AI-Interview/
Content-Creator and public APIs) rebuilt into this repo's layered spec-builder/response-handler/
model/test framework, extended to also cover session-cookie auth.

**Full file-by-file status:** [`DO_API_PORT_STATUS.md`](DO_API_PORT_STATUS.md) at the repo root
tracks every source file's port status — this is the single source of truth for what's done.
Everything is ported; a handful of files are deliberately-not-ported dead/duplicate code, documented
in that file with the reasoning (see its `tests/flows/` and `utils/api_helper.py` entries).

### How this mirrors the source

| do-api-automation                                    | python-api-automation                                              |
|--------------------------------------------------------|----------------------------------------------------------------------|
| `utils/api_helper.py::make_request`                     | `src/core/rest_client.py::execute_request` (generic HTTP-verb executor) |
| `utils/config.py`                                       | `src/core/do_api_config.py`                                          |
| `utils/generic_helpers.py`                               | `src/core/do_api_helpers.py`                                         |
| `utils/logger.py`                                        | `src/core/do_api_logger.py`                                          |
| `utils/validator.py`                                     | `src/core/response_validator.py`                                     |
| `utils/failure_tracker.py`                                | `src/core/failure_tracker.py`                                        |
| `utils/auth.py` (`AuthManager`)                            | `src/core/auth_manager.py`                                           |
| `utils/email_reader.py`                                    | `src/core/email_reader.py`                                           |
| `utils/header_generator.py` (`generate_headers`/`generate_params`, "default" case) | `src/specs/session_auth_headers.py` + per-domain `src/specs/*_spec_builder.py` methods (named `api_identifier` cases ported directly into the relevant domain's spec builder) |
| `utils/constants.py` (`STATIC_HEADERS`)                    | `src/constants/headers/static_headers.py`                            |
| repeated browser-fingerprint header blocks in `header_generator.py` | `src/constants/headers/browser_fingerprint_headers.py` (factored into named constants instead of re-pasted per function) |
| `tests/public_apis/{problems,invite,fn}/`                   | `tests/public_apis/{problems,invite,fn}/` + `src/{specs,responses}/{problems,invite,fn}_*.py` |
| `tests/regression_api_methods/<domain>/*.py`                | `src/responses/<domain>_response_handler.py` (one method per source function) |
| `payloads/regression/<domain>/*.py`                          | `src/helpers/<domain>/payloads.py`                                    |
| `tests/test_regression/test_<domain>/*.py`                    | `tests/regression/<domain>/*.py`                                     |
| `resources/data/data.csv`                                    | `tests/data/do_api_automation/data.csv` (byte-for-byte copy)         |

`shared_data` (a plain dict threaded through every source function call) is replaced throughout by
explicit method parameters and return values — the same information flows, but through normal
function signatures instead of a mutable grab-bag dict. Session-cookie-auth domains build a fresh
`AuthManager` per test (no cross-test session reuse), matching the source exactly.

### Domains ported

`public_apis/problems`, `public_apis/invite`, `public_apis/fn` (DoSelect-Api-Key/Secret header
auth), `regression/doiq`, `regression/ai_interview`, `regression/content_creator`,
`regression/contest`, `regression/hacker`, `regression/interview`, `regression/recruit`
(session-cookie auth via `AuthManager`).

### Running against the live API

Needs the same environment variables as the source repo (`BASE_URL`, `DOSELECT_API_KEY`,
`DOSELECT_API_SECRET`, `DOSELECT_PRIMARY_DOMAIN`, `RECRUITER_EMAIL`/`RECRUITER_PASSWORD`, etc. —
see that repo's `postactivate.sample`) sourced into the shell before `pytest` runs. Without them,
every ported test still **collects** cleanly but fails at request/login time (no live host to
reach) — that's the expected "no credentials" mode, not a port defect.

```bash
pytest -m regression        # session-cookie-auth domains
pytest -m public             # public_apis/* (API-key auth)
pytest tests/regression/doiq tests/public_apis  # run specific domains directly
```
