📌 Project Overview
Stellar Skills is a fully-featured, production-grade full-stack web application for Stellar Skills (Pvt) Ltd. — a leading EdTech company bridging the gap between traditional education and modern technology. The website serves as a complete digital presence: service showcase, team profiles, program enrollment, course purchases, job applications, media gallery, contact forms, and a comprehensive admin management panel.
The project is built across four files (HTML, CSS, JavaScript, Python) — a polished vanilla frontend powered by a Flask REST API backend with a SQLite database, real email delivery, and server-side session authentication. The codebase was built solo by Ahmad Nisar (Team: One Man Army).

🏢 Company Information
DetailInfoCompanyStellar Skills (Pvt) Ltd.Founded2020IndustryEdTech / Education TechnologyAddressBlock H3, Phase 2, Johar Town, Lahore, Punjab, PakistanPhone+92-326-5011116 (Mon–Fri, 9AM–6PM PST)
Certifications: ISO 9001:2015 · Microsoft Partner · GDPR Compliant · Google for Education Partner · AWS Certified · Accredited Education Provider

🗂️ Website Sections
Hero — Dynamic typing text, glowing badge, two CTA buttons, and an embedded interactive Spline 3D robot with AOS animations.
Trusted Clients — Infinite auto-scrolling marquee of real partner logos with CSS translateX animation.
Animated Service Cards — Four mouse-tracking spotlight cards (Programs · School · College · University) using getBoundingClientRect + mousemove for a real-time torch-glow effect.
About Us — Company story, vertical interactive timeline (2020–2025), certification badges, and embedded Spline 3D particle scene.
Team — Azeem Ikhlaq (Managing Director) and Syed Sameer Hussain (CEO) with hover-revealed social links.
Testimonials — Three client cards with quote styling.
Services — Six cards: K-12 Programs, Higher Education, Corporate Upskilling, Automation & Innovation, Tech Bootcamps, Analytics & Insights.
Automation Platform — Four smart-classroom highlights with live scroll-triggered animated counters (Students Trained · Partner Schools · Success Rate · Countries).
Programs & Internships — 3-tab layout (Bootcamps / Internships / Workshops) with a program application modal connected to the backend.
Courses — Three tier categories (School · College · Commercial) dynamically loaded from the database, with a full payment-screenshot upload and purchase flow.
Gallery — Filterable media grid (All · Videos · Photos) with full-screen lightbox modal.
Careers — Job listings loaded live from the database, each with an authenticated apply modal and resume upload.
FAQ — Five expandable accordion questions.
Contact — Validated contact form, info cards, embedded Google Map, social links — all backed by real email delivery.
Footer — Quick links, resources, newsletter subscription.

🔐 Authentication & User Flow
Full server-side session authentication powered by Flask + Werkzeug:

Sign Up — OTP email verification (6-digit code, 10-minute expiry) before account creation
Sign In — Email or username login with hashed password check; supports "admin" shorthand
Forgot Password — OTP-based reset flow with expiry validation
Resend OTP — Refresh verification or reset codes
Session persistence — /api/check-session restores login state on page load
Sign Out — Clears server-side session

All modals support click-outside and Escape-to-close with real-time inline validation.

🛡️ Admin Panel
A fully functional, protected admin panel accessible via secret keyboard shortcut:
TabFunctionalityPost JobCreate listings: Title, Company, Location, Type, Salary, Experience, Description, RequirementsManage JobsView, toggle active/inactive, delete any listingApplicationsView all submissions, update status (Pending → Reviewed → Accepted → Rejected), add notes, auto-email applicantsUsersView all registered accounts, delete non-admin usersCoursesAdd / delete course tiers (School · College · Commercial)PurchasesView payment screenshot submissions, approve or reject with automated email notification
Live Theme Switcher: 4 color themes (Purple · Blue · Green · Dark Red) via CSS variable overrides.

