// ─── Force reveal AOS on mobile ────────────────────────────────────────────────
if (window.innerWidth < 768) {
    document.querySelectorAll('[data-aos]').forEach(function(el) {
        el.removeAttribute('data-aos');
        el.removeAttribute('data-aos-delay');
        el.removeAttribute('data-aos-duration');
        el.style.setProperty('opacity', '1', 'important');
        el.style.setProperty('transform', 'none', 'important');
        el.style.setProperty('transition', 'none', 'important');
        el.style.setProperty('visibility', 'visible', 'important');
    });
}

AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true,
    offset: 0,
    disable: function() { return window.innerWidth < 768; }
});

// ─── Global State ──────────────────────────────────────────────────────────────
let currentUser = null;
let isAdmin = false;
let pendingSignupEmail = '';
let currentApplyJobId = null;
let currentPurchaseCourseId = null;
let currentCourseTab = 'school';
let resumeBase64 = null;
let paymentBase64 = null;

// ─── API Helper ────────────────────────────────────────────────────────────────
async function api(method, url, body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    return res.json();
}

// ─── Custom Cursor ──────────────────────────────────────────────────────────────
const cursor = document.getElementById('customCursor');
let mouseX = 0, mouseY = 0;
let isTouching = false;
let touchTimeout;

if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        updateCursorPosition();
    });
    document.addEventListener('mousedown', () => cursor.classList.add('click'));
    document.addEventListener('mouseup', () => cursor.classList.remove('click'));

    const hoverEls = document.querySelectorAll('a, button, .service-card, .team-member, .interactive-element, .client-logo, .program-card, .animated-service-card, .course-card');
    hoverEls.forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
}

document.addEventListener('touchstart', (e) => {
    isTouching = true;
    cursor.classList.add('touching', 'touch');
    const t = e.touches[0];
    mouseX = t.clientX;
    mouseY = t.clientY;
    updateCursorPosition();
    clearTimeout(touchTimeout);
}, { passive: true });

document.addEventListener('touchmove', (e) => {
    if (isTouching) {
        const t = e.touches[0];
        mouseX = t.clientX;
        mouseY = t.clientY;
        updateCursorPosition();
    }
}, { passive: true });

document.addEventListener('touchend', () => {
    clearTimeout(touchTimeout);
    touchTimeout = setTimeout(() => {
        cursor.classList.remove('touching', 'touch');
        isTouching = false;
    }, 300);
}, { passive: true });

function updateCursorPosition() {
    cursor.style.left = mouseX + 'px';
    cursor.style.top = mouseY + 'px';
}

// ─── Card Animation ─────────────────────────────────────────────────────────────
function initializeCardAnimation() {
    const cardAnimationContainer = document.getElementById('cardAnimationContainer');
    const programsAnimatedCard   = document.getElementById('programsAnimatedCard');
    const schoolAnimatedCard     = document.getElementById('schoolAnimatedCard');
    const collegeAnimatedCard    = document.getElementById('collegeAnimatedCard');
    const universityAnimatedCard = document.getElementById('universityAnimatedCard');

    let hasClicked = false;
    let animationStarted = false;
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        [schoolAnimatedCard, collegeAnimatedCard, universityAnimatedCard].forEach(card => {
            if (card) {
                card.style.opacity = '0';
                card.style.visibility = 'visible';
                card.style.pointerEvents = 'none';
            }
        });
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animationStarted) {
                animationStarted = true;
                setTimeout(() => programsAnimatedCard.classList.add('entrance-animation'), isMobile ? 300 : 100);
            }
        });
    }, { threshold: isMobile ? 0.1 : 0.3, rootMargin: isMobile ? '0px 0px -20px 0px' : '0px 0px -100px 0px' });

    observer.observe(cardAnimationContainer);

    programsAnimatedCard.addEventListener('click', function () {
        if (hasClicked) return;
        hasClicked = true;
        cardAnimationContainer.classList.add('split-animation');

        if (isMobile) {
            setTimeout(() => {
                [schoolAnimatedCard, collegeAnimatedCard, universityAnimatedCard].forEach(card => {
                    if (card) {
                        card.style.opacity = '1';
                        card.style.visibility = 'visible';
                        card.style.pointerEvents = 'auto';
                    }
                });
            }, 100);
        }

        const rect = programsAnimatedCard.getBoundingClientRect();
        createRippleEffect(rect.left + rect.width / 2, rect.top + rect.height / 2);
        if (isMobile && 'vibrate' in navigator) navigator.vibrate(50);
    });

    function handleCardClick(targetSection) {
        if (!hasClicked) return;
        const element = document.querySelector(targetSection);
        if (element) {
            const offset = isMobile ? 80 : 100;
            window.scrollTo({ top: element.getBoundingClientRect().top + window.pageYOffset - offset, behavior: 'smooth' });
        }
        if (isMobile && 'vibrate' in navigator) navigator.vibrate(30);
    }

    schoolAnimatedCard.addEventListener('click', () => handleCardClick('#programs'));
    collegeAnimatedCard.addEventListener('click', () => handleCardClick('#programs'));
    universityAnimatedCard.addEventListener('click', () => handleCardClick('#programs'));
}

