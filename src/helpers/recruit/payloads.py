"""
Ports payloads/regression/recruit/*.py from https://github.com/doselect/do-api-automation.git.

Started as a minimal slice (create_test_payload/add_problem_payload) added by the `hacker`-porting
agent for its attempt-flow prerequisite calls (see recruit_api_path.py's docstring); extended here
to cover the rest of the domain. Every function takes explicit parameters instead of a `shared_data`
dict, per the established ai_interview/contest convention — callers (RecruitResponseHandler methods)
resolve defaults (CSV/env constants) themselves before calling in.

`ADD_SECTION_PAYLOAD`/`DELETE_SECTION_PAYLOAD` are exposed as functions returning a fresh dict each
call (rather than the source's module-level mutable dicts that call sites `.copy()`d before
mutating) — same literal values, safer than sharing mutable module state across tests.
"""
from __future__ import annotations

import random

from src.core.do_api_config import DOSELECT_COMPANY_SLUG, RECRUITER_USERNAME


def create_test_payload(test_type: str = "RECRUIT", duration: int = 120) -> dict:
    """Mirrors payloads/regression/recruit/create_test.py::create_test_payload."""
    resolved_type = "GEN" if test_type == "RECRUIT" else "LRN"
    return {
        "creator": f"/api/v1/user/{RECRUITER_USERNAME}",
        "name": f"Test API Automation - {random.randint(1, 9999)}",
        "duration": duration,
        "category": "PRI",
        "test_type": resolved_type,
        "mode": "TIM",
        "owner": f"/api/v1/company/{DOSELECT_COMPANY_SLUG}",
    }


def add_problem_payload(problem_slug: str, section_slug: str, context_slug: str) -> dict:
    """Mirrors payloads/regression/recruit/add_problem.py::add_problem_payload."""
    return {
        "action": "add",
        "context": "test",
        "context_slug": context_slug,
        "problem_slug": problem_slug,
        "section_slug": section_slug,
    }


# ---------------------------------------------------------------------------------------------
# add_section.py
# ---------------------------------------------------------------------------------------------


def add_section_payload() -> dict:
    """Mirrors payloads/regression/recruit/add_section.py::ADD_SECTION_PAYLOAD."""
    return {
        "action": "add",
        "test_slug": "",  # populated by the caller
        "section": {
            "name": "Section 2",
            "duration": 0,
            "shuffle": False,
            "sample": 0,
            "description": "",
            "slug": "",
        },
    }


def delete_section_payload() -> dict:
    """Mirrors payloads/regression/recruit/add_section.py::DELETE_SECTION_PAYLOAD."""
    return {
        "action": "delete",
        "test_slug": "dal01",
        "section_slug": "ece025e102e54e9e958d380ce8351fd0",
        "section": {
            "custom_scoring": {"enabled": False, "penalty": 0, "score": 0},
            "description": "",
            "duration": 0,
            "is_timed": False,
            "name": "Section 2",
            "problems": [],
            "sample": 0,
            "shuffle": False,
            "slug": "ece025e102e54e9e958d380ce8351fd0",
            "isExpanded": True,
        },
    }


# ---------------------------------------------------------------------------------------------
# create_invite.py
# ---------------------------------------------------------------------------------------------


def create_invite_payload(test_slug: str, invite_type: str = "candidate") -> dict:
    """
    Mirrors payloads/regression/recruit/create_invite.py::create_invite_payload(shared_data, type)
    (`type` renamed `invite_type` — shadows the builtin). Returns `None` for any other `invite_type`,
    same as the source's `if/elif` with no `else` (the two call sites in the source only ever pass
    "candidate" or "team").
    """
    from src.core.do_api_helpers import generate_random_email

    if invite_type == "candidate":
        return {
            "email_list": [{"email": generate_random_email(), "name": ""}],
            "context": "test",
            "slug": test_slug,
            "subject": "INFOEDGE's Invitation to Test Automation",
            "email_body": (
                "PGgyPjxzcGFuIHN0eWxlPSJjb2xvcjogcmdiKDYzLCA4MSwgMTgxKTsiPkhlbGxvIHtjYW5kaWRhdGVfbmFtZX0sPC9zcGFuPjwvaDI+"
                "PHA+UGxlYXNlIHJlYWQgdGhyb3VnaCB0aGUgYmVsb3cgaW5zdHJ1Y3Rpb25zIGFuZCBhdHRlbXB0IHRoZSB0ZXN0LiBXZSB3aWxsIGdl"
                "dCBiYWNrIHRvIHlvdSBwb3N0IHlvdXIgYXNzZXNzbWVudCBjb21wbGV0aW9uIGFuZCByZXZpZXcuPC9wPg=="
            ),
            "email_body_changed": False,
            "send_email_notification": False,
        }
    if invite_type == "team":
        return {"email_list": [generate_random_email()], "context": "team", "member_type": "MEM"}
    return None


