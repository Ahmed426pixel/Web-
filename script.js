// Admin Credentials (Frontend Only)
const ADMIN_CREDENTIALS = {
   username: 'admin',
   password: 'admin'
};

// Force reveal all AOS elements on mobile BEFORE AOS initializes so nothing stays hidden
if (window.innerWidth < 768) {
   document.querySelectorAll('[data-aos]').forEach(function(el) {
       el.removeAttribute('data-aos');
       el.removeAttribute('data-aos-delay');
       el.removeAttribute('data-aos-duration');
       el.removeAttribute('data-aos-offset');
       el.style.setProperty('opacity', '1', 'important');
       el.style.setProperty('transform', 'none', 'important');
       el.style.setProperty('transition', 'none', 'important');
       el.style.setProperty('visibility', 'visible', 'important');
   });
}

// Initialize AOS (disabled on mobile since we handle it above)
AOS.init({
   duration: 800,
   easing: 'ease-in-out',
   once: true,
   offset: 0,
   disable: function() {
       return window.innerWidth < 768;
   }
});

// Global Data Storage
let userData = {
   users: [],
   applications: [],
   contacts: [],
   newsletters: [],
   jobs: [
       {
           id: 1,
           title: 'Frontend Developer',
           company: 'Stellar Skills',
           location: 'Lahore, Pakistan',
           type: 'Full-time',
           salary: '$40,000 - $60,000',
           experience: 'Mid Level',
           description: 'We are looking for a skilled Frontend Developer to join our team and help build amazing user interfaces for our educational platform.',
           requirements: [
               'Bachelor\'s degree in Computer Science or related field',
               '3+ years of experience with React.js',
               'Strong knowledge of HTML, CSS, and JavaScript',
               'Experience with responsive design',
               'Familiarity with version control (Git)'
           ],
           postedDate: new Date().toISOString().split('T')[0]
       },
       {
           id: 2,
           title: 'UI/UX Designer',
           company: 'Stellar Skills',
           location: 'Remote',
           type: 'Full-time',
           salary: '$35,000 - $50,000',
           experience: 'Entry Level',
           description: 'Join our design team to create intuitive and engaging user experiences for our educational technology products.',
           requirements: [
               'Bachelor\'s degree in Design or related field',
               'Proficiency in Figma and Adobe Creative Suite',
               '2+ years of UI/UX design experience',
               'Strong portfolio showcasing web and mobile designs',
               'Understanding of user-centered design principles'
           ],
           postedDate: new Date().toISOString().split('T')[0]
       }
   ]
};

let currentUser = null;
let isAdmin = false;

// Custom Cursor
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

   const hoverElements = document.querySelectorAll('a, button, .service-card, .team-member, .interactive-element, .client-logo, .program-card, .animated-service-card');
   hoverElements.forEach(el => {
       el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
       el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
   });
}

document.addEventListener('touchstart', (e) => {
   isTouching = true;
   cursor.classList.add('touching', 'touch');
   const touch = e.touches[0];
   mouseX = touch.clientX;
   mouseY = touch.clientY;
   updateCursorPosition();
   clearTimeout(touchTimeout);
}, { passive: true });