function createRippleEffect(x, y) {
    const isMobile = window.innerWidth <= 768;
    const ripple = document.createElement('div');
    ripple.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:${isMobile ? 15 : 20}px;height:${isMobile ? 15 : 20}px;background:radial-gradient(circle,rgba(255,255,255,.8) 0%,transparent 70%);border-radius:50%;transform:translate(-50%,-50%) scale(0);animation:rippleExpand ${isMobile ? '.8s' : '1s'} ease-out forwards;pointer-events:none;z-index:1000;`;
    document.body.appendChild(ripple);
    setTimeout(() => { if (ripple.parentNode) ripple.remove(); }, isMobile ? 800 : 1000);
}

// ─── Loader ─────────────────────────────────────────────────────────────────────
let modelsLoaded = 0;
let modelsErrored = 0;
let loadingTimeout;
const totalModels = document.querySelectorAll('[data-spline-url]').length;

function updateLoadingProgress() {
    const progressBar = document.getElementById('loadingProgress');
    const loaderText  = document.getElementById('loaderStatusText');
    const loaderPct   = document.getElementById('loaderPercent');
    const progress = totalModels > 0 ? Math.round((modelsLoaded / totalModels) * 100) : 100;
    if (progressBar) progressBar.style.width = progress + '%';
    if (loaderText)  loaderText.textContent = totalModels > 0 ? `Loading 3D Models...` : 'Initializing...';
    if (loaderPct)   loaderPct.textContent = progress + '%';
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.classList.add('hide');
        setTimeout(startTypingAnimation, 500);
        setTimeout(() => { loader.style.display = 'none'; }, 1900);
    }
}

function loadSplineModels() {
    const containers = document.querySelectorAll('[data-spline-url]');
    if (!containers.length) { setTimeout(hideLoader, 1000); return; }

    loadingTimeout = setTimeout(() => { hideLoader(); }, 20000);

    containers.forEach((container, index) => {
        const url = container.getAttribute('data-spline-url');
        const iframe = container.querySelector('iframe');
        const loading = container.querySelector('.spline-loading');
        const newIframe = document.createElement('iframe');

        newIframe.src = url;
        newIframe.frameBorder = '0';
        newIframe.loading = 'lazy';
        newIframe.style.cssText = 'width:100%;height:100%;border:none;background:transparent;';

        let hasLoaded = false;
        let retryCount = 0;
        const maxRetries = window.innerWidth <= 768 ? 1 : 2;

        const handleLoad = () => {
            if (hasLoaded) return;
            hasLoaded = true;
            modelsLoaded++;
            if (loading) { loading.style.opacity = '0'; setTimeout(() => { if (loading.parentNode) loading.remove(); }, 300); }
            updateLoadingProgress();
            if (modelsLoaded >= totalModels) { clearTimeout(loadingTimeout); setTimeout(hideLoader, 300); }
        };

        const handleError = () => {
            if (hasLoaded) return;
            if (retryCount < maxRetries) { retryCount++; setTimeout(() => { newIframe.src = url + '?retry=' + retryCount; }, 1000 * retryCount); return; }
            hasLoaded = true;
            modelsErrored++;
            modelsLoaded++;
            updateLoadingProgress();
            if (modelsLoaded >= totalModels) { clearTimeout(loadingTimeout); setTimeout(hideLoader, 300); }
        };

        const iframeTimeout = setTimeout(() => { if (!hasLoaded) handleError(); }, 10000);

        newIframe.onload = () => { clearTimeout(iframeTimeout); handleLoad(); };
        newIframe.onerror = handleError;

        const isMobile = window.innerWidth <= 768;
        const isHero = container.closest('.hero');
        const isAbout = container.closest('.about-visual');
        const delay = isHero ? (isMobile ? 300 : 100) : isAbout ? (isMobile ? 1000 : 500) : (isMobile ? 2000 + index * 500 : 1000 + index * 300);

        setTimeout(() => {
            try { if (iframe) iframe.replaceWith(newIframe); else container.appendChild(newIframe); }
            catch (e) { handleError(); }
        }, delay);
    });
}

// ─── Typing Animation ────────────────────────────────────────────────────────────
const typingTexts = ['Developers', 'Students', 'Educators', 'Innovators', 'Leaders', 'Creators'];
let textIndex = 0, charIndex = 0, isDeleting = false;

function typeText() {
    const el = document.getElementById('typingText');
    if (!el) return;
    const current = typingTexts[textIndex];
    if (!isDeleting) {
        el.textContent = current.substring(0, charIndex + 1);
        charIndex++;
        if (charIndex === current.length) { isDeleting = true; setTimeout(typeText, 2000); return; }
    } else {
        el.textContent = current.substring(0, charIndex - 1);
        charIndex--;
        if (charIndex === 0) { isDeleting = false; textIndex = (textIndex + 1) % typingTexts.length; }
    }
    setTimeout(typeText, isDeleting ? 60 : 120);
}

function startTypingAnimation() { setTimeout(typeText, 1000); }

// ─── Navigation ──────────────────────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
const navLinks = document.querySelectorAll('.nav-link');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const navMenu = document.getElementById('navMenu');

mobileMenuToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    const icon = mobileMenuToggle.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-times');
    document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
});

window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 100);
    const scrollProgress = document.getElementById('scrollProgress');
    const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    scrollProgress.style.width = ((window.scrollY / windowHeight) * 100) + '%';
});

const sections = document.querySelectorAll('section[id]');
function updateActiveLink() {
    const scrollY = window.scrollY + 100;
    sections.forEach(section => {
        const h = section.offsetHeight;
        const top = section.offsetTop - 100;
        const id = section.getAttribute('id');
        if (scrollY > top && scrollY <= top + h) {
            navLinks.forEach(l => l.classList.remove('active'));
            const active = document.querySelector(`.nav-link[href="#${id}"]`);
            if (active) active.classList.add('active');
        }
    });
}
window.addEventListener('scroll', updateActiveLink);

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            navMenu.classList.remove('active');
            const icon = mobileMenuToggle.querySelector('i');
            icon.classList.add('fa-bars');
            icon.classList.remove('fa-times');
            document.body.style.overflow = '';
        }
    });
});

// ─── FAQ Accordion ────────────────────────────────────────────────────────────────
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const item = question.parentElement;
        const isActive = item.classList.contains('active');
        document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
        if (!isActive) item.classList.add('active');
    });
});

// ─── Stat Counter ─────────────────────────────────────────────────────────────────
const statNums = document.querySelectorAll('.stat-number');
let statsAnimated = false;

function animateStats() {
    if (statsAnimated) return;
    const statsContainer = document.querySelector('.stats-container');
    if (!statsContainer) return;
    const rect = statsContainer.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
        statsAnimated = true;
        statNums.forEach(num => {
            const target = parseInt(num.getAttribute('data-target'));
            let count = 0;
            const step = target / 100;
            const interval = setInterval(() => {
                count += step;
                if (count >= target) { count = target; clearInterval(interval); }
                num.textContent = Math.round(count) + (num.getAttribute('data-target') === '95' ? '%' : '+');
            }, 20);
        });
    }
}
window.addEventListener('scroll', animateStats);

// ─── Programs Tabs ────────────────────────────────────────────────────────────────
document.querySelectorAll('.tab-btn[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn[data-tab]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.getElementById(btn.getAttribute('data-tab')).classList.add('active');
    });
});

// ─── Validation ───────────────────────────────────────────────────────────────────
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePhone(phone) {
    return /^[\+]?[1-9][\d]{6,14}$/.test(phone.replace(/\s|-/g, ''));
}

function showError(fieldId, message) {
    const el = document.getElementById(fieldId + 'Error');
    if (el) { el.textContent = message; el.style.display = 'block'; }
}

function hideError(fieldId) {
    const el = document.getElementById(fieldId + 'Error');
    if (el) el.style.display = 'none';
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 50);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, 300);
    }, 3500);
}

function showError2(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification toast-error';
    toast.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 50);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, 300);
    }, 4000);
}

function setLoading(buttonId, loading) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    btn.disabled = loading;
    if (loading) { btn.dataset.originalText = btn.innerHTML; btn.innerHTML = '<span class="spinner-border"></span> Loading...'; }
    else if (btn.dataset.originalText) btn.innerHTML = btn.dataset.originalText;
}

// ─── User Auth UI ─────────────────────────────────────────────────────────────────
function updateNavForUser(user, admin) {
    const authBtn        = document.getElementById('navAuthBtn');
    const userInfo       = document.getElementById('navUserInfo');
    const userName       = document.getElementById('navUserName');
    const navAvatar      = document.getElementById('navUserAvatar');
    const mobileChip     = document.getElementById('navMobileUserChip');
    const mobileAvatar   = document.getElementById('navMobileAvatar');
    const mobileAuthBtn  = document.getElementById('navMobileAuthBtn');

    if (user) {
        // Get initials for avatar
        const initials = user.name
            ? user.name.split(' ').map(w => w[0]).slice(0,2).join('').toUpperCase()
            : '?';

        authBtn.style.display  = 'none';
        userInfo.style.display = 'list-item';
        userName.textContent   = user.name || 'User';
        if (navAvatar)    navAvatar.textContent   = initials;
        if (mobileChip)   mobileChip.style.display = 'flex';
        if (mobileAvatar) mobileAvatar.textContent = initials;
        if (mobileAuthBtn) mobileAuthBtn.style.display = 'none';
    } else {
        authBtn.style.display  = 'list-item';
        userInfo.style.display = 'none';
        if (mobileChip)   mobileChip.style.display  = 'none';
        if (mobileAuthBtn) mobileAuthBtn.style.display = 'flex';
    }
}

async function checkSession() {
    try {
        const data = await api('GET', '/api/check-session');
        if (data.logged_in) {
            currentUser = data.user;
            isAdmin = data.is_admin;
            updateNavForUser(currentUser, isAdmin);
        }
    } catch (e) { /* session check failed silently */ }
}

// ─── Sign In ──────────────────────────────────────────────────────────────────────
async function handleSignIn(e) {
    e.preventDefault();
    const emailField = document.getElementById('signInEmail').value.trim();
    const password   = document.getElementById('signInPassword').value;

    ['signInEmail', 'signInPassword'].forEach(hideError);

    if (!emailField) { showError('signInEmail', 'Please enter your email or username'); return; }
    if (!password)   { showError('signInPassword', 'Please enter your password'); return; }

    setLoading('signInBtn', true);
    try {
        const data = await api('POST', '/api/signin', { email: emailField, password });
        if (data.success) {
            currentUser = data.user;
            isAdmin = data.is_admin;
            updateNavForUser(currentUser, isAdmin);
            showSuccess(data.message);
            closeModal('signInModal');
            document.getElementById('signInForm').reset();
            if (isAdmin) showAdminPanel();
        } else {
            showError('signInPassword', data.message);
        }
    } catch (e) {
        showError('signInPassword', 'Connection error. Please try again.');
    }
    setLoading('signInBtn', false);
}

// ─── Sign Up ──────────────────────────────────────────────────────────────────────
async function handleSignUp(e) {
    e.preventDefault();
    const name            = document.getElementById('signUpName').value.trim();
    const email           = document.getElementById('signUpEmail').value.trim();
    const phone           = document.getElementById('signUpPhone').value.trim();
    const password        = document.getElementById('signUpPassword').value;
    const confirmPassword = document.getElementById('signUpConfirmPassword').value;

    ['signUpName', 'signUpEmail', 'signUpPhone', 'signUpPassword', 'signUpConfirmPassword'].forEach(hideError);

    let isValid = true;
    if (!name)                  { showError('signUpName', 'Please enter your full name'); isValid = false; }
    if (!validateEmail(email))  { showError('signUpEmail', 'Please enter a valid email'); isValid = false; }
    if (!validatePhone(phone))  { showError('signUpPhone', 'Please enter a valid phone number'); isValid = false; }
    if (password.length < 8)    { showError('signUpPassword', 'Password must be at least 8 characters'); isValid = false; }
    if (password !== confirmPassword) { showError('signUpConfirmPassword', 'Passwords do not match'); isValid = false; }
    if (!isValid) return;

    setLoading('signUpBtn', true);
    try {
        const data = await api('POST', '/api/signup', { name, email, phone, password });
        if (data.success) {
            pendingSignupEmail = email;
            closeModal('signUpModal');
            document.getElementById('signUpForm').reset();
            showOTPModal(email);
        } else {
            showError('signUpEmail', data.message);
        }
    } catch (e) {
        showError('signUpEmail', 'Connection error. Please try again.');
    }
    setLoading('signUpBtn', false);
}

// ─── OTP Verification ─────────────────────────────────────────────────────────────
function showOTPModal(email) {
    document.getElementById('otpEmail').textContent = email;
    document.getElementById('otpError').style.display = 'none';
    document.getElementById('otpError').textContent = '';
    // Clear inputs
    document.querySelectorAll('#otpInputs .otp-digit').forEach(i => i.value = '');
    document.getElementById('otpModal').classList.add('active');
    // Setup OTP input navigation
    setupOTPInputs('otpInputs');
    setTimeout(() => { const first = document.querySelector('#otpInputs .otp-digit'); if (first) first.focus(); }, 300);
}

function setupOTPInputs(containerId) {
    const inputs = document.querySelectorAll(`#${containerId} .otp-digit`);
    inputs.forEach((input, i) => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/\D/, '');
            if (this.value && i < inputs.length - 1) inputs[i + 1].focus();
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && i > 0) inputs[i - 1].focus();
        });
        input.addEventListener('paste', function(e) {
            const pasted = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '').slice(0, 6);
            inputs.forEach((inp, idx) => { inp.value = pasted[idx] || ''; });
            e.preventDefault();
        });
    });
}

