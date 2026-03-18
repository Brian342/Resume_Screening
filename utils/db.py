from datetime import datetime, timedelta
import sqlite3
import json
import os
import time
import random
import string
import smtplib
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_PATH = os.path.join(os.path.dirname(__file__), "Resume_app.db")


# Connection Helper
def get_connection():
    """
    Opens and creates a connection to the sqlite Database.
    check_same_thread = False is required because streamlit runs
    on multiple threads and streamlit would otherwise create more Errors
    detect_types allows us to store and retrieve Python datetime objects
    directly instead of converting them manually.
    """
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )

    #
    #
    conn.row_factory = sqlite3.Row

    return conn


# Table definitions
def create_table():
    """
    Creates all tables if they do not already exist.
    This runs every time the app starts. It is safe to call repeatedly
    because of the IF NOT EXIST Clause.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # user Table-----------------------------------
    # Stores both job seekers and employers in one table
    # The 'Role' column tells us which type of user they are.
    # Passwords are stored as hashed strings (never plain text)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT        NOT NULL,
    emaIl           TEXT        NOT NULL UNIQUE,
    password        TEXT        NOT NULL,
    role            TEXT        NOT NULL CHECK(role IN ('seeker', 'employer')),
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
    )
    """)

    #
