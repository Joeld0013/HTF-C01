// Password toggle functionality
document.getElementById('togglePassword').addEventListener('click', function() {
    const password = document.getElementById('password');
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
});

// Error popup functions
function showError(message) {
    const popup = document.getElementById('errorPopup');
    document.getElementById('errorMessage').textContent = message;
    popup.style.display = 'block';
    setTimeout(hideError, 5000); // Auto-hide after 5 seconds
}

function hideError() {
    document.getElementById('errorPopup').style.display = 'none';
}

// Form submission
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch('login.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = 'templates/admin.html';
        } else {
            showError(result.message || 'Invalid email or password');
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
        console.error('Error:', error);
    }
});

// Check for URL errors on page load
window.addEventListener('load', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    
    if (error) {
        let errorMessage = '';
        switch (error) {
            case 'empty_fields':
                errorMessage = 'Please fill in all fields';
                break;
            case 'invalid_credentials':
                errorMessage = 'Invalid email or password';
                break;
            case 'database_error':
                errorMessage = 'Database error occurred';
                break;
            default:
                errorMessage = 'Login failed';
        }
        showError(errorMessage);
        // Clean the URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});