document.addEventListener('touchmove', (e) => {
   if (isTouching) {
       const touch = e.touches[0];
       mouseX = touch.clientX;
       mouseY = touch.clientY;
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

// Card Animation
function initializeCardAnimation() {
   const cardAnimationContainer = document.getElementById('cardAnimationContainer');
   const programsAnimatedCard = document.getElementById('programsAnimatedCard');
   const schoolAnimatedCard = document.getElementById('schoolAnimatedCard');
   const collegeAnimatedCard = document.getElementById('collegeAnimatedCard');
   const universityAnimatedCard = document.getElementById('universityAnimatedCard');

   let hasClicked = false;
   let animationStarted = false;
   const isMobile = window.innerWidth <= 768;

   if (isMobile) {
       [schoolAnimatedCard, collegeAnimatedCard, universityAnimatedCard].forEach((card, index) => {
           if (card) {
               card.style.opacity = '0';
               card.style.visibility = 'visible';
               card.style.pointerEvents = 'none';
           }
       });
   }

   const observerOptions = {
       threshold: isMobile ? 0.1 : 0.3,
       rootMargin: isMobile ? '0px 0px -20px 0px' : '0px 0px -100px 0px'
   };

   const observer = new IntersectionObserver((entries) => {
       entries.forEach(entry => {
           if (entry.isIntersecting && !animationStarted) {
               animationStarted = true;
               const delay = isMobile ? 300 : 100;
               setTimeout(() => {
                   programsAnimatedCard.classList.add('entrance-animation');
               }, delay);
           }
       });
   }, observerOptions);

   observer.observe(cardAnimationContainer);

   programsAnimatedCard.addEventListener('click', function(e) {
       if (hasClicked) return;
       hasClicked = true;
       cardAnimationContainer.classList.add('split-animation');

       if (isMobile) {
           setTimeout(() => {
               [schoolAnimatedCard, collegeAnimatedCard, universityAnimatedCard].forEach((card, index) => {
                   if (card) {
                       card.style.opacity = '1';
                       card.style.visibility = 'visible';
                       card.style.pointerEvents = 'auto';
                   }
               });
           }, 100);
       }

       const rect = programsAnimatedCard.getBoundingClientRect();
       createRippleEffect(rect.left + rect.width/2, rect.top + rect.height/2);

       if (isMobile && 'vibrate' in navigator) {
           navigator.vibrate(50);
       }
   });

   function handleCardClick(targetSection) {
       if (hasClicked) {
           const element = document.querySelector(targetSection);
           if (element) {
               const offset = isMobile ? 80 : 100;
               const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
               const targetPosition = elementPosition - offset;

               window.scrollTo({
                   top: targetPosition,
                   behavior: 'smooth'
               });
           }

           if (isMobile && 'vibrate' in navigator) {
               navigator.vibrate(30);
           }
       }
   }

   schoolAnimatedCard.addEventListener('click', () => handleCardClick('#programs'));
   collegeAnimatedCard.addEventListener('click', () => handleCardClick('#programs'));
   universityAnimatedCard.addEventListener('click', () => handleCardClick('#programs'));
}

function createRippleEffect(x, y) {
   const isMobile = window.innerWidth <= 768;
   const ripple = document.createElement('div');

   ripple.style.position = 'fixed';
   ripple.style.left = x + 'px';
   ripple.style.top = y + 'px';
   ripple.style.width = isMobile ? '15px' : '20px';
   ripple.style.height = isMobile ? '15px' : '20px';
   ripple.style.background = 'radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%)';
   ripple.style.borderRadius = '50%';
   ripple.style.transform = 'translate(-50%, -50%) scale(0)';
   ripple.style.animation = `rippleExpand ${isMobile ? '0.8s' : '1s'} ease-out forwards`;
   ripple.style.pointerEvents = 'none';
   ripple.style.zIndex = '1000';

   document.body.appendChild(ripple);

   setTimeout(() => {
       if (ripple.parentNode) {
           ripple.remove();
       }
   }, isMobile ? 800 : 1000);
}

// Loader Management
let modelsLoaded = 0;
let modelsErrored = 0;
let loadingTimeout;
const totalModels = document.querySelectorAll('[data-spline-url]').length;

function updateLoadingProgress() {
   const progressBar = document.getElementById('loadingProgress');
   const loaderText = document.querySelector('.loader-text');
   const progress = totalModels > 0 ? Math.round((modelsLoaded / totalModels) * 100) : 100;

   if (progressBar) {
       progressBar.style.width = progress + '%';
   }

   if (loaderText) {
       if (totalModels > 0) {
           loaderText.textContent = `Loading 3D Models... ${progress}%`;
       } else {
           loaderText.textContent = 'Initializing...';
       }
   }
}

function hideLoader() {
   const loader = document.getElementById('loader');
   if (loader) {
       loader.classList.add('hide');
       setTimeout(() => {
           startTypingAnimation();
       }, 500);
       setTimeout(() => {
           loader.style.display = 'none';
       }, 1900);
   }
}

function loadSplineModels() {
   const splineContainers = document.querySelectorAll('[data-spline-url]');

   if (splineContainers.length === 0) {
       setTimeout(hideLoader, 1000);
       return;
   }

   const timeoutDuration = 20000;
   loadingTimeout = setTimeout(() => {
       console.log('Spline loading timeout reached');
       hideLoader();
   }, timeoutDuration);

   splineContainers.forEach((container, index) => {
       const url = container.getAttribute('data-spline-url');
       const iframe = container.querySelector('iframe');
       const loading = container.querySelector('.spline-loading');
       const newIframe = document.createElement('iframe');

       newIframe.src = url;
       newIframe.frameBorder = '0';
       newIframe.loading = 'lazy';
       newIframe.style.cssText = `
           width: 100%;
           height: 100%;
           border: none;
           background: transparent;
           transform: translateZ(0);
           will-change: transform;
       `;

       let hasLoaded = false;
       let retryCount = 0;
       const maxRetries = window.innerWidth <= 768 ? 1 : 2;

       const handleLoad = function() {
           if (hasLoaded) return;
           hasLoaded = true;

           modelsLoaded++;

           if (loading) {
               loading.style.opacity = '0';
               setTimeout(() => {
                   if (loading.parentNode) {
                       loading.remove();
                   }
               }, 300);
           }

           updateLoadingProgress();

           if (modelsLoaded >= totalModels) {
               clearTimeout(loadingTimeout);
               setTimeout(hideLoader, 300);
           }
       };

       const handleError = function() {
           if (hasLoaded) return;

           if (retryCount < maxRetries) {
               retryCount++;
               console.log(`Retrying Spline model ${index + 1}, attempt ${retryCount}`);
               setTimeout(() => {
                   newIframe.src = url + '?retry=' + retryCount;
               }, 1000 * retryCount);
               return;
           }

           hasLoaded = true;
           modelsErrored++;

           if (loading) {
               const isMobile = window.innerWidth <= 768;
               loading.innerHTML = `
                   <div style="
                       display: flex;
                       flex-direction: column;
                       align-items: center;
                       justify-content: center;
                       color: var(--text-secondary);
                       font-size: ${isMobile ? '0.75rem' : '0.875rem'};
                       height: 100%;
                       text-align: center;
                       padding: 1rem;
                   ">
                       <i class="fas fa-cube" style="font-size: ${isMobile ? '1.5rem' : '2rem'}; margin-bottom: 0.5rem; opacity: 0.3;"></i>
                       <div>3D Content Loading...</div>
                       ${isMobile ? '<div style="font-size: 0.625rem; margin-top: 0.25rem; opacity: 0.7;">May take a moment on mobile</div>' : ''}
                   </div>
               `;
           }

           modelsLoaded++;
           updateLoadingProgress();

           if (modelsLoaded >= totalModels) {
               clearTimeout(loadingTimeout);
               setTimeout(hideLoader, 300);
           }
       };

       const iframeTimeout = setTimeout(() => {
           if (!hasLoaded) {
               console.log(`Spline model ${index + 1} timeout`);
               handleError();
           }
       }, 10000);

       newIframe.onload = function() {
           clearTimeout(iframeTimeout);
           handleLoad();
       };

       newIframe.onerror = handleError;

       const isHeroModel = container.closest('.hero');
       const isAboutModel = container.closest('.about-visual');
       const isMobile = window.innerWidth <= 768;

       let delay = 0;
       if (isHeroModel) {
           delay = isMobile ? 300 : 100;
       } else if (isAboutModel) {
           delay = isMobile ? 1000 : 500;
       } else {
           delay = isMobile ? 2000 + (index * 500) : 1000 + (index * 300);
       }

       setTimeout(() => {
           try {
               if (iframe) {
                   iframe.replaceWith(newIframe);
               } else {
                   container.appendChild(newIframe);
               }
           } catch (error) {
               console.error('Error loading Spline model:', error);
               handleError();
           }
       }, delay);
   });
}

// Typing Animation
const typingTexts = ['Developers', 'Students', 'Educators', 'Innovators', 'Leaders', 'Creators'];
let textIndex = 0;
let charIndex = 0;
let isDeleting = false;
const typingSpeed = 120;
const deletingSpeed = 60;
const pauseTime = 2000;

function typeText() {
   const currentText = typingTexts[textIndex];
   const typingElement = document.getElementById('typingText');

   if (!typingElement) return;

   if (!isDeleting) {
       typingElement.textContent = currentText.substring(0, charIndex + 1);
       charIndex++;

       if (charIndex === currentText.length) {
           isDeleting = true;
           setTimeout(typeText, pauseTime);
           return;
       }
   } else {
       typingElement.textContent = currentText.substring(0, charIndex - 1);
       charIndex--;

       if (charIndex === 0) {
           isDeleting = false;
           textIndex = (textIndex + 1) % typingTexts.length;
       }
   }

   setTimeout(typeText, isDeleting ? deletingSpeed : typingSpeed);
}

function startTypingAnimation() {
   setTimeout(typeText, 1000);
}

// Navigation
const navbar = document.getElementById('navbar');
const navLinks = document.querySelectorAll('.nav-link');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const navMenu = document.getElementById('navMenu');

mobileMenuToggle.addEventListener('click', () => {
   navMenu.classList.toggle('active');
   const icon = mobileMenuToggle.querySelector('i');
   icon.classList.toggle('fa-bars');
   icon.classList.toggle('fa-times');
});

window.addEventListener('scroll', () => {
   if (window.scrollY > 100) {
       navbar.classList.add('scrolled');
   } else {
       navbar.classList.remove('scrolled');
   }

   const scrollProgress = document.getElementById('scrollProgress');
   const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
   const scrolled = (window.scrollY / windowHeight) * 100;
   scrollProgress.style.width = scrolled + '%';
});

const sections = document.querySelectorAll('section[id]');

function updateActiveLink() {
   const scrollY = window.scrollY + 100;

   sections.forEach(section => {
       const sectionHeight = section.offsetHeight;
       const sectionTop = section.offsetTop - 100;
       const sectionId = section.getAttribute('id');

       if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
           navLinks.forEach(link => {
               link.classList.remove('active');
               if (link.getAttribute('href') === '#' + sectionId) {
                   link.classList.add('active');
               }
           });
       }
   });
}

window.addEventListener('scroll', updateActiveLink);

function scrollToTop() {
   window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Stats Animation
const statNumbers = document.querySelectorAll('.stat-number');
let hasAnimated = false;

function animateStats() {
   statNumbers.forEach(stat => {
       const target = parseInt(stat.getAttribute('data-target'));
       const increment = target / 50;
       let current = 0;

       const updateNumber = () => {
           if (current < target) {
               current += increment;
               stat.textContent = Math.ceil(current);
               setTimeout(updateNumber, 30);
           } else {
               stat.textContent = target + (stat.parentElement.querySelector('.stat-label').textContent.includes('%') ? '' : '+');
           }
       };

       updateNumber();
   });
}

const observerOptions = {
   threshold: 0.1,
   rootMargin: window.innerWidth < 768 ? '0px 0px 0px 0px' : '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
   entries.forEach(entry => {
       if (entry.isIntersecting) {
           if (entry.target.classList.contains('stats-container') && !hasAnimated) {
               animateStats();
               hasAnimated = true;
           }
           entry.target.style.opacity = '1';
           entry.target.style.transform = 'translateY(0)';
       }
   });
}, observerOptions);

document.querySelectorAll('.stats-container, .service-card, .timeline-item').forEach(el => {
   if (window.innerWidth < 768) {
       // On mobile: show everything immediately, no scroll-triggered hiding
       el.style.opacity = '1';
       el.style.transform = 'none';
       el.style.transition = 'all 0.6s ease';
       // Trigger counter animation for stats-container on mobile since observer is skipped
       if (el.classList.contains('stats-container') && !hasAnimated) {
           hasAnimated = true;
           setTimeout(animateStats, 300);
       }
   } else {
       el.style.opacity = '0';
       el.style.transform = 'translateY(30px)';
       el.style.transition = 'all 0.6s ease';
       observer.observe(el);
   }
});

// Tabs
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(btn => {
   btn.addEventListener('click', () => {
       const tabId = btn.getAttribute('data-tab');

       tabButtons.forEach(b => b.classList.remove('active'));
       btn.classList.add('active');

       tabContents.forEach(content => {
           content.classList.remove('active');
           if (content.id === tabId) {
               content.classList.add('active');
           }
       });
   });
});

// FAQ
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
   const question = item.querySelector('.faq-question');

   question.addEventListener('click', () => {
       faqItems.forEach(otherItem => {
           if (otherItem !== item) {
               otherItem.classList.remove('active');
           }
       });
       item.classList.toggle('active');
   });
});

