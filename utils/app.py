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
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# Password Helpers
def hash_password(plain_password: str) -> str:
    """Hashes a plain-text password using bcrypt. Returns a string."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")  # Store as String in SQLite


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Returns True if plain_password matches the stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# Login Logic
def do_login(email: str, password: str):
    """
    Looks up the user by email, verifies their password,
    and populates session_state if correct.

    This function is called when the login button is clicked.
    it does Not Display anything - it only updates state.
    The UI re-runs after this and shows the dashboard.
    """

    user = get_user_by_email(email.strip().lower())

    if user in None:
        return False, "No account found with that email."

    if not verify_password(password, user["password"]):
        return False, "Incorrect password."

    # Credentials are correct - populate session state
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["user_name"] = user["full_name"]
    st.session_state["user_email"] = user["email"]
    st.session_state["role"] = user["role"]

    return True, "Login successful."


# Signup Logic

def do_signup(full_name: str, email: str, password: str, role: str):
    """
    Validates Inputs and creates a new user account.

    Returns (success: bool, message: str)
    """
    # Basic Validation - never trust user input
    if not full_name.strip():
        return False, "Please enter your full name."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    hashed = hash_password(password)
    success = create_user(
        full_name=full_name.strip(),
        email=email.strip().lower(),
        password_hash=hashed,
        role=role
    )

    if not success:
        return False, "An account with that email already exists."

    return True, "Account Created: Please Log In."


# LogOut
def do_logout():
    """
    Clears all session states and returns users to the login screen.
    Called when the user clicks the Logout button in the sidebar
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()  # Re-set defaults so the app doesn't break
    st.rerun()  # Force the page to reload immediately


# Login Page UI
def show_login_page():
    """Renders the Login Form."""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🧳 JobMatch")
        st.markdown("##### Pioneer Insurance Group Job Match Platform")
        st.divider()

        st.markdown("### Sign in to your account")

        # st.text_input returns whatever the user typed as a string
        email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        # type="password" hides the characters as the user types

        # st.button returns True only on the frame the user clicks it
        if st.button("Log in", use_container_width=True, type="primary"):
            if not email or not password:
                st.warning("Please fill in all fields!!")
            else:
                success, message = do_login(email, password)
                if success:
                    st.success(message)
                    st.rerun() # Re-run the script - now logged_in=True, shows dashboard

                else:
                    st.error(message)