# ---------------------------------------------------------------------------------------------
# create_lock.py
# ---------------------------------------------------------------------------------------------


def create_lock_payload(test_slug: str) -> dict:
    """Mirrors payloads/regression/recruit/create_lock.py::CREATE_LOCK_PAYLOAD (test_slug substituted fresh, not module-mutated)."""
    return {"resource_type": "test", "resource_slug": test_slug}


# ---------------------------------------------------------------------------------------------
# delete_invite.py
# ---------------------------------------------------------------------------------------------


def delete_invite_payload(invite_id) -> dict:
    """Mirrors payloads/regression/recruit/delete_invite.py::get_delete_invite_payload."""
    return {"id": invite_id}


# ---------------------------------------------------------------------------------------------
# patch_company.py
# ---------------------------------------------------------------------------------------------


def patch_company_payload(company_details_json: dict) -> dict:
    """
    Mirrors payloads/regression/recruit/patch_company.py::get_patch_company_payload: takes the
    prior GET /company/{slug} response body (source read it back off `shared_data["company_details"]`,
    a stashed `requests.Response`), drops `resource_uri`, and randomizes the first perk's description.
    """
    from src.core.do_api_helpers import generate_random_string

    payload = dict(company_details_json)
    payload.pop("resource_uri", None)
    if payload.get("perks"):
        payload["perks"][0]["description"] = generate_random_string()
    return payload


# ---------------------------------------------------------------------------------------------
# patch_solution_review.py
# ---------------------------------------------------------------------------------------------


def patch_solution_review_payload(status: str, total_score) -> dict:
    """Mirrors payloads/regression/recruit/patch_solution_review.py::patch_solution_review_payload."""
    return {"status": status, "total_score": total_score}


# ---------------------------------------------------------------------------------------------
# patch_test_details.py
# ---------------------------------------------------------------------------------------------

