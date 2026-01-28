/**
 * Felix Tang Portfolio - Main JavaScript
 * 前端开发者作品集网站交互脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    // ==================== 
    // Check for successful form submission 
    // ====================
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('submitted') === 'true') {
        // Show success notification
        setTimeout(() => {
            showNotification('🎉 提交成功！我会尽快与您联系。', 'success');
            // Clean up URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }, 500);
    }

    // ==================== 
    // Navigation 
    // ====================
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    const navItems = document.querySelectorAll('.nav-links a');

    // Scroll effect for navbar
    function handleScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Back to top button visibility
        const backToTop = document.getElementById('backToTop');
        if (window.scrollY > 500) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }

        // Update active nav link based on scroll position
        updateActiveNavLink();
    }

    window.addEventListener('scroll', handleScroll);

    // Mobile navigation toggle
    navToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        const icon = this.querySelector('i');
        if (navLinks.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    });

    // Close mobile menu when clicking a link
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navLinks.classList.remove('active');
            const icon = navToggle.querySelector('i');
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        });
    });

    // Update active navigation link based on scroll position
    function updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPos = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                navItems.forEach(item => {
                    item.classList.remove('active');
                    if (item.getAttribute('href') === '#' + sectionId) {
                        item.classList.add('active');
                    }
                });
            }
        });
    }

    // ==================== 
    // Portfolio Carousel 
    // ====================
    function initCarousel() {
        const track = document.getElementById('carouselTrack');
        const slides = document.querySelectorAll('.carousel-slide');
        const prevBtn = document.getElementById('carouselPrev');
        const nextBtn = document.getElementById('carouselNext');
        const dotsContainer = document.getElementById('carouselDots');
        const dots = document.querySelectorAll('.carousel-dot');
        
        if (!track || slides.length === 0) return;
        
        let currentIndex = 0;
        let autoplayInterval;
        const slideCount = slides.length;
        
        // Update carousel position
        function goToSlide(index) {
            if (index < 0) index = slideCount - 1;
            if (index >= slideCount) index = 0;
            
            currentIndex = index;
            track.style.transform = `translateX(-${currentIndex * 100}%)`;
            
            // Update dots
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === currentIndex);
            });
        }
        
        // Next slide
        function nextSlide() {
            goToSlide(currentIndex + 1);
        }
        
        // Previous slide
        function prevSlide() {
            goToSlide(currentIndex - 1);
        }
        
        // Event listeners for buttons
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                resetAutoplay();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                resetAutoplay();
            });
        }
        
        // Event listeners for dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                goToSlide(index);
                resetAutoplay();
            });
        });
        
        // Touch/swipe support
        let touchStartX = 0;
        let touchEndX = 0;
        
        track.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        track.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });
        
        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
                resetAutoplay();
            }
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Only trigger if carousel is in viewport
            const carouselRect = track.getBoundingClientRect();
            const isInViewport = carouselRect.top < window.innerHeight && carouselRect.bottom > 0;
            
            if (isInViewport) {
                if (e.key === 'ArrowLeft') {
                    prevSlide();
                    resetAutoplay();
                } else if (e.key === 'ArrowRight') {
                    nextSlide();
                    resetAutoplay();
                }
            }
        });
        
        // Autoplay
        function startAutoplay() {
            autoplayInterval = setInterval(nextSlide, 5000);
        }
        
        function resetAutoplay() {
            clearInterval(autoplayInterval);
            startAutoplay();
        }
        
        // Pause autoplay on hover
        const carouselContainer = document.querySelector('.carousel-container');
        if (carouselContainer) {
            carouselContainer.addEventListener('mouseenter', () => {
                clearInterval(autoplayInterval);
            });
            
            carouselContainer.addEventListener('mouseleave', () => {
                startAutoplay();
            });
        }
        
        // Start autoplay
        startAutoplay();
        
        // Intersection Observer to pause autoplay when not visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    startAutoplay();
                } else {
                    clearInterval(autoplayInterval);
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(track);
    }
    
    initCarousel();

    // ==================== 
    // Smooth Scroll 
    // ====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 70;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ==================== 
    // Back to Top 
    // ====================
    const backToTop = document.getElementById('backToTop');
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // ==================== 
    // Contact Form 
    // ====================
    const contactForm = document.getElementById('contactForm');
    
    contactForm.addEventListener('submit', function(e) {
        // Get form data for validation
        const userName = document.getElementById('userName').value.trim();
        const userContact = document.getElementById('userContact').value.trim();
        const projectType = document.getElementById('projectType').value;
        const description = document.getElementById('description').value.trim();

        // Validate form
        if (!userName || !userContact || !projectType || !description) {
            e.preventDefault();
            showNotification('请填写所有必填项', 'error');
            return;
        }

        // Show loading state (form will submit naturally via FormSubmit)
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 提交中...';
        submitBtn.disabled = true;
    });

    // ==================== 
    // Notification 
    // ====================
    function showNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 10px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;

        // Add animation keyframes
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(100px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            @keyframes slideOut {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100px);
                }
            }
        `;
        document.head.appendChild(style);

        // Append to body
        document.body.appendChild(notification);

        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 1rem;
            opacity: 0.8;
        `;
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => notification.remove(), 300);
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    // ==================== 
    // Skill Bar Animation 
    // ====================
    function animateSkillBars() {
        const skillBars = document.querySelectorAll('.skill-progress');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const width = entry.target.style.width;
                    entry.target.style.width = '0%';
                    setTimeout(() => {
                        entry.target.style.width = width;
                    }, 100);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        skillBars.forEach(bar => observer.observe(bar));
    }

    animateSkillBars();

    // ==================== 
    // Scroll Animation 
    // ====================
    function initScrollAnimation() {
        const animatedElements = document.querySelectorAll(
            '.service-card, .carousel-slide, .process-item, .skill-card'
        );

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease';
            observer.observe(el);
        });
    }

    initScrollAnimation();

    // ==================== 
    // Typing Effect for Hero 
    // ====================
    function initTypingEffect() {
        const codeWindow = document.querySelector('.window-body code');
        if (!codeWindow) return;

        const originalHTML = codeWindow.innerHTML;
        codeWindow.innerHTML = '';
        
        let i = 0;
        const typeInterval = setInterval(() => {
            if (i < originalHTML.length) {
                codeWindow.innerHTML = originalHTML.substring(0, i + 1);
                i++;
            } else {
                clearInterval(typeInterval);
            }
        }, 20);
    }

    // Delay typing effect for better UX
    setTimeout(initTypingEffect, 500);

    // ==================== 
    // Parallax Effect 
    // ====================
    function initParallax() {
        const hero = document.querySelector('.hero');
        
        window.addEventListener('scroll', () => {
            const scrolled = window.scrollY;
            if (scrolled < window.innerHeight) {
                hero.style.backgroundPositionY = scrolled * 0.5 + 'px';
            }
        });
    }

    initParallax();

    // ==================== 
    // Stats Counter Animation 
    // ====================
    function animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const value = target.textContent;
                    const numericValue = parseInt(value);
                    
                    if (!isNaN(numericValue)) {
                        let current = 0;
                        const increment = numericValue / 50;
                        const suffix = value.replace(/[0-9]/g, '');
                        
                        const counter = setInterval(() => {
                            current += increment;
                            if (current >= numericValue) {
                                target.textContent = value;
                                clearInterval(counter);
                            } else {
                                target.textContent = Math.floor(current) + suffix;
                            }
                        }, 30);
                    }
                    
                    observer.unobserve(target);
                }
            });
        }, { threshold: 0.5 });

        stats.forEach(stat => observer.observe(stat));
    }

    animateStats();

    // ==================== 
    // Console Easter Egg 
    // ====================
    console.log(`
    %c欢迎查看源代码！%c
    
    我是 Felix Tang，一名拥有8年经验的前端开发工程师。
    如果你正在寻找优秀的前端开发者，欢迎联系我！
    
    📧 Email: felix@example.com
    💬 微信: FelixTang_Dev
    
    `, 
    'color: #6366f1; font-size: 20px; font-weight: bold;',
    'color: #64748b; font-size: 14px;'
    );
});