function getOTPValue(containerId) {
    return Array.from(document.querySelectorAll(`#${containerId} .otp-digit`)).map(i => i.value).join('');
}

async function submitOTP() {
    const otp = getOTPValue('otpInputs');
    const errorEl = document.getElementById('otpError');
    errorEl.style.display = 'none';

    if (otp.length !== 6) { errorEl.textContent = 'Please enter all 6 digits'; errorEl.style.display = 'block'; return; }

    setLoading('verifyOtpBtn', true);
    try {
        const data = await api('POST', '/api/verify-email', { email: pendingSignupEmail, otp });
        if (data.success) {
            closeModal('otpModal');
            showSuccess('Account verified! You can now sign in.');
            showSignInModal();
        } else {
            errorEl.textContent = data.message;
            errorEl.style.display = 'block';
        }
    } catch (e) {
        errorEl.textContent = 'Connection error.';
        errorEl.style.display = 'block';
    }
    setLoading('verifyOtpBtn', false);
}

async function resendOTP() {
    try {
        const data = await api('POST', '/api/resend-verification', { email: pendingSignupEmail });
        if (data.success) showSuccess('New code sent!');
        else showError2(data.message);
    } catch (e) { showError2('Connection error.'); }
}

// ─── Forgot / Reset Password ──────────────────────────────────────────────────────
let forgotEmail = '';