// Form Validation
function validateEmail(email) {
   const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
   return emailRegex.test(email);
}

function validatePhone(phone) {
   const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
   return phoneRegex.test(phone.replace(/\s/g, ''));
}

function validatePassword(password) {
   return password.length >= 8;
}

function showError(fieldId, message) {
   const errorElement = document.getElementById(fieldId + 'Error');
   if (errorElement) {
       errorElement.textContent = message;
       errorElement.style.display = 'block';
   }
}

function hideError(fieldId) {
   const errorElement = document.getElementById(fieldId + 'Error');
   if (errorElement) {
       errorElement.style.display = 'none';
   }
}

function showSuccess(message) {
   const toast = document.createElement('div');
   toast.style.cssText = `
       position: fixed;
       top: 20px;
       right: 20px;
       background: var(--primary-color);
       color: white;
       padding: 1rem 2rem;
       border-radius: 10px;
       z-index: 10000;
       animation: slideIn 0.3s ease;
       box-shadow: 0 10px 30px rgba(0,0,0,0.3);
       max-width: calc(100vw - 40px);
       font-size: ${window.innerWidth <= 768 ? '0.875rem' : '1rem'};
   `;
   toast.textContent = message;
   document.body.appendChild(toast);

   setTimeout(() => {
       toast.style.animation = 'slideOut 0.3s ease';
       setTimeout(() => {
           if (toast.parentNode) {
               toast.remove();
           }
       }, 300);
   }, 3000);
}