PATCH_TEST_DETAILS_PAYLOAD: dict = {
    "access_type": "INV",
    "allowed_technologies": {},
    "archived": False,
    "cacheProblemData": False,
    "contest_id": None,
    "context_name": "test",
    "cover_url": None,
    "custom_scoring": {
        "0e20087ee81744459b9a317704b875b0": {"enabled": False, "penalty": 0, "score": 0},
        "b3e8ebeebd7e4c81b93c6b8782db42f6": {"enabled": True, "penalty": 2, "score": 22},
        "d687378d0ddc450ea7f210556642fa98": {"enabled": False, "penalty": 0, "score": 0},
        "enabled": False,
    },
    "cutoff": 45,
    "duration": 90,
    "email_lead_sent": False,
    "enable_feedback_page": True,
    "enable_leaderboard": False,
    "end_time": None,
    "excel_report_fields": [
        {
            "category": "Personal Details",
            "data": [
                {"key": "0", "label": "Name", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "1", "label": "Email", "problemwise_enabled": True, "sectionwise_enabled": True},
            ],
        },
        {
            "category": "Assessment Details",
            "data": [
                {"key": "2", "label": "Status", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "3", "label": "Invited On(Date)", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "4", "label": "Started At(Date)", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "5", "label": "Started At(Time)", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "6", "label": "Submitted At(Date)", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "7", "label": "Submitted At(Time)", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "8", "label": "Time Zone", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "9", "label": "Time Taken", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "10", "label": "Total no. of Problems", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "11", "label": "No. of Problems Solved", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "12", "label": "Technologies Used", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "13", "label": "Verdict", "problemwise_enabled": True, "sectionwise_enabled": True},
            ],
        },
        {
            "category": "Report Url",
            "data": [{"key": "14", "label": "Report URL", "problemwise_enabled": True, "sectionwise_enabled": True}],
        },
        {
            "category": "Score Details",
            "data": [
                {"key": "15", "label": "Test Max Score", "problemwise_enabled": True, "sectionwise_enabled": True},
                {
                    "key": "16",
                    "label": "Candidate Total Score (based on Best Attempts)",
                    "problemwise_enabled": True,
                    "sectionwise_enabled": True,
                },
                {
                    "key": "17",
                    "label": "Candidate Total Score (based on Last Attempt)",
                    "problemwise_enabled": True,
                    "sectionwise_enabled": True,
                },
                {"key": "18", "label": "% based on Best Attempt", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "19", "label": "% based on Last Attempt", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "20", "label": "Code Quality Score", "problemwise_enabled": True, "sectionwise_enabled": True},
            ],
        },
        {
            "category": "Malpractice Information",
            "data": [
                {"key": "21", "label": "Proctoring Verdict", "problemwise_enabled": True, "sectionwise_enabled": True},
                {
                    "key": "22",
                    "label": "Total Number of Violations",
                    "problemwise_enabled": True,
                    "sectionwise_enabled": True,
                },
                {
                    "key": "23",
                    "label": "Test Window Violation (minutes)",
                    "problemwise_enabled": True,
                    "sectionwise_enabled": True,
                },
                {"key": "24", "label": "Captured Frames Details", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "25", "label": "Missing Frames Details", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "29", "label": "Plagiarism Details", "problemwise_enabled": True, "sectionwise_enabled": True},
            ],
        },
        {
            "category": "Level Information",
            "data": [
                {"key": "26", "label": "Max Score", "problemwise_enabled": True, "sectionwise_enabled": True},
                {"key": "27", "label": "Candidate Score", "problemwise_enabled": True, "sectionwise_enabled": True},
            ],
        },
    ],
    "has_coding_problems": False,
    "has_jobrole": False,
    "has_unique_section_slug": True,
    "in_learn_feed": False,
    "instructions": (
        "<ol><li><!--block-->If you are solving a coding problem, you will either be required to choose a "
        "programming language from the options that have been enabled by the administrator or choose your "
        "preferred programming language in case no options have been enabled by the administrator. "
        "<strong>Note:</strong> In case you're solving coding problems: All inputs are from STDIN and output to "
        "STDOUT.</li><li><!--block-->If the test mandates you to use the webcam, please provide the required "
        "permissions and access.</li><li><!--block-->To know the results, please contact the administrator.</li>"
        "<li><!--block-->To refer to the FAQ document, you can click on the HELP button which is present in the "
        "top right corner of the test environment.</li></ol><div><!--block-->Best wishes from Performance "
        "testing(DoSelect)!</div>"
    ),
    "intellisense": False,
    "interview_avatar": None,
    "interview_voice_template": None,
    "is_active": False,
    "is_contest_published": None,
    "is_having_next_phase": None,
    "is_live": True,
    "is_locked": False,
    "is_test_created_for_phase": None,
    "is_timed_section": False,
    "level": "EAS",
    "max_invite_reset": 0,
    "max_score": None,
    "mode": "TIM",
    "name": "Test Automation 2",
    "phase_id": None,
    "phase_order": None,
    "problem_section_map": {
        "bbmwy": "b3e8ebeebd7e4c81b93c6b8782db42f6",
        "m5b0e": "0e20087ee81744459b9a317704b875b0",
    },
    "public_access_password": None,
    "public_access_slug": None,
    "redirection_url": None,
    "section_count": 1,
    "section_history": {
        "0e20087ee81744459b9a317704b875b0": {"name": "Section 2", "sample": 1},
        "b3e8ebeebd7e4c81b93c6b8782db42f6": {"name": "Section 11", "sample": 1},
        "d687378d0ddc450ea7f210556642fa98": {"name": "Section 3", "sample": 0},
    },
    "settings": {
        "cache_flow_enabled": True,
        "display": {"problem_names": False, "section_names": True},
        "fullstack_ide": {"disable_download_workspace": False, "disable_upload_workspace": False},
        "hacker_extra_data": {"custom_data": {"enabled": False, "fields": []}, "profile_data": False},
        "invite_email": {
            "email_body": (
                '<h2><span style="color: rgb(63, 81, 181);">Hello {candidate_name},</span></h2><p>Please read '
                "through the below instructions and attempt the test. We will get back to you post your "
                "assessment completion and review.</p>"
            ),
            "subject": "DoSelect Test Assessment's Invitation to Test Automation",
        },
        "invites": {
            "allowed_email_domains": [],
            "expiry": {"date": "", "days": 365, "enabled": True},
            "message": "",
        },
        "mcq_option_shuffle": False,
        "plagiarism": {"enabled": False, "match_merging": False, "model": "jplag", "threshold": 0.9},
        "proctor": {
            "browser_tolerance": {"count": -1, "enabled": False, "warning": False},
            "compare": {"fingerprint": {"flag": 1, "max": 0}, "navigation": {"flag": 3, "max": 10}},
            "enabled": False,
            "snapshot": False,
            "video": {"enabled": False},
        },
        "reminders": {"days_after_creation": 3, "days_before_expiry": 1, "enabled": False},
        "reports": {
            "admin_emails": [],
            "answer_section": False,
            "confirmation": {"enabled": False, "message": ""},
            "correct_answer": False,
            "hide_report_summary": False,
            "send_to_candidate": False,
        },
        "secure_browser": {"enabled": True},
        "support": {"email": "", "phone": ""},
        "treat_as_contest": False,
        "user_permissions": {},
    },
    "stage": None,
    "start_time": None,
    "status": "DRA",
    "sub_test_type": "NRL",
    "system_settings": {
        "SCR": ["1621", "1697", "1698", "1677", "1694"],
        "SCR_v2": {"percentage": 0},
        "batch_proctoring": [
            118567, 118238, 118571, 118570, 130034, 130039, 128620, 130043, 130037, 128624, 129427, 128627,
            129432, 130042, 132829, 130041, 129433, 130038, 129431, 132830, 129430, 132823, 130040, 130036,
            130035, 132828, 128626, 129426, 132826, 129453,
        ],
        "batch_proctoring_scaling": {"ab": True, "percentage": 10},
        "cache_flow_test_slugs": [
            "goom3", "wmr83", "yey08", "ebwgw", "wmlwa", "xx54x", "mbq9l", "5red3", "6olgo", "3e64v", "vobvm",
            "86xbl", "x68xr",
        ],
        "cache_problem_data": {
            "owner_ids": [8571, 14069],
            "test_ids": [
                90819, 90919, 90137, 90200, 89999, 90151, 90803, 90032, 90766, 90142, 90786, 90023, 90916,
                90021, 90152, 90250,
            ],
        },
        "direct_pdf": {},
        "disabled_test_project_slugs": ["nov6db", "wl3rrm", "nopqqy", "bpgrry"],
        "doiq_company_slugs": ["doselect_performance_testing", "doselect_doiq"],
        "dynamo_db_in_invite_flow": {
            "dynamo_db_deprecated": False,
            "read_from_dynamo_db": True,
            "write_to_dynamo_db": True,
        },
        "gateway_infra_scaler": [16012],
        "generic_infra_scaler": {"backend_enabled": True, "frontend_enabled": True},
        "hide_admin_pdf_report": {"slugs": ["aptech_staging", "aptech", "aptech_university", "aptech_lcms_staging"]},
        "plagiarism_config": {
            "enabled": True,
            "match_merging": False,
            "model": "jplag",
            "threshold": 0.9,
            "threshold_pb": 0.65,
        },
        "prescaling_config": {
            "asg_configuration": {
                "advanced_engine_api": "do-proctor-engine-api-asg",
                "advanced_external_api": "do-proctor-external-api-asg",
                "central_internal_api": "do-central-internal-api-asg",
                "engine_api": "do-proctor-engine-api-asg",
                "external_api": "do-proctor-external-api-asg",
                "fn_api": "api_server",
                "fn_web": "do-fnweb-asg",
                "hackathon": "do-hackathon-service-asg",
                "reporting_service": "reporting_service_asg",
                "standard_engine_api": "do-proctor-engine-api-asg",
                "standard_external_api": "do-proctor-external-api-asg",
                "web": "do-webservers-asg",
                "websocket": "do-websocket-asg",
                "yoda_eval": "yoda-eval",
                "yoda_eval_large": "yoda-eval-large-asg",
            },
            "min_max_configuration": {
                "advanced_engine_api": {"MAX": 10, "MIN": 1},
                "advanced_external_api": {"MAX": 120, "MIN": 3},
                "central_internal_api": {"MAX": 10, "MIN": 2},
                "engine_api": {"MAX": 10, "MIN": 1},
                "external_api": {"MAX": 120, "MIN": 3},
                "fn_api": {"MAX": 40, "MIN": 3},
                "fn_web": {"MAX": 40, "MIN": 3},
                "hackathon": {"MAX": 10, "MIN": 2},
                "reporting_service": {"MAX": 10, "MIN": 2},
                "standard_engine_api": {"MAX": 10, "MIN": 1},
                "standard_external_api": {"MAX": 120, "MIN": 3},
                "web": {"MAX": 40, "MIN": 4},
                "websocket": {"MAX": 40, "MIN": 3},
                "yoda_eval": {"MAX": 300, "MIN": 4},
                "yoda_eval_large": {"MAX": 120, "MIN": 0},
            },
            "scaling_criteria": {
                "MAX_SCALABLE_INVITES": 50000,
                "advanced_engine_api": 200,
                "advanced_external_api": 28,
                "central_internal_api": 500,
                "contest_web_factor": 0.15,
                "engine_api": 200,
                "external_api": 28,
                "factor": 0.4,
                "fn_api": 100,
                "fn_web": 100,
                "hackathon": 200,
                "standard_engine_api": 200,
                "standard_external_api": 350,
                "web": 100,
                "websocket_short_type": 500,
                "websocket_yoda": 250,
                "yoda_eval": 6,
                "yoda_eval_large": 300,
            },
            "scaling_flow_type": {
                "ADVANCED_PROCTORING": 500,
                "ENABLE_ADVANCED_PROCTORING": 2000,
                "ENABLE_STANDARD_PROCTORING": 15000,
                "SCR": 100000,
                "SCR_CACHE": 100000,
                "SHORT_TYPE": 100000,
                "SHORT_TYPE_CACHE": 100000,
                "STANDARD_PROCTORING": 1000,
            },
        },
        "proctor_prefix_mod_value": 5,
        "proctor_system_time_mismatch": {},
        "proctoring": {
            "ab": True,
            "allowed_embed_companies": ["staging_cocreate", "carelon", "edubridge"],
            "batch_count_image": 10,
            "batch_count_video": 50,
            "feedback": True,
            "percentage": 100,
        },
        "project_based_compilation_alert": {
            "fetch_solution_for_last_n_hours": 6,
            "ignore_logs_with_strings": [
                "Task :compileJava FAILED", "COMPILATION ERROR :", "Build FAILED.", "Component Failures [",
                "SyntaxError:", "ImportError:", "IndentationError:", "ReferenceError", "TypeError",
                "Error: listen EADDRINUSE", "Error in render", "Error: Adjacent JSX elements must be wrapped",
                "Template parse errors", "Cannot find module", "Can't resolve", "Module not found",
                "Cannot find name", "AttributeError:", "NameError:", "No tests to run",
            ],
            "teams_webhook_url": (
                "https://infoedge.webhook.office.com/webhookb2/e59cee00-8982-4ce4-a921-d2b4cd8677d9@"
                "0ee9b5f9-52b3-4351-8198-c4804cd66b68/IncomingWebhook/b966d0c9b1554d4c9bd7d60a952be1b6/"
                "16b900ba-d10d-442d-8fb8-8a1d1a533d04/V2G9Akg2lpc8bFt3yj_iVhju3ibb-mrgzhHnsW3QR_jGE1"
            ),
        },
        "project_based_problems_settings": {"merge_candidate_results_with_default_testcases": True},
        "short_type": [
            130034, 130039, 128620, 130043, 130037, 128624, 129427, 128627, 129432, 130042, 132829, 130041,
            129433, 130038, 129431, 132830, 129430, 132823, 130040, 130036, 130035, 132828, 128626, 129426,
            132826,
        ],
        "sqs_scaling_consumer_rate": {"event-analysis": "4"},
        "tss_deletion_configured": {},
        "uix_compilation_alert": {
            "fetch_solution_for_last_n_hours": 6,
            "ignore_logs_with_strings": ["\\d+ failing", "Test Suites: \\d+ failed"],
            "teams_webhook_url": (
                "https://infoedge.webhook.office.com/webhookb2/e59cee00-8982-4ce4-a921-d2b4cd8677d9@"
                "0ee9b5f9-52b3-4351-8198-c4804cd66b68/IncomingWebhook/b966d0c9b1554d4c9bd7d60a952be1b6/"
                "16b900ba-d10d-442d-8fb8-8a1d1a533d04/V2G9Akg2lpc8bFt3yj_iVhju3ibb-mrgzhHnsW3QR_jGE1"
            ),
        },
        "yoda_mysql": {"percentage": "0"},
        "yoda_scaling_consumer_rate": {
            "dba-eval": "0.12",
            "dba-eval-new": "0.4",
            "dba-interactive": "0.12",
            "dba-interactive-new": "0.4",
            "mli-eval": "0.4",
            "mssql-eval-new": "0.4",
            "mssql-interactive-new": "0.4",
            "oracle-eval-new": "0.4",
            "oracle-interactive-new": "0.4",
            "scr-eval": "0.4",
            "scr-interactive": "0.4",
            "uix-eval": "0.4",
        },
    },
    "tags": [],
    "technologies": [],
    "test_type": "GEN",
    "test_type_verbose": "assessment",
    "total_test_score": 0,
    "visibility": [],
}