async function sendResetCode() {
    const email = document.getElementById('forgotEmail').value.trim();
    const errorEl = document.getElementById('forgotEmailError');
    errorEl.style.display = 'none';

    if (!validateEmail(email)) { errorEl.textContent = 'Please enter a valid email'; errorEl.style.display = 'block'; return; }

    setLoading('sendResetBtn', true);
    try {
        const data = await api('POST', '/api/forgot-password', { email });
        if (data.success) {
            forgotEmail = email;
            document.getElementById('resetEmailDisplay').textContent = email;
            document.getElementById('forgotStep1').style.display = 'none';
            document.getElementById('forgotStep2').style.display = 'block';
            setupOTPInputs('resetOtpInputs');
            setTimeout(() => { const f = document.querySelector('#resetOtpInputs .otp-digit'); if (f) f.focus(); }, 200);
        } else {
            errorEl.textContent = data.message;
            errorEl.style.display = 'block';
        }
    } catch (e) {
        errorEl.textContent = 'Connection error.';
        errorEl.style.display = 'block';
    }
    setLoading('sendResetBtn', false);
}

async function submitResetPassword() {
    const otp         = getOTPValue('resetOtpInputs');
    const newPw       = document.getElementById('newPassword').value;
    const confirmPw   = document.getElementById('confirmNewPassword').value;
    const errorEl     = document.getElementById('resetError');
    errorEl.style.display = 'none';

    if (otp.length !== 6)    { errorEl.textContent = 'Enter the 6-digit code'; errorEl.style.display = 'block'; return; }
    if (newPw.length < 8)    { errorEl.textContent = 'Password must be at least 8 characters'; errorEl.style.display = 'block'; return; }
    if (newPw !== confirmPw) { errorEl.textContent = 'Passwords do not match'; errorEl.style.display = 'block'; return; }

    setLoading('resetPasswordBtn', true);
    try {
        const data = await api('POST', '/api/reset-password', { email: forgotEmail, otp, newPassword: newPw });
        if (data.success) {
            closeModal('forgotPasswordModal');
            showSuccess('Password reset! You can now sign in.');
            showSignInModal();
        } else {
            errorEl.textContent = data.message;
            errorEl.style.display = 'block';
        }
    } catch (e) {
        errorEl.textContent = 'Connection error.';
        errorEl.style.display = 'block';
    }
    setLoading('resetPasswordBtn', false);
}

// ─── Sign Out ─────────────────────────────────────────────────────────────────────
async function handleSignOut() {
    try { await api('POST', '/api/signout'); } catch (e) {}
    currentUser = null;
    isAdmin = false;
    updateNavForUser(null, false);
    closeAdminPanel();
    showSuccess('Signed out successfully.');
}

// ─── Join Program ─────────────────────────────────────────────────────────────────
async function handleJoinProgram(e) {
    e.preventDefault();
    const name       = document.getElementById('joinName').value.trim();
    const email      = document.getElementById('joinEmail').value.trim();
    const phone      = document.getElementById('joinPhone').value.trim();
    const program    = document.getElementById('joinProgram').value;
    const experience = document.getElementById('joinExperience').value.trim();

    ['joinName', 'joinEmail', 'joinPhone', 'joinProgram', 'joinExperience'].forEach(hideError);

    let isValid = true;
    if (!name)                { showError('joinName', 'Please enter your full name'); isValid = false; }
    if (!validateEmail(email)){ showError('joinEmail', 'Please enter a valid email'); isValid = false; }
    if (!validatePhone(phone)){ showError('joinPhone', 'Please enter a valid phone number'); isValid = false; }
    if (!program)             { showError('joinProgram', 'Please select a program'); isValid = false; }
    if (!experience)          { showError('joinExperience', 'Please describe your experience'); isValid = false; }
    if (!isValid) return;

    setLoading('joinBtn', true);
    try {
        const data = await api('POST', '/api/apply-program', { name, email, phone, program, experience });
        if (data.success) {
            showSuccess(data.message);
            closeModal('joinModal');
            document.getElementById('joinForm').reset();
        } else {
            showError('joinExperience', data.message);
        }
    } catch (e) {
        showError('joinExperience', 'Connection error. Please try again.');
    }
    setLoading('joinBtn', false);
}

// ─── Contact Form ─────────────────────────────────────────────────────────────────
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name    = document.getElementById('name').value.trim();
        const email   = document.getElementById('email').value.trim();
        const phone   = document.getElementById('phone').value.trim();
        const subject = document.getElementById('subject').value.trim();
        const message = document.getElementById('message').value.trim();

        let isValid = true;
        contactForm.querySelectorAll('.form-group').forEach(group => {
            const input = group.querySelector('input, textarea');
            const error = group.querySelector('.error-message');
            if (input && input.hasAttribute('required') && !input.value.trim()) {
                if (error) error.style.display = 'block';
                isValid = false;
            } else {
                if (error) error.style.display = 'none';
            }
        });

        if (!isValid) return;

        const submitBtn = contactForm.querySelector('[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border"></span> Sending...';

        try {
            const data = await api('POST', '/api/contact', { name, email, phone, subject, message });
            if (data.success) {
                showSuccess(data.message);
                contactForm.reset();
            } else {
                showError2(data.message);
            }
        } catch (err) {
            showError2('Connection error. Please try again.');
        }
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Send Message <i class="fas fa-paper-plane"></i>';
    });
}

// ─── Newsletter ───────────────────────────────────────────────────────────────────
async function subscribeNewsletter(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value.trim();
    if (!validateEmail(email)) { showError2('Please enter a valid email address.'); return; }

    try {
        const data = await api('POST', '/api/newsletter', { email });
        if (data.success) { showSuccess(data.message); e.target.reset(); }
        else showError2(data.message);
    } catch (err) { showError2('Connection error.'); }
}

