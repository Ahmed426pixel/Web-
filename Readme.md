📌 Project Overview
Stellar Skills is a fully-featured, production-grade full-stack web application for Stellar Skills (Pvt) Ltd. — a leading EdTech company bridging the gap between traditional education and modern technology. The website serves as a complete digital presence: service showcase, team profiles, program enrollment, course purchases, job applications, media gallery, contact forms, a comprehensive admin management panel, and an advanced engagement platform featuring gamification, real-time notifications, AI-powered recruitment, digital certificates, support ticketing, course scheduling, and bulk email campaigns. The project is built across four files (HTML, CSS, JavaScript, Python) — a polished vanilla frontend powered by a Flask REST API backend with SQLite, real email delivery, server-side session authentication, and optional Anthropic Claude AI and PDF generation integrations. The codebase was built solo by Ahmad Nisar (Team: One Man Army).

🏢 Company Information
DetailInfoCompanyStellar Skills (Pvt) Ltd.Founded2020IndustryEdTech / Education TechnologyAddressBlock H3, Phase 2, Johar Town, Lahore, Punjab, PakistanPhone+92-326-5011116 (Mon–Fri, 9AM–6PM PST)
Certifications: ISO 9001:2015 · Microsoft Partner · GDPR Compliant · Google for Education Partner · AWS Certified · Accredited Education Provider

🗂️ Website Sections
Hero — Dynamic typing text cycling through career roles, glowing badge, two CTA buttons, and an embedded interactive Spline 3D greeting robot with AOS animations.
Trusted Clients — Infinite auto-scrolling marquee of real partner logos with GPU-promoted CSS translateX animation.
Animated Service Cards — Four mouse-tracking spotlight cards (Programs · School · College · University) using getBoundingClientRect + mousemove for a real-time torch-glow effect.
About Us — Company story, vertical interactive timeline (2020–2025), certification badges, and an embedded Spline 3D particle scene.
Team — Azeem Ikhlaq (Managing Director) and Syed Sameer Hussain (CEO) with hover-revealed social links.
Testimonials — Three client cards with quote styling.
Services — Six cards: K-12 Programs, Higher Education, Corporate Upskilling, Automation & Innovation, Tech Bootcamps, Analytics & Insights.
Automation Platform — Four smart-classroom feature highlights with live scroll-triggered animated counters (Students Trained · Partner Schools · Success Rate · Countries).
Programs & Internships — 3-tab layout (Bootcamps / Internships / Workshops) with a program application modal connected to the backend.
Courses — Three tier categories (School · College · Commercial) dynamically loaded from the database, each with a full payment-screenshot upload and purchase flow. Approved students can view and enroll in available course batches/schedules.
Gallery — Filterable media grid (All · Videos · Photos) with full-screen lightbox modal.
Careers — Job listings loaded live from the database, each with an authenticated apply modal and resume/CV upload. AI screening runs automatically on submission.
FAQ — Five expandable accordion questions.
Contact — Validated contact form, info cards, embedded Google Map, social links — backed by real email delivery.
Footer — Quick links, resources, newsletter subscription.

🔐 Authentication & User Flow
Full server-side session authentication powered by Flask + Werkzeug:

Sign Up — OTP email verification (6-digit code, 10-minute expiry) before account creation
Sign In — Email or username login with hashed password check; supports "admin" shorthand
Forgot Password — OTP-based reset flow with expiry validation
Resend OTP — Refresh verification or reset codes
Session persistence — /api/check-session restores login state on page load, reconnects SSE stream
Sign Out — Clears server-side session and disconnects real-time event stream

All modals support click-outside and Escape-to-close with real-time inline validation. Multi-language support (English · Urdu · Arabic) via request lang parameter, with full translation fallback.

