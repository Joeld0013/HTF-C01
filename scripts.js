document.addEventListener('DOMContentLoaded', function() {
    // Role selection
    const roleOptions = document.querySelectorAll('.role-option');
    
    roleOptions.forEach(option => {
        option.addEventListener('click', function() {
            roleOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Form submission
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const role = document.querySelector('.role-option.active').dataset.role;
        
        console.log('Login attempt:', { email, password, role });
        
        // Replace with actual authentication logic
        alert(`Signed in as ${role}\nEmail: ${email}`);

    });




    
        const togglePassword = document.querySelector('.toggle-password');
        const password = document.getElementById('password');
    
        togglePassword.addEventListener('click', function() {
            // Toggle the eye icon
            this.classList.toggle('fa-eye-slash');
            this.classList.toggle('fa-eye');
            
            // Toggle the password field type
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
        });
    });