// ─── Jobs ─────────────────────────────────────────────────────────────────────────
async function loadJobs() {
    const grid = document.getElementById('jobsGrid');
    if (!grid) return;

    grid.innerHTML = `<div style="text-align:center;grid-column:1/-1;padding:2rem;"><div class="loader-spinner"></div></div>`;

    try {
        const data = await api('GET', '/api/jobs');
        if (!data.success || !data.jobs.length) {
            grid.innerHTML = `<div style="text-align:center;grid-column:1/-1;padding:3rem;">
                <i class="fas fa-briefcase" style="font-size:3rem;color:var(--text-secondary);opacity:.5;margin-bottom:1rem;display:block;"></i>
                <h3 style="color:var(--text-secondary);">No openings right now</h3>
                <p style="color:var(--text-secondary);opacity:.7;">Check back soon!</p>
            </div>`;
            return;
        }

        grid.innerHTML = data.jobs.map(job => `
            <div class="job-card" data-aos="fade-up">
                <h3 class="job-title">${job.title}</h3>
                <div class="job-company">${job.company}</div>
                <div class="job-details">
                    <div class="job-detail"><i class="fas fa-map-marker-alt"></i> ${job.location}</div>
                    <div class="job-detail"><i class="fas fa-clock"></i> ${job.type}</div>
                    <div class="job-detail"><i class="fas fa-level-up-alt"></i> ${job.experience}</div>
                    ${job.salary ? `<div class="job-detail"><i class="fas fa-dollar-sign"></i> ${job.salary}</div>` : ''}
                </div>
                <div class="job-description">${job.description}</div>
                <div class="job-requirements">
                    <h4>Requirements:</h4>
                    <ul>${(job.requirements || []).map(r => `<li>${r}</li>`).join('')}</ul>
                </div>
                <div class="job-actions">
                    <button class="btn btn-primary" onclick="applyForJob(${job.id}, '${job.title.replace(/'/g, "\\'")}')">
                        Apply Now <i class="fas fa-paper-plane"></i>
                    </button>
                    <div class="job-date">Posted: ${job.posted_date ? new Date(job.posted_date).toLocaleDateString() : 'Recently'}</div>
                </div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `<div style="text-align:center;grid-column:1/-1;padding:2rem;color:var(--text-secondary);">Failed to load jobs.</div>`;
    }
}

function applyForJob(jobId, jobTitle) {
    if (!currentUser) {
        showSuccess('Please sign in to apply.');
        showSignInModal();
        return;
    }
    currentApplyJobId = jobId;
    document.getElementById('applyJobTitle').textContent = `Position: ${jobTitle}`;
    document.getElementById('resumeError').style.display = 'none';
    resumeBase64 = null;
    document.getElementById('resumeFile').value = '';
    document.getElementById('resumePreview').style.display = 'none';
    closeAllModals();
    document.getElementById('jobApplyModal').classList.add('active');
}

function handleResumeSelect(input) {
    const file = input.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
        document.getElementById('resumeError').textContent = 'File must be under 5MB';
        document.getElementById('resumeError').style.display = 'block';
        return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
        resumeBase64 = e.target.result;
        document.getElementById('resumeFileName').textContent = file.name;
        document.getElementById('resumeFileSize').textContent = (file.size / 1024).toFixed(1) + ' KB';
        document.getElementById('resumePreview').style.display = 'flex';
        document.getElementById('resumeError').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function clearResume() {
    resumeBase64 = null;
    document.getElementById('resumeFile').value = '';
    document.getElementById('resumePreview').style.display = 'none';
}

async function submitJobApplication() {
    const errorEl = document.getElementById('resumeError');
    if (!resumeBase64) {
        errorEl.textContent = 'Please upload your resume';
        errorEl.style.display = 'block';
        return;
    }
    setLoading('submitApplicationBtn', true);
    try {
        const data = await api('POST', '/api/apply-job', { job_id: currentApplyJobId, resume: resumeBase64 });
        if (data.success) {
            closeModal('jobApplyModal');
            showSuccess(data.message);
            clearResume();
        } else {
            errorEl.textContent = data.message;
            errorEl.style.display = 'block';
        }
    } catch (e) {
        errorEl.textContent = 'Connection error.';
        errorEl.style.display = 'block';
    }
    setLoading('submitApplicationBtn', false);
}

// ─── Courses ──────────────────────────────────────────────────────────────────────
let allCourses = { school: [], college: [], commercial: [] };

async function loadCourses() {
    const grid = document.getElementById('coursesGrid');
    if (!grid) return;

    try {
        const data = await api('GET', '/api/courses');
        if (data.success) {
            allCourses = data.courses;
            renderCourseTab(currentCourseTab);
        }
    } catch (e) {
        grid.innerHTML = '<p style="text-align:center;color:var(--text-secondary);">Failed to load courses.</p>';
    }
}

function renderCourseTab(tab) {
    currentCourseTab = tab;
    const grid = document.getElementById('coursesGrid');
    if (!grid) return;

    const courses = allCourses[tab] || [];

    if (!courses.length) {
        grid.innerHTML = `<div style="text-align:center;padding:3rem;color:var(--text-secondary);"><i class="fas fa-book" style="font-size:3rem;opacity:.5;display:block;margin-bottom:1rem;"></i><p>No courses available in this category yet.</p></div>`;
        return;
    }

    const categoryIcons = { school: 'fas fa-child', college: 'fas fa-user-graduate', commercial: 'fas fa-industry' };
    const categoryColors = { school: '#4ade80', college: '#60a5fa', commercial: '#f59e0b' };

    grid.innerHTML = courses.map(course => `
        <div class="course-card" data-aos="fade-up">
            <div class="course-card-top" style="background: linear-gradient(135deg, var(--bg-secondary) 0%, ${categoryColors[tab]}15 100%);">
                <div class="course-badge" style="color:${categoryColors[tab]};border-color:${categoryColors[tab]}40;">
                    <i class="${categoryIcons[tab]}"></i> ${course.category.charAt(0).toUpperCase() + course.category.slice(1)}
                </div>
                <h3 class="course-title">${course.title}</h3>
                <p class="course-description">${course.description}</p>
                <div class="course-ideal">
                    <i class="fas fa-users"></i> ${course.ideal_for}
                </div>
            </div>
            <div class="course-features">
                <h4>What You'll Learn</h4>
                <ul>
                    ${(course.features || []).map(f => `<li><i class="fas fa-check" style="color:${categoryColors[tab]};"></i> ${f}</li>`).join('')}
                </ul>
            </div>
            <div class="course-footer">
                <div class="course-price">
                    <span class="price-label">Investment</span>
                    <span class="price-amount">$${course.price.toFixed(2)}</span>
                </div>
                <button class="btn btn-primary course-enroll-btn" onclick="enrollCourse(${course.id}, '${course.title.replace(/'/g, "\\'")}', ${course.price})">
                    Enroll Now <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Course tabs
document.querySelectorAll('.tab-btn[data-course-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn[data-course-tab]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderCourseTab(btn.getAttribute('data-course-tab'));
    });
});

