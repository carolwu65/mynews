// Main logic for Seminar Registration Site

// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Scroll Reveal Animation
const revealElements = document.querySelectorAll('.reveal');
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
            revealObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

revealElements.forEach(el => revealObserver.observe(el));

// Form Submission with Back-end API
const form = document.getElementById('submission-form');
const successMsg = document.getElementById('success-msg');

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = form.querySelector('button');
        const originalText = btn.innerText;
        
        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            org: document.getElementById('org').value,
            type: document.getElementById('type').value
        };

        // UI Loading state
        btn.innerText = '處理中...';
        btn.disabled = true;
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                form.style.display = 'none';
                successMsg.style.display = 'block';
                console.log('Registration successful');
            } else {
                throw new Error('Server responded with an error');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('報名失敗，請稍後再試。');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});
