// Login Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    // Only run if we're on the login page
    if (!loginForm) {
        return;
    }
    
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const rememberMe = document.getElementById('rememberMe');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const loginBtn = loginForm.querySelector('.btn-login');

    // Don't check if already logged in - let the server handle it
    // This prevents infinite redirect loops
    
    // Load saved username if available
    const savedUsername = localStorage.getItem('saved_username');
    if (savedUsername) {
        username.value = savedUsername;
        rememberMe.checked = true;
    }

    // Handle form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        errorMessage.style.display = 'none';

        const usernameValue = username.value.trim();
        const passwordValue = password.value;

        // Validate inputs
        if (!usernameValue || !passwordValue) {
            showError('Please enter both username and password');
            return;
        }

        // Disable button and show loading state
        loginBtn.disabled = true;
        loginBtn.classList.add('loading');
        const originalText = loginBtn.textContent;
        loginBtn.textContent = 'Logging in...';

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: usernameValue,
                    password: passwordValue
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }

            // Save credentials if remember me is checked
            if (rememberMe.checked) {
                localStorage.setItem('saved_username', usernameValue);
            } else {
                localStorage.removeItem('saved_username');
            }

            // Store auth token
            if (data.token) {
                sessionStorage.setItem('authToken', data.token);
                sessionStorage.setItem('username', data.username);
                if (rememberMe.checked) {
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('username', data.username);
                }
            }

            // Redirect to main page
            window.location.href = '/';

        } catch (error) {
            showError(error.message || 'An error occurred during login');
        } finally {
            // Re-enable button
            loginBtn.disabled = false;
            loginBtn.classList.remove('loading');
            loginBtn.textContent = originalText;
        }
    });

    function showError(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Clear error message when user starts typing
    [username, password].forEach(field => {
        field.addEventListener('focus', function() {
            errorMessage.style.display = 'none';
        });
    });
});