function enrollCourse(courseId, title, price) {
    if (!currentUser) {
        showSuccess('Please sign in to enroll.');
        showSignInModal();
        return;
    }
    currentPurchaseCourseId = courseId;
    document.getElementById('purchaseCourseInfo').innerHTML = `
        <div class="purchase-course-summary">
            <div style="font-size:1.1rem;font-weight:700;margin-bottom:0.25rem;">${title}</div>
            <div class="purchase-price-tag">$${price.toFixed(2)}</div>
        </div>`;
    document.getElementById('purchaseError').style.display = 'none';
    paymentBase64 = null;
    document.getElementById('paymentFile').value = '';
    document.getElementById('paymentPreview').style.display = 'none';
    closeAllModals();
    document.getElementById('purchaseModal').classList.add('active');
}

function handlePaymentSelect(input) {
    const file = input.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
        document.getElementById('purchaseError').textContent = 'File must be under 5MB';
        document.getElementById('purchaseError').style.display = 'block';
        return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
        paymentBase64 = e.target.result;
        document.getElementById('paymentFileName').textContent = file.name;
        document.getElementById('paymentThumb').src = e.target.result;
        document.getElementById('paymentPreview').style.display = 'block';
        document.getElementById('purchaseError').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

function clearPayment() {
    paymentBase64 = null;
    document.getElementById('paymentFile').value = '';
    document.getElementById('paymentPreview').style.display = 'none';
}

async function submitCoursePurchase() {
    const errorEl = document.getElementById('purchaseError');
    if (!paymentBase64) {
        errorEl.textContent = 'Please upload your payment screenshot';
        errorEl.style.display = 'block';
        return;
    }

    // Get price from displayed info
    const priceText = document.querySelector('.purchase-price-tag');
    const amount = priceText ? parseFloat(priceText.textContent.replace('$', '')) : 0;

    setLoading('submitPurchaseBtn', true);
    try {
        const data = await api('POST', '/api/purchase-course', {
            course_id: currentPurchaseCourseId,
            payment_screenshot: paymentBase64,
            payment_amount: amount
        });
        if (data.success) {
            closeModal('purchaseModal');
            showSuccess(data.message);
            clearPayment();
        } else {
            errorEl.textContent = data.message;
            errorEl.style.display = 'block';
        }
    } catch (e) {
        errorEl.textContent = 'Connection error.';
        errorEl.style.display = 'block';
    }
    setLoading('submitPurchaseBtn', false);
}

// ─── Gallery ──────────────────────────────────────────────────────────────────────
function openGalleryModal(element) {
    const modal = document.getElementById('galleryModal');
    const content = document.getElementById('galleryModalContent');

    const video = element.querySelector('video');
    const image = element.querySelector('img');

    if (video) {
        const src = video.querySelector('source').src;
        content.innerHTML = `<video controls autoplay style="max-width:100%;max-height:85vh;border-radius:12px;">
            <source src="${src}" type="video/mp4"></video>`;
    } else if (image) {
        content.innerHTML = `<img src="${image.src}" alt="${image.alt}" style="max-width:100%;max-height:85vh;border-radius:12px;display:block;">`;
    }

    modal.classList.add('active');
}

function closeGalleryModal() {
    const modal = document.getElementById('galleryModal');
    const content = document.getElementById('galleryModalContent');
    const v = content.querySelector('video');
    if (v) v.pause();
    modal.classList.remove('active');
    content.innerHTML = '';
}

// Gallery Tabs
document.addEventListener('DOMContentLoaded', function() {
    const galleryTabs  = document.querySelectorAll('.gallery-tab-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');

    galleryTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            galleryTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const filter = tab.getAttribute('data-gallery-tab');
            galleryItems.forEach(item => {
                if (filter === 'all') item.style.display = 'block';
                else item.style.display = item.getAttribute('data-type') === filter.slice(0, -1) ? 'block' : 'none';
            });
        });
    });
});

// ─── Admin Panel ───────────────────────────────────────────────────────────────────
function showAdminPanel() {
    document.getElementById('adminPanel').classList.add('active');
    loadAdminData();
}

function closeAdminPanel() {
    document.getElementById('adminPanel').classList.remove('active');
}

function loadAdminData() {
    loadAdminJobs();
    loadAdminApplications();
    loadAdminUsers();
    loadAdminCourses();
    loadAdminPurchases();
}

document.querySelectorAll('.admin-nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.admin-nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
        document.getElementById(btn.getAttribute('data-section')).classList.add('active');
    });
});

// Admin Post Job
document.getElementById('jobForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('[type="submit"]');
    btn.disabled = true;

    const body = {
        title:       document.getElementById('jobTitle').value,
        company:     document.getElementById('jobCompany').value,
        location:    document.getElementById('jobLocation').value,
        type:        document.getElementById('jobType').value,
        salary:      document.getElementById('jobSalary').value,
        experience:  document.getElementById('jobExperience').value,
        description: document.getElementById('jobDescription').value,
        requirements: document.getElementById('jobRequirements').value
    };

    try {
        const data = await api('POST', '/api/admin/post-job', body);
        if (data.success) {
            showSuccess(data.message);
            e.target.reset();
            loadAdminJobs();
            loadJobs();
        } else { showError2(data.message); }
    } catch (err) { showError2('Connection error.'); }
    btn.disabled = false;
});

async function loadAdminJobs() {
    const el = document.getElementById('adminJobsList');
    try {
        const data = await api('GET', '/api/admin/get-jobs');
        if (!data.success || !data.jobs.length) {
            el.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-secondary);"><p>No jobs posted yet.</p></div>`;
            return;
        }
        el.innerHTML = data.jobs.map(job => `
            <div class="admin-card">
                <div class="admin-card-header">
                    <div>
                        <h4>${job.title}</h4>
                        <p>${job.company} · ${job.location} · ${job.type}</p>
                    </div>
                    <div class="admin-card-actions">
                        <span class="status-badge ${job.is_active ? 'status-accepted' : 'status-rejected'}">${job.is_active ? 'Active' : 'Inactive'}</span>
                        <button class="btn-icon btn-danger" onclick="adminDeleteJob(${job.id})"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
                <p style="font-size:.875rem;color:var(--text-secondary);">${job.description.substring(0, 120)}...</p>
            </div>
        `).join('');
    } catch (e) { el.innerHTML = '<p style="color:var(--text-secondary)">Failed to load.</p>'; }
}

async function adminDeleteJob(jobId) {
    if (!confirm('Delete this job posting?')) return;
    const data = await api('DELETE', `/api/admin/delete-job/${jobId}`);
    if (data.success) { showSuccess(data.message); loadAdminJobs(); loadJobs(); }
    else showError2(data.message);
}