⚙️ Backend — Flask REST API
Runtime: Python 3, Flask, Flask-CORS, Werkzeug
Database: SQLite (stellar_skills.db) with 8 tables:
TablePurposeusersRegistered accounts with hashed passwords and admin flagemail_verificationPending OTP records with expirypassword_resetReset OTP records with expiryjobsJob listings with active/inactive toggleapplicationsJob and program applications with status trackingcoursesCourse catalog by category (school / college / commercial)course_purchasesPayment screenshot submissions with approval workflowcontactsContact form submissionsnewsletterEmail subscriber list
Email: Real SMTP delivery via Gmail for OTP verification, welcome emails, application confirmations, purchase updates, and admin notifications.
API Endpoints (20+):
/api/signup · /api/verify-email · /api/resend-verification · /api/signin · /api/signout · /api/forgot-password · /api/reset-password · /api/check-session · /api/jobs · /api/apply-job · /api/apply-program · /api/courses · /api/purchase-course · /api/contact · /api/newsletter · /api/admin/* (jobs, applications, users, courses, purchases)
Auth decorators: @login_required and @admin_required protect all sensitive routes.

✨ Advanced Frontend Features
Cinematic Loader — Multi-layered: conic-gradient ink disk, SVG feTurbulence grain, iris-out clip-path close with 4 collapsing ring overlays, logo ink-drop reveal, shimmer brand name, animated progress bar with glowing tracker dot. Auto-fallback at 25s.
Custom Cursor — 20px glowing gradient circle (desktop only) with hover, click, and touch states. pointer-events: none prevents blocking.
Spline 3D Integration — Two lazy-loaded interactive scenes: greeting robot (hero) and particle system (about).
Typing Text Engine — Pure JS typewriter cycling through career roles with cursor-blink simulation.
Mouse-Tracking Glow Cards — Real-time radial-gradient spotlight on service cards using getBoundingClientRect.
IntersectionObserver Counters — requestAnimationFrame easing over 2000ms, fires once per session.
AOS Animations — Scroll-triggered fade-in/out on all sections; fully disabled on ≤767px to prevent invisible-content bugs.
Scroll-Linked UI — Progress bar, nav scroll-direction tracking with slideDown animation, smooth anchor scrolling.
Mobile-First Responsive — Three breakpoints (480px · 768px · 1024px), hamburger drawer nav, touch feedback with passive listeners.
Dynamic CSS Variable Theme System — Full design token set (--primary-color, --bg-primary, --glow-primary, etc.) overridable at runtime.
Performance Engineering — Native lazy images, GPU-promoted marquee (will-change: transform), lazy Spline iframe injection, passive touch listeners, performance.getEntriesByType tracking.

🛠️ Tech Stack
TechnologyUsageHTML5 / CSS3Semantic structure, Grid, Flexbox, clip-path, conic-gradient, backdrop-filterVanilla JS (ES6+)All frontend logic — zero frameworksPython 3 / FlaskREST API backend, session management, routingSQLitePersistent local database (8 tables)WerkzeugPassword hashing and securityFlask-CORSCross-origin request handlingSMTP / GmailReal transactional email deliverySpline 3DInteractive embedded 3D scenesAOS.js 2.3.1Scroll-triggered entrance animationsFont Awesome 6.4.0Icon systemGoogle FontsPoppins, Playfair Display, QuicksandGitHub RawAsset hosting (images, videos)GitHub PagesFrontend deployment

📂 Project Structure
Web-/
├── index.html     — Complete frontend UI
├── styles.css     — Full design system & animations
├── script.js      — Frontend logic & API integration
└── app.py         — Flask backend, REST API, database, email

🚀 Getting Started
bash# 1. Clone the repository
git clone https://github.com/ahmed426pixel/Web-.git
cd Web-

# 2. Install Python dependencies
pip install flask flask-cors werkzeug

# 3. Start the backend
python app.py

# 4. Open in browser
http://localhost:5000

🏆 Achievements Summary
AchievementDetails🏗️ ArchitectureFull-stack: Flask API + SQLite + SMTP + Vanilla JS frontend🔐 Auth SystemOTP email verification, hashed passwords, server-side sessions📧 Email IntegrationReal transactional emails for all user actions🛒 Purchase FlowCourse payment screenshot upload with admin approval workflow🎬 Animation ComplexityMulti-stage iris-out loader with iris rings, grain, conic gradients🌐 3D Integration2 embedded Spline 3D interactive scenes🖱️ UX PolishCustom cursor with 3 states, mouse-tracking spotlight cards📱 ResponsivenessFully tested across mobile, tablet, laptop, desktop🗄️ Database8 normalized tables with foreign keys and cascade rules🎨 Design SystemCSS variable token system with 4 live switchable themes

© 2025 Stellar Skills (Pvt) Ltd. | All Rights Reserved. Built with ❤️ by Ahmad Nisar — Team: One Man Army
