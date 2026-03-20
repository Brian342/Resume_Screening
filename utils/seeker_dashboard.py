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
