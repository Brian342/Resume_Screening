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