🛡️ Admin Panel
A fully protected admin panel accessible to admin accounts, with 10 tabs:
TabFunctionalityPost JobCreate listings: Title, Company, Location, Type, Salary, Experience, Description, RequirementsManage JobsView, toggle active/inactive, delete any listingApplicationsView all submissions with resume/CV viewer, update status (Pending → Reviewed → Accepted → Rejected), AI score badge, run AI screening on demand🤖 AI ScreeningDedicated tab: full applicant list with AI match scores, one-click AI analysis modal (score/100, strengths, gaps, suggested interview questions, powered by Claude AI)UsersView all registered accounts, delete non-admin usersCoursesAdd / delete course tiers (School · College · Commercial), manage course batches/schedulesPurchasesView payment screenshot submissions with inline image preview, approve or reject with automated email notification, issue PDF certificates to approved students📊 AnalyticsLive dashboard: total users, jobs, applications, revenue, conversion rate, daily signups chart, daily revenue chart, applications by status, top courses by enrollment, points leaderboard🎫 TicketsView all support tickets, reply to tickets, update ticket status (Open → In Progress → Resolved)📧 CampaignsBulk email sender targeting newsletter subscribers, verified users, or all users; 4 quick-fill templates (New Course, Special Offer, Event, Update)

⚙️ Backend — Flask REST API
Runtime: Python 3, Flask, Flask-CORS, Werkzeug
Database: SQLite (stellar_skills.db) with 15 tables:
TablePurposeusersRegistered accounts with hashed passwords and admin flagemail_verificationPending OTP records with expirypassword_resetReset OTP records with expiryjobsJob listings with active/inactive toggleapplicationsJob and program applications with status, AI score, and AI reportcoursesCourse catalog by category (school / college / commercial)course_purchasesPayment screenshot submissions with approval workflowcontactsContact form submissionsnewsletterEmail subscriber listcertificatesIssued PDF certificates with unique UIDs and public verificationsupport_ticketsUser support tickets with category, priority, and statusticket_repliesAdmin and user replies per ticketuser_pointsGamification point log per user eventuser_badgesEarned achievement badges per usercourse_batchesScheduled course cohorts with seats, dates, instructorbatch_enrollmentsStudent enrollment records per batch
Email: Real SMTP delivery via Gmail for OTP verification, welcome emails, application confirmations, purchase updates, certificate delivery (as PDF attachment), ticket reply notifications, and admin notifications.
Optional integrations:

anthropic — Claude AI for automated resume screening (graceful demo fallback if key not set)
reportlab + qrcode + Pillow — PDF certificate generation with QR code verification (graceful fallback if not installed)


🌐 API Endpoints (35+)
Auth
POST /api/signup · POST /api/verify-email · POST /api/resend-verification · POST /api/signin · POST /api/signout · POST /api/forgot-password · POST /api/reset-password · GET /api/check-session
Public
GET /api/jobs · GET /api/courses · POST /api/contact · POST /api/newsletter · GET /api/leaderboard · GET /api/verify-certificate/<uid>
Authenticated Users
POST /api/apply-job · POST /api/apply-program · POST /api/purchase-course · GET /api/my-certificates · GET /api/download-certificate/<uid> · POST /api/tickets · GET /api/tickets/my · GET /api/tickets/<uid>/replies · GET /api/my-profile · GET /api/courses/<id>/batches · POST /api/enroll-batch · GET /api/events (SSE stream)
Admin
GET /api/admin/analytics · GET /api/admin/get-jobs · POST /api/admin/post-job · DELETE /api/admin/delete-job/<id> · PUT /api/admin/toggle-job/<id> · GET /api/admin/applications · PUT /api/admin/update-application/<id> · DELETE /api/admin/delete-application/<id> · POST /api/admin/ai-screen-application/<id> · GET /api/admin/ai-report/<id> · GET /api/admin/users · DELETE /api/admin/delete-user/<id> · GET /api/admin/courses · POST /api/admin/add-course · DELETE /api/admin/delete-course/<id> · GET /api/admin/purchases · PUT /api/admin/approve-purchase/<id> · POST /api/admin/issue-certificate/<id> · GET /api/admin/tickets · POST /api/admin/tickets/<uid>/reply · POST /api/admin/batches · POST /api/admin/send-newsletter
Auth decorators: @login_required and @admin_required protect all sensitive routes.

