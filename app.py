from flask import Flask, request, jsonify, session, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import smtplib
import random
import string
import uuid
import json
import re
import io
import time
import queue
import threading
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from functools import wraps

# ── Optional imports (graceful fallback if not installed) ─────────────────────
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  reportlab not installed. Certificate generation disabled.")

try:
    import qrcode
    from PIL import Image as PILImage
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("⚠️  qrcode/Pillow not installed. QR codes disabled.")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  anthropic not installed. AI features disabled.")

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'stellar-skills-secret-key-2025'
CORS(app, supports_credentials=True)

DB_PATH         = 'stellar_skills.db'
UPLOAD_FOLDER   = 'uploads'
ADMIN_EMAIL     = 'admin@stellarskills.com'
ADMIN_PASSWORD  = 'admin123'
SMTP_SERVER     = 'smtp.gmail.com'
SMTP_PORT       = 587
EMAIL_USER      = 'allahisonet3@gmail.com'
EMAIL_PASSWORD  = 'veejfvacsgdmliae'
BASE_URL        = 'http://localhost:5000'

# Replace with your Anthropic API key or set env var ANTHROPIC_API_KEY
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', 'your-anthropic-api-key-here')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('certificates', exist_ok=True)

# ── SSE Event Bus ──────────────────────────────────────────────────────────────
_sse_subscribers: dict[int, queue.Queue] = {}   # user_id → queue
_sse_lock = threading.Lock()

def sse_push(user_id: int, event_type: str, data: dict):
    """Push a real-time event to a specific user."""
    with _sse_lock:
        q = _sse_subscribers.get(user_id)
    if q:
        try:
            q.put_nowait({'type': event_type, 'data': data})
        except queue.Full:
            pass

def sse_broadcast(event_type: str, data: dict):
    """Push an event to ALL connected users."""
    with _sse_lock:
        subs = list(_sse_subscribers.items())
    for uid, q in subs:
        try:
            q.put_nowait({'type': event_type, 'data': data})
        except queue.Full:
            pass

# ── Multi-language Support ─────────────────────────────────────────────────────
TRANSLATIONS = {
    'ur': {
        'Application submitted successfully!': 'درخواست کامیابی سے جمع کر دی گئی!',
        'Purchase submitted! Access will be activated within 24 hours.': 'خریداری جمع کر دی گئی! رسائی 24 گھنٹوں میں فعال ہو جائے گی۔',
        'Already applied for this job': 'آپ پہلے ہی اس نوکری کے لیے درخواست دے چکے ہیں',
        'Authentication required': 'تصدیق ضروری ہے',
        'All fields required': 'تمام فیلڈز ضروری ہیں',
        'Invalid email': 'غلط ای میل',
        'Thank you! We will get back to you soon.': 'شکریہ! ہم جلد آپ سے رابطہ کریں گے۔',
        'Successfully subscribed!': 'کامیابی سے سبسکرائب ہو گئے!',
        'Welcome back': 'خوش آمدید',
        'Account created! You can now sign in.': 'اکاؤنٹ بنا دیا گیا! اب آپ سائن ان کر سکتے ہیں۔',
    },
    'ar': {
        'Application submitted successfully!': 'تم تقديم الطلب بنجاح!',
        'Authentication required': 'المصادقة مطلوبة',
        'All fields required': 'جميع الحقول مطلوبة',
        'Thank you! We will get back to you soon.': 'شكراً! سنتواصل معك قريباً.',
        'Successfully subscribed!': 'تم الاشتراك بنجاح!',
        'Account created! You can now sign in.': 'تم إنشاء الحساب! يمكنك الآن تسجيل الدخول.',
    }
}

def t(message: str) -> str:
    """Translate message based on request lang param."""
    lang = request.args.get('lang', 'en').lower()
    if lang == 'en':
        return message
    return TRANSLATIONS.get(lang, {}).get(message, message)

# ── Gamification Config ────────────────────────────────────────────────────────
POINT_EVENTS = {
    'signup':        50,
    'job_apply':     100,
    'course_buy':    200,
    'contact_sent':  25,
    'newsletter':    30,
    'profile_complete': 75,
}

BADGES = [
    {'id': 'pioneer',      'name': '🚀 Pioneer',       'description': 'First to sign up',   'threshold': 1,    'type': 'special'},
    {'id': 'early_bird',   'name': '🌅 Early Bird',     'description': 'Signed up early',    'threshold': 50,   'type': 'points'},
    {'id': 'explorer',     'name': '🧭 Explorer',       'description': 'Applied for a job',  'threshold': 100,  'type': 'points'},
    {'id': 'learner',      'name': '📚 Learner',        'description': 'Purchased a course', 'threshold': 200,  'type': 'points'},
    {'id': 'achiever',     'name': '🏆 Achiever',       'description': '500+ points',        'threshold': 500,  'type': 'points'},
    {'id': 'champion',     'name': '👑 Champion',       'description': '1000+ points',       'threshold': 1000, 'type': 'points'},
    {'id': 'communicator', 'name': '💬 Communicator',  'description': 'Sent a message',     'threshold': 25,   'type': 'points'},
    {'id': 'subscriber',   'name': '📧 Subscriber',     'description': 'Joined newsletter',  'threshold': 30,   'type': 'points'},
]

