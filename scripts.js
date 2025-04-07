document.addEventListener('DOMContentLoaded', function() {
    // Form submission
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        console.log('Login attempt:', { email, password });

        // Replace with actual authentication logic
        alert(`Signed in /nEmail: ${email}`);
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
