# do-api-automation → python-api-automation Port Status

Tracks conversion of every file in https://github.com/doselect/do-api-automation.git into
this repo's layered spec-builder/response-handler/model/test framework (mirroring the Salary
Data API example). Checked = ported into this repo. `[~]` = partially ported / superseded by an
equivalent in this framework rather than a literal file-for-file copy. Updated as work
progresses — this is the single source of truth for what remains; nothing is "done" until it's
checked here.

Legend: `[x]` fully ported · `[~]` partially ported (see note) · `[ ]` not started.

## Progress summary

- **`interview` complete** (28 tests + 42 regression_api_methods + 11 payload modules + the
  email-OTP helper). Investigated the auth story per-file rather than assuming one: every
  interview-management call (job roles, interviews, feedback, scheduling, search, ...) builds its
  headers with a bare `generate_headers(USER_TYPE_RECRUITER, "default", shared_data)` — i.e.
  interview management runs as the recruiter role, so `InterviewSpecBuilder` reuses
  `default_recruiter_headers(auth_manager)` for all of them via one `default_spec(path)` helper.
  Two endpoints are genuinely different: `get_interview_gateway.py` merges the literal, auth-
  unrelated `get_interview_gateway_headers` dict with the recruiter default headers overlaid on
  top (ported as `interview_gateway_spec`); `post_send_otp.py` calls
  `generate_headers(USER_TYPE_INTERVIEWER, "default", shared_data)`, and since
  `get_default_headers`'s `match user_type` has no `"interviewer"` case, that call is genuinely
  unauthenticated (`{"accept": "application/json, text/plain, */*"}` only, no cookie/csrf at all,
  no AuthManager access) — ported as `send_otp_spec`. `utils/email_reader.py` (real IMAP/Gmail,
  not HTTP) ported as a plain core utility `src/core/email_reader.py` (mirrors `EmailReader` +
  module functions byte-for-byte), with `get_email_otp.py`'s `get_otp_from_email_helper` ported as
  `src/helpers/interview/email_otp.py` on top of it; `test_email_otp_reading.py` calls that
  directly (no session-auth fixture). The source's
  `'tests/test_regression/test_interview/test_search_interviews active.py'` (space in filename) was
  normalized to `test_search_interviews_active.py` for safe, unambiguous pytest collection — its
  body still preserves the source's own copy-paste quirk (function named
  `test_search_expired_interviews` even though it searches `status="ACTIVE"`). Cross-file call
  chains preserved as one response-handler method calling another (not duplicated):
  `get_latest_job_role_slug` is reused by 9 other methods, exactly as in the source. Two real
  source bugs found and fixed (documented in `interview_response_handler.py`'s method docstrings):
  `delete_invite_interviewer.py` referenced an unbound local (`payload`) when called without a
  prior `post_invite_interviewer` — as `test_delete_invite_interviewer.py` does — now sends no body
  in that case instead of raising `NameError`; `post_join_interview.py`'s candidate-join params
  identifier (`"join_as_candidate_in_interview_params"`) never actually matches
  `generate_params`'s dispatcher case (`"join_as_participant_in_interview"`), so it silently always
  returned `{}` — preserved as-is (documented, not "fixed", since the resulting payload is still
  correct after the source's own subsequent `.update()`).
- **`hacker` complete** (5 flow tests + 20 regression_api_methods + 4 payload modules). The
  candidate/hacker side never logs in via `AuthManager`/`/login` — the source never builds a
  hacker `AuthManager` either; `shared_data["hacker_csrf_token"]`/`["hacker_cookie"]` are seeded
  from `/gateways/test` response cookies (an access-code "test invite link" exchange, not a
  username/password login), then replaced again after the form-submit redirect. Ported as
  `src/specs/hacker_spec_builder.py::CandidateSession`, a small mutable object that duck-types
  `AuthManager.csrf_token`/`.cookie` so `session_auth_headers.default_hacker_headers` can be reused
  unmodified. The four "websocket" source files are plain Socket.IO long-polling HTTP GET/POST
  calls (no websocket library involved), ported through `execute_request` like everything else;
  `connect_websocket`'s three-call sequence + cookie-merge + `get_sid_from_response` extraction
  (new in `src/core/do_api_helpers.py`, alongside a new `encode_url`) collapse into one
  `HackerResponseHandler.connect_websocket` method. Two form-encoded POSTs
  (`post_test_gateway`/`post_test_gateway_submit`) and one raw-string-body POST
  (`post_websocket_polling`) bypass `execute_request` for direct `requests.post(data=...)` calls,
  same documented-deviation rationale as `ai_interview_response_handler.py::post_upload_file`.
  `post_submit_solution` (source folder: `regression_api_methods/recruit/`) is ported under hacker
  instead — it authenticates as `USER_TYPE_CANDIDATE` and its payload lives in
  `payloads/regression/hacker/solutions_submit.py`, so it's functionally a hacker endpoint despite
  its source folder. Verified `session_auth_headers.py::default_hacker_headers` already matches the
  source's `get_default_headers("hacker", ...)` exactly (origin/referer = `DO_TEST_INTERFACE_DOMAIN`)
  — no bug found in it this time (a prior domain already fixed one). Also added a **minimal, 5-call
  slice of `recruit`** (`src/specs/recruit_spec_builder.py` /
  `src/responses/recruit_response_handler.py` / `src/helpers/recruit/payloads.py`) — just
  `post_create_test`, the "recruiter" branch of `tests/regression_api_methods/common/
  get_test_details.py`, `get_list_of_problems`, `post_add_problem`, `get_problem_details` — because
  the 5 hacker attempt-flow tests need a recruiter to create/populate a test before the candidate
  side can run; the other ~35 `recruit/*` files are still out of scope (see that section below,
  still tracked `[ ]`; the 5 files this slice touches are marked `[~]`). Data threads through
  explicit method params/return dicts and local test variables instead of a `shared_data` fixture,
  per the established `ai_interview` convention. `candidate_session`/`hacker_spec_builder`/
  `hacker_response_handler`/`recruit_spec_builder`/`recruit_response_handler` fixtures live in
  `tests/regression/hacker/conftest.py` (not the shared `tests/regression/conftest.py`) since the
  candidate-session fixture doesn't fit that file's "authenticate immediately" fixture pattern the
  way `recruiter_auth_manager` does.
- **All three `public_apis/*` domains complete** (DoSelect-Api-Key/Secret header auth,
  stateless, no shared_data threading): `problems/` (18 tests), `invite/` (11 tests + the
  `post_invite_candidate` cross-domain helper used later by hacker attempt-flow tests), `fn/`
  (10 tests). 39 tests total, all collect cleanly; executing them fails only on missing live
  credentials (see "Running against the live API" below), not on code defects.
- **Core plumbing added** (additive — nothing existing for the Salary Data API port was changed
  in a way that breaks it): `src/core/do_api_config.py`, `src/core/do_api_helpers.py`,
  `src/core/response_validator.py`, `src/core/failure_tracker.py`,
  `src/core/rest_client.py::execute_request` (generic HTTP-verb executor + Allure request/response
  attachment, alongside the pre-existing GET-only functions),
  `src/constants/headers/header_constants.py` (DoSelect-Api-Key/Secret constants added), plus
  per-domain `src/constants/paths/*_api_path.py`, `src/specs/*_spec_builder.py`,
  `src/responses/*_response_handler.py` for problems/invite/fn.
- **Session-auth template complete: `doiq`** (8 tests + 8 regression_api_methods, all collect
  cleanly; executing fails only on missing live credentials, confirmed the same way as the
  public_apis domains). This is the template for the remaining session-cookie-auth domains:
  `AuthManager` (`src/core/auth_manager.py`) does the HTML-scraped-CSRF + session-cookie login;
  a per-domain `*SpecBuilder` takes the authenticated `AuthManager` and builds per-endpoint
  headers (mirroring the corresponding `utils/header_generator.py` functions) lazily, since
  csrf/cookie aren't known until login has run; a per-domain `*ResponseHandler` executes through
  `rest_client.execute_request`, replacing the source's raw `requests.get/post` +
  try/except/finally logging boilerplate (same requests, same assertions — the boilerplate was
  logging scaffolding, not assertions).
- **`ai_interview` complete** (12 tests + 11 regression_api_methods + 4 payload modules), reusing
  `doiq_response_handler` directly for the shared `/doiq/*` calls (confirmed cross-domain fixture
  sharing works via `tests/regression/conftest.py`). Also added `src/specs/session_auth_headers.py`
  (ports the `generate_headers`/`get_default_headers` "default" case for recruiter/hacker/
  content_creator/reviewer — reusable by every remaining session-auth domain) and a second
  browser-fingerprint constant (`CHROME_LINUX_FINGERPRINT_HEADERS`).
- **`content_creator` complete** (2 tests + 6 regression_api_methods + 6 payload modules). Adds
  `ContentCreatorSpecBuilder` taking *two* AuthManagers (content-creator/moderator role +
  reviewer/moderator role, matching the source's two-login flow), and the
  `resolve_creator_username` port of `_get_content_creator_username`.
- **`contest` complete** (37 tests + 37 regression_api_methods + 31 payload modules — the source
  directories actually hold 37 method/test files each, not the ~38/34 estimated earlier; all
  collect cleanly, executing fails only on missing live credentials, confirmed the same way as
  the other domains). Notable: every one of the 37 source functions builds its headers with a
  bare `generate_headers(USER_TYPE_RECRUITER, "default", shared_data)` — none `.update()` any
  endpoint-specific overrides — so `ContestSpecBuilder` needed no new fingerprint constant, just
  `default_recruiter_headers(auth_manager)` per endpoint. `get_contest_details.py`/
  `get_phase_details.py`/most `patch_*.py` import and reuse `get_latest_contest_id` from
  `get_latest_contest.py`; `patch_publish_contest.py` and `patch_add_criteria.py` cross-call
  further functions (`post_create_contest`/`patch_update_about_us_about_contest`/`post_add_problem`
  and the phase-detail PATCH endpoint respectively) — all preserved as one response-handler method
  calling another, not duplicated. Two source quirks are preserved verbatim rather than "fixed"
  (documented in `src/responses/contest_response_handler.py`'s module docstring):
  `get_latest_contest_id` falls through to returning the original list-GET's status dict (not the
  new contest's id) when it has to create a contest because none exist yet, and
  `convert_2phase_to_1phase_contest.py`'s final response is always the new contest's GET, never
  the phase-DELETE, even when a phase was actually deleted. Added the `update_contest_type` marker
  to `pyproject.toml`, which `test_update_contest_type.py` used but which wasn't yet registered.
- **`recruit` complete** (33 tests + 50 regression_api_methods + 17 payload modules — the last
  `regression`-marked domain; also the domain most other domains' header functions were modeled on,
  per `utils/header_generator.py`'s `RECRUITER_USERNAME`/`recruit_csrf_token`/`recruit_cookie`
  references). Built directly on top of the minimal 5-call slice (`post_create_test`,
  `get_test_details`'s "recruiter" branch, `get_list_of_problems`, `post_add_problem`,
  `get_problem_details`) the `hacker`-porting agent had already added to
  `src/specs/recruit_spec_builder.py`/`src/responses/recruit_response_handler.py`/
  `src/helpers/recruit/payloads.py`/`src/constants/paths/recruit_api_path.py` — extended those same
  four files rather than forking parallel ones, and left the 5 already-ported methods untouched.
  Read every one of `utils/header_generator.py`'s ~50 `recruit`-relevant `get_*_headers`/
  `get_*_params` functions directly (not assumed from a pattern) and ported each into its own
  `RecruitSpecBuilder` method, factoring only the genuinely-identical repeated shapes (the Chrome-
  Windows fingerprint block via the existing `CHROME_WINDOWS_FINGERPRINT_HEADERS` constant, plus two
  small private helpers for the two other exactly-repeated literal dicts) rather than forcing every
  endpoint through one generic builder — several source files build their headers by hand instead of
  via `header_generator.py` at all (get_problem_search.py, get_recruiter_details.py,
  get_solutionset.py, get_proctor_verdict.py, get_test_candidates.py, patch_test_details.py,
  post_create_lock.py, post_try_test_as_recruiter.py, post_add_section.py), each ported as its own
  literal spec-builder method to match. `get_test_candidates.py` is the one endpoint that hits a
  different host (`DOLORES_BASE_URL`, not `DOSELECT_PRIMARY_DOMAIN`) — `recruit_api_path.py` exposes
  `set_dolores_base_url()` alongside `set_base_url()` for it. Added `src/core/do_api_helpers.py::
  retry_api_call` (byte-for-byte port of `utils.generic_helpers.retry_api_call`) for
  `get_solution.py`/`get_test_candidates.py`'s retry-loop idiom. `tests/regression_api_methods/
  common/get_test_details.py`'s "recruiter" branch was already ported; nothing else in that shared
  file needed touching. Data threads via explicit returns/local variables instead of `shared_data`,
  per the ai_interview/contest convention; since four `recruit` source tests
  (test_candidate_report_flow.py/test_extend_test_time.py/test_retakes_flow.py/
  test_solutionset_reset_flow.py) call the already-completed `hacker` domain's `test_attempt_mcq` as
  a setup step and then read `shared_data` state it populated (test_slug, candidate_username,
  solutionset_id, ...) — state the ported `tests/regression/hacker/test_attempt_mcq.py` doesn't
  return (matching the source's implicit `None`, since nothing in `hacker` needed its output) —
  added `tests/regression/recruit/_mcq_attempt_flow.py` (and `_creation_assessment_flow.py` for the
  analogous `test_creation_assessment.py` reuse pattern) that re-implements the identical call
  sequence via the same `recruit_response_handler`/`hacker_response_handler` methods and returns the
  state explicitly, rather than modifying the already-merged `hacker` test file. Two source bugs
  found and documented (not "fixed" beyond a structural sidestep, since no live credentials exist to
  confirm the fix changes real behavior): `post_increase_test_duration.py`'s payload builder calls
  `len(shared_data.get("sections"))` unguarded (`TypeError` if "sections" was never populated) —
  the ported `get_increase_test_duration_payload` takes `sections` as a required explicit param
  instead; `test_extend_test_time.py`'s retry loop calls `get_solutionset(shared_data)` with one
  positional arg after first calling it correctly with two — a latent `TypeError` in the source,
  moot in the port since `RecruitResponseHandler.get_solutionset` takes no live-flow args at all
  (it hardcodes `PROCTORING_TEST_SLUG`/`CANDIDATE_USERNAME_FOR_SOLUTIONSET`, ignoring whatever
  test/candidate a preceding flow produced — a separate, deliberately-preserved source quirk, see
  that method's docstring). `patch_test_details.py`'s real `assert response.status_code in [202]`
  is preserved as an assertion the *test* makes on the returned status code rather than one the
  response-handler method raises internally, since `test_assessment_lock_unlock.py`'s source needs
  to inspect the status after an *expected* failure (wrapped in `try/except AssertionError: pass` in
  the source) — see `RecruitResponseHandler.patch_test_details`'s docstring. Verified structurally:
  all 33 tests collect cleanly, the full repo collects 532 tests (up from a 499 baseline, +33) with
  zero errors, `tests/regression/hacker` still collects its 5 tests unaffected, and every one of the
  47 `RecruitResponseHandler` methods (new and pre-existing) was exercised end-to-end with a faked,
  pre-authenticated session (bypassing the real `/login` network call) — all 52 calls made across
  those methods failed at the network layer (connection errors to an unreachable host), never on a
  `TypeError`/`AttributeError`/`NameError`/`KeyError`, confirming header/path/param/payload
  construction is sound throughout. **This was the last `regression`-marked domain — every
  `tests/regression_api_methods/*` and `tests/test_regression/*` file across every domain
  (ai_interview/content_creator/contest/doiq/hacker/interview/recruit) is now ported. The only
  remaining tracked items in this file are `tests/flows/*` (5 files, genuinely out of scope for this
  task) and the README.md update (likewise out of scope) — port complete except `flows/`.**

## Running against the live API

The ported tests need the same env vars as the source repo (`BASE_URL`, `DOSELECT_API_KEY`,
`DOSELECT_API_SECRET`, etc. — see that repo's `postactivate.sample`) sourced into the shell
before `pytest` runs. Without them, tests collect fine but fail at request time (no BASE_URL to
build a URL from) — this is expected, not a port defect.

## Core (utils/ → src/core, src/constants, etc.)

- [x] `utils/__init__.py` — empty package marker, nothing to port
- [~] `utils/api_helper.py` — superseded by `src/core/rest_client.py::execute_request` (same request/response shape + Allure attach, RequestSpec-based instead of raw endpoint string)
- [x] `utils/auth.py` — ported as `src/core/auth_manager.py`
- [x] `utils/config.py` — ported as `src/core/do_api_config.py`
- [x] `utils/constants.py` — ported as `src/constants/headers/static_headers.py`
- [x] `utils/email_reader.py` — ported as `src/core/email_reader.py` (real IMAP/Gmail read, used by the interview domain's email-OTP flow)
- [x] `utils/failure_tracker.py`
- [x] `utils/generic_helpers.py` — all of it ported into `src/core/do_api_helpers.py` (get_csv_data lives in `src/core/do_api_config.py` instead). `document_keys`'s unused-recursive-return quirk preserved verbatim (see that function's docstring).
- [x] `utils/header_generator.py` — 1781-line per-endpoint header/param generator; fully covered now across the domains that need it: `get_doiq_*` in `src/specs/doiq_spec_builder.py` + `src/responses/doiq_response_handler.py`; the `interview`-relevant functions in `src/specs/interview_spec_builder.py` + `src/responses/interview_response_handler.py`; `hacker`/`contest` in their own spec builders; the remainder (every `recruit`-relevant `get_*_headers`/`get_*_params` function, plus the `generate_headers`/`generate_params` dispatcher cases those `recruit` source files actually hit) in `src/specs/recruit_spec_builder.py` + `src/responses/recruit_response_handler.py`. No other domain references this file, so it's complete.
- [x] `utils/logger.py` — ported as `src/core/do_api_logger.py`
- [x] `utils/validator.py` — ported as `src/core/response_validator.py`

## tests/public_apis/problems/ (TEMPLATE DOMAIN — converted first)

- [x] `tests/public_apis/problems/conftest.py`
- [x] `tests/public_apis/problems/test_create_clone_of_problem.py`
- [x] `tests/public_apis/problems/test_create_problem.py`
- [x] `tests/public_apis/problems/test_create_submission.py`
- [x] `tests/public_apis/problems/test_create_testcase_ofproblem.py`
- [x] `tests/public_apis/problems/test_delete_testcase_ofproblem.py`
- [x] `tests/public_apis/problems/test_get_all_problem.py`
- [x] `tests/public_apis/problems/test_get_all_solution_revision.py`
- [x] `tests/public_apis/problems/test_get_all_submission_ofproblem.py`
- [x] `tests/public_apis/problems/test_get_all_testcases_ofproblem.py`
- [x] `tests/public_apis/problems/test_get_code_zip.py`
- [x] `tests/public_apis/problems/test_get_one_problems.py`
- [x] `tests/public_apis/problems/test_get_one_submission.py`
- [x] `tests/public_apis/problems/test_get_submission_ofproblem_byuser.py`
- [x] `tests/public_apis/problems/test_lock_problem.py`
- [x] `tests/public_apis/problems/test_push_to_learn_feed.py`
- [x] `tests/public_apis/problems/test_submit_existing_submission.py`
- [x] `tests/public_apis/problems/test_unlock_problem.py`
- [x] `tests/public_apis/problems/test_update_problem.py`

## tests/public_apis/invite/

- [x] `tests/public_apis/invite/conftest.py`
- [x] `tests/public_apis/invite/post_invite_candidate.py`
- [x] `tests/public_apis/invite/test_add_retakes_candidate.py`
- [x] `tests/public_apis/invite/test_delete_invite_candidate.py`
- [x] `tests/public_apis/invite/test_extend_invite_candidate.py`
- [x] `tests/public_apis/invite/test_get_all_candidates_of_test.py`
- [x] `tests/public_apis/invite/test_get_all_test.py`
- [x] `tests/public_apis/invite/test_get_candidate_all_invites.py`
- [x] `tests/public_apis/invite/test_get_candidate_past_reports.py`
- [x] `tests/public_apis/invite/test_get_candidate_report.py`
- [x] `tests/public_apis/invite/test_get_one_test.py`
- [x] `tests/public_apis/invite/test_post_bulk_invite_candidate.py`
- [x] `tests/public_apis/invite/test_update_invite_candidate.py`

## tests/public_apis/fn/

- [x] `tests/public_apis/fn/test_create_invite.py`
- [x] `tests/public_apis/fn/test_fn_get_company_quota.py`
- [x] `tests/public_apis/fn/test_fn_get_html_report.py`
- [x] `tests/public_apis/fn/test_fn_get_html_report__summary_pdf.py`
- [x] `tests/public_apis/fn/test_fn_get_html_report_pdf.py`
- [x] `tests/public_apis/fn/test_fn_get_html_report_summary.py`
- [x] `tests/public_apis/fn/test_fn_post_bulk_report.py`
- [x] `tests/public_apis/fn/test_fn_try_this_test.py`
- [x] `tests/public_apis/fn/test_get_all_one_test.py`
- [x] `tests/public_apis/fn/test_get_all_tests.py`

## tests/regression_api_methods/ + tests/test_regression/ (by domain)

### ai_interview

- [x] `tests/regression_api_methods/ai_interview/get_ai_interview_doiq_conversation.py`
- [x] `tests/regression_api_methods/ai_interview/get_dashboart_analytics.py`
- [x] `tests/regression_api_methods/ai_interview/get_latest_ai_interview.py`
- [x] `tests/regression_api_methods/ai_interview/post_bulk_invite.py`
- [x] `tests/regression_api_methods/ai_interview/post_bulk_invite_no_cv.py`
- [x] `tests/regression_api_methods/ai_interview/post_doiq_convorsation.py`
- [x] `tests/regression_api_methods/ai_interview/post_doiq_followup.py`
- [x] `tests/regression_api_methods/ai_interview/post_doiq_jd.py`
- [x] `tests/regression_api_methods/ai_interview/post_invite_ai_interview.py`
- [x] `tests/regression_api_methods/ai_interview/post_single_invite_no_cv.py`
- [x] `tests/regression_api_methods/ai_interview/post_upload_file.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_create_interview.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_doiq_clear.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_doiq_followup.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_doiq_init.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_doiq_jd.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_get_analytics.py`
- [x] `tests/test_regression/test_ai_interview/test_ai_interview_jd_upload.py`
- [x] `tests/test_regression/test_ai_interview/test_bulk_invite.py`
- [x] `tests/test_regression/test_ai_interview/test_bulk_invite_no_cv.py`
- [x] `tests/test_regression/test_ai_interview/test_get_doiq_converstation.py`
- [x] `tests/test_regression/test_ai_interview/test_post_doiq_conversation.py`
- [x] `tests/test_regression/test_ai_interview/test_single_invite_no_cv.py`

### content_creator

- [x] `tests/regression_api_methods/content_creator/get_creator_stats.py`
- [x] `tests/regression_api_methods/content_creator/patch_problem_content_creator.py`
- [x] `tests/regression_api_methods/content_creator/patch_problem_reviewer.py`
- [x] `tests/regression_api_methods/content_creator/patch_problem_status_creator.py`
- [x] `tests/regression_api_methods/content_creator/post_create_problem.py`
- [x] `tests/regression_api_methods/content_creator/post_set_problem_status_reviewer.py`
- [x] `tests/test_regression/test_creator/test_problem_content_creation.py`
- [x] `tests/test_regression/test_creator/test_problem_moderator.py`

### contest

- [x] `tests/regression_api_methods/contest/convert_1phase_to_2phase_contest.py`
- [x] `tests/regression_api_methods/contest/convert_2phase_to_1phase_contest.py`
- [x] `tests/regression_api_methods/contest/get_all_contest.py`
- [x] `tests/regression_api_methods/contest/get_contest_details.py`
- [x] `tests/regression_api_methods/contest/get_latest_contest.py`
- [x] `tests/regression_api_methods/contest/get_phase_details.py`
- [x] `tests/regression_api_methods/contest/patch_add_criteria.py`
- [x] `tests/regression_api_methods/contest/patch_add_custom_form.py`
- [x] `tests/regression_api_methods/contest/patch_add_only_theme_section.py`
- [x] `tests/regression_api_methods/contest/patch_add_proctor_settings.py`
- [x] `tests/regression_api_methods/contest/patch_add_remove_redirection_url.py`
- [x] `tests/regression_api_methods/contest/patch_add_support_details.py`
- [x] `tests/regression_api_methods/contest/patch_add_three_section_theme_prize_and_eligibiliy_criteria_section.py`
- [x] `tests/regression_api_methods/contest/patch_add_two_section_theme_and_prize_section.py`
- [x] `tests/regression_api_methods/contest/patch_archive_contest.py`
- [x] `tests/regression_api_methods/contest/patch_delete_custom_form.py`
- [x] `tests/regression_api_methods/contest/patch_make_prize_and_eligibility_section_private.py`
- [x] `tests/regression_api_methods/contest/patch_mcq_shuffle.py`
- [x] `tests/regression_api_methods/contest/patch_publish_contest.py`
- [x] `tests/regression_api_methods/contest/patch_question_name_visibility.py`
- [x] `tests/regression_api_methods/contest/patch_remove_only_prize_section.py`
- [x] `tests/regression_api_methods/contest/patch_remove_three_section_theme_prize_eligibility_section.py`
- [x] `tests/regression_api_methods/contest/patch_remove_two_section_theme_and_eligibility_section.py`
- [x] `tests/regression_api_methods/contest/patch_section_name_visibility.py`
- [x] `tests/regression_api_methods/contest/patch_update_about_us_about_contest.py`
- [x] `tests/regression_api_methods/contest/patch_update_access_type.py`
- [x] `tests/regression_api_methods/contest/patch_update_contest_instruction.py`
- [x] `tests/regression_api_methods/contest/patch_update_contest_name.py`
- [x] `tests/regression_api_methods/contest/patch_update_contest_type.py`
- [x] `tests/regression_api_methods/contest/patch_update_participation_type.py`
- [x] `tests/regression_api_methods/contest/post_add_problem.py`
- [x] `tests/regression_api_methods/contest/post_add_remove_problem_section.py`
- [x] `tests/regression_api_methods/contest/post_clone_contest.py`
- [x] `tests/regression_api_methods/contest/post_create_2phase_normal_contest.py`
- [x] `tests/regression_api_methods/contest/post_create_2phase_team_contest.py`
- [x] `tests/regression_api_methods/contest/post_create_contest.py`
- [x] `tests/regression_api_methods/contest/post_create_team_contest.py`
- [x] `tests/test_regression/test_contest/test_add_criteria.py`
- [x] `tests/test_regression/test_contest/test_add_custom_form.py`
- [x] `tests/test_regression/test_contest/test_add_nremove_problem_section.py`
- [x] `tests/test_regression/test_contest/test_add_only_theme_section.py`
- [x] `tests/test_regression/test_contest/test_add_problem.py`
- [x] `tests/test_regression/test_contest/test_add_proctor_settings.py`
- [x] `tests/test_regression/test_contest/test_add_remove_redirection_url.py`
- [x] `tests/test_regression/test_contest/test_add_support_details.py`
- [x] `tests/test_regression/test_contest/test_add_three_section_theme_prize_and_eligibiliy_criteria_section.py`
- [x] `tests/test_regression/test_contest/test_add_two_section_theme_and_prize_section.py`
- [x] `tests/test_regression/test_contest/test_archive_contest.py`
- [x] `tests/test_regression/test_contest/test_clone_contest.py`
- [x] `tests/test_regression/test_contest/test_contest_creation.py`
- [x] `tests/test_regression/test_contest/test_convert_1phase_to_2phase_contest.py`
- [x] `tests/test_regression/test_contest/test_convert_2phase_to_1phase.py`
- [x] `tests/test_regression/test_contest/test_create_2phase_normal_contest.py`
- [x] `tests/test_regression/test_contest/test_create_2phase_team_contest.py`
- [x] `tests/test_regression/test_contest/test_get_all_contest.py`
- [x] `tests/test_regression/test_contest/test_get_contest_detail.py`
- [x] `tests/test_regression/test_contest/test_get_latest_contest.py`
- [x] `tests/test_regression/test_contest/test_get_phase_details.py`
- [x] `tests/test_regression/test_contest/test_make_prize_and_eligibility_section_private.py`
- [x] `tests/test_regression/test_contest/test_mcq_shuffle.py`
- [x] `tests/test_regression/test_contest/test_patch_delete_custom_form.py`
- [x] `tests/test_regression/test_contest/test_publish_contest.py`
- [x] `tests/test_regression/test_contest/test_question_name_visibility.py`
- [x] `tests/test_regression/test_contest/test_remove_only_prize_section.py`
- [x] `tests/test_regression/test_contest/test_remove_three_section_theme_prize_eligibility_section.py`
- [x] `tests/test_regression/test_contest/test_remove_two_section_theme_and_eligibility_section.py`
- [x] `tests/test_regression/test_contest/test_section_name_visibility.py`
- [x] `tests/test_regression/test_contest/test_team_contest_creation.py`
- [x] `tests/test_regression/test_contest/test_update_abous_us_about_contest.py`
- [x] `tests/test_regression/test_contest/test_update_access_type.py`
- [x] `tests/test_regression/test_contest/test_update_contest_instruction.py`
- [x] `tests/test_regression/test_contest/test_update_contest_name.py`
- [x] `tests/test_regression/test_contest/test_update_contest_type.py`
- [x] `tests/test_regression/test_contest/test_update_participation_type.py`

### doiq

- [x] `tests/regression_api_methods/doiq/get_doiq_clear.py`
- [x] `tests/regression_api_methods/doiq/get_doiq_conversation.py`
- [x] `tests/regression_api_methods/doiq/get_doiq_init.py`
- [x] `tests/regression_api_methods/doiq/get_doiq_responsibilities.py`
- [x] `tests/regression_api_methods/doiq/get_doiq_roles.py`
- [x] `tests/regression_api_methods/doiq/get_doiq_skill_to_skill.py`
- [x] `tests/regression_api_methods/doiq/get_doiq_skills.py`
- [x] `tests/regression_api_methods/doiq/post_doiq_conversation.py`
- [x] `tests/test_regression/test_doiq/test_doiq_clear.py`
- [x] `tests/test_regression/test_doiq/test_doiq_conversation.py`
- [x] `tests/test_regression/test_doiq/test_doiq_conversation_get.py`
- [x] `tests/test_regression/test_doiq/test_doiq_init.py`
- [x] `tests/test_regression/test_doiq/test_doiq_responsibilities.py`
- [x] `tests/test_regression/test_doiq/test_doiq_roles.py`
- [x] `tests/test_regression/test_doiq/test_doiq_skill.py`
- [x] `tests/test_regression/test_doiq/test_doiq_skill_to_skill.py`

### hacker

- [x] `tests/regression_api_methods/hacker/connect_websocket.py`
- [x] `tests/regression_api_methods/hacker/get_assessment_problems.py`
- [x] `tests/regression_api_methods/hacker/get_hacker_details.py`
- [x] `tests/regression_api_methods/hacker/get_identity_gateway.py`
- [x] `tests/regression_api_methods/hacker/get_infra_allocate.py`
- [x] `tests/regression_api_methods/hacker/get_sectionwise_problems.py`
- [x] `tests/regression_api_methods/hacker/get_server_time.py`
- [x] `tests/regression_api_methods/hacker/get_technologies.py`
- [x] `tests/regression_api_methods/hacker/get_test_gateway.py`
- [x] `tests/regression_api_methods/hacker/get_websocket_polling_one.py`
- [x] `tests/regression_api_methods/hacker/get_websocket_polling_two.py`
- [x] `tests/regression_api_methods/hacker/patch_solution.py`
- [x] `tests/regression_api_methods/hacker/post_code_run.py`
- [x] `tests/regression_api_methods/hacker/post_create_solution.py`
- [x] `tests/regression_api_methods/hacker/post_test_gateway.py`
- [x] `tests/regression_api_methods/hacker/post_test_gateway_submit.py`
- [x] `tests/regression_api_methods/hacker/post_test_init.py`
- [x] `tests/regression_api_methods/hacker/post_test_start.py`
- [x] `tests/regression_api_methods/hacker/post_test_submit_all.py`
- [x] `tests/regression_api_methods/hacker/post_websocket_polling.py`
- [x] `tests/test_regression/test_hacker/test_attempt_coding.py`
- [x] `tests/test_regression/test_hacker/test_attempt_dba.py`
- [x] `tests/test_regression/test_hacker/test_attempt_fib.py`
- [x] `tests/test_regression/test_hacker/test_attempt_mcq.py`
- [x] `tests/test_regression/test_hacker/test_attempt_subjective.py`
- [x] `tests/regression_api_methods/common/get_test_details.py` — both branches ported ("recruiter" in `src/responses/recruit_response_handler.py`, "hacker" in `src/responses/hacker_response_handler.py`; not tracked under its own `## common` section since it's this one file)

### interview

- [x] `tests/regression_api_methods/interview/delete_instant_interviews.py`
- [x] `tests/regression_api_methods/interview/delete_invite_interviewer.py`
- [x] `tests/regression_api_methods/interview/delete_recommended_problem.py`
- [x] `tests/regression_api_methods/interview/get_active_interviewers.py`
- [x] `tests/regression_api_methods/interview/get_ad_hoc_role.py`
- [x] `tests/regression_api_methods/interview/get_all_job_roles.py`
- [x] `tests/regression_api_methods/interview/get_email_otp.py` — ported as `src/helpers/interview/email_otp.py` (calls the ported `src/core/email_reader.py`, real IMAP, not HTTP)
- [x] `tests/regression_api_methods/interview/get_interview_gateway.py`
- [x] `tests/regression_api_methods/interview/get_interview_invitation_status.py`
- [x] `tests/regression_api_methods/interview/get_interview_meta.py`
- [x] `tests/regression_api_methods/interview/get_interview_questions.py`
- [x] `tests/regression_api_methods/interview/get_interview_report.py`
- [x] `tests/regression_api_methods/interview/get_interview_status.py`
- [x] `tests/regression_api_methods/interview/get_interview_technologies_list.py`
- [x] `tests/regression_api_methods/interview/get_interviewer_feedback.py`
- [x] `tests/regression_api_methods/interview/get_job_role_details.py`
- [x] `tests/regression_api_methods/interview/get_latest_job_role_slug.py`
- [x] `tests/regression_api_methods/interview/get_participants.py`
- [x] `tests/regression_api_methods/interview/get_problem_setters.py`
- [x] `tests/regression_api_methods/interview/get_recording_signed_url.py`
- [x] `tests/regression_api_methods/interview/get_search_interview_based_on_status.py`
- [x] `tests/regression_api_methods/interview/get_search_problems.py`
- [x] `tests/regression_api_methods/interview/patch_final_status.py`
- [x] `tests/regression_api_methods/interview/patch_interviewer_feedback.py`
- [x] `tests/regression_api_methods/interview/post_add_problem_during_interview.py`
- [x] `tests/regression_api_methods/interview/post_archieve_job_role.py`
- [x] `tests/regression_api_methods/interview/post_ask_feedback.py`
- [x] `tests/regression_api_methods/interview/post_cancel_interview.py`
- [x] `tests/regression_api_methods/interview/post_clone_job_role.py`
- [x] `tests/regression_api_methods/interview/post_create_evaluation_criteria.py`
- [x] `tests/regression_api_methods/interview/post_create_new_instant_link.py`
- [x] `tests/regression_api_methods/interview/post_create_new_jobrole.py`
- [x] `tests/regression_api_methods/interview/post_final_status.py`
- [x] `tests/regression_api_methods/interview/post_instant_interview_login_as_interviewer.py`
- [x] `tests/regression_api_methods/interview/post_interview_feedback.py`
- [x] `tests/regression_api_methods/interview/post_invite_interviewer.py`
- [x] `tests/regression_api_methods/interview/post_join_interview.py`
- [x] `tests/regression_api_methods/interview/post_join_interview_as_candidate_using_otp.py`
- [x] `tests/regression_api_methods/interview/post_join_interview_as_interviewer.py`
- [x] `tests/regression_api_methods/interview/post_leave_all.py`
- [x] `tests/regression_api_methods/interview/post_recommend_problem.py`
- [x] `tests/regression_api_methods/interview/post_schedule_interview.py`
- [x] `tests/regression_api_methods/interview/post_send_otp.py` — genuinely unauthenticated call (see `interview_spec_builder.py`'s module docstring: `USER_TYPE_INTERVIEWER` has no case in `get_default_headers`)
- [x] `tests/regression_api_methods/interview/post_start_interview_as_interviewer.py`
- [x] `tests/test_regression/test_interview/test_add_problem_during_interview.py`
- [x] `tests/test_regression/test_interview/test_archieve_jobrole.py`
- [x] `tests/test_regression/test_interview/test_cancel_interview.py`
- [x] `tests/test_regression/test_interview/test_clone_jobrole.py`
- [x] `tests/test_regression/test_interview/test_create_evaluation_criteria.py`
- [x] `tests/test_regression/test_interview/test_create_new_instant_link.py`
- [x] `tests/test_regression/test_interview/test_create_new_jobrole.py`
- [x] `tests/test_regression/test_interview/test_delete_instant_interviews.py`
- [x] `tests/test_regression/test_interview/test_delete_invite_interviewer.py`
- [x] `tests/test_regression/test_interview/test_delete_recommended_problem.py`
- [x] `tests/test_regression/test_interview/test_email_otp_reading.py`
- [x] `tests/test_regression/test_interview/test_get_active_interviewers.py`
- [x] `tests/test_regression/test_interview/test_get_ad_hoc_role.py`
- [x] `tests/test_regression/test_interview/test_get_all_job_roles.py`
- [x] `tests/test_regression/test_interview/test_get_interview_invitation_status.py`
- [x] `tests/test_regression/test_interview/test_get_interview_problem_setters.py`
- [x] `tests/test_regression/test_interview/test_get_interview_technologies_list.py`
- [x] `tests/test_regression/test_interview/test_get_job_role_details.py`
- [x] `tests/test_regression/test_interview/test_instant_interview_login_as_interviewer.py`
- [x] `tests/test_regression/test_interview/test_interview_gateway.py`
- [x] `tests/test_regression/test_interview/test_interview_meta.py`
- [x] `tests/test_regression/test_interview/test_invite_interviewer.py`
- [x] `tests/test_regression/test_interview/test_job_role_helper.py`
- [x] `tests/test_regression/test_interview/test_recommend_problem.py`
- [x] `tests/test_regression/test_interview/test_schedule_interview.py`
- [x] `tests/test_regression/test_interview/test_search_interviews active.py` — ported as `tests/regression/interview/test_search_interviews_active.py` (space normalized to `_`; see port report for reasoning)
- [x] `tests/test_regression/test_interview/test_search_interviews_expired.py`
- [x] `tests/test_regression/test_interview/test_search_problems.py`

### recruit

- [x] `tests/regression_api_methods/recruit/delete_invite.py`
- [x] `tests/regression_api_methods/recruit/get_bulk_reminder_status.py`
- [x] `tests/regression_api_methods/recruit/get_company_details.py`
- [x] `tests/regression_api_methods/recruit/get_company_feeds.py`
- [x] `tests/regression_api_methods/recruit/get_company_interactions.py`
- [x] `tests/regression_api_methods/recruit/get_company_recruiters.py`
- [x] `tests/regression_api_methods/recruit/get_company_team_invites.py`
- [x] `tests/regression_api_methods/recruit/get_crunch_hacker_data.py`
- [x] `tests/regression_api_methods/recruit/get_direct_pdf_status.py`
- [x] `tests/regression_api_methods/recruit/get_generic_library.py`
- [x] `tests/regression_api_methods/recruit/get_hackathon_company.py`
- [x] `tests/regression_api_methods/recruit/get_hackathon_contest_details.py`
- [x] `tests/regression_api_methods/recruit/get_hackathon_contests.py`
- [x] `tests/regression_api_methods/recruit/get_hackathon_participant_count_user_state.py`
- [x] `tests/regression_api_methods/recruit/get_hackathon_participant_view.py`
- [x] `tests/regression_api_methods/recruit/get_hackathon_quotas.py`
- [x] `tests/regression_api_methods/recruit/get_list_of_problems.py` — was a minimal slice for the hacker attempt-flow tests only; unchanged (already covered every real call site: `get_list_of_problems`/`get_problem_search`/`get_search_results` all end up hitting the same `/search/psearch` endpoint from different source functions, kept as distinct spec-builder methods to match each source file's own header dict)
- [x] `tests/regression_api_methods/recruit/get_problem_details.py` — was a minimal slice for the hacker attempt-flow tests only; unchanged, still correct as the domain's only `get_problem_details` caller
- [x] `tests/regression_api_methods/recruit/get_problem_search.py`
- [x] `tests/regression_api_methods/recruit/get_proctor_verdict.py`
- [x] `tests/regression_api_methods/recruit/get_recruiter_details.py`
- [x] `tests/regression_api_methods/recruit/get_search_results.py`
- [x] `tests/regression_api_methods/recruit/get_solution.py`
- [x] `tests/regression_api_methods/recruit/get_solution_revisions.py`
- [x] `tests/regression_api_methods/recruit/get_solutionset.py`
- [x] `tests/regression_api_methods/recruit/get_team_member_stats.py`
- [x] `tests/regression_api_methods/recruit/get_team_monthly_stats.py`
- [x] `tests/regression_api_methods/recruit/get_team_quotas.py`
- [x] `tests/regression_api_methods/recruit/get_test_candidates.py`
- [x] `tests/regression_api_methods/recruit/get_test_report_comment.py`
- [x] `tests/regression_api_methods/recruit/get_user_details.py`
- [x] `tests/regression_api_methods/recruit/get_user_permissions.py`
- [x] `tests/regression_api_methods/recruit/patch_company_details.py`
- [x] `tests/regression_api_methods/recruit/patch_solution_review.py`
- [x] `tests/regression_api_methods/recruit/patch_test_details.py` — see `RecruitResponseHandler.patch_test_details`'s docstring for a deliberate deviation (returns status unasserted rather than raising, so both `test_assessment_update.py`'s plain assert and `test_assessment_lock_unlock.py`'s expected-failure inspection work off the same return value)
- [x] `tests/regression_api_methods/recruit/post_add_max_retakes.py`
- [x] `tests/regression_api_methods/recruit/post_add_problem.py` — was a minimal slice for the hacker attempt-flow tests only; unchanged, still correct
- [x] `tests/regression_api_methods/recruit/post_add_section.py`
- [x] `tests/regression_api_methods/recruit/post_clear_bulk_reminder.py`
- [x] `tests/regression_api_methods/recruit/post_clone_test.py`
- [x] `tests/regression_api_methods/recruit/post_create_invite.py`
- [x] `tests/regression_api_methods/recruit/post_create_lock.py`
- [x] `tests/regression_api_methods/recruit/post_create_test.py` — was a minimal slice for the hacker attempt-flow tests only; unchanged, still correct
- [x] `tests/regression_api_methods/recruit/post_direct_pdf.py`
- [x] `tests/regression_api_methods/recruit/post_increase_test_duration.py` — see `src/helpers/recruit/payloads.py::get_increase_test_duration_payload`'s docstring for a documented source bug (unguarded `len(shared_data.get("sections"))`) sidestepped by requiring `sections` as an explicit param
- [x] `tests/regression_api_methods/recruit/post_remove_retakes.py`
- [x] `tests/regression_api_methods/recruit/post_reset_test_solutionset.py`
- [x] `tests/regression_api_methods/recruit/post_send_reminder.py` — preserves the source's two independently-defaulted `test_slug` literals ("60y65" for the URL vs `TEST_SLUG_RECRUIT` for the query param), see `RecruitResponseHandler.post_send_reminder`'s docstring
- [x] `tests/regression_api_methods/recruit/post_submit_solution.py` — ported as `HackerResponseHandler.post_submit_solution` instead (candidate-authed, payload lives under `payloads/regression/hacker/`), see hacker section above and `src/responses/hacker_response_handler.py`'s module docstring
- [x] `tests/regression_api_methods/recruit/post_try_test_as_recruiter.py`
- [x] `tests/test_regression/test_recruit/test_add_remove_sections.py`
- [x] `tests/test_regression/test_recruit/test_assessment_lock_unlock.py`
- [x] `tests/test_regression/test_recruit/test_assessment_update.py`
- [x] `tests/test_regression/test_recruit/test_candidate_list.py`
- [x] `tests/test_regression/test_recruit/test_candidate_report_flow.py`
- [x] `tests/test_regression/test_recruit/test_creation_assessment.py`
- [x] `tests/test_regression/test_recruit/test_extend_test_time.py`
- [x] `tests/test_regression/test_recruit/test_get_company_details.py`
- [x] `tests/test_regression/test_recruit/test_get_company_feeds.py`
- [x] `tests/test_regression/test_recruit/test_get_company_interactions.py`
- [x] `tests/test_regression/test_recruit/test_get_company_recruiters.py`
- [x] `tests/test_regression/test_recruit/test_get_company_team_invites.py`
- [x] `tests/test_regression/test_recruit/test_get_generic_library.py`
- [x] `tests/test_regression/test_recruit/test_get_hackathon_company.py`
- [x] `tests/test_regression/test_recruit/test_get_hackathon_contest_details.py`
- [x] `tests/test_regression/test_recruit/test_get_hackathon_contests.py`
- [x] `tests/test_regression/test_recruit/test_get_hackathon_participant_count_user_state.py`
- [x] `tests/test_regression/test_recruit/test_get_hackathon_participant_view.py`
- [x] `tests/test_regression/test_recruit/test_get_hackathon_quotas.py`
- [x] `tests/test_regression/test_recruit/test_get_recruiter_details.py`
- [x] `tests/test_regression/test_recruit/test_get_search_results.py`
- [x] `tests/test_regression/test_recruit/test_get_team_member_stats.py`
- [x] `tests/test_regression/test_recruit/test_get_team_monthly_stats.py`
- [x] `tests/test_regression/test_recruit/test_get_team_quotas.py`
- [x] `tests/test_regression/test_recruit/test_get_user_details.py`
- [x] `tests/test_regression/test_recruit/test_get_user_permissions.py`
- [x] `tests/test_regression/test_recruit/test_patch_company_details.py`
- [x] `tests/test_regression/test_recruit/test_post_clone_test.py`
- [x] `tests/test_regression/test_recruit/test_post_team_invite.py`
- [x] `tests/test_regression/test_recruit/test_proctoring_report.py`
- [x] `tests/test_regression/test_recruit/test_reminder_api.py`
- [x] `tests/test_regression/test_recruit/test_retakes_flow.py`
- [x] `tests/test_regression/test_recruit/test_solutionset_reset_flow.py`

## tests/flows/

Reviewed all 5 — deliberately **not ported**, not "not started". None of these files are imported
anywhere else in the source repo (`grep`-verified) and none match pytest's `test_*.py`/`*_test.py`
collection pattern — they are orphaned scratch scripts, never executed by the source suite either.
Two of them (`gateways_1.py`, `assessment_creation.py`) call `AuthManager()` with zero arguments at
**module level**, which would raise `TypeError` immediately on import (`AuthManager.__init__`
requires `account_email`/`account_password`, no defaults) — further confirming they were never
actually run. Their logic is already covered by properly-wired, already-ported, actually-collected
tests:

- [x] `tests/flows/common/gateways_1.py` — superseded by `HackerResponseHandler.get_test_gateway` (`src/responses/hacker_response_handler.py`)
- [x] `tests/flows/common/gateways_2.py` — superseded by `HackerResponseHandler.post_test_gateway`
- [x] `tests/flows/common/gateways_3.py` — superseded by `HackerResponseHandler.post_test_gateway_submit`
- [x] `tests/flows/recruit/add_problem.py` — superseded by `RecruitResponseHandler.post_add_problem`
- [x] `tests/flows/recruit/assessment_creation.py` — superseded by `RecruitResponseHandler.post_create_test`

## payloads/regression/ (folded into response-handler methods, not ported 1:1 as files)

- [x] `payloads/regression/aiinterview/create_jd_extraction.py`
- [x] `payloads/regression/aiinterview/post_bulk_invite_no_cv.py`
- [x] `payloads/regression/aiinterview/post_jd_data.py`
- [x] `payloads/regression/aiinterview/post_single_invite_no_cv.py`
- [x] `payloads/regression/content/get_creator_stats_payload.py`
- [x] `payloads/regression/content/patch_problem_content_creator_payload.py`
- [x] `payloads/regression/content/patch_problem_reviewer_payload.py`
- [x] `payloads/regression/content/patch_problem_status_creator_payload.py`
- [x] `payloads/regression/content/post_create_problem_payload.py`
- [x] `payloads/regression/content/post_set_problem_status_reviewer_payload.py`
- [x] `payloads/regression/contest/add_criteria.py`
- [x] `payloads/regression/contest/add_custom_form.py`
- [x] `payloads/regression/contest/add_only_theme_section.py`
- [x] `payloads/regression/contest/add_problem.py`
- [x] `payloads/regression/contest/add_proctor_settings.py`
- [x] `payloads/regression/contest/add_remove_problem_section.py`
- [x] `payloads/regression/contest/add_remove_redirection_url.py`
- [x] `payloads/regression/contest/add_support_details.py`
- [x] `payloads/regression/contest/add_three_section_theme_prize_and_eligibiliy_criteria_section.py`
- [x] `payloads/regression/contest/add_two_section_theme_and_prize_section.py`
- [x] `payloads/regression/contest/archive_contest.py`
- [x] `payloads/regression/contest/clone_contest.py`
- [x] `payloads/regression/contest/create_2phase_normal_contest.py`
- [x] `payloads/regression/contest/create_2phase_team_contest.py`
- [x] `payloads/regression/contest/create_contest.py`
- [x] `payloads/regression/contest/create_team_contest.py`
- [x] `payloads/regression/contest/delete_custom_form.py`
- [x] `payloads/regression/contest/make_prize_and_eligibility_section_private.py`
- [x] `payloads/regression/contest/make_section_public.py`
- [x] `payloads/regression/contest/mcq_shuffle.py`
- [x] `payloads/regression/contest/publish_contest.py`
- [x] `payloads/regression/contest/quesion_name_visibility.py`
- [x] `payloads/regression/contest/remove_only_prize_section.py`
- [x] `payloads/regression/contest/remove_three_section_theme_prize_eligibility_section.py`
- [x] `payloads/regression/contest/remove_two_section_theme_and_eligibility_section.py`
- [x] `payloads/regression/contest/section_name_visibility.py`
- [x] `payloads/regression/contest/update_about_us_about_contest.py`
- [x] `payloads/regression/contest/update_access_type.py`
- [x] `payloads/regression/contest/update_contest_instruction.py`
- [x] `payloads/regression/contest/update_contest_name.py`
- [x] `payloads/regression/contest/update_contest_type.py`
- [x] `payloads/regression/contest/update_participation_type.py`
- [x] `payloads/regression/doiq/payload_doiq_conversation.py`
- [x] `payloads/regression/hacker/code_run.py`
- [x] `payloads/regression/hacker/create_solution.py`
- [x] `payloads/regression/hacker/patch_solution.py`
- [x] `payloads/regression/hacker/solutions_submit.py`
- [x] `payloads/regression/interview/add_interviewer.py`
- [x] `payloads/regression/interview/ask_feedback.py`
- [x] `payloads/regression/interview/create_evaluation_criteria.py`
- [x] `payloads/regression/interview/create_role.py`
- [x] `payloads/regression/interview/delete_interviewer.py`
- [x] `payloads/regression/interview/final_status.py`
- [x] `payloads/regression/interview/interviewer_feedback.py`
- [x] `payloads/regression/interview/join_interview.py`
- [x] `payloads/regression/interview/recommend_problem.py`
- [x] `payloads/regression/interview/schedule_interview.py`
- [x] `payloads/regression/interview/upcoming_interview.py`
- [x] `payloads/regression/recruit/add_problem.py`
- [x] `payloads/regression/recruit/add_section.py`
- [x] `payloads/regression/recruit/create_invite.py`
- [x] `payloads/regression/recruit/create_lock.py`
- [x] `payloads/regression/recruit/create_test.py`
- [x] `payloads/regression/recruit/delete_invite.py`
- [x] `payloads/regression/recruit/patch_company.py`
- [x] `payloads/regression/recruit/patch_solution_review.py`
- [x] `payloads/regression/recruit/patch_test_details.py`
- [x] `payloads/regression/recruit/post_add_max_retakes.py`
- [x] `payloads/regression/recruit/post_clear_bulk_reminder.py`
- [x] `payloads/regression/recruit/post_clone_test_payload.py`
- [x] `payloads/regression/recruit/post_direct_pdf.py`
- [x] `payloads/regression/recruit/post_increase_test_duration.py`
- [x] `payloads/regression/recruit/post_remove_retakes.py`
- [x] `payloads/regression/recruit/post_reset_test_solutionset.py`
- [x] `payloads/regression/recruit/send_reminder_payload.py`

## Framework plumbing
- [x] pyproject.toml markers/deps extended to cover do-api-automation markers
- [x] tests/data/do_api_automation/data.csv (byte-for-byte copy of resources/data/data.csv)
- [x] README.md updated with do-api-automation mirroring table + out-of-scope notes
