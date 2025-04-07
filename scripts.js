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
            window.location.href = 'admin.html';
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
// Forgot Password Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Modal elements
    const modal = document.getElementById('forgotPasswordModal');
    const closeBtn = document.querySelector('.close-modal');
    const forgotLink = document.querySelector('.footer-links a[href="#"]');
    
    // Form elements
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const verifyBtn = document.getElementById('verifyEmailBtn');
    const resetBtn = document.getElementById('resetPasswordBtn');
    const statusDiv = document.getElementById('resetStatus');
  
    // Open modal when Forgot Password is clicked
    forgotLink.addEventListener('click', function(e) {
      e.preventDefault();
      modal.style.display = 'block';
      // Reset form
      step1.style.display = 'block';
      step2.style.display = 'none';
      statusDiv.textContent = '';
    });
  
    // Close modal
    closeBtn.addEventListener('click', function() {
      modal.style.display = 'none';
    });
  
    // Close when clicking outside modal
    window.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    });
  
    // Verify email
    verifyBtn.addEventListener('click', function() {
      const email = document.getElementById('resetEmail').value.trim();
      
      if (!email) {
        statusDiv.textContent = 'Please enter your email';
        return;
      }
  
      // In a real app, you would check against your database here
      // This is just a mock validation
      if (email === 'admin@example.com' || email === 'joel@gmail.com') {
        step1.style.display = 'none';
        step2.style.display = 'block';
        statusDiv.textContent = '';
      } else {
        statusDiv.textContent = 'Email not found in our system';
      }
    });
  
    // Reset password
    resetBtn.addEventListener('click', function() {
      const newPass = document.getElementById('newPassword').value;
      const confirmPass = document.getElementById('confirmPassword').value;
      
      if (!newPass || !confirmPass) {
        statusDiv.textContent = 'Please fill in both fields';
        return;
      }
      
      if (newPass !== confirmPass) {
        statusDiv.textContent = 'Passwords do not match';
        return;
      }
      
      if (newPass.length < 6) {
        statusDiv.textContent = 'Password must be at least 6 characters';
        return;
      }
  
      // In a real app, you would send this to your server
      statusDiv.style.color = '#4CAF50';
      statusDiv.textContent = 'Password reset successful!';
      
      // Close modal after 2 seconds
      setTimeout(() => {
        modal.style.display = 'none';
      }, 2000);
    });
  });