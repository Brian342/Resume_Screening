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

# Global Style
st.markdown("""
    <style>
        /* Hide the default Streamlit top menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
 
        /* Make the main container a bit narrower and centered */
        .block-container {
            padding-top: 2rem;
            max-width: 900px;
        }
 
        /* Style for our custom card-like containers */
        .auth-box {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 2rem;
            border: 1px solid #e0e0e0;
        }
 
        /* Make the role selector pills look nicer */
        div[data-testid="stRadio"] > div {
            flex-direction: row;
            gap: 1rem;
        }
    </style>
""", unsafe_allow_html=True)


# Session State Initialisation
def init_session_state():
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": None,
        "user_email": None,
        "role": None,
        "auth_page": "login"  # starts o the login form by default
    }
