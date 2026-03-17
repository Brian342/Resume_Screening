import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
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

# ==================== EMAIL CONFIGURATION ====================
GMAIL_ENABLED = True
GMAIL_USER = "saolinashipae@gmail.com"
GMAIL_APP_PASSWORD = "gtjn fgdp fmdm heih"

# Page config
st.set_page_config(page_title="CREDIT CARD FRAUD DETECTION", layout="wide", initial_sidebar_state="expanded")

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

    * { font-family: 'Sora', sans-serif; }

    /* ---- LOGIN PAGE ---- */
    .login-wrapper {
        max-width: 480px;
        margin: 4rem auto;
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 20px;
        padding: 3rem 2.5rem;
        box-shadow: 0 30px 60px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.08);
        text-align: center;
    }
    .login-logo {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    .login-title {
        font-family: 'Space Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: #e0e0ff;
        letter-spacing: 0.1rem;
        margin-bottom: 0.25rem;
    }
    .login-sub {
        font-size: 0.85rem;
        color: #8888aa;
        margin-bottom: 2rem;
        letter-spacing: 0.05rem;
    }
    .role-card {
        display: inline-block;
        padding: 0.6rem 1.4rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .role-admin {
        background: linear-gradient(90deg, #7f5af0, #6b46e0);
        color: white;
    }
    .role-cardholder {
        background: linear-gradient(90deg, #2cb67d, #20a67a);
        color: white;
    }

    /* ---- MAIN APP ---- */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        font-family: 'Space Mono', monospace;
    }
    .fraud-alert {
        background-color: #ff4444;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        animation: pulse 2s infinite;
    }
    .safe-alert {
        background-color: #00C851;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
    }
    .otp-alert {
        background-color: #ff9800;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
    }
    .blocked-alert {
        background-color: #d32f2f;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        border: 3px solid #b71c1c;
    }
    .location-info {
        background-color: #2196F3;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .otp-box {
        background-color: #f5f5f5;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #ff9800;
        text-align: center;
        margin: 1rem 0;
    }
    .otp-code {
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 0.5rem;
        color: #ff9800;
        font-family: 'Space Mono', monospace;
    }
    .email-config-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .admin-badge {
        background: linear-gradient(135deg, #7f5af0, #6b46e0);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .cardholder-badge {
        background: linear-gradient(135deg, #2cb67d, #20a67a);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== EMAIL SENDING FUNCTION ====================

def send_otp_email(to_email, otp_code, transaction_details, anomalies):
    if not GMAIL_ENABLED:
        print(f"🔶 DEMO MODE: OTP would be sent to {to_email}")
        print(f"🔶 OTP Code: {otp_code}")
        return True

    try:
        app_password = GMAIL_APP_PASSWORD.replace(" ", "")
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Fraud Detection Team <{GMAIL_USER}>"
        msg['To'] = to_email
        msg['Subject'] = '🔐 Transaction Verification Required'

        card_last_4 = transaction_details['cc_num'][-4:]

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: white; border: 3px solid #ff9800; border-radius: 10px;
                            padding: 30px; text-align: center; margin: 25px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .otp-code {{ font-size: 42px; font-weight: bold; letter-spacing: 12px;
                             color: #ff9800; font-family: 'Courier New', monospace; margin: 10px 0; }}
                .details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                           border-left: 4px solid #667eea; }}
                .details h3 {{ margin-top: 0; color: #667eea; }}
                .detail-item {{ margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                .detail-item:last-child {{ border-bottom: none; }}
                .anomaly {{ background: #fff3cd; padding: 12px; margin: 8px 0;
                           border-left: 4px solid #ff9800; border-radius: 4px; }}
                .warning {{ background: #ff4444; color: white; padding: 20px;
                           border-radius: 8px; margin: 20px 0; text-align: center; }}
                .footer {{ text-align: center; color: #666; font-size: 13px; margin-top: 30px;
                          padding-top: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Transaction Verification</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Security Alert</p>
                </div>
                <div class="content">
                    <p style="font-size: 16px; margin-bottom: 20px;">Dear Customer,</p>
                    <p style="font-size: 15px;">We detected unusual activity on your card ending in <strong>****{card_last_4}</strong>.</p>
                    <div class="details">
                        <h3>📋 Transaction Details</h3>
                        <div class="detail-item"><strong>💰 Amount:</strong> KES {transaction_details['amount']:,.2f}</div>
                        <div class="detail-item"><strong>🏪 Merchant:</strong> {transaction_details['merchant']}</div>
                        <div class="detail-item"><strong>📍 Location:</strong> {transaction_details['location']}</div>
                        <div class="detail-item"><strong>🕐 Time:</strong> {transaction_details['timestamp'].strftime('%B %d, %Y at %I:%M %p')}</div>
                    </div>
                    <h3 style="color: #ff9800; margin-top: 25px;">⚠️ Anomalies Detected:</h3>
                    {''.join([f'<div class="anomaly"><strong>•</strong> {anomaly}</div>' for anomaly in anomalies])}
                    <p style="margin-top: 25px; font-size: 16px;"><strong>If this was you, verify using the code below:</strong></p>
                    <div class="otp-box">
                        <p style="margin: 0; color: #666; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">Your Verification Code</p>
                        <div class="otp-code">{otp_code}</div>
                        <p style="margin: 10px 0 0 0; color: #999; font-size: 14px;">⏱️ Valid for 10 minutes</p>
                    </div>
                    <div class="warning">
                        <h3 style="margin: 0 0 10px 0;">⚠️ Did NOT authorize this?</h3>
                        <p style="margin: 0; font-size: 15px;">Contact us immediately:</p>
                        <p style="margin: 10px 0 0 0;"><strong>📞 Phone:</strong> +254-XXX-XXXX<br><strong>📧 Email:</strong> support@yourbank.com</p>
                    </div>
                    <div class="footer">
                        <p>• Never share your OTP with anyone, including bank staff</p>
                        <p>• If you didn't request this, contact us now</p>
                        <p style="color: #999;">This is an automated security message</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
TRANSACTION VERIFICATION REQUIRED
Card ending in ****{card_last_4}
Amount: KES {transaction_details['amount']:,.2f}
Merchant: {transaction_details['merchant']}
Location: {transaction_details['location']}
Time: {transaction_details['timestamp'].strftime('%Y-%m-%d %I:%M %p')}

Your OTP: {otp_code}
Valid for 10 minutes.

If you did not authorize this, call +254-XXX-XXXX immediately.
        """

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, app_password)
        server.send_message(msg)
        server.quit()
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail Authentication Failed!")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


# ==================== DATABASE ====================

class FraudDatabase:
    """Manages persistent storage with OTP support and user auth"""

    def __init__(self, db_name="fraud_detection_otp.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cc_num TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                merchant TEXT,
                category TEXT,
                amount REAL,
                latitude REAL,
                longitude REAL,
                location_name TEXT,
                risk_score REAL,
                is_fraud INTEGER,
                hour INTEGER,
                day_of_week INTEGER,
                transaction_status TEXT DEFAULT 'approved',
                otp_sent INTEGER DEFAULT 0,
                otp_verified INTEGER DEFAULT 0,
                otp_code TEXT,
                otp_expires_at DATETIME,
                anomaly_types TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Card profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_profiles (
                cc_num TEXT PRIMARY KEY,
                user_email TEXT,
                email_verified INTEGER DEFAULT 0,
                phone_number TEXT,
                first_transaction DATETIME,
                last_transaction DATETIME,
                total_transactions INTEGER,
                total_amount REAL,
                avg_amount REAL,
                max_amount REAL,
                min_amount REAL,
                fraud_count INTEGER,
                legitimate_count INTEGER,
                common_categories TEXT,
                common_locations TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # OTP logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otp_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                cc_num TEXT,
                otp_code TEXT,
                sent_at DATETIME,
                expires_at DATETIME,
                verified_at DATETIME,
                attempts INTEGER DEFAULT 0,
                status TEXT DEFAULT 'sent',
                email_sent_to TEXT,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
            )
        ''')

        # ==================== USER ACCOUNTS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'cardholder')),
                email TEXT,
                full_name TEXT,
                cc_num TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')

        # Seed default admin account (admin / admin123)
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, 'admin', 'System Administrator', 'admin@frauddetect.com')
        ''', ('admin', self.hash_password('admin123')))

        # Indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cc_num ON transactions(cc_num)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON transactions(transaction_status)')

        conn.commit()
        conn.close()

    # ==================== AUTH METHODS ====================

    def register_user(self, username, password, role, email, full_name, cc_num=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email, full_name, cc_num)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, self.hash_password(password), role, email, full_name, cc_num))
            conn.commit()
            # If cardholder with cc_num, save email to card profiles too
            if role == 'cardholder' and cc_num and email:
                conn.close()
                self.save_email(cc_num, email)
                return True, "Registration successful!"
            conn.close()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Username already exists. Please choose a different username."
        except Exception as e:
            conn.close()
            return False, f"Registration failed: {e}"

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, role, email, full_name, cc_num
            FROM users WHERE username = ? AND password_hash = ?
        ''', (username, self.hash_password(password)))
        result = cursor.fetchone()
        if result:
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE username = ?',
                           (datetime.now().isoformat(), username))
            conn.commit()
        conn.close()
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'role': result[2],
                'email': result[3],
                'full_name': result[4],
                'cc_num': result[5]
            }
        return None

    def get_all_users(self):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT id, username, role, email, full_name, cc_num, created_at, last_login FROM users ORDER BY created_at DESC', conn)
        conn.close()
        return df

    # ==================== TRANSACTION METHODS ====================

    def save_transaction(self, transaction_data):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO transactions
            (cc_num, timestamp, merchant, category, amount, latitude, longitude,
             location_name, risk_score, is_fraud, hour, day_of_week,
             transaction_status, otp_sent, otp_verified, otp_code, otp_expires_at, anomaly_types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_data['cc_num'],
            transaction_data['timestamp'],
            transaction_data['merchant'],
            transaction_data['category'],
            transaction_data['amount'],
            transaction_data['latitude'],
            transaction_data['longitude'],
            transaction_data['location_name'],
            transaction_data.get('risk_score', 0),
            transaction_data.get('is_fraud', 0),
            transaction_data['hour'],
            transaction_data['day_of_week'],
            transaction_data.get('transaction_status', 'approved'),
            transaction_data.get('otp_sent', 0),
            transaction_data.get('otp_verified', 0),
            transaction_data.get('otp_code'),
            transaction_data.get('otp_expires_at'),
            transaction_data.get('anomaly_types')
        ))

        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.update_card_profile(transaction_data['cc_num'])
        return transaction_id

    def update_transaction_status(self, transaction_id, status, otp_verified=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET transaction_status = ?, otp_verified = ?
            WHERE id = ?
        ''', (status, 1 if otp_verified else 0, transaction_id))
        conn.commit()
        conn.close()

    def save_otp_log(self, otp_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO otp_logs
            (transaction_id, cc_num, otp_code, sent_at, expires_at, email_sent_to, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            otp_data['transaction_id'],
            otp_data['cc_num'],
            otp_data['otp_code'],
            otp_data['sent_at'],
            otp_data['expires_at'],
            otp_data['email'],
            'sent'
        ))
        conn.commit()
        conn.close()

    def verify_otp(self, transaction_id, entered_otp):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT otp_code, otp_expires_at FROM transactions WHERE id = ?
        ''', (transaction_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False, "Transaction not found"

        stored_otp, expires_at = result

        if datetime.now() > datetime.fromisoformat(expires_at):
            conn.close()
            return False, "OTP expired"

        if str(entered_otp) == str(stored_otp):
            cursor.execute('''
                UPDATE otp_logs
                SET verified_at = ?, status = 'verified'
                WHERE transaction_id = ?
            ''', (datetime.now().isoformat(), transaction_id))
            conn.commit()
            conn.close()
            return True, "OTP verified successfully"
        else:
            cursor.execute('''
                UPDATE otp_logs SET attempts = attempts + 1 WHERE transaction_id = ?
            ''', (transaction_id,))
            conn.commit()
            conn.close()
            return False, "Invalid OTP code"

    def get_card_history(self, cc_num, limit=None):
        conn = self.get_connection()
        query = 'SELECT * FROM transactions WHERE cc_num = ? ORDER BY timestamp DESC'
        if limit:
            query += f' LIMIT {limit}'
        df = pd.read_sql_query(query, conn, params=(cc_num,))
        conn.close()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def get_card_profile(self, cc_num):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM card_profiles WHERE cc_num = ?', (cc_num,))
        result = cursor.fetchone()
        conn.close()
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        return None

    def save_email(self, cc_num, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO card_profiles (cc_num, user_email, email_verified)
            VALUES (?, ?, 0)
            ON CONFLICT(cc_num) DO UPDATE SET
                user_email = excluded.user_email,
                updated_at = CURRENT_TIMESTAMP
        ''', (cc_num, email))
        conn.commit()
        conn.close()

    def update_card_profile(self, cc_num):
        try:
            history_df = self.get_card_history(cc_num)
            if history_df.empty:
                return

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT user_email FROM card_profiles WHERE cc_num = ?', (cc_num,))
            existing = cursor.fetchone()
            existing_email = existing[0] if existing else None

            stats = {
                'cc_num': cc_num,
                'user_email': existing_email,
                'first_transaction': str(history_df['timestamp'].min()),
                'last_transaction': str(history_df['timestamp'].max()),
                'total_transactions': len(history_df),
                'total_amount': float(history_df['amount'].sum()),
                'avg_amount': float(history_df['amount'].mean()),
                'max_amount': float(history_df['amount'].max()),
                'min_amount': float(history_df['amount'].min()),
                'fraud_count': int(history_df['is_fraud'].sum()),
                'legitimate_count': int((history_df['is_fraud'] == 0).sum()),
                'common_categories': json.dumps(history_df['category'].value_counts().head(5).to_dict()),
                'common_locations': json.dumps(history_df['location_name'].value_counts().head(5).to_dict())
            }

            cursor.execute('''
                INSERT INTO card_profiles
                (cc_num, user_email, first_transaction, last_transaction, total_transactions,
                 total_amount, avg_amount, max_amount, min_amount, fraud_count,
                 legitimate_count, common_categories, common_locations, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(cc_num) DO UPDATE SET
                    last_transaction = excluded.last_transaction,
                    total_transactions = excluded.total_transactions,
                    total_amount = excluded.total_amount,
                    avg_amount = excluded.avg_amount,
                    max_amount = excluded.max_amount,
                    min_amount = excluded.min_amount,
                    fraud_count = excluded.fraud_count,
                    legitimate_count = excluded.legitimate_count,
                    common_categories = excluded.common_categories,
                    common_locations = excluded.common_locations,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                stats['cc_num'], stats['user_email'], stats['first_transaction'],
                stats['last_transaction'], stats['total_transactions'], stats['total_amount'],
                stats['avg_amount'], stats['max_amount'], stats['min_amount'],
                stats['fraud_count'], stats['legitimate_count'],
                stats['common_categories'], stats['common_locations']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating card profile: {e}")


# Initialize database
@st.cache_resource
def get_database():
    return FraudDatabase()

db = get_database()


# ==================== GEOCODING ====================

@st.cache_resource
def get_geocoder():
    return Nominatim(user_agent="fraud_detection_otp_v1")

def geocode_location(location_name, attempt=0, max_attempts=3):
    if not location_name or location_name.strip() == "":
        return None, None, None
    try:
        geocoder = get_geocoder()
        location = geocoder.geocode(location_name, timeout=10)
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None
    except GeocoderTimedOut:
        if attempt < max_attempts:
            time.sleep(1)
            return geocode_location(location_name, attempt + 1, max_attempts)
        return None, None, None
    except Exception:
        return None, None, None


# ==================== HELPER FUNCTIONS ====================

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def mask_email(email):
    if not email or '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 3:
        masked_local = local[0] + '***'
    else:
        masked_local = local[0] + '***' + local[-1]
    return f"{masked_local}@{domain}"

def haversine(lat1, lon1, lat2, lon2):
    try:
        return geodesic((lat1, lon1), (lat2, lon2)).km
    except:
        return 0

def is_holiday_season():
    month = datetime.now().month
    return month in [11, 12]


# ==================== ANOMALY DETECTION ====================

def detect_anomalies(cc_num, amount, lat, lon, location_name, category, timestamp, history_df, profile):
    anomalies = []
    risk_score = 0

    if history_df.empty or not profile:
        return {'action': 'APPROVE', 'anomalies': [], 'risk_score': 0, 'reasons': ['First transaction for this card']}

    avg_amount = profile['avg_amount']
    max_amount = profile['max_amount']
    common_locations = json.loads(profile['common_locations'])
    common_categories = json.loads(profile['common_categories'])

    # 1. Amount anomaly
    if amount > (avg_amount * 3):
        anomalies.append({'type': 'amount', 'severity': 'high',
                          'description': f'Amount KES{amount:,.2f} is {amount/avg_amount:.1f}x higher than normal (KES{avg_amount:,.2f})'})
        risk_score += 30

    # 2. Distance / impossible travel
    last_trans = history_df.iloc[0]
    time_diff_minutes = abs((timestamp - last_trans['timestamp']).total_seconds() / 60)

    if time_diff_minutes > 0 and last_trans['latitude'] and last_trans['longitude']:
        distance = haversine(last_trans['latitude'], last_trans['longitude'], lat, lon)
        required_speed_kmh = (distance / time_diff_minutes) * 60

        if required_speed_kmh > 900 and distance > 50:
            return {
                'action': 'BLOCK',
                'anomalies': [{'type': 'impossible_travel', 'severity': 'critical',
                               'description': f'Impossible travel: {distance:.0f} km in {time_diff_minutes:.0f} minutes (requires {required_speed_kmh:.0f} km/h)'}],
                'risk_score': 100,
                'reasons': ['Physical impossibility detected - card likely stolen']
            }

    # 3. Location anomaly
    is_new_location = location_name not in common_locations
    if is_new_location and amount > (avg_amount * 3):
        anomalies.append({'type': 'location_amount', 'severity': 'high',
                          'description': f'New location ({location_name}) with high amount (KES{amount:,.2f})'})
        risk_score += 25
    elif is_new_location:
        anomalies.append({'type': 'location', 'severity': 'medium',
                          'description': f'Transaction from new location: {location_name}'})
        risk_score += 10

    # 4. Category anomaly
    is_new_category = category not in common_categories
    if is_new_category and amount > 10000:
        anomalies.append({'type': 'category_amount', 'severity': 'high',
                          'description': f'First time using {category} category with amount > KES10,000'})
        risk_score += 20
    elif is_new_category and amount > 5000:
        anomalies.append({'type': 'category', 'severity': 'medium',
                          'description': f'First transaction in {category} category'})
        risk_score += 10

    # 5. Time anomaly
    hour = timestamp.hour
    if (0 <= hour <= 4) and len(anomalies) > 0:
        anomalies.append({'type': 'time_supporting', 'severity': 'medium',
                          'description': f'Transaction at unusual hour ({hour}:00)'})
        risk_score += 15

    # 6. Velocity anomaly
    one_hour_ago = timestamp - timedelta(hours=1)
    recent_transactions = history_df[history_df['timestamp'] >= one_hour_ago]
    transaction_count = len(recent_transactions) + 1
    velocity_threshold = 10 if is_holiday_season() else 5

    if transaction_count >= velocity_threshold:
        season_note = " (Black Friday/Holiday season)" if is_holiday_season() else ""
        anomalies.append({'type': 'velocity', 'severity': 'high',
                          'description': f'{transaction_count} transactions in 1 hour{season_note}'})
        risk_score += 20

    if len(anomalies) > 0:
        action = 'SEND_OTP'
        reasons = [a['description'] for a in anomalies]
    else:
        action = 'APPROVE'
        reasons = ['All patterns normal for this card']

    return {'action': action, 'anomalies': anomalies, 'risk_score': min(risk_score, 100), 'reasons': reasons}


# ==================== UI HELPERS ====================

def create_risk_gauge(risk_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fraud Risk Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': '#00C851'},
                {'range': [30, 60], 'color': '#ffbb33'},
                {'range': [60, 100], 'color': '#ff4444'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
        }
    ))
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
    return fig

def create_transaction_timeline(history_df):
    if history_df.empty:
        return None
    colors = ['red' if fraud else 'green' for fraud in history_df['is_fraud']]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['timestamp'], y=history_df['amount'],
        mode='markers+lines',
        marker=dict(size=10, color=colors),
        text=history_df['merchant'],
        hovertemplate='<b>%{text}</b><br>Amount: KES%{y:.2f}<br>%{x}<extra></extra>'
    ))
    fig.update_layout(title="Transaction History Timeline",
                      xaxis_title="Time", yaxis_title="Amount (KES)", height=400)
    return fig


# ==================== SESSION STATE INIT ====================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'auth_page' not in st.session_state:
    st.session_state.auth_page = 'login'   # 'login' | 'register'


# ==================== LOGIN / REGISTER PAGE ====================

def render_auth_page():
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 0.5rem 0;">
        <div style="font-size:3.5rem;">🛡️</div>
        <div style="font-family:'Space Mono',monospace; font-size:1.6rem; font-weight:700;
                    background: linear-gradient(90deg,#667eea,#764ba2);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            FRAUD DETECTION SYSTEM
        </div>
        <div style="color:#888; font-size:0.9rem; margin-top:0.3rem; letter-spacing:0.05rem;">
            Secure · Real-time · Intelligent
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])

    with col_c:
        # Tab switcher between Login and Register
        page = st.session_state.auth_page

        tab_login, tab_register = st.tabs(["🔐  Sign In", "📝  Register"])

        # ---- LOGIN TAB ----
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔐 Sign In", use_container_width=True, type="primary", key="btn_login"):
                if username and password:
                    user = db.login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background: linear-gradient(135deg,#1a1a2e,#16213e); border-radius:10px;
                        padding:1rem 1.2rem; border:1px solid rgba(102,126,234,0.3); font-size:0.82rem; color:#aaa;">
                <b style="color:#667eea;">🔑 Default Admin Account</b><br>
                Username: <code style="color:#e0e0ff;">admin</code> &nbsp;|&nbsp;
                Password: <code style="color:#e0e0ff;">admin123</code>
            </div>
            """, unsafe_allow_html=True)

        # ---- REGISTER TAB ----
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)

            role = st.selectbox("Register as", ["Cardholder", "Admin"], key="reg_role")

            col1, col2 = st.columns(2)
            with col1:
                reg_username = st.text_input("Username *", key="reg_username", placeholder="Choose a username")
                reg_password = st.text_input("Password *", type="password", key="reg_password", placeholder="Min 6 characters")
            with col2:
                reg_fullname = st.text_input("Full Name *", key="reg_fullname", placeholder="Your full name")
                reg_email = st.text_input("Email Address *", key="reg_email", placeholder="your@email.com")

            reg_cc = None
            if role == "Cardholder":
                reg_cc = st.text_input("Credit Card Number *", key="reg_cc",
                                       placeholder="e.g. 4532-1234-5678-9010",
                                       help="This links your account to your card for OTP and transaction history")

            confirm_password = st.text_input("Confirm Password *", type="password", key="reg_confirm", placeholder="Repeat password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 Create Account", use_container_width=True, type="primary", key="btn_register"):
                # Validation
                errors = []
                if not reg_username or len(reg_username) < 3:
                    errors.append("Username must be at least 3 characters.")
                if not reg_password or len(reg_password) < 6:
                    errors.append("Password must be at least 6 characters.")
                if reg_password != confirm_password:
                    errors.append("Passwords do not match.")
                if not reg_email or '@' not in reg_email:
                    errors.append("Valid email address required.")
                if not reg_fullname:
                    errors.append("Full name is required.")
                if role == "Cardholder" and not reg_cc:
                    errors.append("Credit card number is required for Cardholder registration.")

                if errors:
                    for e in errors:
                        st.error(f"❌ {e}")
                else:
                    success, msg = db.register_user(
                        username=reg_username,
                        password=reg_password,
                        role=role.lower(),
                        email=reg_email,
                        full_name=reg_fullname,
                        cc_num=reg_cc if role == "Cardholder" else None
                    )
                    if success:
                        st.success(f"✅ {msg} You can now sign in.")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")


# ==================== SIDEBAR (when logged in) ====================

def render_sidebar():
    user = st.session_state.user
    with st.sidebar:
        # User info
        badge_class = "admin-badge" if user['role'] == 'admin' else "cardholder-badge"
        role_label = "👑 Admin" if user['role'] == 'admin' else "💳 Cardholder"
        st.markdown(f'<div class="{badge_class}">{role_label}</div>', unsafe_allow_html=True)
        st.markdown(f"**{user['full_name']}**")
        st.caption(f"@{user['username']}")
        if user.get('email'):
            st.caption(f"📧 {mask_email(user['email'])}")
        if user['role'] == 'cardholder' and user.get('cc_num'):
            st.caption(f"💳 ···· {user['cc_num'][-4:]}")

        st.divider()

        # Email status
        st.markdown("### 📧 Email Status")
        if GMAIL_ENABLED:
            st.success("✅ Gmail Enabled")
            st.info(f"📤 Sending from:\n{GMAIL_USER}")
        else:
            st.warning("⚠️ Demo Mode")
            st.info("OTP shown on screen\n(not sent to email)")

        st.divider()

        # DB stats (admin only)
        if user['role'] == 'admin':
            st.markdown("### 💾 Database Status")
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DISTINCT cc_num) FROM card_profiles')
            total_cards = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM transactions')
            total_transactions = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM transactions WHERE otp_sent = 1')
            otp_sent_count = cursor.fetchone()[0]
            conn.close()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cards", total_cards)
                st.metric("OTP Sent", otp_sent_count)
            with col2:
                st.metric("Transactions", total_transactions)
                if total_transactions > 0:
                    st.metric("OTP Rate", f"{otp_sent_count/total_transactions*100:.1f}%")

            st.divider()
            st.markdown("### ⚙️ Settings")
            if st.button("🗑️ Clear Database", use_container_width=True):
                if st.session_state.get('confirm_clear', False):
                    if os.path.exists("fraud_detection_otp.db"):
                        os.remove("fraud_detection_otp.db")
                    st.cache_resource.clear()
                    st.success("Database cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm")

        st.divider()

        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()


# ==================== CARDHOLDER VIEW ====================

def render_cardholder_view():
    user = st.session_state.user
    cc_num = user.get('cc_num', '')
    user_email = user.get('email', '')

    st.markdown('<div class="main-header">💳 My Card Portal</div>', unsafe_allow_html=True)

    if not GMAIL_ENABLED:
        st.markdown("""
        <div class="email-config-box">
            <h3 style="margin-top:0;">⚠️ Gmail Not Configured — Running in Demo Mode</h3>
            <p>OTP codes will be displayed on screen instead of being sent to your email.</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔍 Analyze Transaction", "📊 My Card History"])

    # ---- TAB 1: ANALYZE TRANSACTION ----
    with tab1:
        st.header("🔍 Analyze New Transaction")
        st.info("📌 **How it works:** Anomalies trigger OTP verification. Impossible travel is blocked immediately.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💳 Card & Transaction Info")

            # Card number — locked to the registered card
            if cc_num:
                st.success(f"💳 Card: ···· {cc_num[-4:]}  |  📧 {mask_email(user_email)}")
                active_cc = cc_num
            else:
                active_cc = st.text_input("Credit Card Number", placeholder="e.g. 4532-1234-5678-9010")
                if not user_email or '@' not in user_email:
                    user_email = st.text_input("📧 Email for OTP", placeholder="your@email.com")

            merchant = st.text_input("Merchant Name", "SuperMart Kenya")
            category = st.selectbox("Category", [
                "Groceries", "Gas Station", "Restaurant", "Online Shopping",
                "Electronics", "Travel", "Entertainment", "Jewelry", "Other"
            ])
            amt = st.number_input("Amount (KES)", 0.0, value=500.0, step=50.0)

        with col2:
            st.subheader("📍 Location & Time")
            method = st.radio("Location Entry", ["🌍 Auto-detect", "📌 Manual"], horizontal=True)

            if method == "🌍 Auto-detect":
                location_name = st.text_input("Location Name", "Nairobi, Kenya")
                if st.button("🔍 Find Coordinates"):
                    with st.spinner("Locating..."):
                        lat, lon, addr = geocode_location(location_name)
                        if lat:
                            st.session_state.trans_lat = lat
                            st.session_state.trans_lon = lon
                            st.session_state.trans_addr = addr
                            st.success(f"✅ {addr}")
                if hasattr(st.session_state, 'trans_lat'):
                    lat = st.session_state.trans_lat
                    lon = st.session_state.trans_lon
                    location_name = st.session_state.trans_addr
                else:
                    lat, lon = 0.0, 0.0
            else:
                location_name = st.text_input("Location Name", "Custom Location")
                lat = st.number_input("Latitude", format="%.6f", value=-1.286389)
                lon = st.number_input("Longitude", format="%.6f", value=36.817223)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                trans_date = st.date_input("Date", datetime.now())
            with col_t2:
                trans_time = st.time_input("Time", datetime.now().time())
            timestamp = datetime.combine(trans_date, trans_time)

        st.divider()

        if st.button("🔍 ANALYZE TRANSACTION", type="primary", use_container_width=True):
            if lat == 0.0 and lon == 0.0:
                st.warning("⚠️ Please find coordinates first!")
            elif not user_email or '@' not in user_email:
                st.error("❌ Valid email required for OTP verification!")
            elif not active_cc:
                st.error("❌ Please enter your card number.")
            else:
                st.divider()
                st.header("📊 Analysis Results")

                history_df = db.get_card_history(active_cc)
                profile = db.get_card_profile(active_cc)

                result = detect_anomalies(active_cc, amt, lat, lon, location_name, category, timestamp, history_df, profile)
                action = result['action']
                anomalies = result['anomalies']
                risk_score = result['risk_score']
                reasons = result['reasons']

                col_g1, col_g2 = st.columns([1, 2])
                with col_g1:
                    if action == 'BLOCK':
                        st.markdown('<div class="blocked-alert">🚫 BLOCKED</div>', unsafe_allow_html=True)
                    elif action == 'SEND_OTP':
                        st.markdown('<div class="otp-alert">📧 OTP REQUIRED</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="safe-alert">✅ APPROVED</div>', unsafe_allow_html=True)
                with col_g2:
                    st.plotly_chart(create_risk_gauge(risk_score), use_container_width=True)

                st.divider()

                if action == 'BLOCK':
                    st.error("### 🚫 Transaction Blocked — Impossible Travel Detected")
                    st.write("This transaction was blocked automatically due to physical impossibility.")
                    for reason in reasons:
                        st.error(f"• {reason}")
                    st.warning("Please contact your bank immediately if this wasn't you.")

                    transaction_data = {
                        'cc_num': active_cc, 'timestamp': timestamp, 'merchant': merchant,
                        'category': category, 'amount': amt, 'latitude': lat, 'longitude': lon,
                        'location_name': location_name, 'risk_score': risk_score, 'is_fraud': 1,
                        'hour': timestamp.hour, 'day_of_week': timestamp.weekday(),
                        'transaction_status': 'blocked', 'otp_sent': 0, 'otp_verified': 0,
                        'anomaly_types': json.dumps([a['type'] for a in anomalies])
                    }
                    db.save_transaction(transaction_data)
                    st.info("💾 Blocked transaction has been logged.")

                elif action == 'SEND_OTP':
                    st.warning("### 📧 Verification Required")
                    st.write("Anomalies detected — please verify your identity to proceed:")

                    for anomaly in anomalies:
                        emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(anomaly['severity'], '⚪')
                        st.warning(f"{emoji} **{anomaly['type'].replace('_', ' ').title()}:** {anomaly['description']}")

                    st.divider()

                    otp_code = generate_otp()
                    expires_at = datetime.now() + timedelta(minutes=10)

                    transaction_data = {
                        'cc_num': active_cc, 'timestamp': timestamp, 'merchant': merchant,
                        'category': category, 'amount': amt, 'latitude': lat, 'longitude': lon,
                        'location_name': location_name, 'risk_score': risk_score, 'is_fraud': 0,
                        'hour': timestamp.hour, 'day_of_week': timestamp.weekday(),
                        'transaction_status': 'pending', 'otp_sent': 1, 'otp_verified': 0,
                        'otp_code': otp_code, 'otp_expires_at': expires_at.isoformat(),
                        'anomaly_types': json.dumps([a['type'] for a in anomalies])
                    }
                    transaction_id = db.save_transaction(transaction_data)

                    otp_log_data = {
                        'transaction_id': transaction_id, 'cc_num': active_cc,
                        'otp_code': otp_code, 'sent_at': datetime.now().isoformat(),
                        'expires_at': expires_at.isoformat(), 'email': user_email
                    }
                    db.save_otp_log(otp_log_data)

                    email_sent = send_otp_email(user_email, otp_code, {
                        'cc_num': active_cc, 'amount': amt, 'merchant': merchant,
                        'location': location_name, 'timestamp': timestamp
                    }, reasons)

                    if email_sent:
                        if GMAIL_ENABLED:
                            st.success(f"✅ OTP sent via Gmail to {mask_email(user_email)}")
                            st.info("📬 Check your inbox (may take 1–2 minutes)")
                        else:
                            st.success(f"✅ OTP generated for {mask_email(user_email)}")
                            st.markdown(f"""
                            <div class="otp-box">
                                <p style="margin: 0; color: #666;">🔒 DEMO MODE — Your OTP Code:</p>
                                <p class="otp-code">{otp_code}</p>
                                <p style="margin: 0; font-size: 0.9rem; color: #999;">Expires in 10 minutes</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.info("📝 Enable Gmail to send real emails.")

                        st.divider()
                        st.subheader("🔐 Enter Verification Code")
                        entered_otp = st.text_input("6-Digit Code", max_chars=6, placeholder="000000")

                        if st.button("✅ Verify & Approve Transaction", type="primary"):
                            if entered_otp:
                                is_valid, message = db.verify_otp(transaction_id, entered_otp)
                                if is_valid:
                                    db.update_transaction_status(transaction_id, 'approved', otp_verified=True)
                                    st.success("### ✅ Transaction Approved!")
                                    st.balloons()
                                    st.write(f"**Amount:** KES{amt:,.2f}")
                                    st.write(f"**Merchant:** {merchant}")
                                    st.write(f"**Location:** {location_name}")
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.warning("Please enter the OTP code.")
                    else:
                        st.error("❌ Failed to send OTP. Please check your email configuration.")

                else:  # APPROVE
                    st.success("### ✅ Transaction Approved")
                    st.write("No anomalies detected — transaction processed normally.")
                    for reason in reasons:
                        st.info(f"• {reason}")

                    transaction_data = {
                        'cc_num': active_cc, 'timestamp': timestamp, 'merchant': merchant,
                        'category': category, 'amount': amt, 'latitude': lat, 'longitude': lon,
                        'location_name': location_name, 'risk_score': risk_score, 'is_fraud': 0,
                        'hour': timestamp.hour, 'day_of_week': timestamp.weekday(),
                        'transaction_status': 'approved', 'otp_sent': 0, 'otp_verified': 0,
                        'anomaly_types': json.dumps([])
                    }
                    db.save_transaction(transaction_data)
                    st.success("💾 Transaction saved.")

    # ---- TAB 2: MY CARD HISTORY ----
    with tab2:
        st.header("📊 My Transaction History")

        view_cc = cc_num if cc_num else st.text_input("Enter your card number to view history")

        if view_cc:
            profile = db.get_card_profile(view_cc)
            history_df = db.get_card_history(view_cc)

            if not history_df.empty and profile:
                st.markdown("### 💳 Card Profile")
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: st.metric("Total Trans.", profile['total_transactions'])
                with c2: st.metric("Avg Amount", f"KES{profile['avg_amount']:,.2f}")
                with c3: st.metric("Max Amount", f"KES{profile['max_amount']:,.2f}")
                with c4:
                    otp_count = len(history_df[history_df['otp_sent'] == 1])
                    st.metric("OTP Sent", otp_count)
                with c5:
                    blocked_count = len(history_df[history_df['transaction_status'] == 'blocked'])
                    st.metric("Blocked", blocked_count)

                if profile.get('user_email'):
                    st.info(f"📧 Registered Email: {mask_email(profile['user_email'])}")

                st.divider()
                st.markdown("### 📅 Transaction Timeline")
                fig = create_transaction_timeline(history_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                st.divider()
                st.markdown("### 📋 All Transactions")
                display_df = history_df[['timestamp', 'merchant', 'category', 'amount',
                                         'location_name', 'risk_score', 'transaction_status', 'otp_sent']].copy()
                display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                display_df['otp_sent'] = display_df['otp_sent'].map({0: '❌', 1: '✅'})
                display_df['transaction_status'] = display_df['transaction_status'].map({
                    'approved': '✅ Approved', 'pending': '⏳ Pending', 'blocked': '🚫 Blocked'
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No transaction history found for this card.")


# ==================== ADMIN VIEW ====================

def render_admin_view():
    st.markdown('<div class="main-header">🛡️ Admin Control Panel</div>', unsafe_allow_html=True)

    if not GMAIL_ENABLED:
        st.markdown("""
        <div class="email-config-box">
            <h3 style="margin-top:0;">⚠️ Gmail Not Configured — Running in Demo Mode</h3>
            <p><strong>OTP codes will be displayed on screen instead of being sent to email.</strong></p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Analyze Transaction",
        "📂 Card History",
        "📈 Dashboard",
        "👥 User Management"
    ])

    # ---- TAB 1: ANALYZE TRANSACTION (admin can analyze any card) ----
    with tab1:
        st.header("🔍 Analyze Any Transaction")
        st.info("📌 Admin can analyze transactions for any card number.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💳 Card & Transaction Info")
            cc_num = st.text_input("Credit Card Number", "4532-1234-5678-9010",
                                   help="Card will be registered with email if new")

            profile = db.get_card_profile(cc_num)
            if profile and profile.get('user_email'):
                st.success(f"✅ Card registered | Email: {mask_email(profile['user_email'])}")
                user_email = profile['user_email']
            else:
                st.warning("⚠️ New card — email required for OTP verification")
                user_email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
                if user_email and st.button("💾 Register Email"):
                    db.save_email(cc_num, user_email)
                    st.success("✅ Email registered!")
                    st.rerun()

            merchant = st.text_input("Merchant Name", "SuperMart Kenya")
            category = st.selectbox("Category", [
                "Groceries", "Gas Station", "Restaurant", "Online Shopping",
                "Electronics", "Travel", "Entertainment", "Jewelry", "Other"
            ])
            amt = st.number_input("Amount (KES)", 0.0, value=500.0, step=50.0)

        with col2:
            st.subheader("📍 Location & Time")
            method = st.radio("Location Entry", ["🌍 Auto-detect", "📌 Manual"], horizontal=True)

            if method == "🌍 Auto-detect":
                location_name = st.text_input("Location Name", "Nairobi, Kenya")
                if st.button("🔍 Find Coordinates"):
                    with st.spinner("Locating..."):
                        lat, lon, addr = geocode_location(location_name)
                        if lat:
                            st.session_state.trans_lat = lat
                            st.session_state.trans_lon = lon
                            st.session_state.trans_addr = addr
                            st.success(f"✅ {addr}")
                if hasattr(st.session_state, 'trans_lat'):
                    lat = st.session_state.trans_lat
                    lon = st.session_state.trans_lon
                    location_name = st.session_state.trans_addr
                else:
                    lat, lon = 0.0, 0.0
            else:
                location_name = st.text_input("Location Name", "Custom Location")
                lat = st.number_input("Latitude", format="%.6f", value=-1.286389)
                lon = st.number_input("Longitude", format="%.6f", value=36.817223)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                trans_date = st.date_input("Date", datetime.now())
            with col_t2:
                trans_time = st.time_input("Time", datetime.now().time())
            timestamp = datetime.combine(trans_date, trans_time)

        st.divider()

        if st.button("🔍 ANALYZE TRANSACTION", type="primary", use_container_width=True):
            if lat == 0.0 and lon == 0.0:
                st.warning("⚠️ Please find coordinates first!")
            elif not user_email or '@' not in user_email:
                st.error("❌ Valid email required for OTP verification!")
            else:
                st.divider()
                st.header("📊 Analysis Results")

                history_df = db.get_card_history(cc_num)
                profile = db.get_card_profile(cc_num)

                result = detect_anomalies(cc_num, amt, lat, lon, location_name, category, timestamp, history_df, profile)
                action = result['action']
                anomalies = result['anomalies']
                risk_score = result['risk_score']
                reasons = result['reasons']

                col_g1, col_g2 = st.columns([1, 2])
                with col_g1:
                    if action == 'BLOCK':
                        st.markdown('<div class="blocked-alert">🚫 BLOCKED</div>', unsafe_allow_html=True)
                    elif action == 'SEND_OTP':
                        st.markdown('<div class="otp-alert">📧 OTP REQUIRED</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="safe-alert">✅ APPROVED</div>', unsafe_allow_html=True)
                with col_g2:
                    st.plotly_chart(create_risk_gauge(risk_score), use_container_width=True)

                st.divider()

                if action == 'BLOCK':
                    st.error("### 🚫 Transaction Blocked — Impossible Travel Detected")
                    for reason in reasons:
                        st.error(f"• {reason}")
                    st.warning("**Action Required:** Card flagged for manual review.")

                    transaction_data = {
                        'cc_num': cc_num, 'timestamp': timestamp, 'merchant': merchant,
                        'category': category, 'amount': amt, 'latitude': lat, 'longitude': lon,
                        'location_name': location_name, 'risk_score': risk_score, 'is_fraud': 1,
                        'hour': timestamp.hour, 'day_of_week': timestamp.weekday(),
                        'transaction_status': 'blocked', 'otp_sent': 0, 'otp_verified': 0,
                        'anomaly_types': json.dumps([a['type'] for a in anomalies])
                    }
                    db.save_transaction(transaction_data)
                    st.success("💾 Blocked transaction logged to database")

                elif action == 'SEND_OTP':
                    st.warning("### 📧 OTP Verification Required")
                    st.write("Anomalies detected — verification needed to proceed:")

                    for anomaly in anomalies:
                        emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(anomaly['severity'], '⚪')
                        st.warning(f"{emoji} **{anomaly['type'].replace('_', ' ').title()}:** {anomaly['description']}")

                    st.divider()

                    otp_code = generate_otp()
                    expires_at = datetime.now() + timedelta(minutes=10)

                    transaction_data = {
                        'cc_num': cc_num, 'timestamp': timestamp, 'merchant': merchant,
                        'category': category, 'amount': amt, 'latitude': lat, 'longitude': lon,
                        'location_name': location_name, 'risk_score': risk_score, 'is_fraud': 0,
                        'hour': timestamp.hour, 'day_of_week': timestamp.weekday(),
                        'transaction_status': 'pending', 'otp_sent': 1, 'otp_verified': 0,
                        'otp_code': otp_code, 'otp_expires_at': expires_at.isoformat(),
                        'anomaly_types': json.dumps([a['type'] for a in anomalies])
                    }
                    transaction_id = db.save_transaction(transaction_data)

                    otp_log_data = {
                        'transaction_id': transaction_id, 'cc_num': cc_num,
                        'otp_code': otp_code, 'sent_at': datetime.now().isoformat(),
                        'expires_at': expires_at.isoformat(), 'email': user_email
                    }
                    db.save_otp_log(otp_log_data)

                    email_sent = send_otp_email(user_email, otp_code, {
                        'cc_num': cc_num, 'amount': amt, 'merchant': merchant,
                        'location': location_name, 'timestamp': timestamp
                    }, reasons)

                    if email_sent:
                        if GMAIL_ENABLED:
                            st.success(f"✅ OTP sent via Gmail to {mask_email(user_email)}")
                            st.info("📬 Check inbox (may take 1–2 minutes)")
                        else:
                            st.success(f"✅ OTP generated for {mask_email(user_email)}")
                            st.markdown(f"""
                            <div class="otp-box">
                                <p style="margin: 0; color: #666;">🔒 DEMO MODE — OTP Code:</p>
                                <p class="otp-code">{otp_code}</p>
                                <p style="margin: 0; font-size: 0.9rem; color: #999;">Expires in 10 minutes</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.info("📝 Enable Gmail to send real emails.")

                        st.divider()
                        st.subheader("🔐 Enter Verification Code")
                        entered_otp = st.text_input("6-Digit Code", max_chars=6, placeholder="000000")

                        if st.button("✅ Verify & Approve Transaction", type="primary"):
                            if entered_otp:
                                is_valid, message = db.verify_otp(transaction_id, entered_otp)
                                if is_valid:
                                    db.update_transaction_status(transaction_id, 'approved', otp_verified=True)
                                    st.success("### ✅ Transaction Approved!")
                                    st.balloons()
                                    st.write(f"**Amount:** KES{amt:,.2f}")
                                    st.write(f"**Merchant:** {merchant}")
                                    st.write(f"**Location:** {location_name}")
                                    st.success("Transaction completed successfully!")
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.warning("Please enter the OTP code.")
                    else:
                        st.error("❌ Failed to send OTP. Please check your email configuration.")

                else:  # APPROVE
                    st.success("### ✅ Transaction Approved")
                    st.write("No anomalies detected — transaction processed normally.")
                    for reason in reasons:
                        st.info(f"• {reason}")

                    transaction_data = {
                        'cc_num': cc_num, 'timestamp': timestamp, 'merchant': merchant,
                        'category': category, 'amount': amt, 'latitude': lat, 'longitude': lon,
                        'location_name': location_name, 'risk_score': risk_score, 'is_fraud': 0,
                        'hour': timestamp.hour, 'day_of_week': timestamp.weekday(),
                        'transaction_status': 'approved', 'otp_sent': 0, 'otp_verified': 0,
                        'anomaly_types': json.dumps([])
                    }
                    db.save_transaction(transaction_data)
                    st.success("💾 Transaction saved to database")

    # ---- TAB 2: CARD HISTORY ----
    with tab2:
        st.header("📂 View Card Transaction History")
        search_cc = st.text_input("Search Credit Card Number", placeholder="Enter card number")

        if search_cc:
            profile = db.get_card_profile(search_cc)
            history_df = db.get_card_history(search_cc)

            if not history_df.empty and profile:
                st.markdown("### 💳 Card Profile")
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: st.metric("Total Trans.", profile['total_transactions'])
                with c2: st.metric("Avg Amount", f"KES{profile['avg_amount']:,.2f}")
                with c3: st.metric("Max Amount", f"KES{profile['max_amount']:,.2f}")
                with c4:
                    otp_count = len(history_df[history_df['otp_sent'] == 1])
                    st.metric("OTP Sent", otp_count)
                with c5:
                    blocked_count = len(history_df[history_df['transaction_status'] == 'blocked'])
                    st.metric("Blocked", blocked_count)

                if profile.get('user_email'):
                    st.info(f"📧 Registered Email: {mask_email(profile['user_email'])}")

                st.divider()
                st.markdown("### 📅 Transaction Timeline")
                fig = create_transaction_timeline(history_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                st.divider()
                st.markdown("### 📋 All Transactions")
                display_df = history_df[['timestamp', 'merchant', 'category', 'amount',
                                         'location_name', 'risk_score', 'transaction_status', 'otp_sent']].copy()
                display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                display_df['otp_sent'] = display_df['otp_sent'].map({0: '❌', 1: '✅'})
                display_df['transaction_status'] = display_df['transaction_status'].map({
                    'approved': '✅ Approved', 'pending': '⏳ Pending', 'blocked': '🚫 Blocked'
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No transaction history found for this card.")

    # ---- TAB 3: DASHBOARD ----
    with tab3:
        st.header("📈 System Dashboard")

        conn = db.get_connection()
        all_trans_df = pd.read_sql_query(
            'SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 1000', conn)
        conn.close()

        if not all_trans_df.empty:
            all_trans_df['timestamp'] = pd.to_datetime(all_trans_df['timestamp'])

            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Transactions", len(all_trans_df))
            with col2:
                total_amount = all_trans_df['amount'].sum()
                st.metric("Total Amount", f"KES{total_amount:,.0f}")
            with col3:
                otp_count = len(all_trans_df[all_trans_df['otp_sent'] == 1])
                otp_rate = (otp_count / len(all_trans_df) * 100) if len(all_trans_df) > 0 else 0
                st.metric("OTP Sent", f"{otp_count} ({otp_rate:.1f}%)")
            with col4:
                blocked_count = len(all_trans_df[all_trans_df['transaction_status'] == 'blocked'])
                st.metric("Blocked", blocked_count)

            st.divider()

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                status_counts = all_trans_df['transaction_status'].value_counts()
                fig1 = px.pie(values=status_counts.values, names=status_counts.index,
                              title='Transaction Status Distribution',
                              color_discrete_map={'approved': '#00C851', 'pending': '#ffbb33', 'blocked': '#ff4444'})
                st.plotly_chart(fig1, use_container_width=True)
            with col_c2:
                fig2 = px.histogram(all_trans_df, x='amount', nbins=30,
                                    title='Transaction Amount Distribution',
                                    labels={'amount': 'Amount (KES)'})
                st.plotly_chart(fig2, use_container_width=True)

            st.divider()
            st.subheader("📋 Recent Transactions")
            recent = all_trans_df.head(20)
            display_df = recent[['timestamp', 'cc_num', 'merchant', 'amount', 'risk_score',
                                  'transaction_status', 'otp_sent']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            display_df['otp_sent'] = display_df['otp_sent'].map({0: '❌', 1: '✅'})
            display_df['transaction_status'] = display_df['transaction_status'].map({
                'approved': '✅', 'pending': '⏳', 'blocked': '🚫'
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("📊 No transactions in database yet. Start analyzing transactions!")

    # ---- TAB 4: USER MANAGEMENT ----
    with tab4:
        st.header("👥 Registered Users")

        users_df = db.get_all_users()
        if not users_df.empty:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Users", len(users_df))
            with col2: st.metric("Admins", len(users_df[users_df['role'] == 'admin']))
            with col3: st.metric("Cardholders", len(users_df[users_df['role'] == 'cardholder']))

            st.divider()

            # Display users table
            display_users = users_df.copy()
            display_users['role'] = display_users['role'].map({'admin': '👑 Admin', 'cardholder': '💳 Cardholder'})
            display_users['created_at'] = pd.to_datetime(display_users['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            display_users['last_login'] = pd.to_datetime(display_users['last_login'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M').fillna('Never')
            display_users = display_users.rename(columns={
                'id': 'ID', 'username': 'Username', 'role': 'Role',
                'email': 'Email', 'full_name': 'Full Name',
                'cc_num': 'Card Number', 'created_at': 'Registered', 'last_login': 'Last Login'
            })
            st.dataframe(display_users, use_container_width=True, hide_index=True)
        else:
            st.info("No users found.")


# ==================== MAIN APP ROUTER ====================

if not st.session_state.logged_in:
    render_auth_page()
else:
    render_sidebar()
    user = st.session_state.user

    if user['role'] == 'admin':
        render_admin_view()
    else:
        render_cardholder_view()

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🛡️ <b>Fraud Detection with Gmail OTP Verification</b></p>
        <p style='font-size: 0.9rem;'>✨ Real-time anomaly detection · Gmail OTP · Role-based access</p>
    </div>
    """, unsafe_allow_html=True)