✨ Advanced Frontend Features
Cinematic Loader — Multi-layered: conic-gradient ink disk, SVG feTurbulence grain overlay, iris-out clip-path close with 4 collapsing ring overlays, logo ink-drop reveal, shimmer brand name, animated progress bar with glowing tracker dot. Auto-fallback at 25s.
Custom Cursor — 20px glowing gradient circle (desktop only) with hover, click, and touch states. Uses event delegation so cursor hover works correctly inside all dynamically loaded content including the admin panel. pointer-events: none prevents interaction blocking. z-index 999999 ensures always-on-top visibility.
Real-Time Notifications (SSE) — Persistent EventSource connection per logged-in user. Push events: points earned, badge unlocked, certificate issued, application status update, purchase update, ticket reply, AI screening complete, new job, new course. Auto-reconnects after 5s on error. Styled toast banners with purple left-border and WiFi icon.
Gamification System — Points awarded for: signup (50), job apply (100), course purchase (200), contact form (25), newsletter (30). 8 achievement badges (Pioneer, Early Bird, Explorer, Learner, Achiever, Champion, Communicator, Subscriber). Points and new badges delivered via real-time SSE toast. Points badge displayed live in the nav bar. Public leaderboard and personal profile modal (rank, total points, badges, activity log).
AI Resume Screening — On job application, Claude AI automatically screens the resume in a background thread, scores it 0–100, and delivers the result via SSE. Admin can also trigger re-screening on demand from both the Applications tab and the dedicated AI Screening tab. Report modal shows: score ring, recommendation badge, executive summary, strengths, gaps, and suggested interview questions. Falls back to demo mode if API key is not set.
PDF Certificates — Admin issues certificates from the Purchases tab. ReportLab generates a landscape A4 PDF with gradient background, decorative triple border, student name in italic, course details, completion date, unique certificate ID, director signature line, and a QR code linking to a public verification page. Certificate is emailed to the student as an attachment. Users can download their certificates from their profile.
Support Ticket System — Users open tickets from a modal with category (General, Technical, Billing, Course, Other) and priority (Normal, High, Urgent). Admin replies from the Tickets tab with status updates. Users see reply threads per ticket. Ticket reply triggers SSE notification to the user.
Course Batch Scheduling — Admin creates batch cohorts per course (name, start/end dates, max seats, instructor, schedule). After purchase approval, users can enroll in available batches. Enrollment is confirmed via SSE push event.
Bulk Email Campaigns — Admin selects audience (newsletter subscribers, verified users, or all users), writes subject and body, and sends with one click. Four quick-fill templates: New Course, Special Offer, Event, Announcement.
Analytics Dashboard — Live overview: total users, jobs, applications, revenue, conversion rate. Charts: daily signups (7-day bar chart), daily revenue (7-day), applications by status (colour-coded), top courses by enrollment, points leaderboard top 5.
Global Admin File Store — Base64 resume and payment screenshot data is stored in a JavaScript memory map keyed by short IDs. onclick handlers reference only the key, preventing HTML attribute overflow errors that caused files to silently fail to open.
Spline 3D Integration — Two lazy-loaded interactive scenes: greeting robot (hero) and particle system (about).
Typing Text Engine — Pure JS typewriter cycling through career roles with cursor-blink simulation.
Mouse-Tracking Glow Cards — Real-time radial-gradient spotlight on service cards using getBoundingClientRect.
IntersectionObserver Counters — requestAnimationFrame easing over 2000ms, fires once per session.
AOS Animations — Scroll-triggered fade-in on all sections; fully disabled on ≤767px to prevent invisible-content bugs.
Scroll-Linked UI — Scroll progress bar, nav scroll-direction tracking with slideDown animation, smooth anchor scrolling.
Mobile-First Responsive — Three breakpoints (480px · 768px · 1024px), hamburger drawer nav, touch feedback with passive listeners.
Dynamic CSS Variable Theme System — Full design token set (--primary-color, --bg-primary, --glow-primary, etc.) overridable at runtime. Default theme: Purple.
Toast Notification System — Two variants: success (green) and error (red), plus a distinct real-time SSE variant (purple left-border). All auto-dismiss after 3–5 seconds.
Ripple Effect — Click-anywhere ripple on both desktop and mobile with size adaptation.