# ---------------------------------------------------------------------------------------------
# post_add_max_retakes.py / post_remove_retakes.py
# ---------------------------------------------------------------------------------------------


def post_add_max_retakes_payload(invite_id, retake_count) -> dict:
    """Mirrors payloads/regression/recruit/post_add_max_retakes.py::post_add_max_retakes_payload."""
    return {"invite_id": invite_id, "num_retakes": retake_count}


def post_remove_retakes_payload(invite_id, retake_count) -> dict:
    """Mirrors payloads/regression/recruit/post_remove_retakes.py::post_remove_retakes_payload."""
    return {"invite_id": invite_id, "num_retakes": retake_count}


# ---------------------------------------------------------------------------------------------
# post_clear_bulk_reminder.py / post_clone_test_payload.py / post_reset_test_solutionset.py
# ---------------------------------------------------------------------------------------------


def post_clear_bulk_reminder_payload() -> dict:
    """Mirrors payloads/regression/recruit/post_clear_bulk_reminder.py::post_clear_bulk_reminder_payload."""
    return {}


def post_clone_test_payload() -> dict:
    """Mirrors payloads/regression/recruit/post_clone_test_payload.py::POST_CLONE_TEST_PAYLOAD."""
    return {}


def post_reset_test_solutionset_payload() -> list:
    """Mirrors payloads/regression/recruit/post_reset_test_solutionset.py::POST_RESET_TEST_SOLUTIONSET_PAYLOAD."""
    return []


