📌 Project Overview
Stellar Skills is a fully-featured, production-grade website for Stellar Skills (Pvt) Ltd. — a leading EdTech company that bridges the gap between traditional education and modern technology. The website serves as a complete digital presence: service showcase, team profiles, program enrollment, job applications, media gallery, contact forms, and a full admin management panel.
The entire project is built as a single HTML file with zero frameworks, zero build tools, and zero backend dependencies — making it a remarkable demonstration of advanced frontend engineering.

🏢 Company Information
DetailInfoCompanyStellar Skills (Pvt) Ltd.Founded2020IndustryEdTech / Education TechnologyAddressBlock H3, Phase 2, Johar Town, Lahore, Punjab, PakistanPhone+92-326-5011116 (Mon–Fri, 9AM–6PM PST)Google MapsView on Google Maps
Certifications & Partnerships

✅ ISO 9001:2015 Certified
✅ Microsoft Partner
✅ GDPR Compliant
✅ Accredited Education Provider
✅ Google for Education Partner
✅ AWS Certified

Company Timeline
YearMilestone2020🚀 Company Founded — mission to make quality education accessible to all2021🏫 First School Partnership — launched first smart classroom solution2023🤖 AI Integration — introduced AI-powered learning personalization2025🌍 Global Expansion — reaching students across 50+ countries

🗂️ Website Sections — Complete Breakdown
1. 🚀 Hero Section

Glowing "Transforming Education" badge with rocket icon
Dynamic typing text effect — headline cycles through career roles (Developers, Designers, etc.)
Compelling subheading: "The best way to reach your potential instead of staying stagnant"
Two CTA Buttons: Explore Programs → #programs and Book a Call → #contact
Embedded interactive 3D robot (Spline scene — greeting robot that reacts to user interaction)
AOS fade-right on content, fade-left on 3D visual

2. 🏢 Trusted Clients (Marquee Banner)

Auto-scrolling infinite horizontal marquee of real partner/client logos
Smooth continuous CSS animation using translateX keyframes
5 unique partner logos hosted on GitHub raw assets, duplicated for seamless loop
Logo cards with hover scale + glow effect

3. 🎴 Animated Service Cards (Mouse-Tracking Spotlight)
Four full-size animated cards with real-time cursor glow:

Programs — School — College — University
Each card has a mouseGlow div that follows the cursor using getBoundingClientRect + mousemove
Creates a torch-light spotlight effect unique to each card

4. 🧑‍💼 About Us

Company origin story and mission
Vertical interactive timeline (2020 → 2021 → 2023 → 2025)
Certification & partnership badges grid
Embedded Spline 3D particle system scene
AOS scroll-triggered reveal animations throughout

5. 👥 Team — Meet the Innovators

Azeem Ikhlaq — Managing Director
Syed Sameer Hussain — CEO
Real photos hosted on GitHub
Hover effects with animated reveal of social links

6. 💬 Client Testimonials

Dr. Ahmad Hassan — Principal, Green Valley School
Fatima Ali — Software Developer, Tech Solutions
Maria Rodriguez — HR Director, Global Corp
Card-based layout with quote styling

7. 🧩 Services — Comprehensive Educational Solutions
Six service cards:

K-12 Programs — Enrichment clubs, workshops, curriculum support
Higher Education — Career readiness, AI labs, research projects
Corporate Upskilling — Digital transformation training
Automation & Innovation — Smart classrooms and learning portals
Tech Bootcamps — Intensive coding and technology programs
Analytics & Insights — Data-driven educational performance reporting

8. ⚙️ Educational Automation Platform
Four automation feature highlights:

🎯 Smart Attendance — Facial recognition with real-time reporting
💳 Fee Management — Online payments and automated reminders
📚 LMS Integration — Seamless unified learning management
📊 Analytics Dashboard — Student performance & institutional metrics

Live animated counters (scroll-triggered):

Students Trained | Partner Schools | Success Rate % | Countries Reached

9. 🎓 Programs & Internships (3-Tab Layout)
Summer Bootcamps:

Web Development Bootcamp (12 weeks — HTML, CSS, JS, React, Node.js)
AI/ML Fundamentals (10 weeks — Python, TensorFlow, Machine Learning)
Mobile App Development (React Native & Flutter)

Internships:

Frontend Developer Intern (6 months — real client projects + mentorship)
Backend Developer Intern (Databases, APIs, server-side technologies)
UI/UX Design Intern (User interfaces and experience design)

Workshops:

Startup Weekend (48-hour build-your-startup challenge)
Cybersecurity Basics
Cloud Computing 101 (AWS, Azure, cloud architecture)

