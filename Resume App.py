# import packages
import streamlit as st
import pandas as pd

# style the layout
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
        df = pd.read_sql_query(
            'SELECT id, username, role, email, full_name, cc_num, created_at, last_login FROM users ORDER BY created_at DESC',
            conn)
        conn.close()
        return df