function setLoading(buttonId, isLoading) {
   const button = document.getElementById(buttonId);
   if (isLoading) {
       button.classList.add('loading');
       button.disabled = true;
   } else {
       button.classList.remove('loading');
       button.disabled = false;
   }
}

// User Authentication
function handleSignIn(e) {
   e.preventDefault();
   setLoading('signInBtn', true);

   const emailField = document.getElementById('signInEmail').value.trim();
   const password = document.getElementById('signInPassword').value;

   hideError('signInEmail');
   hideError('signInPassword');

   let isValid = true;

   if (!emailField) {
       showError('signInEmail', 'Please enter your username or email');
       isValid = false;
   }

   if (!password) {
       showError('signInPassword', 'Please enter your password');
       isValid = false;
   }

   if (isValid) {
       setTimeout(() => {
           // Check for admin credentials: username=admin, password=admin
           if ((emailField === ADMIN_CREDENTIALS.username || emailField === 'admin') && password === ADMIN_CREDENTIALS.password) {
               isAdmin = true;
               currentUser = { name: 'Admin', email: emailField, role: 'admin' };
               showSuccess('Welcome Admin!');
               closeModal('signInModal');
               document.getElementById('signInForm').reset();
               showAdminPanel();
           } else {
               showError('signInPassword', 'Invalid username or password');
           }

           setLoading('signInBtn', false);
       }, 800);
   } else {
       setLoading('signInBtn', false);
   }
}

function handleSignUp(e) {
   e.preventDefault();
   setLoading('signUpBtn', true);

   const name = document.getElementById('signUpName').value;
   const email = document.getElementById('signUpEmail').value;
   const phone = document.getElementById('signUpPhone').value;
   const password = document.getElementById('signUpPassword').value;
   const confirmPassword = document.getElementById('signUpConfirmPassword').value;

   ['signUpName', 'signUpEmail', 'signUpPhone', 'signUpPassword', 'signUpConfirmPassword'].forEach(hideError);

   let isValid = true;

   if (!name.trim()) {
       showError('signUpName', 'Please enter your full name');
       isValid = false;
   }

   if (!validateEmail(email)) {
       showError('signUpEmail', 'Please enter a valid email address');
       isValid = false;
   }

   if (!validatePhone(phone)) {
       showError('signUpPhone', 'Please enter a valid phone number');
       isValid = false;
   }

   if (!validatePassword(password)) {
       showError('signUpPassword', 'Password must be at least 8 characters long');
       isValid = false;
   }

   if (password !== confirmPassword) {
       showError('signUpConfirmPassword', 'Passwords do not match');
       isValid = false;
   }

   if (isValid) {
       setTimeout(() => {
           showSuccess('Account created successfully! We\'ll be in touch soon.');
           closeModal('signUpModal');
           document.getElementById('signUpForm').reset();
           setLoading('signUpBtn', false);
       }, 800);
   } else {
       setLoading('signUpBtn', false);
   }
}