"Join Internship" CTA opens a full program application modal
10. 🖼️ Project Gallery (Filterable Media)
Tab filter buttons: All | Videos | Photos
Videos (from GitHub raw assets):
Robotics Workshop · AI Learning Session · Student Projects · Technology Demo · Innovation Lab
Photos:
Smart Classroom · Team Collaboration · Technology Lab · Training Session · Achievement Ceremony
Click any item → opens full-screen lightbox modal · Escape key or backdrop click to close
11. 💼 Careers — Dynamic Job Openings

Jobs rendered dynamically from admin-managed data (JavaScript array)
Each card: title, company, location, type, salary, experience level
Apply Now opens job application modal with the job title pre-filled

12. ❓ FAQ Accordion
Five expandable questions:

Age groups served · Internship duration · Certificate issuance · Fee structure · Curriculum customization

13. 📞 Contact Section

Contact form with full client-side validation (name, email, phone, subject, message)
Visit, Call, and Email info cards
Embedded Google Map with loading state and graceful fallback
Social media icons

14. 🔻 Footer

Company tagline and description
Quick Links (About, Services, Programs, Contact)
Resources (Documentation, Blog, Case Studies, Support)
Newsletter subscription
Copyright © 2025 Stellar Skills (Pvt) Ltd.


🔐 Modals & User Flow System
ModalFieldsSign InUsername/Email, Password + validationSign UpFull Name, Email, Phone, Password, Confirm Password + strength checkJoin ProgramFull Name, Email, Phone, Program Selector, Experience DescriptionApply for JobFull Name, Email, Phone, Program (pre-filled), Experience
All modals support:

Click outside (backdrop) to close
Escape key to close
Real-time field validation with inline error messages


🛡️ Admin Panel (Advanced Secret Feature)
A fully functional password-protected admin panel built in pure JavaScript:

Activation: Secret keyboard shortcut
Escape key closes the panel

TabFunctionalityPost JobCreate listings with: Title, Company, Location, Type, Salary, Experience Level, Description, RequirementsManage JobsView all active job postings + delete any listingApplicationsView all submitted job applicationsUsersView all registered user accounts
Live Theme Switcher: 4 color themes — Purple (default), Blue, Green, Dark Red — applied instantly via CSS variable overrides.

✨ Advanced Technologies & Techniques Used
🎬 Cinematic Loader Animation
The most technically complex feature — a multi-layered animated loading screen:

Concept: Liquid Ink Morphing Synapses
conic-gradient rotating ink disk with 30s loop + blur(60px) atmospheric glow
Animated grain texture via inline SVG feTurbulence filter with grainShift keyframe
Logo: ink-drop reveal animation (scale(0.2) → scale(1.08) → scale(1) with blur clearance)
Brand name: Playfair Display font, transparent with gradient clip-path, shimmer animation at 200% background-size
Tagline: Quicksand font, letter-spacing animate from 0.1em → 0.42em
Progress bar: Worm-track with glowing ::after dot that tracks the bar's right edge
Iris-Out close: clip-path: circle(150%) → circle(0%) over 1.8s with brightness, saturate, blur filter stages
4 iris ring overlays that collapse inward as clip-path closes
Fallback auto-hide at 25s timeout

🖱️ Custom Cursor (Desktop Only)

20px glowing purple/pink gradient circle follows mouse globally
Hover state: 40px transparent ring with border
Click state: scales to 0.8x, turns pink
Touch state: larger ring for tap feedback
Hidden on touch devices via @media (hover: hover) and (pointer: fine)
pointer-events: none so it never blocks clicks

🌐 Spline 3D Model Integration

Two separate Spline scenes embedded as iframes
Hero: Greeting robot — interactive, responds to mouse movement
About: Floating particle system animation
Lazy loading: iframe src injected by JavaScript only when page loads (not in HTML)
Loading spinners shown during Spline initialization

📜 AOS (Animate On Scroll Library)

Scroll-triggered fade-up, fade-right, fade-left animations on all sections
Custom data-aos-duration and data-aos-delay per element
Mobile fix: AOS completely disabled on screens ≤767px via CSS specificity override to prevent invisible content bug

✍️ Typing Text Engine

Pure JavaScript setInterval-based typewriter
Cursor-blink simulation during pause
Character-by-character type → pause → backspace → next word loop

🃏 Mouse-Tracking Glow Cards

mousemove event on each service card
getBoundingClientRect() used to get cursor position relative to card
Radial gradient mouseGlow div repositioned in real-time
Creates a dynamic torch/spotlight effect

📊 IntersectionObserver Counter Animation