🗄️ Database — 16 Tables
users · email_verification · password_reset · jobs · applications · courses · course_purchases · contacts · newsletter · certificates · support_tickets · ticket_replies · user_points · user_badges · course_batches · batch_enrollments
All tables use foreign keys with CASCADE rules. Migration function runs at every startup to safely add missing columns to existing databases without data loss.

🛠️ Tech Stack
TechnologyUsageHTML5 / CSS3Semantic structure, Grid, Flexbox, clip-path, conic-gradient, backdrop-filterVanilla JS (ES6+)All frontend logic — zero frameworksPython 3 / FlaskREST API backend, session management, routing, SSESQLitePersistent local database (16 tables)WerkzeugPassword hashing and securityFlask-CORSCross-origin request handlingSMTP / GmailReal transactional email with attachment supportAnthropic Claude AIAutomated resume screening and scoringReportLabPDF certificate generationqrcode + PillowQR code embedding in certificatesSpline 3DInteractive embedded 3D scenesAOS.js 2.3.1Scroll-triggered entrance animationsFont Awesome 6.4.0Icon systemGoogle FontsPoppins, Playfair Display, QuicksandGitHub RawAsset hosting (images, videos)

📂 Project Structure
Web-/
├── index.html   — Complete frontend UI (1,661 lines)
├── styles.css   — Full design system & animations (4,662 lines)
├── script.js    — Frontend logic & API integration (2,464 lines)
└── app.py       — Flask backend, REST API, database, email, AI, PDF (2,393 lines)

🚀 Getting Started
bash# 1. Clone the repository
git clone https://github.com/ahmed426pixel/Web-.git
cd Web-

# 2. Install Python dependencies
pip install flask flask-cors werkzeug reportlab qrcode pillow anthropic

# 3. (Optional) Set Anthropic API key for real AI screening
set ANTHROPIC_API_KEY=your-key-here

# 4. Start the backend
python app.py

# 5. Open in browser
http://localhost:5000

🏆 Achievements Summary
AchievementDetails🏗️ ArchitectureFull-stack: Flask API + SQLite + SMTP + Vanilla JS frontend🔐 Auth SystemOTP email verification, hashed passwords, server-side sessions📧 Email IntegrationReal transactional emails for all user actions including PDF attachments⚡ Real-Time EngineServer-Sent Events (SSE) push notifications for 10+ event types🤖 AI RecruitmentClaude AI automated resume screening with score, strengths, gaps, interview questions🎓 Certificate SystemReportLab PDF generation with QR code, unique UID, public verification, email delivery🎫 Support SystemFull ticketing with categories, priorities, admin replies, SSE notifications🏅 GamificationPoints engine, 8 badges, leaderboard, personal profile dashboard📅 Course SchedulingBatch system with seat management, enrollment, SSE confirmation📢 Email CampaignsBulk sender with audience segmentation and 4 quick templates📊 AnalyticsLive dashboard with 6 KPIs, 4 chart views, revenue tracking, leaderboard🛒 Purchase FlowCourse payment screenshot upload with admin approval and certificate issuance🎬 Animation ComplexityMulti-stage iris-out loader with iris rings, grain, conic gradients🌐 3D Integration2 embedded Spline 3D interactive scenes🖱️ UX PolishCustom cursor with 3 states + event delegation, mouse-tracking spotlight cards📱 ResponsivenessFully tested across mobile, tablet, laptop, desktop🗄️ Database16 normalized tables with foreign keys, cascade rules, and safe auto-migration🌍 InternationalizationUrdu and Arabic translation layer with per-request language switching

© 2025 Stellar Skills (Pvt) Ltd. | All Rights Reserved. Built with ❤️ by Ahmad Nisar — Team: One Man Army
