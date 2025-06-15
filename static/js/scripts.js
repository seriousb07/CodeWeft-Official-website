const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    const isExpanded = navMenu.classList.contains('active');
    hamburger.setAttribute('aria-expanded', isExpanded);
    hamburger.textContent = isExpanded ? '✕' : '☰';
});

const navLinks = document.querySelectorAll('.nav-menu a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.textContent = '☰';
    });
});

const fadeInElements = document.querySelectorAll('.fade-in');
const observerOptions = { threshold: 0.2 };

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

fadeInElements.forEach(element => observer.observe(element));

const contactForm = document.getElementById('contact-form');
const newsletterForm = document.getElementById('newsletter-form');

function handleFormSubmit(form, endpoint, successMessage, errorMessage) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formMessage = form.querySelector('.form-message');
        const submitBtn = form.querySelector('button');
        
        formMessage.style.display = 'none';
        formMessage.className = 'form-message';
        submitBtn.disabled = true;
        submitBtn.textContent = endpoint === '/contact' ? 'Sending...' : 'Subscribing...';

        try {
            const formData = new FormData(form);
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (response.ok) {
                formMessage.textContent = successMessage;
                formMessage.className = 'form-message success';
                form.reset();
            } else {
                formMessage.textContent = result.detail || errorMessage;
                formMessage.className = 'form-message error';
            }
        } catch (error) {
            formMessage.textContent = errorMessage;
            formMessage.className = 'form-message error';
        } finally {
            formMessage.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.textContent = endpoint === '/contact' ? 'Send' : 'Subscribe';
        }
    });
}

if (contactForm) {
    handleFormSubmit(contactForm, '/contact', 
        "Message sent successfully! We'll get back to you soon.",
        "Failed to send message. Please try again later."
    );
}

if (newsletterForm) {
    handleFormSubmit(newsletterForm, '/newsletter',
        "Subscribed successfully! Stay tuned for updates.",
        "Failed to subscribe. Please try again later."
    );
}