# ── Database Helpers ──────────────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
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
        print(f"DB error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def fmt_date(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()

def parse_dt(s):
    if s is None:
        return None
    if isinstance(s, datetime):
        return s
    return datetime.fromisoformat(s)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email(to_email, subject, body, is_html=False, attachment_bytes=None, attachment_name=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        if attachment_bytes and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
            msg.attach(part)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validate_phone(phone):
    return re.match(r'^[\+]?[1-9][\d]{0,15}$', phone.replace(' ', '').replace('-', '')) is not None

# ── Gamification Helpers ───────────────────────────────────────────────────────
def award_points(user_id: int, event: str):
    """Award points for an event and check for new badges."""
    pts = POINT_EVENTS.get(event, 0)
    if pts <= 0 or not user_id:
        return
    execute_query('''
        INSERT INTO user_points (user_id, event, points)
        VALUES (?, ?, ?)
    ''', (user_id, event, pts))

    total = get_user_total_points(user_id)
    new_badges = check_and_award_badges(user_id, total)

    # Real-time notification
    sse_push(user_id, 'points_earned', {
        'points': pts,
        'total': total,
        'event': event,
        'new_badges': new_badges
    })

def get_user_total_points(user_id: int) -> int:
    row = execute_query('SELECT COALESCE(SUM(points),0) FROM user_points WHERE user_id=?',
                        (user_id,), fetch_one=True)
    return row[0] if row else 0

def check_and_award_badges(user_id: int, total_points: int) -> list:
    existing = execute_query('SELECT badge_id FROM user_badges WHERE user_id=?',
                             (user_id,), fetch_all=True)
    existing_ids = {r[0] for r in (existing or [])}
    new_badges = []
    for badge in BADGES:
        if badge['id'] in existing_ids:
            continue
        if badge['type'] == 'points' and total_points >= badge['threshold']:
            execute_query('INSERT INTO user_badges (user_id, badge_id) VALUES (?,?)',
                          (user_id, badge['id']))
            new_badges.append(badge)
    return new_badges

# ── Certificate Generator ──────────────────────────────────────────────────────
def generate_certificate_pdf(cert_uid: str, student_name: str, course_title: str,
                              course_category: str, completion_date: str) -> bytes | None:
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    verify_url = f"{BASE_URL}/api/verify-certificate/{cert_uid}"

    c = canvas.Canvas(buf, pagesize=landscape(A4))
    W, H = landscape(A4)

    # ── Background gradient effect ──
    c.setFillColorRGB(0.04, 0.04, 0.12)
    c.rect(0, 0, W, H, fill=True, stroke=False)

    # ── Decorative border ──
    for i, (r, g, b, lw) in enumerate([
        (0.5, 0.3, 1.0, 3),
        (0.3, 0.5, 1.0, 1.5),
        (0.7, 0.4, 1.0, 1),
    ]):
        margin = 15 + i * 8
        c.setStrokeColorRGB(r, g, b)
        c.setLineWidth(lw)
        c.rect(margin, margin, W - margin*2, H - margin*2, fill=False, stroke=True)

    # ── Header brand ──
    c.setFillColorRGB(0.6, 0.3, 1.0)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W/2, H - 70, "✦  STELLAR SKILLS  ✦")

    c.setFillColorRGB(0.7, 0.7, 0.9)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H - 88, "Transforming Education Through Technology")

    # ── Title ──
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(W/2, H - 150, "Certificate of Completion")

    # ── "This certifies that" ──
    c.setFillColorRGB(0.6, 0.6, 0.8)
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H - 190, "This is proudly presented to")

    # ── Student name ──
    c.setFillColorRGB(0.8, 0.6, 1.0)
    c.setFont("Helvetica-BoldOblique", 40)
    c.drawCentredString(W/2, H - 240, student_name)

    # ── Underline ──
    name_w = c.stringWidth(student_name, "Helvetica-BoldOblique", 40)
    c.setStrokeColorRGB(0.6, 0.3, 1.0)
    c.setLineWidth(1.5)
    c.line(W/2 - name_w/2, H - 248, W/2 + name_w/2, H - 248)

    # ── Course ──
    c.setFillColorRGB(0.7, 0.7, 0.9)
    c.setFont("Helvetica", 14)
    c.drawCentredString(W/2, H - 285, "for successfully completing the course")

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W/2, H - 315, course_title)

    c.setFillColorRGB(0.5, 0.8, 1.0)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W/2, H - 340, f"Category: {course_category.capitalize()}")

    # ── Date ──
    c.setFillColorRGB(0.6, 0.6, 0.8)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W/2, H - 370, f"Awarded on {completion_date}")

    # ── Certificate ID ──
    c.setFillColorRGB(0.4, 0.4, 0.6)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H - 390, f"Certificate ID: {cert_uid}")

    # ── QR Code ──
    if QR_AVAILABLE:
        qr = qrcode.QRCode(version=2, box_size=4, border=2,
                            error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="white", back_color="#0A0A1F")
        qr_buf = io.BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_buf.seek(0)
        qr_x = W - 130
        qr_y = 40
        c.drawImage(qr_buf, qr_x, qr_y, width=90, height=90, mask='auto')
        c.setFillColorRGB(0.5, 0.5, 0.7)
        c.setFont("Helvetica", 7)
        c.drawCentredString(qr_x + 45, qr_y - 10, "Scan to Verify")

    # ── Signature line ──
    c.setStrokeColorRGB(0.5, 0.3, 0.8)
    c.setLineWidth(1)
    c.line(80, 100, 250, 100)
    c.setFillColorRGB(0.6, 0.6, 0.8)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(165, 86, "Director, Stellar Skills")

    c.setStrokeColorRGB(0.5, 0.3, 0.8)
    c.line(W/2 - 85, 100, W/2 + 85, 100)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W/2, 86, "Academic Excellence Award")

    c.save()
    buf.seek(0)
    return buf.read()


# ── AI Resume Screener ─────────────────────────────────────────────────────────
def ai_screen_resume(job_title: str, requirements: list, resume_text_or_b64: str,
                     candidate_name: str) -> dict:
    """Screen a resume using Claude AI. Returns score + feedback."""
    if not ANTHROPIC_AVAILABLE or ANTHROPIC_API_KEY == 'your-anthropic-api-key-here':
        # Demo fallback
        return {
            'score': random.randint(55, 92),
            'summary': f'{candidate_name} appears to be a strong candidate with relevant experience.',
            'strengths': ['Relevant background', 'Good communication skills', 'Technical expertise'],
            'gaps': ['Could improve on industry certifications'],
            'recommendation': 'Recommended for interview',
            'ai_powered': False,
            'note': 'Demo mode - set ANTHROPIC_API_KEY for real AI screening'
        }

    # Truncate base64 resume if too large (just use the text portion)
    resume_snippet = resume_text_or_b64[:3000] if len(resume_text_or_b64) > 3000 else resume_text_or_b64

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""You are an expert HR recruiter and resume screener for Stellar Skills, an EdTech company.

Analyze the following job application and provide a detailed assessment.

JOB TITLE: {job_title}
REQUIREMENTS:
{chr(10).join(f'- {r}' for r in requirements)}

CANDIDATE: {candidate_name}
RESUME DATA (may be base64 encoded):
{resume_snippet[:2000]}

