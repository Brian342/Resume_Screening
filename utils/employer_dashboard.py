"""
employer_dashboard.py — Employer Section
=========================================
This file contains ONE function: show_employer_dashboard()
It is imported and called from app.py inside the main() router.

It has three tabs:
  Tab 1 — Overview   : metrics + list of their posted jobs
  Tab 2 — Post a Job : form to create a new job listing
  Tab 3 — Applicants : review applicants, approve or reject, send email

IMPORTS USED:
  db.py functions  — all database reads/writes
  email_utils.py   — sending approval/rejection emails (we build this next)
  streamlit        — all UI components
  json             — to decode the answers stored as JSON in the DB
"""
import streamlit as st
import json
from db import (
    create_job,
    get_jobs_by_employer,
    get_applications_by_job,
    update_application_score,
    toggle_job_active
)

try:
    from email_utils import send_approval_email, send_rejection_email

    EMAIL_READY = True
except ImportError:
    EMAIL_READY = False


# Helper - Score Colour
def score_color(score):
    """
    Returns a colour hex based on the AI score Value.
    Used to colour-code scores in the applicant table.
    Green -> 70 and above (strong Match)
    Orange -> 40 to 69 (possible match)
    Red -> below 40 (weak match)
    """
    if score is None:
        return "#888888"  # grey - not scored yet
    if score >= 70:
        return "#2e7d32"  # green
    if score >= 40:
        return "#e65100"  # orange
    return "#c62828"      # red
