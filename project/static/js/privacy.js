// Плавная прокрутка к якорям
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.legal-nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
