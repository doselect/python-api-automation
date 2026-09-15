"""
Ports payloads/regression/contest/*.py from https://github.com/doselect/do-api-automation.git —
every payload-builder function, mirrored verbatim (same literal values, same field names).

`payloads/regression/contest/make_section_public.py` is an empty file in the source (no function
defined) — nothing to port from it.

`payloads/regression/contest/create_2phase_normal_contest.py` and
`create_2phase_team_contest.py` each end with module-level "example usage" code
(`payload = create_2phase_contest_payload(phase_count=2); print(payload["phases"])`) that runs a
throwaway call and a `print` at *import time*. That's debug/example scaffolding with no effect on
any assertion or return value — dropped here rather than ported (it would otherwise fire on every
`import` of this module).
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

import pytz

# ---------------------------------------------------------------------------------------------
# add_criteria.py
# ---------------------------------------------------------------------------------------------


def add_criteria_payload() -> dict:
    """Mirrors add_criteria.py::add_criteria_payload."""
    return {"criteria": random.randint(0, 100), "criteriaType": "percentage"}


# ---------------------------------------------------------------------------------------------
# add_custom_form.py
# ---------------------------------------------------------------------------------------------


def update_participant_data_settings_payload() -> dict:
    """Mirrors add_custom_form.py::update_participant_data_settings_payload."""
    return {
        "completeDoselectProfilePrompt": False,
        "participantDataSettings": (
            '[{"name":"name11","type":"input","isRequired":true,"options":"","id":"customField_0","isAdded":true},'
            '{"name":"description1","input":"textArea","isRequired":false,"options":"","id":"customField_1","isAdded":true},'
            '{"name":"gender","type":"radioButton","isRequired":false,"options":"F,M","id":"customField_2","isAdded":true}]'
        ),
    }


# ---------------------------------------------------------------------------------------------
# add_only_theme_section.py
# ---------------------------------------------------------------------------------------------


def add_theme_section_payload() -> dict:
    """Mirrors add_only_theme_section.py::add_theme_section_payload."""
    return {
        "landingPageSections": [
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutChallenge",
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
            },
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutUs",
                "value": f"<p>DoSelect is a collaborative, technology-independent hiring platform - {random.randint(1, 9999)}</p>",
            },
            {
                "isPrimary": False,
                "isVisible": True,
                "sectionName": "theme",
                "value": f"<p>Theme Section - {random.randint(1, 9999)}</p>",
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# add_problem.py
# ---------------------------------------------------------------------------------------------


def add_problem_payload(section_slug, context_slug) -> dict:
    """Mirrors add_problem.py::add_problem_payload."""
    return {
        "action": "add",
        "context": "test",
        "context_slug": context_slug,
        "section_slug": section_slug,
    }


# ---------------------------------------------------------------------------------------------
# add_proctor_settings.py
# ---------------------------------------------------------------------------------------------


def proctor_settings_payload(phase_id, proctor_enabled, snapshot_enabled, video_enabled, plagiarism_enabled) -> dict:
    """Mirrors add_proctor_settings.py::proctor_settings_payload."""
    return {
        "phases": [
            {
                "phaseId": phase_id,
                "order": 1,
                "settings": {
                    "proctor": {
                        "browserTolerance": {"count": 2, "warning": False, "enabled": True},
                        "enabled": proctor_enabled,
                        "snapshot": snapshot_enabled,
                        "video": {"enabled": video_enabled},
                    },
                    "plagiarism": {"enabled": plagiarism_enabled},
                },
            }
        ],
        "proctorAndMiscSettings": "phase-wise",
    }


# ---------------------------------------------------------------------------------------------
# add_remove_problem_section.py
# ---------------------------------------------------------------------------------------------

ADD_SECTION_PAYLOAD = {
    "action": "add",
    "test_slug": "",  # Will be populated from shared_data
    "section": {
        "name": f"Contest section - {random.randint(1, 9999)}",
        "duration": 0,
        "shuffle": False,
        "sample": 0,
        "description": "",
        "slug": "",
    },
}


DELETE_SECTION_PAYLOAD = {
    "action": "delete",
    "test_slug": "",
    "section_slug": "",
    "section": {
        "custom_scoring": {"enabled": False, "penalty": 0, "score": 0},
        "description": "",
        "duration": 0,
        "is_timed": False,
        "name": "Section 2",
        "problems": [],
        "sample": 0,
        "shuffle": False,
        "slug": "",
        "isExpanded": True,
    },
}


# ---------------------------------------------------------------------------------------------
# add_remove_redirection_url.py
# ---------------------------------------------------------------------------------------------


def add_redirection_url_payload(phase_id) -> dict:
    """Mirrors add_remove_redirection_url.py::add_redirection_url_payload."""
    return {"phases": [{"phaseId": phase_id, "order": 1, "redirectionUrl": "https://doselect.com/"}]}


def remove_redirection_url_payload(phase_id) -> dict:
    """Mirrors add_remove_redirection_url.py::remove_redirection_url_payload."""
    return {"phases": [{"phaseId": phase_id, "order": 1, "redirectionUrl": ""}]}


# ---------------------------------------------------------------------------------------------
# add_support_details.py
# ---------------------------------------------------------------------------------------------


def add_email_and_phone_number_payload(show_contact) -> dict:
    """Mirrors add_support_details.py::add_email_and_phone_number_payload."""
    return {"contactEmails": "a@doselect.com", "contactPhoneNumbers": "0987654321", "showContact": show_contact}


def add_only_email_payload(show_contact) -> dict:
    """Mirrors add_support_details.py::add_only_email_payload."""
    return {"contactEmails": "a@doselect.com", "contactPhoneNumbers": "", "showContact": show_contact}


def add_only_phone_number_payload(show_contact) -> dict:
    """Mirrors add_support_details.py::add_only_phone_number_payload."""
    return {"contactEmails": "", "contactPhoneNumbers": "0987654321", "showContact": show_contact}


# ---------------------------------------------------------------------------------------------
# add_three_section_theme_prize_and_eligibiliy_criteria_section.py
# ---------------------------------------------------------------------------------------------


def add_three_section_theme_prize_and_eligibility_criteria_section_payload() -> dict:
    """Mirrors add_three_section_theme_prize_and_eligibiliy_criteria_section.py's payload builder."""
    return {
        "landingPageSections": [
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutChallenge",
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
            },
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutUs",
                "value": f"<p>DoSelect is a collaborative, technology-independent hiring platform - {random.randint(1, 9999)}</p>",
            },
            {
                "sectionName": "theme",
                "isVisible": True,
                "value": f"<p>Theme Section - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
            {
                "sectionName": "prizes",
                "isVisible": True,
                "value": f"<p>Prize Section - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
            {
                "sectionName": "eligibilityCriteria",
                "isVisible": True,
                "value": f"<p>Eligibility Criteria - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# add_two_section_theme_and_prize_section.py
# ---------------------------------------------------------------------------------------------


def add_two_section_theme_and_prize_section_payload() -> dict:
    """Mirrors add_two_section_theme_and_prize_section.py::add_two_section_theme_and_prize_section_payload."""
    return {
        "landingPageSections": [
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutChallenge",
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
            },
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutUs",
                "value": f"<p>DoSelect is a collaborative, technology-independent hiring platform - {random.randint(1, 9999)}</p>",
            },
            {
                "sectionName": "theme",
                "isVisible": True,
                "value": f"<p>Theme Section - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
            {
                "sectionName": "prizes",
                "isVisible": True,
                "value": f"<p>Prize Section - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# archive_contest.py
# ---------------------------------------------------------------------------------------------


def archive_contest_payload() -> dict:
    """Mirrors archive_contest.py::archive_contest_payload."""
    return {"isArchived": True}


# ---------------------------------------------------------------------------------------------
# clone_contest.py
# ---------------------------------------------------------------------------------------------


def clone_contest_payload(contest_id) -> dict:
    """Mirrors clone_contest.py::clone_contest_payload."""
    return {
        "contestId": contest_id,
        "phases": [
            {
                "sectionCount": 0,
                "maxScore": 0,
                "settings": {
                    "proctor": {
                        "browserTolerance": {"count": -1, "warning": False, "enabled": False},
                        "compare": {"navigation": {"max": 10, "flag": 3}, "fingerprint": {"max": 0, "flag": 1}},
                        "enabled": False,
                        "snapshot": False,
                        "video": {"enabled": False},
                    },
                    "secureBrowser": {"enabled": False},
                    "plagiarism": {"enabled": False},
                    "support": {"phone": "", "email": ""},
                    "reminders": {"daysBeforeExpiry": 1, "enabled": False, "daysAfterCreation": 3},
                    "reports": {
                        "answerSection": False,
                        "confirmation": {"message": "", "enabled": False},
                        "sendToCandidate": False,
                        "adminEmails": [],
                        "hideReportSummary": True,
                        "correctAnswer": False,
                    },
                    "display": {"sectionNames": True, "problemNames": False},
                    "fullstackIde": {"disableUploadWorkspace": False, "disableDownloadWorkspace": False},
                },
                "redirectionUrl": None,
                "totalQuestions": 0,
                "sections": [
                    {
                        "description": "",
                        "problems": [],
                        "isTimed": False,
                        "duration": 0,
                        "sample": 0,
                        "slug": "e02c1f83de444c1887311351478a6608",
                        "customScoring": {"penalty": 0, "enabled": False, "score": 0},
                        "name": "Section 1",
                        "shuffle": False,
                    }
                ],
                "createDate": "2025-09-11 07:34:16",
                "lastModifiedDate": "2025-09-11 07:34:16",
                "isLocked": False,
                "isStarted": False,
                "isEnded": False,
                "criteria": 40,
                "order": 1,
                "phaseName": "",
                "instructions": (
                    "<ol>\n  <li><!--block-->This is an online contest.</li>\n  <li><!--block-->Please make sure "
                    "that you are using the latest version of the browser. We recommend using Google Chrome.</li>\n  "
                    "<li><!--block-->It's mandatory to disable all the browser extensions and enabled Add-ons or "
                    "open the contest in incognito mode.</li>\n  <li><!--block-->If you are solving a coding "
                    "problem, you will either be required to choose a programming language from the options that "
                    "have been enabled by the administrator or choose your preferred programming language in case "
                    "no options have been enabled by the administrator. <strong>Note:</strong> In case you're "
                    "solving coding problems: All inputs are from STDIN and output to STDOUT.</li>\n  "
                    "<li><!--block-->If contest mandates you to use the webcam, please provide the required "
                    "permissions and access.</li>\n  <li><!--block-->To know the results, please contact the "
                    "administrator.</li>\n  <li><!--block-->To refer to the FAQ document, you can click on the "
                    "HELP button which is present in the top right corner of the contest environment.</li>\n</ol>"
                ),
                "criteriaType": "percentage",
                "phaseStartTime": "2025-09-11 13:09:14",
                "phaseEndTime": "2025-09-11 13:19:14",
                "phaseReminderWebhookSent": False,
                "phaseEvaluatedWebhookSent": False,
                "testSlug": "y3nb1",
                "isEvaluationDoneForShortlistCriteria": None,
            }
        ],
        "isPublished": False,
        "contestType": "hiring_challenge",
        "contestName": "Clone-Contest Automation - 4442",
        "contestVersion": "v2",
        "phaseCount": 1,
        "timezone": "Asia/Kolkata",
        "accessType": "invite_only",
        "contactEmails": "",
        "contactPhoneNumbers": None,
        "tags": [],
        "sendReportToParticipant": False,
        "sendContestEndNote": False,
        "registrationEndTime": "2025-09-11 13:14:14",
        "registrationStartTime": "2025-09-11 13:04:14",
        "contestEndNote": None,
        "isLocked": False,
        "isArchived": False,
        "showContact": True,
        "completeDoselectProfilePrompt": False,
        "minTeamSize": 0,
        "maxTeamSize": 0,
        "maxScore": 0,
        "instructions": None,
        "redirectUrl": None,
        "administrators": None,
        "participantDataSettings": None,
        "landingPageSections": [
            {"sectionName": "aboutChallenge", "isVisible": True, "value": "", "isPrimary": True},
            {
                "sectionName": "aboutUs",
                "isVisible": True,
                "value": "DoSelect is a collaborative, technology-independent hiring platform",
                "isPrimary": True,
            },
        ],
        "backgroundImageUrl": None,
        "contestBannerUrl": None,
        "participationType": "individual",
    }


# ---------------------------------------------------------------------------------------------
# create_2phase_normal_contest.py / create_2phase_team_contest.py
# ---------------------------------------------------------------------------------------------

_ist_timezone = pytz.timezone("Asia/Kolkata")
_registration_start_time = datetime.now(_ist_timezone)
_registration_end_time = _registration_start_time + timedelta(minutes=10)


def _generate_phases(phase_count: int = 2, phase_duration_minutes: int = 10) -> list:
    """
    Mirrors create_2phase_normal_contest.py/create_2phase_team_contest.py's (duplicated)
    generate_phases(phase_count, phase_duration_minutes): first phase starts 5 minutes after
    registration start, each subsequent phase starts 24 hours after the previous phase ends.
    """
    phases = []
    phase_start_time = _registration_start_time + timedelta(minutes=5)
    for i in range(phase_count):
        phase_end_time = phase_start_time + timedelta(minutes=phase_duration_minutes)
        phases.append(
            {
                "phaseStartTime": phase_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "phaseEndTime": phase_end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "order": i + 1,
            }
        )
        phase_start_time = phase_end_time + timedelta(hours=24)
    return phases


def create_2phase_contest_payload(phase_count: int = 2) -> dict:
    """Mirrors create_2phase_normal_contest.py::create_2phase_contest_payload."""
    phases = _generate_phases(phase_count)
    return {
        "contestName": f"Contest Automation - {random.randint(1, 9999)}",
        "timezone": "Asia/Kolkata",
        "phaseCount": str(phase_count),
        "accessType": "invite_only",
        "phases": phases,
        "registrationStartTime": _registration_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "registrationEndTime": _registration_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "redirectUrl": None,
        "participationType": "individual",
        "minTeamSize": 0,
        "maxTeamSize": 0,
        "contestType": "hiring_challenge",
    }


def create_2phase_team_contest_payload(phase_count: int = 2) -> dict:
    """Mirrors create_2phase_team_contest.py::create_2phase_team_contest_payload."""
    phases = _generate_phases(phase_count)
    return {
        "contestName": f"Contest Automation - {random.randint(1, 9999)}",
        "timezone": "Asia/Kolkata",
        "phaseCount": str(phase_count),
        "accessType": "invite_only",
        "phases": phases,
        "registrationStartTime": _registration_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "registrationEndTime": _registration_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "redirectUrl": None,
        "participationType": "team",
        "minTeamSize": 1,
        "maxTeamSize": 2,
        "contestType": "hiring_challenge",
    }


# ---------------------------------------------------------------------------------------------
# create_contest.py / create_team_contest.py
# ---------------------------------------------------------------------------------------------

_phase_start_time = _registration_start_time + timedelta(minutes=5)
_phase_end_time = _phase_start_time + timedelta(minutes=10)


def create_contest_payload() -> dict:
    """Mirrors create_contest.py::create_contest_payload."""
    return {
        "contestName": f"Contest Automation - {random.randint(1, 9999)}",
        "timezone": "Asia/Kolkata",
        "phaseCount": "1",
        "accessType": "invite_only",
        "phases": [
            {
                "phaseStartTime": _phase_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "phaseEndTime": _phase_end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "order": 1,
            }
        ],
        "registrationStartTime": _registration_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "registrationEndTime": _registration_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "redirectUrl": None,
        "participationType": "individual",
        "minTeamSize": 0,
        "maxTeamSize": 0,
        "contestType": "hiring_challenge",
    }


def create_team_contest_payload() -> dict:
    """Mirrors create_team_contest.py::create_team_contest_payload."""
    return {
        "contestName": f"Contest Automation - {random.randint(1, 9999)}",
        "timezone": "Asia/Kolkata",
        "phaseCount": "1",
        "accessType": "invite_only",
        "phases": [
            {
                "phaseStartTime": _phase_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "phaseEndTime": _phase_end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "order": 1,
            }
        ],
        "registrationStartTime": _registration_start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "registrationEndTime": _registration_end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "redirectUrl": None,
        "participationType": "team",
        "minTeamSize": 1,
        "maxTeamSize": 2,
        "contestType": "hiring_challenge",
    }


# ---------------------------------------------------------------------------------------------
# delete_custom_form.py
# ---------------------------------------------------------------------------------------------


def delete_custom_form_payload() -> dict:
    """Mirrors delete_custom_form.py::delete_custom_form_payload."""
    return {
        "completeDoselectProfilePrompt": False,
        "participantDataSettings": (
            '[{"name":"name11","type":"input","isRequired":true,"options":"","id":"customField_0","isAdded":true}]'
        ),
    }


# ---------------------------------------------------------------------------------------------
# make_prize_and_eligibility_section_private.py
# ---------------------------------------------------------------------------------------------


def make_section_private_payload() -> dict:
    """Mirrors make_prize_and_eligibility_section_private.py::make_section_private_payload."""
    return {
        "landingPageSections": [
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutChallenge",
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
            },
            {
                "sectionName": "aboutUs",
                "isVisible": True,
                "value": f"<p>About Us - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
            {
                "sectionName": "theme",
                "isVisible": True,
                "value": f"<p>Theme Section - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
            {
                "sectionName": "prizes",
                "isVisible": False,
                "value": f"<p>Prize Section - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
            {
                "sectionName": "eligibilityCriteria",
                "isVisible": False,
                "value": f"<p>Eligibility Criteria - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# mcq_shuffle.py
# ---------------------------------------------------------------------------------------------


def mcq_shuffle_payload(phase_id, mcq_option_shuffle) -> dict:
    """Mirrors mcq_shuffle.py::mcq_shuffle_payload."""
    return {"phases": [{"phaseId": phase_id, "settings": {"mcqOptionShuffle": mcq_option_shuffle}}]}


# ---------------------------------------------------------------------------------------------
# publish_contest.py
# ---------------------------------------------------------------------------------------------


def publish_contest_payload() -> dict:
    """Mirrors publish_contest.py::publish_contest_payload."""
    return {"isPublished": True}


# ---------------------------------------------------------------------------------------------
# quesion_name_visibility.py
# ---------------------------------------------------------------------------------------------


def hide_question_name_payload(phase_id, problem_visibility) -> dict:
    """Mirrors quesion_name_visibility.py::hide_question_name_payload."""
    return {"phases": [{"phaseId": phase_id, "settings": {"display": {"problemNames": problem_visibility}}}]}


# ---------------------------------------------------------------------------------------------
# remove_only_prize_section.py
# ---------------------------------------------------------------------------------------------


def remove_only_prize_section_payload() -> dict:
    """Mirrors remove_only_prize_section.py::remove_only_prize_section_payload."""
    return {
        "landingPageSections": [
            {
                "sectionName": "aboutChallenge",
                "isVisible": True,
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
            {
                "sectionName": "aboutUs",
                "isVisible": True,
                "value": f"<p>About Us - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
            {
                "isPrimary": False,
                "isVisible": True,
                "sectionName": "theme",
                "value": f"<p>Theme Section - {random.randint(1, 9999)}</p>",
            },
            {
                "sectionName": "eligibilityCriteria",
                "isVisible": True,
                "value": f"<p>Eligibility Criteria - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# remove_three_section_theme_prize_eligibility_section.py
# ---------------------------------------------------------------------------------------------


def remove_three_section_theme_prize_eligibility_section_payload() -> dict:
    """Mirrors remove_three_section_theme_prize_eligibility_section.py's payload builder."""
    return {
        "landingPageSections": [
            {
                "sectionName": "aboutChallenge",
                "isVisible": True,
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
            {
                "sectionName": "aboutUs",
                "isVisible": True,
                "value": f"<p>About Us - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# remove_two_section_theme_and_eligibility_section.py
# ---------------------------------------------------------------------------------------------


def remove_two_section_theme_and_eligibility_section_payload() -> dict:
    """Mirrors remove_two_section_theme_and_eligibility_section.py's payload builder."""
    return {
        "landingPageSections": [
            {
                "sectionName": "aboutChallenge",
                "isVisible": True,
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
            {
                "sectionName": "aboutUs",
                "isVisible": True,
                "value": f"<p>About Us - {random.randint(1, 9999)}</p>",
                "isPrimary": True,
            },
            {
                "sectionName": "prizes",
                "isVisible": True,
                "value": f"<p>Prizes - {random.randint(1, 9999)}</p>",
                "isPrimary": False,
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# section_name_visibility.py
# ---------------------------------------------------------------------------------------------


def section_name_payload(phase_id, section_visibility) -> dict:
    """Mirrors section_name_visibility.py::section_name_payload."""
    return {"phases": [{"phaseId": phase_id, "settings": {"display": {"sectionNames": section_visibility}}}]}


# ---------------------------------------------------------------------------------------------
# update_about_us_about_contest.py
# ---------------------------------------------------------------------------------------------


def update_contest_payload() -> dict:
    """Mirrors update_about_us_about_contest.py::update_contest_payload."""
    return {
        "landingPageSections": [
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutChallenge",
                "value": f"<p>About Challenge - {random.randint(1, 9999)}</p>",
            },
            {
                "isPrimary": True,
                "isVisible": True,
                "sectionName": "aboutUs",
                "value": f"<p>DoSelect is a collaborative, technology-independent hiring platform - {random.randint(1, 9999)}</p>",
            },
        ]
    }


# ---------------------------------------------------------------------------------------------
# update_access_type.py
# ---------------------------------------------------------------------------------------------


def update_access_type_payload(access_type) -> dict:
    """Mirrors update_access_type.py::update_access_type_payload."""
    return {"accessType": access_type}


# ---------------------------------------------------------------------------------------------
# update_contest_instruction.py
# ---------------------------------------------------------------------------------------------


def update_contest_instruction_payload() -> dict:
    """Mirrors update_contest_instruction.py::update_contest_instruction_payload."""
    return {"instructions": f"Update contest instruction - {random.randint(1, 9999)}"}


# ---------------------------------------------------------------------------------------------
# update_contest_name.py
# ---------------------------------------------------------------------------------------------


def update_contest_name_payload() -> dict:
    """Mirrors update_contest_name.py::update_contest_name_payload."""
    return {"contestName": f"Update contest - {random.randint(1, 9999)}"}


# ---------------------------------------------------------------------------------------------
# update_contest_type.py
# ---------------------------------------------------------------------------------------------


def update_contest_type_payload(contest_type) -> dict:
    """Mirrors update_contest_type.py::update_contest_type_payload."""
    return {"contestType": contest_type}


# ---------------------------------------------------------------------------------------------
# update_participation_type.py
# ---------------------------------------------------------------------------------------------


def update_participation_type_payload(participation_type, min_team_size, max_team_size) -> dict:
    """Mirrors update_participation_type.py::update_participation_type_payload."""
    if participation_type == "individual":
        return {"participationType": "individual"}
    return {
        "participationType": participation_type,
        "minTeamSize": min_team_size,
        "maxTeamSize": max_team_size,
    }
