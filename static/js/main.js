// Main JavaScript file for BrailleConnect

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for navbar toggler
    const navbarToggler = document.querySelector('.navbar-toggler');
    
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            navbarCollapse.classList.toggle('show');
        });
    }
    
    // Close notification when close button is clicked
    const notificationCloseBtn = document.querySelector('.notification .btn-close');
    
    if (notificationCloseBtn) {
        notificationCloseBtn.addEventListener('click', function() {
            const notification = document.getElementById('notification');
            notification.classList.remove('show');
        });
    }
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        if (href === currentPath || 
            (currentPath === '/' && href === '/') ||
            (currentPath !== '/' && href !== '/' && currentPath.includes(href))) {
            link.classList.add('active');
        }
    });
});

// Function to show notification - global function
function showNotification(title, message) {
    const notification = document.getElementById('notification');
    const notificationTitle = document.getElementById('notification-title');
    const notificationMessage = document.getElementById('notification-message');
    
    if (notification && notificationTitle && notificationMessage) {
        notificationTitle.textContent = title;
        notificationMessage.textContent = message;
        
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    } else {
        console.log(`Notification: ${title} - ${message}`);
    }
}