async function loadAdminApplications() {
    const el = document.getElementById('applicationsList');
    try {
        const data = await api('GET', '/api/admin/applications');
        if (!data.success || !data.applications.length) {
            el.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-secondary);"><p>No applications yet.</p></div>`;
            return;
        }
        el.innerHTML = data.applications.map(app => `
            <div class="admin-card">
                <div class="admin-card-header">
                    <div>
                        <h4>${app.name}</h4>
                        <p>${app.email} · ${app.phone || 'No phone'}</p>
                        ${app.job_title ? `<p style="color:var(--primary-color);font-size:.875rem;">Job: ${app.job_title}</p>` : ''}
                        ${app.program ? `<p style="color:var(--primary-color);font-size:.875rem;">Program: ${app.program}</p>` : ''}
                    </div>
                    <div class="admin-card-actions">
                        <select onchange="adminUpdateApplication(${app.id}, this.value)" class="admin-select">
                            <option value="pending"  ${app.status==='pending'  ? 'selected' : ''}>Pending</option>
                            <option value="reviewed" ${app.status==='reviewed' ? 'selected' : ''}>Reviewed</option>
                            <option value="accepted" ${app.status==='accepted' ? 'selected' : ''}>Accepted</option>
                            <option value="rejected" ${app.status==='rejected' ? 'selected' : ''}>Rejected</option>
                        </select>
                        <button class="btn-icon btn-danger" onclick="adminDeleteApplication(${app.id})"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
                ${app.experience ? `<p style="font-size:.875rem;color:var(--text-secondary);">${app.experience.substring(0, 150)}...</p>` : ''}
                <div style="font-size:.75rem;color:var(--text-secondary);margin-top:.5rem;">Applied: ${app.applied_at ? new Date(app.applied_at).toLocaleDateString() : 'Unknown'}</div>
                ${app.resume ? `
                <div style="margin-top:.75rem;">
                    <button onclick="openFileInNewTab('${app.resume}')" style="display:inline-flex;align-items:center;gap:.4rem;padding:.4rem .9rem;font-size:.78rem;font-weight:600;border-radius:20px;border:1.5px solid var(--primary-color);background:transparent;color:var(--primary-color);cursor:pointer;font-family:inherit;" onmouseover="this.style.background='var(--primary-color)';this.style.color='#fff'" onmouseout="this.style.background='transparent';this.style.color='var(--primary-color)'">
                        <i class="fas fa-file-alt"></i> View Resume / CV
                    </button>
                </div>` : ''}
            </div>
        `).join('');
    } catch (e) { el.innerHTML = '<p style="color:var(--text-secondary)">Failed to load.</p>'; }
}

async function adminUpdateApplication(appId, status) {
    const data = await api('PUT', `/api/admin/update-application/${appId}`, { status, admin_notes: '' });
    if (data.success) showSuccess(data.message);
    else showError2(data.message);
}

async function adminDeleteApplication(appId) {
    if (!confirm('Delete this application?')) return;
    const data = await api('DELETE', `/api/admin/delete-application/${appId}`);
    if (data.success) { showSuccess(data.message); loadAdminApplications(); }
    else showError2(data.message);
}

async function loadAdminUsers() {
    const el = document.getElementById('usersList');
    try {
        const data = await api('GET', '/api/admin/users');
        if (!data.success || !data.users.length) {
            el.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-secondary);"><p>No users yet.</p></div>`;
            return;
        }
        el.innerHTML = data.users.map(user => `
            <div class="admin-card">
                <div class="admin-card-header">
                    <div>
                        <h4>${user.name} ${user.is_admin ? '<span class="status-badge status-accepted">Admin</span>' : ''}</h4>
                        <p>${user.email} · ${user.phone || 'No phone'}</p>
                        <div style="margin-top:.25rem;">
                            <span class="status-badge ${user.email_verified ? 'status-accepted' : 'status-rejected'}">${user.email_verified ? 'Verified' : 'Unverified'}</span>
                        </div>
                    </div>
                    ${!user.is_admin ? `
                    <div class="admin-card-actions">
                        <button class="btn-icon btn-danger" onclick="adminDeleteUser(${user.id})"><i class="fas fa-trash"></i></button>
                    </div>` : ''}
                </div>
                <div style="font-size:.75rem;color:var(--text-secondary);">Joined: ${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}</div>
            </div>
        `).join('');
    } catch (e) { el.innerHTML = '<p style="color:var(--text-secondary)">Failed to load.</p>'; }
}

async function adminDeleteUser(userId) {
    if (!confirm('Delete this user?')) return;
    const data = await api('DELETE', `/api/admin/delete-user/${userId}`);
    if (data.success) { showSuccess(data.message); loadAdminUsers(); }
    else showError2(data.message);
}

// Admin Courses
document.getElementById('courseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('[type="submit"]');
    btn.disabled = true;

    const body = {
        title:       document.getElementById('courseTitle').value,
        category:    document.getElementById('courseCategory').value,
        description: document.getElementById('courseDescription').value,
        features:    document.getElementById('courseFeatures').value,
        ideal_for:   document.getElementById('courseIdealFor').value,
        price:       document.getElementById('coursePrice').value
    };

    try {
        const data = await api('POST', '/api/admin/add-course', body);
        if (data.success) {
            showSuccess(data.message);
            e.target.reset();
            loadAdminCourses();
            loadCourses();
        } else showError2(data.message);
    } catch (err) { showError2('Connection error.'); }
    btn.disabled = false;
});