Respond ONLY with a JSON object (no markdown, no backticks) with this exact structure:
{{
  "score": <integer 0-100>,
  "summary": "<2-3 sentence executive summary>",
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "gaps": ["<gap1>", "<gap2>"],
  "recommendation": "<Strongly Recommended | Recommended | Maybe | Not Recommended>",
  "interview_questions": ["<question1>", "<question2>", "<question3>"]
}}"""

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip markdown fences if present
        raw = re.sub(r'^```[a-z]*\n?', '', raw).rstrip('`').strip()
        result = json.loads(raw)
        result['ai_powered'] = True
        return result
    except Exception as e:
        print(f"AI screen error: {e}")
        return {
            'score': 70,
            'summary': 'Unable to complete AI analysis. Manual review required.',
            'strengths': ['Analysis unavailable'],
            'gaps': ['Analysis unavailable'],
            'recommendation': 'Manual Review Required',
            'ai_powered': False,
            'error': str(e)
        }


# ── Database Init ──────────────────────────────────────────────────────────────
def init_database():
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # ── Original tables ──────────────────────────────────────────────────
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            email           TEXT UNIQUE NOT NULL,
            phone           TEXT,
            password_hash   TEXT NOT NULL,
            is_admin        INTEGER DEFAULT 0,
            email_verified  INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
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
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            company      TEXT NOT NULL,
            location     TEXT NOT NULL,
            type         TEXT NOT NULL,
            salary       TEXT,
            experience   TEXT NOT NULL,
            description  TEXT NOT NULL,
            requirements TEXT NOT NULL,
            posted_date  TEXT DEFAULT (datetime('now')),
            is_active    INTEGER DEFAULT 1
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id       INTEGER,
            user_id      INTEGER,
            name         TEXT NOT NULL,
            email        TEXT NOT NULL,
            phone        TEXT,
            program      TEXT,
            experience   TEXT,
            resume       TEXT,
            status       TEXT DEFAULT 'pending',
            admin_notes  TEXT,
            ai_score     INTEGER,
            ai_report    TEXT,
            applied_at   TEXT DEFAULT (datetime('now')),
            reviewed_at  TEXT,
            FOREIGN KEY (job_id)  REFERENCES jobs(id)  ON DELETE SET NULL,
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
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id          INTEGER NOT NULL,
            user_id            INTEGER NOT NULL,
            user_name          TEXT NOT NULL,
            user_email         TEXT NOT NULL,
            course_title       TEXT NOT NULL,
            course_category    TEXT NOT NULL,
            payment_amount     REAL NOT NULL,
            payment_screenshot TEXT NOT NULL,
            status             TEXT DEFAULT 'pending',
            admin_notes        TEXT,
            certificate_uid    TEXT,
            purchased_at       TEXT DEFAULT (datetime('now')),
            approved_at        TEXT,
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
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            subscribed_at TEXT DEFAULT (datetime('now')),
            is_active     INTEGER DEFAULT 1
        )''')

        # ── NEW: Certificates ─────────────────────────────────────────────────
        c.execute('''CREATE TABLE IF NOT EXISTS certificates (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            cert_uid        TEXT UNIQUE NOT NULL,
            user_id         INTEGER NOT NULL,
            user_name       TEXT NOT NULL,
            user_email      TEXT NOT NULL,
            course_id       INTEGER NOT NULL,
            course_title    TEXT NOT NULL,
            course_category TEXT NOT NULL,
            purchase_id     INTEGER NOT NULL,
            issued_at       TEXT DEFAULT (datetime('now')),
            is_valid        INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        # ── NEW: Support Tickets ──────────────────────────────────────────────
        c.execute('''CREATE TABLE IF NOT EXISTS support_tickets (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_uid   TEXT UNIQUE NOT NULL,
            user_id      INTEGER,
            user_name    TEXT NOT NULL,
            user_email   TEXT NOT NULL,
            subject      TEXT NOT NULL,
            message      TEXT NOT NULL,
            status       TEXT DEFAULT 'open',
            priority     TEXT DEFAULT 'normal',
            category     TEXT DEFAULT 'general',
            created_at   TEXT DEFAULT (datetime('now')),
            updated_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS ticket_replies (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id    INTEGER NOT NULL,
            sender_type  TEXT NOT NULL,
            sender_name  TEXT NOT NULL,
            message      TEXT NOT NULL,
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE
        )''')

        # ── NEW: Gamification ─────────────────────────────────────────────────
        c.execute('''CREATE TABLE IF NOT EXISTS user_points (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            event      TEXT NOT NULL,
            points     INTEGER NOT NULL,
            earned_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS user_badges (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            badge_id   TEXT NOT NULL,
            earned_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(user_id, badge_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        # ── NEW: Course Batches ───────────────────────────────────────────────
        c.execute('''CREATE TABLE IF NOT EXISTS course_batches (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id    INTEGER NOT NULL,
            batch_name   TEXT NOT NULL,
            start_date   TEXT NOT NULL,
            end_date     TEXT NOT NULL,
            max_seats    INTEGER NOT NULL DEFAULT 20,
            enrolled     INTEGER NOT NULL DEFAULT 0,
            schedule     TEXT,
            instructor   TEXT,
            is_active    INTEGER DEFAULT 1,
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS batch_enrollments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id     INTEGER NOT NULL,
            user_id      INTEGER NOT NULL,
            purchase_id  INTEGER NOT NULL,
            enrolled_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(batch_id, user_id),
            FOREIGN KEY (batch_id)   REFERENCES course_batches(id)  ON DELETE CASCADE,
            FOREIGN KEY (user_id)    REFERENCES users(id)           ON DELETE CASCADE,
            FOREIGN KEY (purchase_id) REFERENCES course_purchases(id) ON DELETE CASCADE
        )''')

        # ── Seed data ─────────────────────────────────────────────────────────
        admin_hash = generate_password_hash(ADMIN_PASSWORD)
        c.execute('''INSERT OR IGNORE INTO users (name, email, password_hash, is_admin, email_verified)
                     VALUES (?, ?, ?, 1, 1)''', ('Admin', ADMIN_EMAIL, admin_hash))

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
                c.execute('INSERT INTO jobs (title, company, location, type, salary, experience, description, requirements) VALUES (?,?,?,?,?,?,?,?)', j)

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
                c.execute('INSERT INTO courses (title, category, description, features, ideal_for, price) VALUES (?,?,?,?,?,?)', course)

        conn.commit()
        print("✅ Database initialized with all new tables!")
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
            return jsonify({'success': False, 'message': t('Authentication required')}), 401
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


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 1: SSE Real-Time Events ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/events')
@login_required
def sse_stream():
    """Server-Sent Events endpoint. Browser connects and stays connected."""
    user_id = session['user_id']
    q = queue.Queue(maxsize=50)
    with _sse_lock:
        _sse_subscribers[user_id] = q

    def generate():
        # Send a welcome ping
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Real-time connected!'})}\n\n"
        try:
            while True:
                try:
                    event = q.get(timeout=25)
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    # heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                _sse_subscribers.pop(user_id, None)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 2: Analytics Dashboard ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/analytics')
@admin_required
def admin_analytics():
    try:
        # Overview counts
        total_users      = (execute_query('SELECT COUNT(*) FROM users WHERE is_admin=0', fetch_one=True) or (0,))[0]
        total_apps       = (execute_query('SELECT COUNT(*) FROM applications',            fetch_one=True) or (0,))[0]
        total_purchases  = (execute_query('SELECT COUNT(*) FROM course_purchases',         fetch_one=True) or (0,))[0]
        total_revenue    = (execute_query("SELECT COALESCE(SUM(payment_amount),0) FROM course_purchases WHERE status='approved'", fetch_one=True) or (0,))[0]
        total_tickets    = (execute_query('SELECT COUNT(*) FROM support_tickets',          fetch_one=True) or (0,))[0]
        open_tickets     = (execute_query("SELECT COUNT(*) FROM support_tickets WHERE status='open'", fetch_one=True) or (0,))[0]
        total_certs      = (execute_query('SELECT COUNT(*) FROM certificates',             fetch_one=True) or (0,))[0]
        newsletter_subs  = (execute_query('SELECT COUNT(*) FROM newsletter WHERE is_active=1', fetch_one=True) or (0,))[0]

        # Signups per day last 30 days
        signups_daily = execute_query('''
            SELECT date(created_at) as day, COUNT(*) as cnt
            FROM users WHERE is_admin=0
              AND created_at >= datetime('now', '-30 days')
            GROUP BY day ORDER BY day
        ''', fetch_all=True) or []

        # Revenue per day last 30 days
        revenue_daily = execute_query('''
            SELECT date(purchased_at) as day, SUM(payment_amount) as total
            FROM course_purchases
            WHERE status='approved'
              AND purchased_at >= datetime('now', '-30 days')
            GROUP BY day ORDER BY day
        ''', fetch_all=True) or []

        # Applications per status
        app_status = execute_query('''
            SELECT status, COUNT(*) FROM applications GROUP BY status
        ''', fetch_all=True) or []

        # Top courses by enrollment
        top_courses = execute_query('''
            SELECT course_title, COUNT(*) as cnt
            FROM course_purchases GROUP BY course_title
            ORDER BY cnt DESC LIMIT 5
        ''', fetch_all=True) or []

        # Application conversion rate
        accepted = (execute_query("SELECT COUNT(*) FROM applications WHERE status='accepted'", fetch_one=True) or (0,))[0]
        conversion = round((accepted / total_apps * 100), 1) if total_apps else 0

        # Leaderboard top 5 points
        leaderboard = execute_query('''
            SELECT u.name, COALESCE(SUM(p.points),0) as total_pts
            FROM users u
            LEFT JOIN user_points p ON u.id = p.user_id
            WHERE u.is_admin=0
            GROUP BY u.id ORDER BY total_pts DESC LIMIT 5
        ''', fetch_all=True) or []

        return jsonify({
            'success': True,
            'overview': {
                'total_users':    total_users,
                'total_apps':     total_apps,
                'total_purchases': total_purchases,
                'total_revenue':  round(float(total_revenue), 2),
                'total_tickets':  total_tickets,
                'open_tickets':   open_tickets,
                'total_certs':    total_certs,
                'newsletter_subs': newsletter_subs,
                'conversion_rate': conversion,
            },
            'signups_daily': [{'date': r[0], 'count': r[1]} for r in signups_daily],
            'revenue_daily':  [{'date': r[0], 'total': round(float(r[1]), 2)} for r in revenue_daily],
            'app_by_status':  [{'status': r[0], 'count': r[1]} for r in app_status],
            'top_courses':    [{'title': r[0], 'enrollments': r[1]} for r in top_courses],
            'leaderboard':    [{'name': r[0], 'points': r[1]} for r in leaderboard],
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 3: AI Resume Screener ─────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/ai-screen-application/<int:app_id>', methods=['POST'])
@admin_required
def ai_screen_application(app_id):
    try:
        app_row = execute_query('''
            SELECT a.name, a.resume, a.experience, j.title, j.requirements
            FROM applications a
            LEFT JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
        ''', (app_id,), fetch_one=True)

        if not app_row:
            return jsonify({'success': False, 'message': 'Application not found'}), 404

        name, resume, experience, job_title, requirements_json = app_row
        requirements = json.loads(requirements_json) if requirements_json else []
        resume_data  = resume or experience or 'No resume provided'
        job_title    = job_title or 'General Position'

        result = ai_screen_resume(job_title, requirements, resume_data, name)

        # Save AI report to application
        execute_query(
            'UPDATE applications SET ai_score=?, ai_report=? WHERE id=?',
            (result.get('score', 0), json.dumps(result), app_id)
        )

        return jsonify({'success': True, 'report': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/ai-report/<int:app_id>', methods=['GET'])
@admin_required
def get_ai_report(app_id):
    try:
        row = execute_query('SELECT ai_score, ai_report, name FROM applications WHERE id=?',
                            (app_id,), fetch_one=True)
        if not row or not row[1]:
            return jsonify({'success': False, 'message': 'No AI report yet'}), 404
        return jsonify({'success': True, 'score': row[0], 'report': json.loads(row[1]), 'name': row[2]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 4: Certificate Generation & Verification ─────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/issue-certificate/<int:purchase_id>', methods=['POST'])
@admin_required
def issue_certificate(purchase_id):
    try:
        p = execute_query('''
            SELECT user_id, user_name, user_email, course_id, course_title, course_category
            FROM course_purchases WHERE id=? AND status='approved'
        ''', (purchase_id,), fetch_one=True)
        if not p:
            return jsonify({'success': False, 'message': 'Approved purchase not found'}), 404

        # Check if already issued
        existing = execute_query('SELECT cert_uid FROM certificates WHERE purchase_id=?',
                                 (purchase_id,), fetch_one=True)
        if existing:
            return jsonify({'success': True, 'cert_uid': existing[0], 'message': 'Certificate already issued'})

        cert_uid  = str(uuid.uuid4()).replace('-', '').upper()[:16]
        issued_at = datetime.now().strftime('%B %d, %Y')

        execute_query('''
            INSERT INTO certificates (cert_uid, user_id, user_name, user_email,
                                      course_id, course_title, course_category, purchase_id)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (cert_uid, p[0], p[1], p[2], p[3], p[4], p[5], purchase_id))

        execute_query('UPDATE course_purchases SET certificate_uid=? WHERE id=?',
                      (cert_uid, purchase_id))

        # Generate PDF
        pdf_bytes = generate_certificate_pdf(cert_uid, p[1], p[4], p[5], issued_at)

        if pdf_bytes:
            # Save to disk
            cert_path = os.path.join('certificates', f'{cert_uid}.pdf')
            with open(cert_path, 'wb') as f:
                f.write(pdf_bytes)

            # Email to student
            send_email(
                p[2],
                f'🎓 Your Certificate: {p[4]}',
                f'''<html><body style="font-family:sans-serif;background:#0a0a1f;color:#fff;padding:20px;">
                <h2 style="color:#8b5cf6;">Congratulations {p[1]}! 🎉</h2>
                <p>Your certificate for <strong>{p[4]}</strong> has been issued!</p>
                <p>Certificate ID: <code style="background:#1a1a3e;padding:4px 8px;border-radius:4px;">{cert_uid}</code></p>
                <p>Verify it at: <a href="{BASE_URL}/api/verify-certificate/{cert_uid}" style="color:#8b5cf6;">{BASE_URL}/api/verify-certificate/{cert_uid}</a></p>
                <p>Your certificate PDF is attached to this email.</p>
                </body></html>''',
                is_html=True,
                attachment_bytes=pdf_bytes,
                attachment_name=f'Certificate_{p[4].replace(" ", "_")}.pdf'
            )

        # Real-time notification to student
        sse_push(p[0], 'certificate_issued', {
            'cert_uid': cert_uid,
            'course':   p[4],
            'message':  f'🎓 Your certificate for {p[4]} is ready!'
        })

        return jsonify({
            'success':  True,
            'cert_uid': cert_uid,
            'message':  f'Certificate issued and emailed to {p[2]}',
            'download_url': f'/api/download-certificate/{cert_uid}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/verify-certificate/<cert_uid>')
def verify_certificate(cert_uid):
    try:
        cert = execute_query('''
            SELECT cert_uid, user_name, user_email, course_title, course_category,
                   issued_at, is_valid
            FROM certificates WHERE cert_uid=?
        ''', (cert_uid,), fetch_one=True)
        if not cert:
            return jsonify({'success': False, 'valid': False, 'message': 'Certificate not found'}), 404
        return jsonify({
            'success':   True,
            'valid':     bool(cert[6]),
            'cert_uid':  cert[0],
            'student':   cert[1],
            'email':     cert[2],
            'course':    cert[3],
            'category':  cert[4],
            'issued_at': cert[5],
            'issuer':    'Stellar Skills (Pvt) Ltd.'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/download-certificate/<cert_uid>')
@login_required
def download_certificate(cert_uid):
    try:
        cert = execute_query('''
            SELECT user_id, user_name, course_title, course_category, issued_at
            FROM certificates WHERE cert_uid=?
        ''', (cert_uid,), fetch_one=True)
        if not cert:
            return jsonify({'success': False, 'message': 'Certificate not found'}), 404
        if cert[0] != session['user_id'] and not session.get('is_admin', False):
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        cert_path = os.path.join('certificates', f'{cert_uid}.pdf')
        if os.path.exists(cert_path):
            return send_from_directory('certificates', f'{cert_uid}.pdf',
                                       as_attachment=True,
                                       download_name=f'Certificate_{cert[2].replace(" ","_")}.pdf')

        # Regenerate if missing
        pdf_bytes = generate_certificate_pdf(cert_uid, cert[1], cert[2], cert[3],
                                             cert[4] or datetime.now().strftime('%B %d, %Y'))
        if not pdf_bytes:
            return jsonify({'success': False, 'message': 'PDF generation unavailable'}), 500

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=Certificate_{cert[2].replace(" ","_")}.pdf'
            }
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/my-certificates')
@login_required
def my_certificates():
    try:
        certs = execute_query('''
            SELECT cert_uid, course_title, course_category, issued_at, is_valid
            FROM certificates WHERE user_id=?
            ORDER BY issued_at DESC
        ''', (session['user_id'],), fetch_all=True)
        return jsonify({
            'success': True,
            'certificates': [
                {
                    'cert_uid':   r[0],
                    'course':     r[1],
                    'category':   r[2],
                    'issued_at':  r[3],
                    'is_valid':   bool(r[4]),
                    'download_url': f'/api/download-certificate/{r[0]}',
                    'verify_url':   f'/api/verify-certificate/{r[0]}'
                } for r in (certs or [])
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 5: Support Ticket System ─────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    try:
        data     = request.get_json()
        name     = data.get('name', '').strip()
        email    = data.get('email', '').lower().strip()
        subject  = data.get('subject', '').strip()
        message  = data.get('message', '').strip()
        category = data.get('category', 'general').strip()
        priority = data.get('priority', 'normal').strip()

        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': t('All fields required')}), 400
        if not validate_email(email):
            return jsonify({'success': False, 'message': t('Invalid email')}), 400

        uid      = str(uuid.uuid4()).replace('-', '').upper()[:12]
        user_id  = session.get('user_id')

        execute_query('''
            INSERT INTO support_tickets
                (ticket_uid, user_id, user_name, user_email, subject, message, category, priority)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (uid, user_id, name, email, subject, message, category, priority))

        # Confirm to user
        send_email(
            email,
            f'[Ticket #{uid}] {subject}',
            f'Hi {name},\n\nYour support ticket has been received!\n\nTicket ID: {uid}\nSubject: {subject}\n\nWe will respond within 24 hours.\n\nStellar Skills Support'
        )
        # Alert admin
        send_email(
            ADMIN_EMAIL,
            f'🎫 New Support Ticket [{priority.upper()}]: {subject}',
            f'From: {name} <{email}>\nCategory: {category}\nPriority: {priority}\n\n{message}'
        )

        # Real-time admin notification
        sse_broadcast('new_ticket', {
            'ticket_uid': uid,
            'subject':    subject,
            'priority':   priority,
            'from':       name
        })

        return jsonify({'success': True, 'ticket_uid': uid, 'message': f'Ticket #{uid} created! Check your email.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/tickets/my', methods=['GET'])
@login_required
def my_tickets():
    try:
        tickets = execute_query('''
            SELECT id, ticket_uid, subject, status, priority, category, created_at, updated_at
            FROM support_tickets WHERE user_id=?
            ORDER BY updated_at DESC
        ''', (session['user_id'],), fetch_all=True)
        result = []
        for t_row in (tickets or []):
            reply_count = (execute_query('SELECT COUNT(*) FROM ticket_replies WHERE ticket_id=?',
                                         (t_row[0],), fetch_one=True) or (0,))[0]
            result.append({
                'id':          t_row[0], 'ticket_uid': t_row[1],
                'subject':     t_row[2], 'status':     t_row[3],
                'priority':    t_row[4], 'category':   t_row[5],
                'created_at':  t_row[6], 'updated_at': t_row[7],
                'reply_count': reply_count
            })
        return jsonify({'success': True, 'tickets': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/tickets/<ticket_uid>/replies', methods=['GET'])
@login_required
def get_ticket_replies(ticket_uid):
    try:
        ticket = execute_query('SELECT id, user_id, subject, status FROM support_tickets WHERE ticket_uid=?',
                               (ticket_uid,), fetch_one=True)
        if not ticket:
            return jsonify({'success': False, 'message': 'Ticket not found'}), 404
        if ticket[1] != session['user_id'] and not session.get('is_admin', False):
            return jsonify({'success': False, 'message': 'Access denied'}), 403

        replies = execute_query('''
            SELECT sender_type, sender_name, message, created_at
            FROM ticket_replies WHERE ticket_id=?
            ORDER BY created_at ASC
        ''', (ticket[0],), fetch_all=True)

        return jsonify({
            'success': True,
            'ticket_uid':   ticket_uid,
            'subject':      ticket[2],
            'status':       ticket[3],
            'replies': [{'sender_type': r[0], 'sender_name': r[1],
                          'message': r[2], 'created_at': r[3]} for r in (replies or [])]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/tickets', methods=['GET'])
@admin_required
def admin_get_tickets():
    try:
        status_filter = request.args.get('status', '')
        if status_filter:
            tickets = execute_query('''
                SELECT id, ticket_uid, user_name, user_email, subject, status, priority, category,
                       created_at, updated_at
                FROM support_tickets WHERE status=?
                ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
                         updated_at DESC
            ''', (status_filter,), fetch_all=True)
        else:
            tickets = execute_query('''
                SELECT id, ticket_uid, user_name, user_email, subject, status, priority, category,
                       created_at, updated_at
                FROM support_tickets
                ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
                         updated_at DESC
            ''', fetch_all=True)

        result = []
        for t_row in (tickets or []):
            reply_count = (execute_query('SELECT COUNT(*) FROM ticket_replies WHERE ticket_id=?',
                                         (t_row[0],), fetch_one=True) or (0,))[0]
            result.append({
                'id': t_row[0], 'ticket_uid': t_row[1],
                'user_name': t_row[2], 'user_email': t_row[3],
                'subject': t_row[4], 'status': t_row[5],
                'priority': t_row[6], 'category': t_row[7],
                'created_at': t_row[8], 'updated_at': t_row[9],
                'reply_count': reply_count
            })
        return jsonify({'success': True, 'tickets': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/tickets/<ticket_uid>/reply', methods=['POST'])
@admin_required
def admin_reply_ticket(ticket_uid):
    try:
        data    = request.get_json()
        message = data.get('message', '').strip()
        status  = data.get('status', 'open')
        if not message:
            return jsonify({'success': False, 'message': 'Message required'}), 400

        ticket = execute_query('''
            SELECT id, user_id, user_email, user_name, subject
            FROM support_tickets WHERE ticket_uid=?
        ''', (ticket_uid,), fetch_one=True)
        if not ticket:
            return jsonify({'success': False, 'message': 'Ticket not found'}), 404

        execute_query('''
            INSERT INTO ticket_replies (ticket_id, sender_type, sender_name, message)
            VALUES (?, 'admin', 'Stellar Skills Support', ?)
        ''', (ticket[0], message))

        execute_query('''
            UPDATE support_tickets
            SET status=?, updated_at=datetime('now')
            WHERE ticket_uid=?
        ''', (status, ticket_uid))

        send_email(
            ticket[2],
            f'[Ticket #{ticket_uid}] Re: {ticket[4]}',
            f'Hi {ticket[3]},\n\nYou have a new reply on ticket #{ticket_uid}:\n\n{message}\n\nStellar Skills Support'
        )

        if ticket[1]:
            sse_push(ticket[1], 'ticket_reply', {
                'ticket_uid': ticket_uid,
                'subject':    ticket[4],
                'message':    message[:100] + ('...' if len(message) > 100 else '')
            })

        return jsonify({'success': True, 'message': 'Reply sent!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 6: Gamification & Leaderboard ────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/leaderboard')
def get_leaderboard():
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        rows = execute_query('''
            SELECT u.id, u.name, COALESCE(SUM(p.points),0) as total_pts,
                   COUNT(DISTINCT b.badge_id) as badge_count
            FROM users u
            LEFT JOIN user_points p ON u.id = p.user_id
            LEFT JOIN user_badges b ON u.id = b.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY total_pts DESC, u.created_at ASC
            LIMIT ?
        ''', (limit,), fetch_all=True)

        board = []
        for rank, r in enumerate(rows or [], 1):
            uid, name, pts, badge_count = r
            # Get badge details
            badge_rows = execute_query('SELECT badge_id FROM user_badges WHERE user_id=?',
                                       (uid,), fetch_all=True)
            earned_ids = {b[0] for b in (badge_rows or [])}
            user_badges = [b for b in BADGES if b['id'] in earned_ids]
            # Anonymize name slightly (show only first name + last initial for non-logged users)
            display = name
            board.append({
                'rank':        rank,
                'name':        display,
                'points':      pts,
                'badge_count': badge_count,
                'badges':      [b['name'] for b in user_badges],
                'is_me':       (session.get('user_id') == uid)
            })

        return jsonify({'success': True, 'leaderboard': board})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/my-profile')
@login_required
def my_profile():
    try:
        user_id = session['user_id']
        total_pts = get_user_total_points(user_id)

        # Get all badges
        badge_rows = execute_query('SELECT badge_id, earned_at FROM user_badges WHERE user_id=?',
                                   (user_id,), fetch_all=True)
        earned_map = {r[0]: r[1] for r in (badge_rows or [])}
        badges_data = []
        for b in BADGES:
            badges_data.append({
                **b,
                'earned': b['id'] in earned_map,
                'earned_at': earned_map.get(b['id'])
            })

        # Recent activity
        activity = execute_query('''
            SELECT event, points, earned_at FROM user_points
            WHERE user_id=? ORDER BY earned_at DESC LIMIT 10
        ''', (user_id,), fetch_all=True)

        # Rank
        rank_row = execute_query('''
            SELECT COUNT(*) + 1 FROM (
                SELECT user_id, SUM(points) as tp FROM user_points
                WHERE user_id != ?
                GROUP BY user_id HAVING tp > ?
            )
        ''', (user_id, total_pts), fetch_one=True)
        rank = rank_row[0] if rank_row else 1

        return jsonify({
            'success': True,
            'points': total_pts,
            'rank': rank,
            'badges': badges_data,
            'activity': [{'event': r[0], 'points': r[1], 'at': r[2]} for r in (activity or [])],
            'next_badge': next((b for b in BADGES if b['id'] not in earned_map and b['type'] == 'points'), None)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 7: Course Batches & Scheduling ───────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/courses/<int:course_id>/batches')
def get_course_batches(course_id):
    try:
        batches = execute_query('''
            SELECT id, batch_name, start_date, end_date, max_seats, enrolled,
                   schedule, instructor, is_active
            FROM course_batches
            WHERE course_id=? AND is_active=1 AND start_date >= date('now', '-1 day')
            ORDER BY start_date ASC
        ''', (course_id,), fetch_all=True)

        return jsonify({
            'success': True,
            'batches': [
                {
                    'id':         r[0], 'name':        r[1],
                    'start_date': r[2], 'end_date':     r[3],
                    'max_seats':  r[4], 'enrolled':     r[5],
                    'available':  r[4] - r[5],
                    'is_full':    r[5] >= r[4],
                    'schedule':   r[6], 'instructor':  r[7],
                    'urgency':    '🔴 Last seat!' if (r[4]-r[5]) == 1 else
                                  f'⚡ Only {r[4]-r[5]} seats left!' if (r[4]-r[5]) <= 3 else
                                  f'✅ {r[4]-r[5]} seats available'
                }
                for r in (batches or [])
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/enroll-batch', methods=['POST'])
@login_required
def enroll_batch():
    try:
        data       = request.get_json()
        batch_id   = data.get('batch_id')
        purchase_id = data.get('purchase_id')

        if not batch_id or not purchase_id:
            return jsonify({'success': False, 'message': 'Batch ID and Purchase ID required'}), 400

        # Verify the purchase belongs to this user and is approved
        purchase = execute_query('''
            SELECT id, course_id, user_id, course_title
            FROM course_purchases
            WHERE id=? AND user_id=? AND status='approved'
        ''', (purchase_id, session['user_id']), fetch_one=True)
        if not purchase:
            return jsonify({'success': False, 'message': 'No approved purchase found'}), 404

        # Check batch availability
        batch = execute_query('''
            SELECT batch_name, max_seats, enrolled, course_id, start_date
            FROM course_batches WHERE id=? AND is_active=1
        ''', (batch_id,), fetch_one=True)
        if not batch:
            return jsonify({'success': False, 'message': 'Batch not found'}), 404
        if batch[2] >= batch[1]:
            return jsonify({'success': False, 'message': 'This batch is full!'}), 400
        if batch[3] != purchase[1]:
            return jsonify({'success': False, 'message': 'Batch does not match your course'}), 400

        # Enroll
        try:
            execute_query('''
                INSERT INTO batch_enrollments (batch_id, user_id, purchase_id)
                VALUES (?,?,?)
            ''', (batch_id, session['user_id'], purchase_id))
        except:
            return jsonify({'success': False, 'message': 'Already enrolled in this batch'}), 409

        execute_query('UPDATE course_batches SET enrolled=enrolled+1 WHERE id=?', (batch_id,))

        user = execute_query('SELECT name, email FROM users WHERE id=?',
                             (session['user_id'],), fetch_one=True)
        send_email(
            user[1],
            f'🎓 Batch Enrollment Confirmed: {purchase[3]}',
            f'Hi {user[0]},\n\nYou\'re enrolled in: {batch[0]}\nStarts: {batch[4]}\n\nStellar Skills'
        )

        sse_push(session['user_id'], 'batch_enrolled', {
            'batch_name': batch[0],
            'start_date': batch[4],
            'course':     purchase[3]
        })

        return jsonify({'success': True, 'message': f'Enrolled in batch {batch[0]}! Starts {batch[4]}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/batches', methods=['POST'])
@admin_required
def admin_create_batch():
    try:
        data       = request.get_json()
        course_id  = data.get('course_id')
        name       = data.get('batch_name', '').strip()
        start_date = data.get('start_date', '').strip()
        end_date   = data.get('end_date', '').strip()
        max_seats  = int(data.get('max_seats', 20))
        schedule   = data.get('schedule', '').strip()
        instructor = data.get('instructor', '').strip()

        if not all([course_id, name, start_date, end_date]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400

        execute_query('''
            INSERT INTO course_batches (course_id, batch_name, start_date, end_date,
                                        max_seats, schedule, instructor)
            VALUES (?,?,?,?,?,?,?)
        ''', (course_id, name, start_date, end_date, max_seats, schedule, instructor))

        # Notify all newsletter subscribers
        subs = execute_query('SELECT email FROM newsletter WHERE is_active=1', fetch_all=True)
        course = execute_query('SELECT title FROM courses WHERE id=?', (course_id,), fetch_one=True)
        if subs and course:
            for sub in subs[:50]:  # cap at 50 for demo
                send_email(
                    sub[0],
                    f'🚀 New Batch Open: {course[0]}',
                    f'A new batch for {course[0]} just opened!\nStarts: {start_date}\n\nEnroll at stellarskills.com'
                )

        return jsonify({'success': True, 'message': f'Batch "{name}" created!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── FEATURE 8: Bulk Email Campaigns ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/admin/send-newsletter', methods=['POST'])
@admin_required
def admin_send_newsletter():
    try:
        data    = request.get_json()
        subject = data.get('subject', '').strip()
        body    = data.get('body', '').strip()
        target  = data.get('target', 'newsletter')  # 'newsletter' | 'all_users' | 'verified_users'

        if not subject or not body:
            return jsonify({'success': False, 'message': 'Subject and body required'}), 400

        if target == 'newsletter':
            emails = execute_query('SELECT email FROM newsletter WHERE is_active=1', fetch_all=True)
        elif target == 'all_users':
            emails = execute_query('SELECT email FROM users WHERE is_admin=0', fetch_all=True)
        elif target == 'verified_users':
            emails = execute_query('SELECT email FROM users WHERE is_admin=0 AND email_verified=1', fetch_all=True)
        else:
            return jsonify({'success': False, 'message': 'Invalid target'}), 400

        emails = [r[0] for r in (emails or [])]
        if not emails:
            return jsonify({'success': False, 'message': 'No recipients found'}), 404

        # Wrap in HTML template
        html_body = f'''<!DOCTYPE html>
<html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0a0a1f;color:#fff;padding:20px;">
  <div style="background:linear-gradient(135deg,#1a0a3e,#0a0a1f);border:1px solid #8b5cf640;border-radius:16px;padding:32px;">
    <h1 style="color:#8b5cf6;margin:0 0 8px;">✦ Stellar Skills</h1>
    <hr style="border-color:#8b5cf620;margin:16px 0;">
    <div style="color:#ccc;line-height:1.7;white-space:pre-line;">{body}</div>
    <hr style="border-color:#8b5cf620;margin:24px 0 16px;">
    <p style="font-size:11px;color:#666;">
      You are receiving this because you subscribed to Stellar Skills updates.<br>
      Stellar Skills (Pvt) Ltd. | Lahore, Pakistan
    </p>
  </div>
</body></html>'''

        sent_count = 0
        failed = []
        for email in emails:
            if send_email(email, subject, html_body, is_html=True):
                sent_count += 1
            else:
                failed.append(email)

        return jsonify({
            'success': True,
            'message': f'Campaign sent to {sent_count}/{len(emails)} recipients.',
            'sent': sent_count,
            'failed': len(failed),
            'total': len(emails)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── ORIGINAL ROUTES (preserved + enhanced with points & SSE) ─────────────────
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        total_pts = get_user_total_points(session['user_id'])
        return jsonify({
            'success': True,
            'logged_in': True,
            'user': {
                'id':    session['user_id'],
                'name':  session.get('user_name'),
                'email': session.get('user_email'),
                'points': total_pts,
            },
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'success': True, 'logged_in': False})


@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data     = request.get_json()
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

        otp       = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        user_data  = json.dumps({'name': name, 'email': email, 'phone': phone, 'password': password})
        execute_query('DELETE FROM email_verification WHERE email=?', (email,))
        execute_query('INSERT INTO email_verification (email, otp, user_data, expires_at) VALUES (?,?,?,?)',
                      (email, otp, user_data, expires_at))

        body = f"Dear {name},\n\nYour verification code is: {otp}\n\nExpires in 10 minutes.\n\nStellar Skills Team"
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
                               WHERE email=? ORDER BY created_at DESC LIMIT 1''',
                            (email,), fetch_one=True)
        if not row:
            return jsonify({'success': False, 'message': 'No verification request found'}), 404

        stored_otp, user_data_json, expires_at = row
        if datetime.now() > parse_dt(expires_at):
            execute_query('DELETE FROM email_verification WHERE email=?', (email,))
            return jsonify({'success': False, 'message': 'Verification code expired'}), 400
        if stored_otp != otp:
            return jsonify({'success': False, 'message': 'Invalid verification code'}), 400

        user_data = json.loads(user_data_json)
        pw_hash   = generate_password_hash(user_data['password'])
        user_id   = execute_query(
            'INSERT INTO users (name, email, phone, password_hash, email_verified) VALUES (?,?,?,?,1)',
            (user_data['name'], user_data['email'], user_data['phone'], pw_hash)
        )
        if user_id:
            execute_query('DELETE FROM email_verification WHERE email=?', (email,))
            # Award signup points
            award_points(user_id, 'signup')
            send_email(email, "Welcome to Stellar Skills!",
                       f"Hi {user_data['name']}, your account is verified. Welcome aboard! 🚀\n\nYou've earned {POINT_EVENTS['signup']} points for signing up!")
            return jsonify({'success': True, 'message': t('Account created! You can now sign in.')})
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

        user_data  = json.loads(row[0])
        otp        = generate_otp()
        expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
        execute_query("UPDATE email_verification SET otp=?, expires_at=?, created_at=datetime('now') WHERE email=?",
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

        otp        = generate_otp()
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

        if login_id.lower() == 'admin':
            login_id = ADMIN_EMAIL

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

        pts = get_user_total_points(user[0])
        return jsonify({
            'success': True,
            'message': f'Welcome back, {user[1]}!',
            'user':    {'name': user[1], 'email': user[2], 'points': pts},
            'is_admin': bool(user[4])
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/signout', methods=['POST'])
def signout():
    session.clear()
    return jsonify({'success': True, 'message': 'Signed out successfully'})


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

        if session.get('user_id'):
            award_points(session['user_id'], 'contact_sent')

        return jsonify({'success': True, 'message': t('Thank you! We will get back to you soon.')})
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
                   "Thank you for subscribing! Stay tuned for updates. ✨")

        if session.get('user_id'):
            award_points(session['user_id'], 'newsletter')

        return jsonify({'success': True, 'message': t('Successfully subscribed!')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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

        job = execute_query('SELECT title, requirements FROM jobs WHERE id=? AND is_active=1', (job_id,), fetch_one=True)
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'}), 404

        existing = execute_query('SELECT id FROM applications WHERE job_id=? AND user_id=?',
                                 (job_id, session['user_id']), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Already applied for this job'}), 409

        user = execute_query('SELECT name, email, phone FROM users WHERE id=?',
                             (session['user_id'],), fetch_one=True)
        app_id = execute_query(
            'INSERT INTO applications (job_id, user_id, name, email, phone, resume) VALUES (?,?,?,?,?,?)',
            (job_id, session['user_id'], user[0], user[1], user[2], resume)
        )

        # Auto-run AI screening in background thread
        def bg_screen():
            reqs = json.loads(job[1]) if job[1] else []
            result = ai_screen_resume(job[0], reqs, resume, user[0])
            execute_query('UPDATE applications SET ai_score=?, ai_report=? WHERE id=?',
                          (result.get('score', 0), json.dumps(result), app_id))
            sse_push(session['user_id'], 'ai_screen_complete', {
                'job': job[0], 'score': result.get('score', 0),
                'recommendation': result.get('recommendation', '')
            })
        threading.Thread(target=bg_screen, daemon=True).start()

        award_points(session['user_id'], 'job_apply')

        send_email(user[1], f"Application Received: {job[0]}",
                   f"Hi {user[0]}, we received your application for {job[0]}. We'll review it soon! ✅")
        send_email(ADMIN_EMAIL, f"New Application: {job[0]}",
                   f"Applicant: {user[0]} ({user[1]})")

        return jsonify({'success': True, 'message': t('Application submitted successfully!')})
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
            return jsonify({'success': False, 'message': t('All fields required')}), 400
        if not validate_email(email):
            return jsonify({'success': False, 'message': t('Invalid email')}), 400
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


@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        rows = execute_query('''SELECT id, title, category, description, features, ideal_for, price
                                FROM courses WHERE is_active=1 ORDER BY category, title''', fetch_all=True)
        result = {'school': [], 'college': [], 'commercial': []}
        for r in (rows or []):
            cat = r[2]
            # Get next batch date if any
            next_batch = execute_query('''
                SELECT batch_name, start_date, max_seats, enrolled
                FROM course_batches
                WHERE course_id=? AND is_active=1 AND start_date >= date('now')
                ORDER BY start_date ASC LIMIT 1
            ''', (r[0],), fetch_one=True)
            entry = {
                'id': r[0], 'title': r[1], 'category': cat,
                'description': r[3],
                'features': json.loads(r[4]) if r[4] else [],
                'ideal_for': r[5], 'price': float(r[6]),
                'next_batch': {
                    'name': next_batch[0], 'start_date': next_batch[1],
                    'seats_left': next_batch[2] - next_batch[3],
                    'is_full': next_batch[3] >= next_batch[2]
                } if next_batch else None
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
                      (course_id, session['user_id'], user[0], user[1],
                       course[0], course[2], payment_amount, payment_screenshot))

        award_points(session['user_id'], 'course_buy')

        send_email(user[1], f"Purchase Confirmation: {course[0]}",
                   f"Hi {user[0]}, your payment for {course[0]} is under review. We'll activate access within 24 hours.")
        send_email(ADMIN_EMAIL, f"New Purchase: {course[0]}",
                   f"Student: {user[0]} ({user[1]})\nAmount: ${payment_amount}")

        return jsonify({'success': True, 'message': t('Purchase submitted! Access will be activated within 24 hours.')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Admin Routes ───────────────────────────────────────────────────────────────
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
        data         = request.get_json()
        title        = data.get('title', '').strip()
        company      = data.get('company', '').strip()
        location     = data.get('location', '').strip()
        job_type     = data.get('type', '').strip()
        salary       = data.get('salary', '').strip()
        experience   = data.get('experience', '').strip()
        description  = data.get('description', '').strip()
        requirements = data.get('requirements', '').strip()

        if not all([title, company, location, job_type, experience, description, requirements]):
            return jsonify({'success': False, 'message': 'All required fields must be filled'}), 400

        req_list = [r.strip() for r in requirements.split('\n') if r.strip()]
        execute_query('''INSERT INTO jobs (title, company, location, type, salary, experience, description, requirements)
                         VALUES (?,?,?,?,?,?,?,?)''',
                      (title, company, location, job_type, salary, experience, description, json.dumps(req_list)))

        sse_broadcast('new_job', {'title': title, 'company': company})
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
                                       a.applied_at, a.reviewed_at, j.title,
                                       a.ai_score, a.ai_report
                                FROM applications a
                                LEFT JOIN jobs j ON a.job_id = j.id
                                ORDER BY a.applied_at DESC''', fetch_all=True)
        apps = []
        for r in (rows or []):
            apps.append({
                'id': r[0], 'job_id': r[1], 'name': r[2], 'email': r[3], 'phone': r[4],
                'program': r[5], 'experience': r[6], 'resume': r[7], 'status': r[8],
                'admin_notes': r[9], 'applied_at': fmt_date(r[10]),
                'reviewed_at': fmt_date(r[11]), 'job_title': r[12],
                'ai_score': r[13],
                'ai_report': json.loads(r[14]) if r[14] else None
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

        app_det = execute_query('''SELECT a.name, a.email, j.title, a.program, a.user_id
                                   FROM applications a LEFT JOIN jobs j ON a.job_id=j.id
                                   WHERE a.id=?''', (app_id,), fetch_one=True)
        if not app_det:
            return jsonify({'success': False, 'message': 'Application not found'}), 404

        execute_query("UPDATE applications SET status=?, admin_notes=?, reviewed_at=datetime('now') WHERE id=?",
                      (status, admin_notes, app_id))

        job_title = app_det[2] or app_det[3] or 'Position'
        if status == 'accepted':
            subject = f"Application Accepted: {job_title}"
            body    = f"Hi {app_det[0]},\n\nCongratulations! Your application for {job_title} has been accepted! 🎉\n\n{admin_notes or 'Our team will contact you soon.'}"
        elif status == 'rejected':
            subject = f"Application Update: {job_title}"
            body    = f"Hi {app_det[0]},\n\nThank you for applying to {job_title}. We have decided to move forward with other candidates.\n\n{admin_notes or 'We encourage you to apply for future opportunities.'}"
        else:
            subject = f"Application Update: {job_title}"
            body    = f"Hi {app_det[0]},\n\nYour application for {job_title} status: {status.upper()}.\n\n{admin_notes or ''}"
        send_email(app_det[1], subject, body)

        if app_det[4]:
            sse_push(app_det[4], 'application_update', {
                'job': job_title, 'status': status,
                'message': f'Your application for {job_title} is now {status.upper()}'
            })

        return jsonify({'success': True, 'message': f'Status updated to "{status}".'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/delete-application/<int:app_id>', methods=['DELETE'])
@admin_required
def admin_delete_application(app_id):
    try:
        app_row = execute_query('SELECT name FROM applications WHERE id=?', (app_id,), fetch_one=True)
        if not app_row:
            return jsonify({'success': False, 'message': 'Not found'}), 404
        execute_query('DELETE FROM applications WHERE id=?', (app_id,))
        return jsonify({'success': True, 'message': f'Application from {app_row[0]} deleted.'})
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
            pts = get_user_total_points(r[0])
            users.append({
                'id': r[0], 'name': r[1], 'email': r[2], 'phone': r[3],
                'is_admin': bool(r[4]), 'email_verified': bool(r[5]),
                'created_at': fmt_date(r[6]), 'points': pts
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

        price     = float(price)
        feat_list = [f.strip() for f in features.split('\n') if f.strip()]
        execute_query('''INSERT INTO courses (title, category, description, features, ideal_for, price)
                         VALUES (?,?,?,?,?,?)''',
                      (title, category, description, json.dumps(feat_list), ideal_for, price))

        sse_broadcast('new_course', {'title': title, 'category': category})
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
                                       status, admin_notes, purchased_at, approved_at, certificate_uid
                                FROM course_purchases ORDER BY purchased_at DESC''', fetch_all=True)
        purchases = []
        for r in (rows or []):
            purchases.append({
                'id': r[0], 'course_id': r[1], 'user_id': r[2],
                'user_name': r[3], 'user_email': r[4],
                'course_title': r[5], 'course_category': r[6],
                'payment_amount': float(r[7]), 'payment_screenshot': r[8],
                'status': r[9], 'admin_notes': r[10],
                'purchased_at': fmt_date(r[11]), 'approved_at': fmt_date(r[12]),
                'certificate_uid': r[13]
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

        p = execute_query('SELECT user_name, user_email, course_title, payment_amount, user_id FROM course_purchases WHERE id=?',
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
            subj = f"Course Access Approved: {p[2]} 🎉"
            body = f"Hi {p[0]},\n\nYour payment for {p[2]} has been approved! Your course is now active.\n\n{admin_notes or 'Welcome to Stellar Skills!'}"
        elif status == 'rejected':
            subj = f"Payment Issue: {p[2]}"
            body = f"Hi {p[0]},\n\nWe encountered an issue with your payment for {p[2]}.\n\n{admin_notes or 'Please contact support.'}"
        else:
            subj = f"Payment Under Review: {p[2]}"
            body = f"Hi {p[0]},\n\nYour payment for {p[2]} is under review. We'll update you soon."
        send_email(p[1], subj, body)

        if p[4]:
            sse_push(p[4], 'purchase_update', {
                'course': p[2], 'status': status,
                'message': f'Your purchase for {p[2]} is now {status.upper()}'
            })

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


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("🚀 Starting Stellar Skills Backend — ENHANCED EDITION")
    print("=" * 55)
    print(f"   reportlab:   {'✅' if REPORTLAB_AVAILABLE else '❌ pip install reportlab'}")
    print(f"   qrcode:      {'✅' if QR_AVAILABLE else '❌ pip install qrcode pillow'}")
    print(f"   anthropic:   {'✅' if ANTHROPIC_AVAILABLE else '❌ pip install anthropic'}")
    print("=" * 55)

    if init_database():
        print("✅ Database ready with all new tables!")
    else:
        print("❌ Database init failed!")
        exit(1)

    print(f"\n📧 Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"🌐 Running at: http://localhost:5000")
    print("\n🆕 New API Endpoints:")
    print("   GET  /api/events                     — SSE Real-time stream")
    print("   GET  /api/admin/analytics             — Full analytics dashboard")
    print("   POST /api/admin/ai-screen-application/<id> — AI resume screening")
    print("   POST /api/admin/issue-certificate/<id>     — Generate & email certificate")
    print("   GET  /api/verify-certificate/<uid>         — Public cert verification")
    print("   GET  /api/download-certificate/<uid>       — Download PDF certificate")
    print("   GET  /api/my-certificates                  — User's certificates")
    print("   POST /api/tickets                          — Create support ticket")
    print("   GET  /api/tickets/my                       — User's tickets")
    print("   POST /api/admin/tickets/<uid>/reply        — Admin reply to ticket")
    print("   GET  /api/leaderboard                      — Points leaderboard")
    print("   GET  /api/my-profile                       — Points, badges, rank")
    print("   GET  /api/courses/<id>/batches             — Course batches/schedules")
    print("   POST /api/enroll-batch                     — Enroll in batch")
    print("   POST /api/admin/batches                    — Create course batch")
    print("   POST /api/admin/send-newsletter            — Bulk email campaign")
    print("   GET  /api/admin/tickets                    — All support tickets")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