# ---------------------------------------------------------------------------------------------
# post_direct_pdf.py
# ---------------------------------------------------------------------------------------------


def post_direct_pdf_payload(test_slug, test_solution_set: list) -> dict:
    """Mirrors payloads/regression/recruit/post_direct_pdf.py::post_direct_pdf_payload."""
    return {"test_slug": test_slug, "test_solution_set": test_solution_set}


# ---------------------------------------------------------------------------------------------
# post_increase_test_duration.py
# ---------------------------------------------------------------------------------------------


def get_increase_test_duration_payload(sections: list, invite_id, duration: int = 1) -> dict:
    """
    Mirrors payloads/regression/recruit/post_increase_test_duration.py::get_increase_test_duration_payload.
    The source calls `len(shared_data.get("sections"))` unguarded — `TypeError` if "sections" was
    never populated in `shared_data` by that point; the ported signature requires `sections`
    explicitly (callers pass `[]` when there's nothing to thread), sidestepping that structurally.
    """
    extend_section_duration = []
    is_section_extend = len(sections) > 1
    payload: dict = {}
    if is_section_extend:
        for section in sections:
            extend_section_duration.append({"section_slug": section.get("slug"), "duration": duration})
        payload = {"is_section_extend": is_section_extend, "extend_section_duration": extend_section_duration}
    payload["invite_ids"] = [invite_id]
    payload["duration_change"] = duration
    return payload


# ---------------------------------------------------------------------------------------------
# send_reminder_payload.py
# ---------------------------------------------------------------------------------------------


def send_reminder_payload(invite_id) -> dict:
    """Mirrors payloads/regression/recruit/send_reminder_payload.py::send_reminder_payload."""
    return {
        "mode": "email",
        "invite_ids": [invite_id],
        "email_body": "Hello, this is a reminder to take the test.",
        "subject": "Reminder to take the test.",
        "secure_browser_enabled": False,
        "shouldProvideCTA": True,
    }
