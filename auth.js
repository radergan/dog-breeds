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

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuthState);
} else {
    checkAuthState();
}
