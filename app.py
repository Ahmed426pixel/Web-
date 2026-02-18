from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = 'stellar-skills-secret-key-2025'
CORS(app, supports_credentials=True)

# ── Local SQLite Database ─────────────────────────────────────────────────────
DB_PATH = 'stellar_skills.db'

UPLOAD_FOLDER = 'uploads'
ADMIN_EMAIL = 'admin@stellarskills.com'
ADMIN_PASSWORD = 'admin123'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'allahisonet3@gmail.com'
EMAIL_PASSWORD = 'veejfvacsgdmliae'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row  # allow dict-like access
    return conn


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute database query with proper error handling."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())

        if fetch_one:
            row = cursor.fetchone()
            result = tuple(row) if row else None
        elif fetch_all:
            rows = cursor.fetchall()
            result = [tuple(r) for r in rows] if rows else []
        else:
            result = cursor.lastrowid

        conn.commit()
        return result

    except Exception as e:
        print(f"Database query error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def fmt_date(dt):
    """Return ISO string whether dt is already a string or a datetime."""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def parse_dt(s):
    """Parse an ISO datetime string (SQLite returns strings)."""
    if s is None:
        return None
    if isinstance(s, datetime):
        return s
    return datetime.fromisoformat(s)


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_email(to_email, subject, body, is_html=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None


def validate_phone(phone):
    return re.match(r'^[\+]?[1-9][\d]{0,15}$', phone.replace(' ', '').replace('-', '')) is not None


def init_database():
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            phone       TEXT,
            password_hash TEXT NOT NULL,
            is_admin    INTEGER DEFAULT 0,
            email_verified INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS email_verification (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT NOT NULL,
            otp         TEXT NOT NULL,
            user_data   TEXT NOT NULL,
            expires_at  TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS password_reset (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT NOT NULL,
            otp         TEXT NOT NULL,
            expires_at  TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            company     TEXT NOT NULL,
            location    TEXT NOT NULL,
            type        TEXT NOT NULL,
            salary      TEXT,
            experience  TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT NOT NULL,
            posted_date TEXT DEFAULT (datetime('now')),
            is_active   INTEGER DEFAULT 1
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS applications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id      INTEGER,
            user_id     INTEGER,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            phone       TEXT,
            program     TEXT,
            experience  TEXT,
            resume      TEXT,
            status      TEXT DEFAULT 'pending',
            admin_notes TEXT,
            applied_at  TEXT DEFAULT (datetime('now')),
            reviewed_at TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS courses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            category    TEXT NOT NULL,
            description TEXT NOT NULL,
            features    TEXT NOT NULL,
            ideal_for   TEXT NOT NULL,
            price       REAL NOT NULL,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS course_purchases (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id       INTEGER NOT NULL,
            user_id         INTEGER NOT NULL,
            user_name       TEXT NOT NULL,
            user_email      TEXT NOT NULL,
            course_title    TEXT NOT NULL,
            course_category TEXT NOT NULL,
            payment_amount  REAL NOT NULL,
            payment_screenshot TEXT NOT NULL,
            status          TEXT DEFAULT 'pending',
            admin_notes     TEXT,
            purchased_at    TEXT DEFAULT (datetime('now')),
            approved_at     TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT NOT NULL,
            phone      TEXT,
            subject    TEXT NOT NULL,
            message    TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS newsletter (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            email        TEXT UNIQUE NOT NULL,
            subscribed_at TEXT DEFAULT (datetime('now')),
            is_active    INTEGER DEFAULT 1
        )''')

        # Default admin user
        admin_hash = generate_password_hash(ADMIN_PASSWORD)
        c.execute('''INSERT OR IGNORE INTO users (name, email, password_hash, is_admin, email_verified)
                     VALUES (?, ?, ?, 1, 1)''', ('Admin', ADMIN_EMAIL, admin_hash))

        # Default jobs
        default_jobs = [
            ('Robotics Instructor', 'Stellar Skills', 'Lahore, Pakistan', 'Full-time',
             '$30,000 - $45,000', 'Mid Level',
             'We are looking for a passionate robotics instructor to join our team.',
             json.dumps(['Bachelor\'s degree in Engineering or related field',
                         '2+ years of teaching experience',
                         'Strong knowledge of robotics and programming',
                         'Excellent communication skills'])),
            ('Frontend Developer', 'Stellar Skills', 'Remote', 'Full-time',
             '$40,000 - $60,000', 'Mid Level',
             'Join our development team to create innovative educational platforms.',
             json.dumps(['Proficiency in HTML, CSS, JavaScript',
                         'Experience with React or Vue.js',
                         '3+ years of web development experience',
                         'Knowledge of responsive design'])),
        ]
        for j in default_jobs:
            c.execute('SELECT COUNT(*) FROM jobs WHERE title=? AND company=?', (j[0], j[1]))
            if c.fetchone()[0] == 0:
                c.execute('''INSERT INTO jobs (title, company, location, type, salary, experience, description, requirements)
                             VALUES (?,?,?,?,?,?,?,?)''', j)

        # Default courses
        default_courses = [
            ('School Robotics Foundation', 'school',
             'Introduction to robotics for young learners with hands-on activities.',
             json.dumps(['Block-based Visual Programming', 'Essential Projects',
                         'Basic Sensors and Motors', 'Problem Solving through Playful Robotics',
                         'Fun Challenges & Team-Based Activities', 'Age-appropriate Content (Grades 1-8)',
                         'Pre-Coding and Algorithm Thinking']),
             'Students Age 6-13', 199.99),
            ('College Robotics Advanced', 'college',
             'Advanced robotics program for college students with programming and engineering focus.',
             json.dumps(['Advanced Programming Languages', 'Complex Project Development',
                         'Engineering Principles', 'Industry-Standard Tools',
                         'Research Projects', 'Career Preparation', 'Certification Program']),
             'College Students & Young Adults', 499.99),
            ('Commercial Robotics Professional', 'commercial',
             'Professional robotics training for commercial applications and industry automation.',
             json.dumps(['Industrial Automation', 'Commercial Applications',
                         'Advanced Control Systems', 'Professional Certification',
                         'Industry Partnerships', 'Real-world Projects', 'Career Placement Support']),
             'Working Professionals & Engineers', 999.99),
        ]
        for course in default_courses:
            c.execute('SELECT COUNT(*) FROM courses WHERE title=? AND category=?', (course[0], course[1]))
            if c.fetchone()[0] == 0:
                c.execute('''INSERT INTO courses (title, category, description, features, ideal_for, price)
                             VALUES (?,?,?,?,?,?)''', course)

        conn.commit()
        print("✅ Database initialized successfully!")
        return True

    except Exception as e:
        print(f"❌ Database init error: {e}")
        return False
    finally:
        if conn:
            conn.close()


# ── Auth Decorators ────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin', False):
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated


# ── Static Files ───────────────────────────────────────────────────────────────
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')


# ── Session Check ──────────────────────────────────────────────────────────────
@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'logged_in': True,
            'user': {
                'id': session['user_id'],
                'name': session.get('user_name'),
                'email': session.get('user_email'),
            },
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'success': True, 'logged_in': False})


# ── Auth ───────────────────────────────────────────────────────────────────────
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name     = data.get('name', '').strip()
        email    = data.get('email', '').lower().strip()
        phone    = data.get('phone', '').strip()
        password = data.get('password', '')

        if not all([name, email, password]):
            return jsonify({'success': False, 'message': 'Name, email and password are required'}), 400
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Invalid phone number format'}), 400
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400

        existing = execute_query('SELECT id FROM users WHERE email=?', (email,), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered'}), 409

        otp = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        user_data = json.dumps({'name': name, 'email': email, 'phone': phone, 'password': password})

        execute_query('DELETE FROM email_verification WHERE email=?', (email,))
        execute_query('''INSERT INTO email_verification (email, otp, user_data, expires_at)
                         VALUES (?,?,?,?)''', (email, otp, user_data, expires_at))

        body = f"""Dear {name},\n\nYour verification code is: {otp}\n\nExpires in 10 minutes.\n\nStellar Skills Team"""
        if send_email(email, "Verify Your Email - Stellar Skills", body):
            return jsonify({'success': True, 'message': f'Verification code sent to {email}.'})
        return jsonify({'success': False, 'message': 'Failed to send verification email'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/verify-email', methods=['POST'])
def verify_email():
    try:
        data  = request.get_json()
        email = data.get('email', '').lower().strip()
        otp   = data.get('otp', '').strip()

        if not email or not otp:
            return jsonify({'success': False, 'message': 'Email and OTP required'}), 400

        row = execute_query('''SELECT otp, user_data, expires_at FROM email_verification
                               WHERE email=? ORDER BY created_at DESC LIMIT 1''', (email,), fetch_one=True)
        if not row:
            return jsonify({'success': False, 'message': 'No verification request found'}), 404

        stored_otp, user_data_json, expires_at = row
        if datetime.now() > parse_dt(expires_at):
            execute_query('DELETE FROM email_verification WHERE email=?', (email,))
            return jsonify({'success': False, 'message': 'Verification code expired'}), 400
        if stored_otp != otp:
            return jsonify({'success': False, 'message': 'Invalid verification code'}), 400

        user_data = json.loads(user_data_json)
        pw_hash = generate_password_hash(user_data['password'])
        user_id = execute_query('''INSERT INTO users (name, email, phone, password_hash, email_verified)
                                   VALUES (?,?,?,?,1)''',
                                (user_data['name'], user_data['email'], user_data['phone'], pw_hash))
        if user_id:
            execute_query('DELETE FROM email_verification WHERE email=?', (email,))
            send_email(email, "Welcome to Stellar Skills!",
                       f"Hi {user_data['name']}, your account is verified. Welcome aboard!")
            return jsonify({'success': True, 'message': 'Account created! You can now sign in.'})
        return jsonify({'success': False, 'message': 'Failed to create account'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data  = request.get_json()
        email = data.get('email', '').lower().strip()
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        row = execute_query('SELECT user_data FROM email_verification WHERE email=? ORDER BY created_at DESC LIMIT 1',
                            (email,), fetch_one=True)
        if not row:
            return jsonify({'success': False, 'message': 'No verification request found'}), 404

        user_data = json.loads(row[0])
        otp = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        execute_query('UPDATE email_verification SET otp=?, expires_at=?, created_at=datetime(\'now\') WHERE email=?',
                      (otp, expires_at, email))

        send_email(email, "New Verification Code - Stellar Skills",
                   f"Hi {user_data['name']}, your new code is: {otp}\n\nExpires in 10 minutes.")
        return jsonify({'success': True, 'message': 'New code sent!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data  = request.get_json()
        email = data.get('email', '').lower().strip()
        if not email or not validate_email(email):
            return jsonify({'success': False, 'message': 'Valid email required'}), 400

        user = execute_query('SELECT name FROM users WHERE email=?', (email,), fetch_one=True)
        if not user:
            return jsonify({'success': False, 'message': 'No account found with this email'}), 404

        otp = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        execute_query('DELETE FROM password_reset WHERE email=?', (email,))
        execute_query('INSERT INTO password_reset (email, otp, expires_at) VALUES (?,?,?)',
                      (email, otp, expires_at))

        send_email(email, "Password Reset Code - Stellar Skills",
                   f"Hi {user[0]},\n\nYour reset code is: {otp}\n\nExpires in 10 minutes.")
        return jsonify({'success': True, 'message': f'Reset code sent to {email}'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data         = request.get_json()
        email        = data.get('email', '').lower().strip()
        otp          = data.get('otp', '').strip()
        new_password = data.get('newPassword', '')

        if not all([email, otp, new_password]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        if len(new_password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400

        row = execute_query('SELECT otp, expires_at FROM password_reset WHERE email=? ORDER BY created_at DESC LIMIT 1',
                            (email,), fetch_one=True)
        if not row:
            return jsonify({'success': False, 'message': 'No reset request found'}), 404

        stored_otp, expires_at = row
        if datetime.now() > parse_dt(expires_at):
            execute_query('DELETE FROM password_reset WHERE email=?', (email,))
            return jsonify({'success': False, 'message': 'Reset code expired'}), 400
        if stored_otp != otp:
            return jsonify({'success': False, 'message': 'Invalid reset code'}), 400

        execute_query('UPDATE users SET password_hash=? WHERE email=?',
                      (generate_password_hash(new_password), email))
        execute_query('DELETE FROM password_reset WHERE email=?', (email,))
        return jsonify({'success': True, 'message': 'Password reset! You can now sign in.'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/signin', methods=['POST'])
def signin():
    try:
        data     = request.get_json()
        login_id = data.get('email', '').strip()
        password = data.get('password', '')

        if not login_id or not password:
            return jsonify({'success': False, 'message': 'Email/username and password required'}), 400

        # Allow "admin" shorthand
        if login_id.lower() == 'admin':
            login_id = ADMIN_EMAIL

        # Try by email, else by name
        user = execute_query(
            'SELECT id, name, email, password_hash, is_admin, email_verified FROM users WHERE email=?',
            (login_id.lower(),), fetch_one=True)
        if not user:
            user = execute_query(
                'SELECT id, name, email, password_hash, is_admin, email_verified FROM users WHERE name=?',
                (login_id,), fetch_one=True)

        if not user or not check_password_hash(user[3], password):
            return jsonify({'success': False, 'message': 'Invalid email/password'}), 401
        if not user[5]:
            return jsonify({'success': False, 'message': 'Please verify your email first'}), 403

        session['user_id']    = user[0]
        session['user_name']  = user[1]
        session['user_email'] = user[2]
        session['is_admin']   = bool(user[4])

        return jsonify({
            'success': True,
            'message': f'Welcome back, {user[1]}!',
            'user': {'name': user[1], 'email': user[2]},
            'is_admin': bool(user[4])
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/signout', methods=['POST'])
def signout():
    session.clear()
    return jsonify({'success': True, 'message': 'Signed out successfully'})


# ── Contact & Newsletter ───────────────────────────────────────────────────────
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data    = request.get_json()
        name    = data.get('name', '').strip()
        email   = data.get('email', '').lower().strip()
        phone   = data.get('phone', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': 'All required fields must be filled'}), 400
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        execute_query('INSERT INTO contacts (name, email, phone, subject, message) VALUES (?,?,?,?,?)',
                      (name, email, phone, subject, message))

        send_email(ADMIN_EMAIL, f"New Contact: {subject}",
                   f"From: {name} <{email}>\nPhone: {phone}\n\n{message}")
        send_email(email, "Thank you for contacting Stellar Skills",
                   f"Hi {name},\n\nWe received your message and will respond within 24 hours.\n\nStellar Skills Team")

        return jsonify({'success': True, 'message': 'Thank you! We will get back to you soon.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/newsletter', methods=['POST'])
def newsletter():
    try:
        data  = request.get_json()
        email = data.get('email', '').lower().strip()
        if not email or not validate_email(email):
            return jsonify({'success': False, 'message': 'Valid email required'}), 400

        existing = execute_query('SELECT id FROM newsletter WHERE email=?', (email,), fetch_one=True)
        if existing:
            return jsonify({'success': True, 'message': 'Already subscribed!'})

        execute_query('INSERT INTO newsletter (email) VALUES (?)', (email,))
        send_email(email, "Subscribed to Stellar Skills Newsletter",
                   "Thank you for subscribing! Stay tuned for updates.")
        return jsonify({'success': True, 'message': 'Successfully subscribed!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Jobs ───────────────────────────────────────────────────────────────────────
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        rows = execute_query('''SELECT id, title, company, location, type, salary, experience,
                                       description, requirements, posted_date
                                FROM jobs WHERE is_active=1 ORDER BY posted_date DESC''', fetch_all=True)
        jobs = []
        for r in (rows or []):
            jobs.append({
                'id': r[0], 'title': r[1], 'company': r[2], 'location': r[3],
                'type': r[4], 'salary': r[5], 'experience': r[6],
                'description': r[7],
                'requirements': json.loads(r[8]) if r[8] else [],
                'posted_date': fmt_date(r[9])
            })
        return jsonify({'success': True, 'jobs': jobs})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/apply-job', methods=['POST'])
@login_required
def apply_job():
    try:
        data   = request.get_json()
        job_id = data.get('job_id')
        resume = data.get('resume')

        if not job_id or not resume:
            return jsonify({'success': False, 'message': 'Job ID and resume required'}), 400

        job = execute_query('SELECT title FROM jobs WHERE id=? AND is_active=1', (job_id,), fetch_one=True)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'}), 404

        existing = execute_query('SELECT id FROM applications WHERE job_id=? AND user_id=?',
                                 (job_id, session['user_id']), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Already applied for this job'}), 409

        user = execute_query('SELECT name, email, phone FROM users WHERE id=?',
                             (session['user_id'],), fetch_one=True)
        execute_query('''INSERT INTO applications (job_id, user_id, name, email, phone, resume)
                         VALUES (?,?,?,?,?,?)''',
                      (job_id, session['user_id'], user[0], user[1], user[2], resume))

        send_email(user[1], f"Application Received: {job[0]}",
                   f"Hi {user[0]}, we received your application for {job[0]}. We'll review it soon!")
        send_email(ADMIN_EMAIL, f"New Application: {job[0]}",
                   f"Applicant: {user[0]} ({user[1]})")

        return jsonify({'success': True, 'message': 'Application submitted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/apply-program', methods=['POST'])
def apply_program():
    try:
        data       = request.get_json()
        name       = data.get('name', '').strip()
        email      = data.get('email', '').lower().strip()
        phone      = data.get('phone', '').strip()
        program    = data.get('program', '').strip()
        experience = data.get('experience', '').strip()

        if not all([name, email, phone, program, experience]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email'}), 400
        if not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Invalid phone'}), 400

        execute_query('INSERT INTO applications (name, email, phone, program, experience) VALUES (?,?,?,?,?)',
                      (name, email, phone, program, experience))

        send_email(email, f"Program Application: {program}",
                   f"Hi {name}, we received your application for {program}. We'll contact you within 3-5 days.")
        send_email(ADMIN_EMAIL, f"New Program Application: {program}",
                   f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nExperience:\n{experience}")

        return jsonify({'success': True, 'message': 'Application submitted! We will contact you within 3-5 business days.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Courses ────────────────────────────────────────────────────────────────────
@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        rows = execute_query('''SELECT id, title, category, description, features, ideal_for, price
                                FROM courses WHERE is_active=1 ORDER BY category, title''', fetch_all=True)
        result = {'school': [], 'college': [], 'commercial': []}
        for r in (rows or []):
            cat = r[2]
            entry = {
                'id': r[0], 'title': r[1], 'category': cat,
                'description': r[3],
                'features': json.loads(r[4]) if r[4] else [],
                'ideal_for': r[5], 'price': float(r[6])
            }
            if cat in result:
                result[cat].append(entry)
        return jsonify({'success': True, 'courses': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/purchase-course', methods=['POST'])
@login_required
def purchase_course():
    try:
        data               = request.get_json()
        course_id          = data.get('course_id')
        payment_screenshot = data.get('payment_screenshot')
        payment_amount     = data.get('payment_amount')

        if not all([course_id, payment_screenshot, payment_amount]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400

        course = execute_query('SELECT title, price, category FROM courses WHERE id=? AND is_active=1',
                               (course_id,), fetch_one=True)
        if not course:
            return jsonify({'success': False, 'message': 'Course not found'}), 404

        existing = execute_query('SELECT id FROM course_purchases WHERE course_id=? AND user_id=?',
                                 (course_id, session['user_id']), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Already purchased this course'}), 409

        user = execute_query('SELECT name, email FROM users WHERE id=?', (session['user_id'],), fetch_one=True)
        execute_query('''INSERT INTO course_purchases
                         (course_id, user_id, user_name, user_email, course_title, course_category,
                          payment_amount, payment_screenshot)
                         VALUES (?,?,?,?,?,?,?,?)''',
                      (course_id, session['user_id'], user[0], user[1], course[0], course[2],
                       payment_amount, payment_screenshot))

        send_email(user[1], f"Purchase Confirmation: {course[0]}",
                   f"Hi {user[0]}, your payment for {course[0]} is under review. We'll activate access within 24 hours.")
        send_email(ADMIN_EMAIL, f"New Purchase: {course[0]}",
                   f"Student: {user[0]} ({user[1]})\nAmount: ${payment_amount}")

        return jsonify({'success': True, 'message': 'Purchase submitted! Access will be activated within 24 hours.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Admin ──────────────────────────────────────────────────────────────────────
@app.route('/api/admin/get-jobs', methods=['GET'])
@admin_required
def admin_get_jobs():
    try:
        rows = execute_query('''SELECT id, title, company, location, type, salary, experience,
                                       description, requirements, posted_date, is_active
                                FROM jobs ORDER BY posted_date DESC''', fetch_all=True)
        jobs = []
        for r in (rows or []):
            jobs.append({
                'id': r[0], 'title': r[1], 'company': r[2], 'location': r[3],
                'type': r[4], 'salary': r[5], 'experience': r[6],
                'description': r[7],
                'requirements': json.loads(r[8]) if r[8] else [],
                'posted_date': fmt_date(r[9]),
                'is_active': bool(r[10])
            })
        return jsonify({'success': True, 'jobs': jobs})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/post-job', methods=['POST'])
@admin_required
def admin_post_job():
    try:
        data        = request.get_json()
        title       = data.get('title', '').strip()
        company     = data.get('company', '').strip()
        location    = data.get('location', '').strip()
        job_type    = data.get('type', '').strip()
        salary      = data.get('salary', '').strip()
        experience  = data.get('experience', '').strip()
        description = data.get('description', '').strip()
        requirements = data.get('requirements', '').strip()

        if not all([title, company, location, job_type, experience, description, requirements]):
            return jsonify({'success': False, 'message': 'All required fields must be filled'}), 400

        req_list = [r.strip() for r in requirements.split('\n') if r.strip()]
        execute_query('''INSERT INTO jobs (title, company, location, type, salary, experience, description, requirements)
                         VALUES (?,?,?,?,?,?,?,?)''',
                      (title, company, location, job_type, salary, experience, description, json.dumps(req_list)))

        return jsonify({'success': True, 'message': f'Job "{title}" posted!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/delete-job/<int:job_id>', methods=['DELETE'])
@admin_required
def admin_delete_job(job_id):
    try:
        job = execute_query('SELECT title FROM jobs WHERE id=?', (job_id,), fetch_one=True)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        execute_query('DELETE FROM jobs WHERE id=?', (job_id,))
        return jsonify({'success': True, 'message': f'Job "{job[0]}" deleted!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/toggle-job/<int:job_id>', methods=['PUT'])
@admin_required
def admin_toggle_job(job_id):
    try:
        job = execute_query('SELECT is_active FROM jobs WHERE id=?', (job_id,), fetch_one=True)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        new_status = 0 if job[0] else 1
        execute_query('UPDATE jobs SET is_active=? WHERE id=?', (new_status, job_id))
        return jsonify({'success': True, 'is_active': bool(new_status)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/applications', methods=['GET'])
@admin_required
def admin_get_applications():
    try:
        rows = execute_query('''SELECT a.id, a.job_id, a.name, a.email, a.phone, a.program,
                                       a.experience, a.resume, a.status, a.admin_notes,
                                       a.applied_at, a.reviewed_at, j.title
                                FROM applications a
                                LEFT JOIN jobs j ON a.job_id = j.id
                                ORDER BY a.applied_at DESC''', fetch_all=True)
        apps = []
        for r in (rows or []):
            apps.append({
                'id': r[0], 'job_id': r[1], 'name': r[2], 'email': r[3], 'phone': r[4],
                'program': r[5], 'experience': r[6], 'resume': r[7], 'status': r[8],
                'admin_notes': r[9], 'applied_at': fmt_date(r[10]),
                'reviewed_at': fmt_date(r[11]), 'job_title': r[12]
            })
        return jsonify({'success': True, 'applications': apps})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/update-application/<int:app_id>', methods=['PUT'])
@admin_required
def admin_update_application(app_id):
    try:
        data        = request.get_json()
        status      = data.get('status')
        admin_notes = data.get('admin_notes', '')

        if not status:
            return jsonify({'success': False, 'message': 'Status required'}), 400
        if status not in ['pending', 'reviewed', 'accepted', 'rejected']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400

        app_det = execute_query('''SELECT a.name, a.email, j.title, a.program
                                   FROM applications a LEFT JOIN jobs j ON a.job_id=j.id
                                   WHERE a.id=?''', (app_id,), fetch_one=True)
        if not app_det:
            return jsonify({'success': False, 'message': 'Application not found'}), 404

        execute_query('''UPDATE applications SET status=?, admin_notes=?, reviewed_at=datetime('now')
                         WHERE id=?''', (status, admin_notes, app_id))

        job_title = app_det[2] or app_det[3] or 'Position'
        if status == 'accepted':
            subject = f"Application Accepted: {job_title}"
            body = f"Hi {app_det[0]},\n\nCongratulations! Your application for {job_title} has been accepted!\n\n{admin_notes or 'Our team will contact you soon.'}"
        elif status == 'rejected':
            subject = f"Application Update: {job_title}"
            body = f"Hi {app_det[0]},\n\nThank you for applying to {job_title}. We have decided to move forward with other candidates at this time.\n\n{admin_notes or 'We encourage you to apply for future opportunities.'}"
        else:
            subject = f"Application Update: {job_title}"
            body = f"Hi {app_det[0]},\n\nYour application for {job_title} status: {status.upper()}.\n\n{admin_notes or ''}"
        send_email(app_det[1], subject, body)

        return jsonify({'success': True, 'message': f'Status updated to "{status}".'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/delete-application/<int:app_id>', methods=['DELETE'])
@admin_required
def admin_delete_application(app_id):
    try:
        app = execute_query('SELECT name FROM applications WHERE id=?', (app_id,), fetch_one=True)
        if not app:
            return jsonify({'success': False, 'message': 'Not found'}), 404
        execute_query('DELETE FROM applications WHERE id=?', (app_id,))
        return jsonify({'success': True, 'message': f'Application from {app[0]} deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        rows = execute_query('''SELECT id, name, email, phone, is_admin, email_verified, created_at
                                FROM users ORDER BY created_at DESC''', fetch_all=True)
        users = []
        for r in (rows or []):
            users.append({
                'id': r[0], 'name': r[1], 'email': r[2], 'phone': r[3],
                'is_admin': bool(r[4]), 'email_verified': bool(r[5]),
                'created_at': fmt_date(r[6])
            })
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/delete-user/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    try:
        if user_id == session.get('user_id'):
            return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
        user = execute_query('SELECT name, is_admin FROM users WHERE id=?', (user_id,), fetch_one=True)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        if user[1]:
            return jsonify({'success': False, 'message': 'Cannot delete admin users'}), 400
        execute_query('DELETE FROM users WHERE id=?', (user_id,))
        return jsonify({'success': True, 'message': f'User "{user[0]}" deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/add-course', methods=['POST'])
@admin_required
def admin_add_course():
    try:
        data        = request.get_json()
        title       = data.get('title', '').strip()
        category    = data.get('category', '').strip()
        description = data.get('description', '').strip()
        features    = data.get('features', '').strip()
        ideal_for   = data.get('ideal_for', '').strip()
        price       = data.get('price', 0)

        if not all([title, category, description, features, ideal_for, price]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        if category not in ['school', 'college', 'commercial']:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400

        price = float(price)
        feat_list = [f.strip() for f in features.split('\n') if f.strip()]
        execute_query('''INSERT INTO courses (title, category, description, features, ideal_for, price)
                         VALUES (?,?,?,?,?,?)''',
                      (title, category, description, json.dumps(feat_list), ideal_for, price))

        return jsonify({'success': True, 'message': f'Course "{title}" added!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/courses', methods=['GET'])
@admin_required
def admin_get_courses():
    try:
        rows = execute_query('''SELECT id, title, category, description, features, ideal_for,
                                       price, created_at, is_active
                                FROM courses ORDER BY created_at DESC''', fetch_all=True)
        courses = []
        for r in (rows or []):
            courses.append({
                'id': r[0], 'title': r[1], 'category': r[2], 'description': r[3],
                'features': json.loads(r[4]) if r[4] else [],
                'ideal_for': r[5], 'price': float(r[6]),
                'created_at': fmt_date(r[7]), 'is_active': bool(r[8])
            })
        return jsonify({'success': True, 'courses': courses})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/delete-course/<int:course_id>', methods=['DELETE'])
@admin_required
def admin_delete_course(course_id):
    try:
        course = execute_query('SELECT title FROM courses WHERE id=?', (course_id,), fetch_one=True)
        if not course:
            return jsonify({'success': False, 'message': 'Not found'}), 404
        execute_query('DELETE FROM courses WHERE id=?', (course_id,))
        return jsonify({'success': True, 'message': f'Course "{course[0]}" deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/purchases', methods=['GET'])
@admin_required
def admin_get_purchases():
    try:
        rows = execute_query('''SELECT id, course_id, user_id, user_name, user_email, course_title,
                                       course_category, payment_amount, payment_screenshot,
                                       status, admin_notes, purchased_at, approved_at
                                FROM course_purchases ORDER BY purchased_at DESC''', fetch_all=True)
        purchases = []
        for r in (rows or []):
            purchases.append({
                'id': r[0], 'course_id': r[1], 'user_id': r[2],
                'user_name': r[3], 'user_email': r[4],
                'course_title': r[5], 'course_category': r[6],
                'payment_amount': float(r[7]), 'payment_screenshot': r[8],
                'status': r[9], 'admin_notes': r[10],
                'purchased_at': fmt_date(r[11]), 'approved_at': fmt_date(r[12])
            })
        return jsonify({'success': True, 'purchases': purchases})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/approve-purchase/<int:purchase_id>', methods=['PUT'])
@admin_required
def admin_approve_purchase(purchase_id):
    try:
        data        = request.get_json()
        status      = data.get('status')
        admin_notes = data.get('admin_notes', '')

        if not status or status not in ['pending', 'approved', 'rejected']:
            return jsonify({'success': False, 'message': 'Valid status required'}), 400

        p = execute_query('SELECT user_name, user_email, course_title, payment_amount FROM course_purchases WHERE id=?',
                          (purchase_id,), fetch_one=True)
        if not p:
            return jsonify({'success': False, 'message': 'Purchase not found'}), 404

        if status == 'approved':
            execute_query("UPDATE course_purchases SET status=?, admin_notes=?, approved_at=datetime('now') WHERE id=?",
                          (status, admin_notes, purchase_id))
        else:
            execute_query('UPDATE course_purchases SET status=?, admin_notes=? WHERE id=?',
                          (status, admin_notes, purchase_id))

        if status == 'approved':
            subj = f"Course Access Approved: {p[2]}"
            body = f"Hi {p[0]},\n\nYour payment for {p[2]} has been approved! Your course is now active.\n\n{admin_notes or 'Welcome to Stellar Skills!'}"
        elif status == 'rejected':
            subj = f"Payment Issue: {p[2]}"
            body = f"Hi {p[0]},\n\nWe encountered an issue with your payment for {p[2]}.\n\n{admin_notes or 'Please contact support.'}"
        else:
            subj = f"Payment Under Review: {p[2]}"
            body = f"Hi {p[0]},\n\nYour payment for {p[2]} is under review. We'll update you soon."
        send_email(p[1], subj, body)

        return jsonify({'success': True, 'message': f'Purchase updated to "{status}".'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Error Handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("🚀 Starting Stellar Skills Backend (SQLite)...")
    if init_database():
        print("✅ Database ready!")
    else:
        print("❌ Database init failed!")
        exit(1)

    print(f"📧 Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("🌐 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
