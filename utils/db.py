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