function handleJoinProgram(e) {
   e.preventDefault();
   setLoading('joinBtn', true);

   const name = document.getElementById('joinName').value;
   const email = document.getElementById('joinEmail').value;
   const phone = document.getElementById('joinPhone').value;
   const program = document.getElementById('joinProgram').value;
   const experience = document.getElementById('joinExperience').value;

   ['joinName', 'joinEmail', 'joinPhone', 'joinProgram', 'joinExperience'].forEach(hideError);

   let isValid = true;

   if (!name.trim()) {
       showError('joinName', 'Please enter your full name');
       isValid = false;
   }

   if (!validateEmail(email)) {
       showError('joinEmail', 'Please enter a valid email address');
       isValid = false;
   }

   if (!validatePhone(phone)) {
       showError('joinPhone', 'Please enter a valid phone number');
       isValid = false;
   }

   if (!program) {
       showError('joinProgram', 'Please select a program');
       isValid = false;
   }

   if (!experience.trim()) {
       showError('joinExperience', 'Please describe your experience');
       isValid = false;
   }

   if (isValid) {
       setTimeout(() => {
           showSuccess('Application submitted successfully! We will review your application and get back to you within 2-3 business days.');
           closeModal('joinModal');
           document.getElementById('joinForm').reset();
           setLoading('joinBtn', false);
       }, 800);
   } else {
       setLoading('joinBtn', false);
   }
}

// Contact Form
const contactForm = document.getElementById('contactForm');
contactForm.addEventListener('submit', (e) => {
   e.preventDefault();

   const name = document.getElementById('name').value;
   const email = document.getElementById('email').value;
   const phone = document.getElementById('phone').value;
   const subject = document.getElementById('subject').value;
   const message = document.getElementById('message').value;

   let isValid = true;
   const formGroups = contactForm.querySelectorAll('.form-group');

   formGroups.forEach(group => {
       const input = group.querySelector('input, textarea');
       const error = group.querySelector('.error-message');

       if (input && input.hasAttribute('required') && !input.value.trim()) {
           if (error) error.style.display = 'block';
           isValid = false;
       } else {
           if (error) error.style.display = 'none';
       }

       if (input && input.type === 'email' && input.value) {
           if (!validateEmail(input.value)) {
               if (error) error.style.display = 'block';
               isValid = false;
           }
       }
   });

   if (isValid) {
       showSuccess('Thank you for your message! We will get back to you within 24 hours.');
       contactForm.reset();
   }
});

// Newsletter
function subscribeNewsletter(e) {
   e.preventDefault();
   const email = e.target.querySelector('input[type="email"]').value;

   if (validateEmail(email)) {
       showSuccess('Thank you for subscribing to our newsletter!');
       e.target.reset();
   } else {
       showSuccess('Please enter a valid email address.');
   }
}

// Job Management
function loadJobs() {
   const jobsGrid = document.getElementById('jobsGrid');
   if (!jobsGrid) return;

   if (userData.jobs.length === 0) {
       jobsGrid.innerHTML = `
           <div style="text-align: center; grid-column: 1 / -1; padding: 3rem;">
               <i class="fas fa-briefcase" style="font-size: 3rem; color: var(--text-secondary); opacity: 0.5; margin-bottom: 1rem;"></i>
               <h3 style="color: var(--text-secondary); margin-bottom: 0.5rem;">No Job Openings</h3>
               <p style="color: var(--text-secondary); opacity: 0.7;">Check back soon for new opportunities!</p>
           </div>
       `;
       return;
   }

   jobsGrid.innerHTML = userData.jobs.map(job => `
       <div class="job-card" data-aos="fade-up">
           <h3 class="job-title">${job.title}</h3>
           <div class="job-company">${job.company}</div>
           <div class="job-details">
               <div class="job-detail">
                   <i class="fas fa-map-marker-alt"></i>
                   ${job.location}
               </div>
               <div class="job-detail">
                   <i class="fas fa-clock"></i>
                   ${job.type}
               </div>
               <div class="job-detail">
                   <i class="fas fa-level-up-alt"></i>
                   ${job.experience}
               </div>
               ${job.salary ? `<div class="job-detail">
                   <i class="fas fa-dollar-sign"></i>
                   ${job.salary}
               </div>` : ''}
           </div>
           <div class="job-description">${job.description}</div>
           <div class="job-requirements">
               <h4>Requirements:</h4>
               <ul>
                   ${job.requirements.map(req => `<li>${req}</li>`).join('')}
               </ul>
           </div>
           <div class="job-actions">
               <button class="btn btn-primary" onclick="applyForJob(${job.id})">
                   Apply Now <i class="fas fa-paper-plane"></i>
               </button>
               <div class="job-date">Posted: ${new Date(job.postedDate).toLocaleDateString()}</div>
           </div>
       </div>
   `).join('');
}

function applyForJob(jobId) {
   const job = userData.jobs.find(j => j.id === jobId);
   if (!job) return;
   showSuccess('Application submitted successfully! We will review your application and get back to you soon.');
}

// Admin Panel
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
}

// Admin Navigation
document.querySelectorAll('.admin-nav-btn').forEach(btn => {
   btn.addEventListener('click', () => {
       const section = btn.getAttribute('data-section');

       // Update nav buttons
       document.querySelectorAll('.admin-nav-btn').forEach(b => b.classList.remove('active'));
       btn.classList.add('active');

       // Update sections
       document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
       document.getElementById(section).classList.add('active');
   });
});