async function loadAdminCourses() {
    const el = document.getElementById('adminCoursesList');
    try {
        const data = await api('GET', '/api/admin/courses');
        if (!data.success || !data.courses.length) {
            el.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-secondary);"><p>No courses yet.</p></div>`;
            return;
        }
        el.innerHTML = data.courses.map(c => `
            <div class="admin-card">
                <div class="admin-card-header">
                    <div>
                        <h4>${c.title}</h4>
                        <p style="text-transform:capitalize;">${c.category} · $${c.price.toFixed(2)}</p>
                        <p style="font-size:.875rem;color:var(--text-secondary);">${c.ideal_for}</p>
                    </div>
                    <div class="admin-card-actions">
                        <span class="status-badge ${c.is_active ? 'status-accepted' : 'status-rejected'}">${c.is_active ? 'Active' : 'Inactive'}</span>
                        <button class="btn-icon btn-danger" onclick="adminDeleteCourse(${c.id})"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (e) { el.innerHTML = '<p style="color:var(--text-secondary)">Failed to load.</p>'; }
}

async function adminDeleteCourse(courseId) {
    if (!confirm('Delete this course?')) return;
    const data = await api('DELETE', `/api/admin/delete-course/${courseId}`);
    if (data.success) { showSuccess(data.message); loadAdminCourses(); loadCourses(); }
    else showError2(data.message);
}

// Admin Purchases
async function loadAdminPurchases() {
    const el = document.getElementById('purchasesList');
    try {
        const data = await api('GET', '/api/admin/purchases');
        if (!data.success || !data.purchases.length) {
            el.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-secondary);"><p>No purchases yet.</p></div>`;
            return;
        }
        el.innerHTML = data.purchases.map(p => `
            <div class="admin-card">
                <div class="admin-card-header">
                    <div>
                        <h4>${p.course_title}</h4>
                        <p>${p.user_name} · ${p.user_email}</p>
                        <p style="color:var(--primary-color);font-weight:600;">$${p.payment_amount.toFixed(2)} · ${p.course_category}</p>
                    </div>
                    <div class="admin-card-actions">
                        <select onchange="adminApprovePurchase(${p.id}, this.value)" class="admin-select">
                            <option value="pending"  ${p.status==='pending'  ? 'selected' : ''}>Pending</option>
                            <option value="approved" ${p.status==='approved' ? 'selected' : ''}>Approved</option>
                            <option value="rejected" ${p.status==='rejected' ? 'selected' : ''}>Rejected</option>
                        </select>
                    </div>
                </div>
                <div style="font-size:.75rem;color:var(--text-secondary);">
                    Purchased: ${p.purchased_at ? new Date(p.purchased_at).toLocaleDateString() : 'Unknown'}
                </div>
                ${p.payment_screenshot ? `<div style="margin-top:.75rem;">
                    <img src="${p.payment_screenshot}" alt="Payment" style="max-height:120px;border-radius:8px;cursor:pointer;display:block;" onclick="openFileInNewTab('${p.payment_screenshot}')" title="Click to open in new tab">
                    <div style="font-size:.7rem;color:var(--text-secondary);margin-top:.3rem;"><i class="fas fa-external-link-alt"></i> Click image to open in new tab</div>
                </div>` : ''}
            </div>
        `).join('');
    } catch (e) { el.innerHTML = '<p style="color:var(--text-secondary)">Failed to load.</p>'; }
}

async function adminApprovePurchase(purchaseId, status) {
    const data = await api('PUT', `/api/admin/approve-purchase/${purchaseId}`, { status, admin_notes: '' });
    if (data.success) showSuccess(data.message);
    else showError2(data.message);
}

// ─── Open base64 file in new tab ───────────────────────────────────────────────
function openFileInNewTab(dataUri) {
    try {
        // Extract base64 data and mime type
        const matches = dataUri.match(/^data:([^;]+);base64,(.+)$/);
        if (!matches) {
            // If it's a plain URL just open it
            window.open(dataUri, '_blank');
            return;
        }
        const mimeType = matches[1];
        const base64Data = matches[2];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: mimeType });
        const blobUrl = URL.createObjectURL(blob);
        const win = window.open(blobUrl, '_blank');
        if (win) {
            // Revoke after a short delay to free memory
            setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
        }
    } catch (err) {
        console.error('Failed to open file:', err);
        showError2('Could not open file. It may be corrupted or too large.');
    }
}

// ─── Modal Helpers ─────────────────────────────────────────────────────────────────
function showSignInModal() {
    closeAllModals();
    document.getElementById('signInModal').classList.add('active');
}

function showSignUpModal() {
    closeAllModals();
    document.getElementById('signUpModal').classList.add('active');
}

function showJoinModal() {
    closeAllModals();
    document.getElementById('joinModal').classList.add('active');
}

function closeModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.remove('active');
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
}

// Click outside to close
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            if (modal.classList.contains('modal-gallery')) closeGalleryModal();
            else modal.classList.remove('active');
        }
    });
});

// ─── Page Transitions & Smooth Scrolling ──────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

const pageTransition = document.querySelector('.page-transition');
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        if (link.getAttribute('href') !== '#') {
            if (pageTransition) {
                pageTransition.classList.add('active');
                setTimeout(() => pageTransition.classList.remove('active'), 500);
            }
        }
    });
});

// Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAllModals();
        closeGalleryModal();
        closeAdminPanel();
    }
    if (e.key === 'Enter' && e.target.classList.contains('tab-btn')) e.target.click();
});

// ─── Image Optimization ───────────────────────────────────────────────────────────
function optimizeImages() {
    document.querySelectorAll('img[src*="github"], img[src*="drive.google"]').forEach(img => {
        if (!img.hasAttribute('loading')) img.setAttribute('loading', 'lazy');
        img.addEventListener('error', function() { this.style.opacity = '0.3'; });
        img.addEventListener('load',  function() { this.style.opacity = '1'; this.style.transition = 'opacity .3s'; });
    });
}

// ─── Service Backgrounds ──────────────────────────────────────────────────────────
function initializeServiceBackgrounds() {
    document.querySelectorAll('.service-card, .program-card').forEach(card => {
        card.classList.add('bg-loaded');
    });
}

// ─── Map ──────────────────────────────────────────────────────────────────────────
function initializeMap() {
    const mapContainer = document.querySelector('.map-container');
    if (!mapContainer) return;
    const iframe = mapContainer.querySelector('iframe');
    if (!iframe) return;
    mapContainer.classList.add('loading');
    iframe.addEventListener('load', () => setTimeout(() => mapContainer.classList.remove('loading'), 500));
    iframe.addEventListener('error', () => { mapContainer.classList.remove('loading'); });
}

// ─── Touch Interactions ───────────────────────────────────────────────────────────
function optimizeTouchInteractions() {
    document.querySelectorAll('.btn, .service-card, .program-card, .team-member, .course-card').forEach(el => {
        el.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.97)';
            this.style.transition = 'transform .1s ease';
        }, { passive: true });
        el.addEventListener('touchend', function() {
            setTimeout(() => { this.style.transform = ''; this.style.transition = 'all .3s ease'; }, 150);
        }, { passive: true });
        el.addEventListener('touchcancel', function() {
            this.style.transform = '';
        }, { passive: true });
    });
}

// ─── Fallback loader ──────────────────────────────────────────────────────────────
setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader && !loader.classList.contains('hide')) hideLoader();
}, 25000);

// ─── Performance ─────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
    setTimeout(() => {
        if ('performance' in window) {
            const perf = performance.getEntriesByType('navigation')[0];
            if (perf) console.log('Page load:', Math.round(perf.loadEventEnd - perf.loadEventStart) + 'ms');
        }
    }, 0);
});

// ─── Init ─────────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    updateLoadingProgress();
    loadSplineModels();
    optimizeImages();
    setTimeout(initializeServiceBackgrounds, 500);
    setTimeout(initializeCardAnimation, 100);
    setTimeout(initializeMap, 1000);
    optimizeTouchInteractions();
    loadJobs();
    loadCourses();
    console.log('✅ Stellar Skills fully initialized!');
});

// Export
window.stellarSkills = {
    showSignInModal, showSignUpModal, showJoinModal, closeAllModals, applyForJob, enrollCourse
};
