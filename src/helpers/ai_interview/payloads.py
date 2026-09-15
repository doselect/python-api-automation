"""
Ports payloads/regression/aiinterview/*.py from https://github.com/doselect/do-api-automation.git.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pytz


def _get_next_quarter_hour(dt: datetime) -> datetime:
    """Mirrors get_next_quarter_hour(dt) (both bulk-invite and single-invite payload modules)."""
    minute = (dt.minute // 15 + 1) * 15
    if minute == 60:
        dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        dt = dt.replace(minute=minute, second=0, microsecond=0)
    return dt


def get_bulk_invite_payload(
    slug: str,
    email_list: list,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    send_email_notification: bool = True,
) -> dict:
    """Mirrors payloads/regression/aiinterview/post_bulk_invite_no_cv.py::get_bulk_invite_payload."""
    if start_date is None or start_time is None:
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)
        rounded_time = _get_next_quarter_hour(now_ist)

        calculated_start_time = rounded_time + timedelta(minutes=15)
        calculated_end_time = calculated_start_time + timedelta(minutes=15)

        if start_date is None:
            start_date = calculated_start_time.strftime("%Y-%m-%d")
        if end_date is None:
            end_date = start_date
        if start_time is None:
            start_time = calculated_start_time.strftime("%H:%M")
        if end_time is None:
            end_time = calculated_end_time.strftime("%H:%M")
    else:
        if end_date is None:
            end_date = start_date

    return {
        "email_list": email_list,
        "start_date": start_date,
        "end_date": end_date,
        "start_time": start_time,
        "end_time": end_time,
        "context": "ai-interview",
        "slug": slug,
        "send_email_notification": send_email_notification,
    }


def post_jd_data_payload() -> dict:
    """Mirrors payloads/regression/aiinterview/post_jd_data.py::post_jd_data_payload."""
    return {
        "preset": "p",
        "input": (
            "Job Title: Software Development Engineer in Test (SDET)  Experience: 2–4 Years Location: [Specify City / Remote] Employment Type: Full-Time  About the Role  "
            "We are looking for a skilled Software Development Engineer in Test (SDET) with 3 years of experience in designing, developing, and executing automated test solutions. "
            "The ideal candidate has strong coding skills, a solid understanding of QA methodologies, and hands-on experience with automation frameworks and CI/CD pipelines.  "
            "Key Responsibilities  Design, develop, and maintain automated test frameworks for web, API, and backend services.  Collaborate with developers, product managers, and QA engineers to define test strategies and ensure comprehensive coverage.  "
            "Develop and execute functional, regression, integration, and performance tests.  Implement test automation in CI/CD pipelines (e.g., Jenkins, GitHub Actions, GitLab CI).  "
            "Identify, document, and track bugs and defects, collaborating closely with the development team for resolutions.  Contribute to code reviews, ensuring quality and reliability in both product and test code.  "
            "Perform API testing using tools like Postman, REST Assured, or requests (Python).  Work with containerized environments (Docker, Kubernetes) and cloud platforms (AWS, GCP, or Azure) for scalable testing.  "
            "Required Skills  Programming: Proficiency in one or more — Python, Java, or JavaScript.  Automation Frameworks: Experience with Pytest, Selenium, Playwright, Cypress, or TestNG.  "
            "API Testing: Hands-on experience with REST API automation using tools/libraries like requests, RestAssured, or Postman.  Version Control: Experience with Git / GitHub / GitLab.  "
            "Build Tools: Maven, Gradle, or similar.  CI/CD: Experience integrating tests in Jenkins, GitHub Actions, or GitLab CI.  Databases: Basic SQL knowledge for data validation.  "
            "Defect Tracking: Experience with JIRA or similar tools.  Good to Have  Experience with Allure reporting, pytest-html, or similar reporting tools.  "
            "Familiarity with performance testing (e.g., JMeter, Locust).  Exposure to microservices and API contract testing (e.g., Pact).  "
            "Knowledge of Docker/Kubernetes and test execution in containerized environments.  Basic understanding of security and load testing.  "
            "Soft Skills  Strong problem-solving and analytical mindset.  Excellent collaboration and communication skills.  Ownership mentality and attention to detail.  "
            "Ability to work independently and in a team-driven agile environment.  Sample Job Title Variants  SDET / QA Automation Engineer  Software Engineer in Test  Test Automation Engineer"
        ),
    }


def get_invite_payload(candidate_email: str) -> dict:
    """
    Mirrors payloads/regression/aiinterview/post_single_invite_no_cv.py::get_invite_payload.

    `cv_collection_type` was "Ask candidate for CV" — wrong for this no-cv flow, and it makes the
    backend 400 with `'is_cv_questions_enabled'` (a KeyError for a field this payload never sends;
    verified live against PLT). "No CV Required" is what the no-cv flow actually needs and returns
    201.
    """
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    rounded_time = _get_next_quarter_hour(now_ist)
    start_time = rounded_time + timedelta(minutes=15)
    if start_time <= now_ist:
        start_time = now_ist + timedelta(days=1, minutes=15)
        start_time = _get_next_quarter_hour(start_time)
    end_time = start_time + timedelta(hours=2)
    time_format = "%B %d,%Y, %H:%M"

    return {
        "preset": "2",
        "summary": {
            "invite_type": "Invite Individually",
            "start_time": start_time.strftime(time_format),
            "end_time": end_time.strftime(time_format),
            "candidate_email": candidate_email,
            "cv_collection_type": "No CV Required",
        },
    }


def ai_interview_jd_extraction_payload(doiq_conversation_response: dict) -> dict:
    """
    Mirrors payloads/regression/aiinterview/create_jd_extraction.py::ai_interview_jd_extraction_payload.
    Takes the raw `/doiq/conversation` JSON response directly (source read it from
    `shared_data["extracted_jd_response"]`) and returns the payload to POST back for the next
    conversation step.
    """
    summary_data = None
    preset_value = None
    for item in doiq_conversation_response.get("result", []):
        if item.get("template") == "interview.edit":
            summary_data = item.get("message", {}).get("content", {}).get("data", {})
            preset_value = item.get("next_preset")
            break

    if not summary_data:
        raise ValueError("Could not find interview summary data in input JSON")

    return {
        "preset": preset_value,
        "summary": {
            "duration": summary_data.get("duration", summary_data.get("default_duration")),
            "role_name": summary_data.get("role_name"),
            "experience": summary_data.get("experience"),
            "good_to_have_skills": summary_data.get("good_to_have_skills"),
            "must_have_skills": summary_data.get("must_have_skills"),
        },
    }
