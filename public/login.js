// API Configuration
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';
const API_BASE_URL = window.API_BASE_URL;

// ============================================================================
// LOGIN FORM HANDLING
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const operatorId = document.getElementById('operatorId').value.trim();
        const password = document.getElementById('password').value;
        const role = document.getElementById('role').value;

        // Clear previous errors
        errorMessage.classList.remove('show');
        errorMessage.textContent = '';

        // Validate input
        if (!operatorId) {
            showError('Please enter your Operator ID');
            return;
        }

        // Disable button during login
        const loginButton = loginForm.querySelector('.login-button');
        const originalText = loginButton.querySelector('.button-text').textContent;
        loginButton.querySelector('.button-text').textContent = 'Authenticating...';
        loginButton.disabled = true;

        try {
            // Call authentication API
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    operator_id: operatorId,
                    password: password,
                    role: role || null
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                let message = 'Authentication failed';

                if (errorData.detail) {
                    if (typeof errorData.detail === 'string') {
                        message = errorData.detail;
                    } else if (Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
                        // Handle Pydantic validation errors
                        message = errorData.detail[0].msg;
                    } else if (typeof errorData.detail === 'object') {
                        message = JSON.stringify(errorData.detail);
                    }
                }

                throw new Error(message);
            }

            const data = await response.json();

            // Store session data
            sessionStorage.setItem('operator', JSON.stringify(data.operator));
            sessionStorage.setItem('sessionToken', data.session_token);
            sessionStorage.setItem('loginTime', new Date().toISOString());

            // Redirect to main dashboard
            window.location.href = '/dashboard.html';

        } catch (error) {
            console.error('Login error:', error);
            showError(error.message || 'Failed to authenticate. Please try again.');

            // Re-enable button
            loginButton.querySelector('.button-text').textContent = originalText;
            loginButton.disabled = false;
        }
    });
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

function fillCredentials(id, password) {
    document.getElementById('operatorId').value = id;
    document.getElementById('password').value = password;
    document.getElementById('operatorId').focus();
}

// ============================================================================
// CHECK IF ALREADY LOGGED IN - DISABLED TO PREVENT REDIRECT LOOPS
// ============================================================================
// window.addEventListener('load', () => {
//     const operator = sessionStorage.getItem('operator');
//     if (operator) {
//         // Already logged in, redirect to dashboard
//         window.location.href = '/dashboard.html';
//     }
// });
