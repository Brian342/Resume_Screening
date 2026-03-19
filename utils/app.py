"""
app.py — Entry Point for the Resume Screening System
=====================================================
This is the FIRST file Streamlit runs when you start the app.
It handles:
  1. Session state setup — remembering who is logged in
  2. Login page — verify email + password
  3. Signup page — register as seeker or employer
  4. Routing — send user to the right dashboard

HOW it WORKS:
  Streamlit re-runs this ENTIRE script from top to bottom every time
  the user clicks a button or types something. This is why we use
  st.session_state — it persists data between this re-runs.

  Session_state is like a backpack the user carries around.
  Once they log in, we put their info in the backpack so every page
  can read it without asking the database again.

RUN THE APP:
  streamlit run app.py

INSTALL REQUIREMENTS FIRST:
  pip installs streamlit bcrypt
"""

import streamlit as st
import bcrypt
from db import get_user_by_email, create_user

# Page Configuration
st.set_page_config(
    page_title="Pioneer Insurance Group Job Match",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

