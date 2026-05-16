// Плавная прокрутка к якорям с учетом высоты хедера
document.addEventListener('DOMContentLoaded', function() {
    const headerHeight = 73; 
    const additionalOffset = 20; 
    
    document.querySelectorAll('.legal-nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            
            if (target) {
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
                const offsetPosition = targetPosition - headerHeight - additionalOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Обновляем URL без прокрутки
                history.pushState(null, null, targetId);
            }
        });
    });
});
