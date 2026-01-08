window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000/api';
const API_BASE_URL = window.API_BASE_URL;

document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');

    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            operator_id: document.getElementById('operatorId').value.trim(),
            name: document.getElementById('fullName').value.trim(),
            email: document.getElementById('email').value.trim(),
            department: document.getElementById('department').value.trim(),
            role: document.getElementById('role').value,
            password: document.getElementById('password').value
        };

        // UI state: loading
        const submitButton = signupForm.querySelector('.login-button');
        const originalText = submitButton.querySelector('.button-text').textContent;
        submitButton.querySelector('.button-text').textContent = 'Creating Account...';
        submitButton.disabled = true;
        errorMessage.classList.remove('show');

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                let message = 'Registration failed';
                if (result.detail) {
                    if (typeof result.detail === 'string') message = result.detail;
                    else if (Array.isArray(result.detail)) message = result.detail[0].msg;
                }
                throw new Error(message);
            }

            // Success
            alert('Account created successfully! Please log in.');
            window.location.href = 'login.html';

        } catch (error) {
            console.error('Registration error:', error);
            errorMessage.textContent = error.message || 'Failed to create account. Please try again.';
            errorMessage.classList.add('show');

            // Re-enable button
            submitButton.querySelector('.button-text').textContent = originalText;
            submitButton.disabled = false;
        }
    });
});
