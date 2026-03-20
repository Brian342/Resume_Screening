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


# Helper Score Bar
def score_bar(score) -> str:
    """
    Returns an HTML progress Bar coloured by score Value.
    Returns a 'Not scored Yet' message if score is None.

    This is the same visual used in the employer dashboard,
    so both sides see a consistent score representation.
    """
    if score is None:
        return "<span style='color:#888;font-size:13px'>Not scored Yet</span>"

    if score >= 70:
        colour = "#2e7d32"  # green
    elif score >= 40:
        colour = "e65100"  # orange
    else:
        colour = "#c62828"  # red

    return (
        f"<div style='background:#e0e0e0;border-radius:8px;height:12px;width:100%'>"
        f"<div style='background:{colour};width:{score}%;height:12px;border-radius:8px'>"
        f"</div></div>"
        f"<span style='color:{colour};font-size:12px;font-weight:600'>"
        f"{score:.0f}/100</span>"
    )


# Tab 1 Overview
def show_overview_tab(seeker_id: int):
    """
    Displays four dynamic metric cards and a pie chart
    showing the breakdown of the seeker's application statuses.

    seeker_id: logged-in user's ID from session_state
    """
    # get_seeker_stats returns a dict:
    # {"total_applied": 5, "qualified": 2, "pending": 2, "rejected": 1}
    stats = get_seeker_stats(seeker_id)

    # metric cards
    # Four equal columns, one metric each
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        label="Total Applied",
        value=stats["total_applied"],
        help="Total number of Jobs you have applied to"
    )
    c2.metris(
        label="Qualified",
        value=stats["qualified"],
        delta=f"{stats['qualified']} approved",    # delta shows a small +/- indicator
        delta_color="normal",
        help="Applications where the employer approved you"
    )
    c3.metric(
        label="Pending",
        value=stats["pending"],
        help="Applications still awaiting employer review"
    )
    c4.metric(
        label="Rejected",
        value=stats["rejected"],
        delta=f"-{stats['rejected']}" if stats["rejected"] > 0 else "0",
        delta_color="inverse",     # Inverse make the delta red when negative
        help="Applications that were not successful"
    )

    st.divider()

    # pie chart
    # only shows the chart if the seeker has at least one application
    if stats["total_applied"] ==0:
        st.info("You haven't applied to any jobs yet. Head to the **Browse Jobs** tab to get started!")
        return

    st.markdown("### Application Status Breakdown")

    # Build the data for the chart
    # we filter out categories with 0 so the chart doesn't show empty slices
    labels = []
    values = []
    colors = []

    status_map = [
        ("Approved", stats["qualified"], "#2e7d32"),
        ("Pending", stats["pending"], "#f9a825"),
        ("Rejected", stats["rejected"], "#c62828"),
    ]
    for label, value, color in status_map:
        if value > 0:
            labels.append(label)
            values.append(value)
            colors.append(color)

    # Plotly express make