// Job Form Handler
document.getElementById('jobForm').addEventListener('submit', (e) => {
   e.preventDefault();

   const jobData = {
       id: Date.now(),
       title: document.getElementById('jobTitle').value,
       company: document.getElementById('jobCompany').value,
       location: document.getElementById('jobLocation').value,
       type: document.getElementById('jobType').value,
       salary: document.getElementById('jobSalary').value,
       experience: document.getElementById('jobExperience').value,
       description: document.getElementById('jobDescription').value,
       requirements: document.getElementById('jobRequirements').value.split('\n').filter(req => req.trim()),
       postedDate: new Date().toISOString().split('T')[0]
   };

   userData.jobs.push(jobData);

   showSuccess('Job posted successfully!');
   document.getElementById('jobForm').reset();
   loadAdminJobs();
   loadJobs();
});

function loadAdminJobs() {
   const adminJobsList = document.getElementById('adminJobsList');

   if (userData.jobs.length === 0) {
       adminJobsList.innerHTML = `
           <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
               <i class="fas fa-briefcase" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
               <p>No jobs posted yet.</p>
           </div>
       `;
       return;
   }

   adminJobsList.innerHTML = userData.jobs.map(job => `
       <div class="job-card" style="margin-bottom: 1rem;">
           <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
               <div>
                   <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">${job.title}</h4>
                   <div style="color: var(--text-secondary); font-size: 0.875rem;">
                       ${job.company} • ${job.location} • ${job.type}
                   </div>
               </div>
               <div style="display: flex; gap: 0.5rem;">
                   <button class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.875rem;" onclick="editJob(${job.id})">
                       <i class="fas fa-edit"></i>
                   </button>
                   <button class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.875rem; background: #dc2626;" onclick="deleteJob(${job.id})">
                       <i class="fas fa-trash"></i>
                   </button>
               </div>
           </div>
           <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">
               ${job.description.substring(0, 150)}${job.description.length > 150 ? '...' : ''}
           </div>
           <div style="display: flex; justify-content: between; align-items: items-center; font-size: 0.75rem; color: var(--text-secondary);">
               <span>Posted: ${new Date(job.postedDate).toLocaleDateString()}</span>
               <span>${userData.applications.filter(app => app.jobId === job.id).length} Applications</span>
           </div>
       </div>
   `).join('');
}

function editJob(jobId) {
   const job = userData.jobs.find(j => j.id === jobId);
   if (!job) return;

   // Fill form with job data
   document.getElementById('jobTitle').value = job.title;
   document.getElementById('jobCompany').value = job.company;
   document.getElementById('jobLocation').value = job.location;
   document.getElementById('jobType').value = job.type;
   document.getElementById('jobSalary').value = job.salary || '';
   document.getElementById('jobExperience').value = job.experience;
   document.getElementById('jobDescription').value = job.description;
   document.getElementById('jobRequirements').value = job.requirements.join('\n');

   // Switch to post job section
   document.querySelectorAll('.admin-nav-btn').forEach(b => b.classList.remove('active'));
   document.querySelector('[data-section="postJob"]').classList.add('active');
   document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
   document.getElementById('postJob').classList.add('active');

   // Remove the job from array (will be re-added when form is submitted)
   userData.jobs = userData.jobs.filter(j => j.id !== jobId);
}

function deleteJob(jobId) {
   if (confirm('Are you sure you want to delete this job posting?')) {
       userData.jobs = userData.jobs.filter(j => j.id !== jobId);
       loadAdminJobs();
       loadJobs();
       showSuccess('Job deleted successfully!');
   }
}

function loadAdminApplications() {
   const applicationsList = document.getElementById('applicationsList');

   if (userData.applications.length === 0) {
       applicationsList.innerHTML = `
           <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
               <i class="fas fa-file-alt" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
               <p>No applications received yet.</p>
           </div>
       `;
       return;
   }

   applicationsList.innerHTML = userData.applications.map(app => `
       <div class="job-card" style="margin-bottom: 1rem;">
           <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
               <div>
                   <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">${app.name}</h4>
                   <div style="color: var(--text-secondary); font-size: 0.875rem;">
                       ${app.email} • ${app.phone || 'No phone'}
                   </div>
                   ${app.jobTitle ? `<div style="color: var(--primary-color); font-size: 0.875rem; margin-top: 0.5rem;">
                       Applied for: ${app.jobTitle}
                   </div>` : ''}
                   ${app.program ? `<div style="color: var(--primary-color); font-size: 0.875rem; margin-top: 0.5rem;">
                       Program: ${app.program}
                   </div>` : ''}
               </div>
               <div style="display: flex; gap: 0.5rem; align-items: center;">
                   <select onchange="updateApplicationStatus(${app.id}, this.value)" style="
                       padding: 0.5rem;
                       border-radius: 5px;
                       border: 1px solid var(--border-color);
                       background: var(--bg-primary);
                       color: var(--text-primary);
                       font-size: 0.875rem;
                   ">
                       <option value="pending" ${app.status === 'pending' ? 'selected' : ''}>Pending</option>
                       <option value="reviewed" ${app.status === 'reviewed' ? 'selected' : ''}>Reviewed</option>
                       <option value="accepted" ${app.status === 'accepted' ? 'selected' : ''}>Accepted</option>
                       <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                   </select>
                   <button class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.875rem; background: #dc2626;" onclick="deleteApplication(${app.id})">
                       <i class="fas fa-trash"></i>
                   </button>
               </div>
           </div>
           ${app.experience ? `<div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">
               <strong>Experience:</strong><br>
               ${app.experience.substring(0, 200)}${app.experience.length > 200 ? '...' : ''}
           </div>` : ''}
           <div style="font-size: 0.75rem; color: var(--text-secondary);">
               Applied: ${new Date(app.appliedAt).toLocaleDateString()}
           </div>
       </div>
   `).join('');
}

