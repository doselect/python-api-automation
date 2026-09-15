"""
Ports payloads/regression/interview/*.py (11 files) from
https://github.com/doselect/do-api-automation.git. `create_join_interview_payload` and
`create_recommend_problem_payload` dropped their unused `shared_data` parameter (the source
functions accepted it but never read it); `upcoming_interview_slug_payload` takes an explicit
`interview_slug` in place of `shared_data.get("interview_slug_upcoming")`.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Optional

from faker import Faker

fake = Faker()


def add_interviewer_payload(full_name: str, email: str) -> dict:
    """Mirrors payloads/regression/interview/add_interviewer.py::add_interviewer_payload."""
    return {
        "full_name": full_name,
        "email": email,
        "member_type": "MEM",
    }


def ask_feedback_payload(review_feedback_message: str = "", interviewer_email: str = "") -> dict:
    """Mirrors payloads/regression/interview/ask_feedback.py::ask_feedback_payload."""
    return {
        "review_feedback_message": review_feedback_message,
        "interviewer_email": interviewer_email,
    }


def create_evaluation_criteria_payload() -> dict:
    """
    Mirrors payloads/regression/interview/create_evaluation_criteria.py::create_evaluation_criteria_payload,
    with a unique suffix appended to `name`. `get_latest_job_role_slug()` reuses whatever job role
    is "latest" in the (shared, persistent) environment rather than creating a fresh one, so a fixed
    name causes the server to reject repeat runs with "Evaluation criteria is already present with
    name: ..." once that role has been tagged once.
    """
    return {
        "name": f"Rating + description {fake.uuid4()[:8]}",
        "type": "rating",
        "sub_types": [],
    }


def create_job_role_payload() -> dict:
    """Mirrors payloads/regression/interview/create_role.py::create_job_role_payload."""
    return {
        "title": "New Jr Interviews",
        "hiring_role": {
            "name": "Back-End Developer",
            "slug": "back-end-developer",
        },
    }


def delete_interviewer_payload(email: str) -> dict:
    """Mirrors payloads/regression/interview/delete_interviewer.py::delete_interviewer_payload."""
    return {"email": email}


def final_status_payload(status: str = "ON_HOLD") -> dict:
    """Mirrors payloads/regression/interview/final_status.py::final_status_payload."""
    return {"status": status}


def interviewer_feedback_payload(
    rating_id: str = "rating57ae2",
    rating_name: str = "Communication Skills",
    rating_type: str = "rating",
    category: str = "default",
    order: int = 1,
    rating: int = 5,
    source: str = "FEEDBACK",
) -> dict:
    """Mirrors payloads/regression/interview/interviewer_feedback.py::interviewer_feedback_payload."""
    return {
        "evaluation_ratings": {
            rating_id: {
                "name": rating_name,
                "type": rating_type,
                "category": category,
                "order": order,
                "rating": rating,
            }
        },
        "source": source,
    }


def create_join_interview_payload() -> dict:
    """Mirrors payloads/regression/interview/join_interview.py::create_join_interview_payload(shared_data)."""
    return {"participant_type": "INTERVIEWER"}


def create_recommend_problem_payload() -> dict:
    """Mirrors payloads/regression/interview/recommend_problem.py::create_recommend_problem_payload."""
    return {}


def create_schedule_interview_payload(
    job_role_name: str = "Software Engineer",
    start_time_offset_minutes: int = 30,
    duration: int = 30,
    timezone: str = "Asia/Kolkata",
    interviewer_list: Optional[list] = None,
) -> dict:
    """Mirrors payloads/regression/interview/schedule_interview.py::create_schedule_interview_payload."""
    # Generate start time and formatted versions
    start_time = datetime.now() + timedelta(minutes=start_time_offset_minutes)
    formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    formatted_display_time = start_time.strftime("%d %b, %I:%M %p")  # ex: 01 Jul, 06:00 PM

    # Generate candidate details
    candidate_name = fake.name()
    candidate_email = f"{candidate_name.lower().replace(' ', '.')}+{random.randint(100, 999)}@example.com"

    # Default interviewer if none provided
    if not interviewer_list:
        interviewer_list = [{"full_name": "Default Interviewer", "email": "default.interviewer@example.com"}]

    payload = {
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "start_time": formatted_start_time,
        "duration": str(duration),
        "timezone": timezone,
        "send_reminder_in": "1",
        "send_email_reminder": "false",
        "email_data[candidate][subject]": f"Interview with {job_role_name} on {formatted_display_time}",
        "email_data[candidate][email_body]": (
            f"You are invited to an interview for the role of {job_role_name} on {formatted_display_time}"
        ),
        "email_data[interviewer][subject]": f"Interview with {candidate_name} is on {formatted_display_time}",
        "email_data[interviewer][email_body]": (
            f"You have been invited to take an interview of {candidate_name} "
            f"for the role of {job_role_name} on {formatted_display_time}"
        ),
    }

    # Add interviewer details dynamically
    for i, interviewer in enumerate(interviewer_list):
        payload[f"invited_interviewers[{i}][full_name]"] = interviewer["full_name"]
        payload[f"invited_interviewers[{i}][email]"] = interviewer["email"]

    return payload


def upcoming_interview_slug_payload(interview_slug: Optional[str] = None) -> dict:
    """Mirrors payloads/regression/interview/upcoming_interview.py::upcoming_interview_slug_payload(shared_data)."""
    return {"slug": [interview_slug]}
