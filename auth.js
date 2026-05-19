/**
 * Authentication state manager for static pages
 * Checks session with backend and updates header accordingly
 */

async function checkAuthState() {
    try {
        const response = await fetch('http://localhost:5000/api/auth/check', {
            credentials: 'include'
        });
        const data = await response.json();
        
        const loggedOutDiv = document.getElementById('auth-logged-out');
        const loggedInDiv = document.getElementById('auth-logged-in');
        
        if (data.logged_in) {
            // Show logged-in state
            loggedOutDiv.style.display = 'none';
            loggedInDiv.style.display = 'flex';
            
            // Update username
            const userNameSpan = loggedInDiv.querySelector('.user-name');
            if (userNameSpan) {
                userNameSpan.textContent = data.username;
            }
            
            // Update avatar initials
            const avatar = loggedInDiv.querySelector('.avatar');
            if (avatar) {
                const initials = getInitials(data.username);
                avatar.setAttribute('data-initial', initials);
                avatar.style.backgroundColor = getColorForUser(data.username);
            }
        } else {
            // Show logged-out state
            loggedOutDiv.style.display = 'flex';
            loggedInDiv.style.display = 'none';
        }
        
        // Setup logout handler
        const signoutBtn = document.getElementById('signout-btn');
        if (signoutBtn) {
            signoutBtn.addEventListener('click', handleLogout);
        }
        
        // Setup dropdown toggle
        setupDropdownToggle();
        
        // Setup modal handlers
        setupModalHandlers();
        
    } catch (error) {
        console.error('Failed to check auth state:', error);
        // Default to logged-out state on error
        const loggedOutDiv = document.getElementById('auth-logged-out');
        const loggedInDiv = document.getElementById('auth-logged-in');
        if (loggedOutDiv) loggedOutDiv.style.display = 'flex';
        if (loggedInDiv) loggedInDiv.style.display = 'none';
    }
}

function getInitials(username) {
    if (!username) return '??';
    const parts = username.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return username.substring(0, 2).toUpperCase();
}

function getColorForUser(username) {
    // Generate consistent color based on username
    const colors = [
        '#5755d9', '#32b643', '#ffb700', '#e85600', 
        '#e74c3c', '#9b59b6', '#3498db', '#1abc9c'
    ];
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
}

async function handleLogout(e) {
    e.preventDefault();
    
    try {
        const response = await fetch('http://localhost:5000/logout', {
            credentials: 'include'
        });
        
        if (response.ok) {
            // Redirect to home or refresh
            window.location.href = '/index.html';
        }
    } catch (error) {
        console.error('Logout failed:', error);
        alert('Logout failed. Please try again.');
    }
}

// Setup dropdown toggle for user menu
function setupDropdownToggle() {
    const dropdown = document.querySelector('.user-dropdown');
    if (dropdown) {
        dropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdownParent = this.closest('.dropdown');
            dropdownParent.classList.toggle('active');
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function closeDropdown(event) {
                if (!dropdownParent.contains(event.target)) {
                    dropdownParent.classList.remove('active');
                    document.removeEventListener('click', closeDropdown);
                }
            });
        });
    }
}

// Setup modal handlers
function setupModalHandlers() {
    // Open login modal
    const loginBtn = document.getElementById('open-login-modal');
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('login-modal');
        });
    }
    
    // Open register modal
    const registerBtn = document.getElementById('open-register-modal');
    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('register-modal');
        });
    }
    
    // Close modals
    document.querySelectorAll('.modal .btn-clear, .modal-overlay').forEach(el => {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal(this.closest('.modal').id);
        });
    });
    
    // Switch between login and register
    const switchToRegister = document.getElementById('switch-to-register');
    if (switchToRegister) {
        switchToRegister.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal('login-modal');
            openModal('register-modal');
        });
    }
    
    const switchToLogin = document.getElementById('switch-to-login');
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal('register-modal');
            openModal('login-modal');
        });
    }
    
    // Form submissions
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterSubmit);
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        document.body.classList.add('modal-open');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const errorDiv = form.querySelector('.form-error');
    
    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in...';
    
    const formData = new FormData(form);
    
    try {
        const response = await fetch('http://localhost:5000/login', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Close modal and reload to update auth state
            closeModal('login-modal');
            location.reload();
        } else {
            // Show error
            if (errorDiv) {
                errorDiv.textContent = data.error || 'Login failed. Please try again.';
                errorDiv.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Login error:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.style.display = 'block';
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
    }
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const errorDiv = form.querySelector('.form-error');
    
    // Clear any previous errors
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
    
    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';
    
    const formData = new FormData(form);
    
    // Client-side validation
    const username = formData.get('username');
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');
    
    // Check all fields are filled
    if (!username || !email || !password || !confirmPassword) {
        if (errorDiv) {
            errorDiv.textContent = 'All fields are required.';
            errorDiv.style.display = 'block';
        }
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
        return;
    }
    
    // Check password length
    if (password.length < 6) {
        if (errorDiv) {
            errorDiv.textContent = 'Password must be at least 6 characters.';
            errorDiv.style.display = 'block';
        }
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
        return;
    }
    
    // Check passwords match
    if (password !== confirmPassword) {
        if (errorDiv) {
            errorDiv.textContent = 'Passwords do not match.';
            errorDiv.style.display = 'block';
        }
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/register', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Close modal and reload to update auth state
            closeModal('register-modal');
            location.reload();
        } else {
            // Show error
            if (errorDiv) {
                errorDiv.textContent = data.error || 'Registration failed. Please try again.';
                errorDiv.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Registration error:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.style.display = 'block';
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
    }
}

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuthState);
} else {
    checkAuthState();
}