function updateApplicationStatus(appId, newStatus) {
   const app = userData.applications.find(a => a.id === appId);
   if (app) {
       app.status = newStatus;
       showSuccess('Application status updated!');
   }
}

function deleteApplication(appId) {
   if (confirm('Are you sure you want to delete this application?')) {
       userData.applications = userData.applications.filter(a => a.id !== appId);
       loadAdminApplications();
       showSuccess('Application deleted successfully!');
   }
}

function loadAdminUsers() {
   const usersList = document.getElementById('usersList');

   if (userData.users.length === 0) {
       usersList.innerHTML = `
           <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
               <i class="fas fa-users" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
               <p>No users registered yet.</p>
           </div>
       `;
       return;
   }

   usersList.innerHTML = userData.users.map(user => `
       <div class="job-card" style="margin-bottom: 1rem;">
           <div style="display: flex; justify-content: space-between; align-items: center;">
               <div>
                   <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">${user.name}</h4>
                   <div style="color: var(--text-secondary); font-size: 0.875rem;">
                       ${user.email} • ${user.phone}
                   </div>
                   <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                       Registered: ${new Date(user.createdAt).toLocaleDateString()}
                   </div>
               </div>
               <button class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.875rem; background: #dc2626;" onclick="deleteUser(${user.id})">
                   <i class="fas fa-trash"></i>
               </button>
           </div>
       </div>
   `).join('');
}

function deleteUser(userId) {
   if (confirm('Are you sure you want to delete this user?')) {
       userData.users = userData.users.filter(u => u.id !== userId);
       loadAdminUsers();
       showSuccess('User deleted successfully!');
   }
}

function openGalleryModal(element) {
  const modal = document.getElementById('galleryModal');
  const content = document.getElementById('galleryModalContent');

  const isVideo = element.querySelector('video');
  const isImage = element.querySelector('img');

  if (isVideo) {
      const videoSrc = isVideo.querySelector('source').src;
      content.innerHTML = `<video controls autoplay style="max-width: 100%; max-height: 90vh; border-radius: 10px;">
          <source src="${videoSrc}" type="video/mp4">
          Your browser does not support the video tag.
      </video>`;
  } else if (isImage) {
      const imgSrc = isImage.src;
      const imgAlt = isImage.alt;
      content.innerHTML = `<img src="${imgSrc}" alt="${imgAlt}" style="max-width: 100%; max-height: 90vh; border-radius: 10px;">`;
  }

  modal.classList.add('active');
}

function closeGalleryModal() {
  const modal = document.getElementById('galleryModal');
  const content = document.getElementById('galleryModalContent');

 
  const video = content.querySelector('video');
  if (video) {
      video.pause();
  }

  modal.classList.remove('active');
  content.innerHTML = '';
}


document.addEventListener('DOMContentLoaded', function() {
  const galleryTabs = document.querySelectorAll('.gallery-tab-btn');
  const galleryItems = document.querySelectorAll('.gallery-item');

  galleryTabs.forEach(tab => {
      tab.addEventListener('click', () => {
       
          galleryTabs.forEach(t => t.classList.remove('active'));
          tab.classList.add('active');

          const filter = tab.getAttribute('data-gallery-tab');


          galleryItems.forEach(item => {
              if (filter === 'all') {
                  item.style.display = 'block';
              } else {
                  const itemType = item.getAttribute('data-type');
                  if (itemType === filter.slice(0, -1)) { 
                      item.style.display = 'block';
                  } else {
                      item.style.display = 'none';
                  }
              }
          });
      });
  });
});



document.querySelectorAll('.modal, .modal-gallery').forEach(modal => {
modal.addEventListener('click', (e) => {
   if (e.target === modal) {
       if (modal.classList.contains('modal-gallery')) {
           closeGalleryModal();
       } else {
           modal.classList.remove('active');
       }
   }
});
});


function optimizeImages() {
   const images = document.querySelectorAll('img[src*="github"], img[src*="drive.google"]');
   images.forEach(img => {
      
       if (!img.hasAttribute('loading')) {
           img.setAttribute('loading', 'lazy');
       }

       
       img.addEventListener('error', function() {
           this.style.opacity = '0.3';
           console.warn('Failed to load image:', this.src);
       });

    
       img.addEventListener('load', function() {
           this.style.opacity = '1';
           this.style.transition = 'opacity 0.3s ease';
       });
   });
}





// Modal Functions
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
   document.getElementById(modalId).classList.remove('active');
}

function closeAllModals() {
   document.querySelectorAll('.modal').forEach(modal => {
       modal.classList.remove('active');
   });
}

// Modal click outside to close
document.querySelectorAll('.modal').forEach(modal => {
   modal.addEventListener('click', (e) => {
       if (e.target === modal) {
           modal.classList.remove('active');
       }
   });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
   anchor.addEventListener('click', function (e) {
       e.preventDefault();
       const target = document.querySelector(this.getAttribute('href'));
       if (target) {
           target.scrollIntoView({
               behavior: 'smooth',
               block: 'start'
           });
       }
   });
});