IntersectionObserver watches the stats section
On intersection: requestAnimationFrame loop animates numbers from 0 → target
Time-based easing over 2000ms for smooth counting
Fires only once per session

📷 Gallery Lightbox & Filter

Tab buttons toggle .active class and filter .gallery-item elements by data-category
Lightbox modal renders <video> or <img> based on item type
Full-screen overlay with object-fit: contain for perfect display
Escape key global listener + backdrop click both close modal

🗺️ Smart Map Component

Iframe wrapped in container with .loading state class
CSS spinner shown via ::before pseudo-element while map loads
load event removes loading state after 500ms delay
error event replaces iframe with address card + Google Maps deep link

📱 Mobile-First Responsive System

Three breakpoints: 480px, 768px, 1024px
Navigation: hamburger icon → full-screen slide-in drawer from left
overflow: hidden on body when mobile nav is open to prevent background scroll
All grids collapse: repeat(3,1fr) → repeat(2,1fr) → 1fr
Touch interactions: touchstart → scale(0.95), touchend → restore (passive listeners)
AOS disabled on mobile (prevents hidden content on scroll)

🎨 Dynamic CSS Variable Theme System
Complete design token system:
css--primary-color, --secondary-color, --accent-color
--bg-primary, --bg-secondary, --bg-card
--text-primary, --text-secondary
--border-color, --glow-primary, --glow-secondary
--nav-bg, --card-hover, --theme-name
All overridable at runtime via Admin Panel theme switcher.
📜 Scroll-Linked UI

Scroll progress bar: window.scrollY / (document.body.scrollHeight - innerHeight) * 100 → bar width
Nav behavior: Tracks scroll direction; applies .scrolled class with slideDown animation
Smooth scroll: All href="#anchor" links use scrollIntoView({ behavior: 'smooth', block: 'start' })

⌨️ Full Keyboard Accessibility

Escape: Closes all modals, gallery lightbox, admin panel globally
Enter: Activates focused .tab-btn elements
Focus trap awareness in modals

🚀 Performance Engineering

Images use native loading="lazy"
Spline iframes injected lazily (not in initial HTML)
will-change: transform on marquee for GPU layer promotion
Card background images preloaded with new Image() + onload callback; bg-loaded class toggled
All touch listeners use { passive: true } for 60fps scroll
Page load performance tracked: performance.getEntriesByType('navigation')
Global stellarSkills object exported for module-like access


🛠️ Complete Tech Stack
TechnologyVersionUsageHTML5LatestSemantic structure, accessibilityCSS3LatestGrid, Flexbox, animations, variables, clip-path, conic-gradientVanilla JavaScriptES6+All logic — zero dependenciesSpline 3DLatestInteractive embedded 3D scenesAOS.js2.3.1Scroll-triggered entrance animationsFont Awesome6.4.0Complete icon systemGoogle Fonts—Poppins, Playfair Display, QuicksandIntersectionObserver APINativeCounter triggers, lazy loadingrequestAnimationFrameNativeSmooth counter animationsCSS clip-pathNativeIris-out loader animationSVG feTurbulenceNativeAnimated grain textureCSS backdrop-filterNativeGlassmorphism effectsGitHub Pages—Free static site deploymentGitHub Raw—Asset hosting (images, videos)

📂 Project Structure
Web-/
│
└── index.html
└── styles.css
└── script.js

The entire project — 6,674 lines — lives in a three files.



🚀 Getting Started Locally
bash# 1. Clone the repository
git clone https://github.com/ahmed426pixel/Web-.git

# 2. Navigate into the folder
cd Web-

# 3. Open directly in browser
open index.html

# OR use VS Code Live Server extension for hot reload

🏆 Hackathon Achievements Summary
This project was submitted by Ahmad Nisar (Team: One Man Army) to a Web Hackathon, where every aspect was built solo:
AchievementDetails📄 Code Volume6,674 lines in a single file🎬 Animation ComplexityMulti-stage iris-out loader with iris rings, grain, conic gradients🌐 3D Integration2 embedded Spline 3D interactive scenes🖱️ UX PolishCustom cursor with 3 states📱 ResponsivenessFully tested across mobile, tablet, laptop, desktop🔐 Security FeaturePassword-protected admin panel🎨 Design SystemComplete CSS variable token system with 4 live themes⚡ PerformanceLazy loading, passive listeners, GPU-optimized animations🚀 DeploymentLive on GitHub Pages

📄 License & Credits
© 2025 Stellar Skills (Pvt) Ltd. | All Rights Reserved.
Built with ❤️ by Ahmad Nisar — Team: One Man Army
