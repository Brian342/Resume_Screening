"""
seeker_dashboard.py — Job Seeker Section
=========================================
This file contains ONE function: show_seeker_dashboard()
It is imported and called from app.py inside the main() router.

It has three tabs:
  Tab 1 — Overview        : dynamic stat metrics + a pie chart of application statuses
  Tab 2 — My Applications : list of every job the seeker has applied to with status + score
  Tab 3 — Browse Jobs     : job cards grid — clicking "View & Apply" stores the job in
                            session_state and routes to the apply page

IMPORTS USED:
  db.py — get_seeker_stats, get_applications_by_seeker, get_all_active_jobs, has_applied
  streamlit — all UI components
  plotly — pie chart on the overview tab

INSTALL:
  pip install plotly
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import (
    get_seeker_stats,
    get_applications_by_seeker,
    get_all_active_jobs,
    has_applied
)


# Helper Status Badge
def status_badge(status: str) -> str:
    """
    Returns a coloured HTML pill badge for an application status.
    we use st.markdown(..., unsafe_allow_html=True) to render these.

    Pending -> grey pill
    approved -> green pill
    rejected -> red pill
    """
    colours = {
        "pending": ("#f0f0f0", "#555555"),
        "approved": ("#e6f4ea", "#2e7d32"),
        "rejected": ("#fdecea", "c62828"),
    }
    bg, fg = colours.get(status, ("#f0f0f0", "#555555"))
    label = status.upper()
    return (
        f"<span style='background:{bg};color:{fg};padding:3px 10px;"
        f"border-radius:12px;font-size:12px;font-weight:600'>{label}</span>"
    )

#