document.addEventListener('DOMContentLoaded', function () {
    // Flash messages hide automatically after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // Add active class to current nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Convert all UTC times to user's local time
    const utcElements = document.querySelectorAll('.utc-time');
    utcElements.forEach(span => {
        const utc = span.dataset.utc;
        if (utc) {
            const local = new Date(utc).toLocaleString(undefined, {
                year: "numeric", month: "2-digit", day: "2-digit",
                hour: "2-digit", minute: "2-digit", second: "2-digit"
            });
            span.textContent = local;
        }
    });
});
