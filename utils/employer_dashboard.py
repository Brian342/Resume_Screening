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
    return "#c62828"  # red


# Tab 1 overview
def show_overview_tab(employer_id):
    """
    Shows summary metrics and a list of the employer's job postings.
    employer_id: the logged-in employer's user ID from session_state
    """
    jobs = get_jobs_by_employer(employer_id)

    # Metric cards
    # Count total applicants across all jobs by summing up applications per job
    total_applicants = 0
    pending_count = 0

    for job in jobs:
        apps = get_applications_by_job(job["id"])
        total_applicants += len(apps)
        pending_count += sum(i for a in apps if a["status"] == "pending")

    # st.columns creates a row of equal-width columns
    # st.metric shows a big number with a label - perfect for dashboards
    col1, col2, col3 = st.columns(3)
    col1.metric("Jobs Posted", len(jobs))
    col2.metric("Total Applicants", total_applicants)
    col3.metric("Pending Reviews", pending_count)

    st.divider()

    # Job Listings Table
    st.markdown("### Your Job Listings")

    if not jobs:
        st.info("You haven't posted any jobs yet. Go to the **Post a Job** tab to get started.")

        return
    for job in jobs:
        # st.expander creates a collapsible section
        # The label shows the job title and its active/paused status
        status_badge = "Active" if job["is_active"] else "Paused"
        with st.expander(f"{job['title']} - {job['company']} | {status_badge}"):

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Location:** {job['location']}")
                st.markdown(f"**Salary:** {job['salary'] or 'Not specified'}")
                st.markdown(f"**Posted:** {str(job['created_at'])[:10]}")

                # Count applicants for this specific job
                apps = get_applications_by_job(job["id"])
                st.markdown(f"**Applicants:** {len(apps)}")

            with col2:
                # Toggle active/paused - lets employer hide a job without deleting it
                if job["is_active"]:
                    if st.button("Paused listing", key=f"Pause_{job['id']}"):
                        toggle_job_active(job["id"], 0)
                        st.success("Job Paused.")
                        st.rerun()
                else:
                    if st.button("Re-activate", key=f"active_{job['id']}"):
                        toggle_job_active(job["id"], 1)
                        st.success("Job re-activated.")
                        st.rerun()

# Tab 2 Post A job