// Mobile Navigation
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

mobileMenuToggle.addEventListener('click', () => {
   if (navMenu.classList.contains('active')) {
       document.body.style.overflow = '';
   } else {
       document.body.style.overflow = 'hidden';
   }
});

// Escape key to close modals and admin panel
document.addEventListener('keydown', (e) => {
   if (e.key === 'Escape') {
       closeAllModals();
       if (isAdmin && document.getElementById('adminPanel').classList.contains('active')) {
           closeAdminPanel();
       }
   }
});

// Initialize Service Backgrounds
function initializeServiceBackgrounds() {
   const serviceCards = document.querySelectorAll('.service-card, .program-card');

   serviceCards.forEach((card) => {
       const computedStyle = getComputedStyle(card, '::before');
       const bgImage = computedStyle.backgroundImage;

       if (bgImage && bgImage !== 'none') {
           const img = new Image();
           const url = bgImage.slice(4, -1).replace(/["']/g, "");

           if (url && url !== 'none') {
               img.onload = function() {
                   card.classList.add('bg-loaded');
               };

               img.onerror = function() {
                   card.classList.add('bg-loaded');
               };

               img.src = url;
           }
       } else {
           card.classList.add('bg-loaded');
       }
   });
}

// Initialize Map
function initializeMap() {
   const mapContainer = document.querySelector('.map-container');
   const mapIframe = mapContainer.querySelector('iframe');

   if (mapIframe) {
       mapContainer.classList.add('loading');

       mapIframe.addEventListener('load', () => {
           setTimeout(() => {
               mapContainer.classList.remove('loading');
           }, 500);
       });

       mapIframe.addEventListener('error', () => {
           mapContainer.classList.remove('loading');
           mapContainer.innerHTML = `
               <div style="
                   display: flex;
                   flex-direction: column;
                   align-items: center;
                   justify-content: center;
                   height: 100%;
                   color: var(--text-secondary);
                   text-align: center;
                   padding: 2rem;
               ">
                   <i class="fas fa-map-marked-alt" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                   <h4 style="margin-bottom: 0.5rem;">Unable to load map</h4>
                   <p style="font-size: 0.875rem; opacity: 0.8;">Block H3, Phase 2, Johar Town<br>Lahore, Punjab, Pakistan</p>
                   <a href="https://www.google.com/maps/place/Stellar+Skills+(Private)+Limited/@31.497136,74.4100161,17z"
                      target="_blank"
                      class="btn btn-primary"
                      style="margin-top: 1rem; font-size: 0.875rem; padding: 0.5rem 1rem;">
                       Open in Google Maps <i class="fas fa-external-link-alt"></i>
                   </a>
               </div>
           `;
       });
   }
}

// Touch Interactions for Mobile
function optimizeTouchInteractions() {
   const touchElements = document.querySelectorAll('.btn, .service-card, .program-card, .team-member, .testimonial-card, .client-logo, .animated-service-card');

   touchElements.forEach(element => {
       element.addEventListener('touchstart', function() {
           this.style.transform = 'scale(0.95)';
           this.style.transition = 'transform 0.1s ease';
       }, { passive: true });

       element.addEventListener('touchend', function() {
           setTimeout(() => {
               this.style.transform = '';
               this.style.transition = 'all 0.3s ease';
           }, 150);
       }, { passive: true });

       element.addEventListener('touchcancel', function() {
           this.style.transform = '';
           this.style.transition = 'all 0.3s ease';
       }, { passive: true });
   });
}

// Page Transitions
const links = document.querySelectorAll('a[href^="#"]');
const pageTransition = document.querySelector('.page-transition');

links.forEach(link => {
   link.addEventListener('click', (e) => {
       const href = link.getAttribute('href');
       if (href !== '#') {
           pageTransition.classList.add('active');
           setTimeout(() => {
               pageTransition.classList.remove('active');
           }, 500);
       }
   });
});

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
   updateLoadingProgress();
   loadSplineModels();
   optimizeImages();
   setTimeout(initializeServiceBackgrounds, 500);
   setTimeout(initializeCardAnimation, 100);
   setTimeout(initializeMap, 1000);
   optimizeTouchInteractions();
   loadJobs(); // Load default job listings

   console.log('Stellar Skills website fully initialized');
});

// Fallback loader hide
setTimeout(() => {
   const loader = document.getElementById('loader');
   if (loader && !loader.classList.contains('hide')) {
       console.log('Fallback loader hide triggered');
       hideLoader();
   }
}, 25000);



document.addEventListener('keydown', function(e) {

   if (e.key === 'Escape') {
       closeAllModals();
       closeGalleryModal();
       closeAdminPanel();
   }


   if (e.key === 'Enter' && e.target.classList.contains('tab-btn')) {
       e.target.click();
   }
});
// Performance tracking
window.addEventListener('load', () => {
   setTimeout(() => {
       if ('performance' in window) {
           const perfData = performance.getEntriesByType('navigation')[0];
           console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
       }
   }, 0);
});

// Export functions for global access
window.stellarSkills = {
   showSignInModal,
   showSignUpModal,
   showJoinModal,
   closeAllModals,
   initializeCardAnimation,
   userData,
   applyForJob
};

console.log('Stellar Skills JavaScript fully loaded and ready!');