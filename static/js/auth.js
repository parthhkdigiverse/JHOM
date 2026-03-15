/**
 * Authentication Manager
 * Handles login, logout, token management
 */

var auth = (function() {
    'use strict';

    // Private variables
    var token = null;
    var user = null;

    // Initialize on load
    function init() {
        token = localStorage.getItem('auth_token');
        var userStr = localStorage.getItem('user');
        try {
            user = userStr ? JSON.parse(userStr) : null;
        } catch (e) {
            user = null;
        }
    }

    // Check if authenticated
    function isAuthenticated() {
        return token !== null && token !== '';
    }

    // Get authorization headers for API calls
    function getAuthHeaders() {
        if (!token) {
            console.warn('[AUTH] No token available');
            return {
                'Content-Type': 'application/json'
            };
        }
        return {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        };
    }

    // Get authorization headers for file upload
    function getAuthHeadersForUpload() {
        if (!token) {
            console.warn('[AUTH] No token available for upload');
            return {};
        }
        return {
            'Authorization': 'Bearer ' + token
        };
    }

    // Handle API errors (including token expiration)
    function handleApiError(response) {
        if (response.status === 401) {
            console.error('[AUTH] Token expired or invalid - redirecting to login');
            alert('Your session has expired. Please login again.');
            logout();
            return true;
        }
        return false;
    }

    // Login function
    function login(username, password) {
        return new Promise(function(resolve, reject) {
            // Validate inputs
            if (!username || !password) {
                resolve({
                    success: false,
                    message: 'Username and password are required'
                });
                return;
            }

            // Create form data
            var formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            // Get API URL
            var apiUrl = getApiUrl(API_CONFIG.ENDPOINTS.LOGIN);

            console.log('[AUTH] Attempting login for user:', username);

            // Make request
            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData.toString()
            })
            .then(function(response) {
                return response.json().then(function(data) {
                    return {
                        status: response.status,
                        ok: response.ok,
                        data: data
                    };
                });
            })
            .then(function(result) {
                if (result.ok && result.data.access_token) {
                    // Success
                    token = result.data.access_token;
                    user = {
                        username: result.data.username || username,
                        full_name: result.data.full_name,
                        role: result.data.role || 'admin'
                    };

                    // Save to localStorage
                    localStorage.setItem('auth_token', token);
                    localStorage.setItem('user', JSON.stringify(user));

                    console.log('[AUTH] Login successful for role:', user.role);

                    resolve({
                        success: true,
                        message: 'Login successful'
                    });
                } else {
                    // Failed
                    var errorMessage = 'Login failed';

                    if (result.data.detail) {
                        if (typeof result.data.detail === 'string') {
                            errorMessage = result.data.detail;
                        } else if (result.data.detail.msg) {
                            errorMessage = result.data.detail.msg;
                        } else if (Array.isArray(result.data.detail)) {
                            var errors = [];
                            for (var i = 0; i < result.data.detail.length; i++) {
                                if (result.data.detail[i].msg) {
                                    errors.push(result.data.detail[i].msg);
                                } else {
                                    errors.push(String(result.data.detail[i]));
                                }
                            }
                            errorMessage = errors.join(', ');
                        } else {
                            errorMessage = 'Invalid credentials';
                        }
                    } else if (result.data.message) {
                        errorMessage = result.data.message;
                    }

                    console.error('[AUTH] Login failed:', errorMessage);

                    resolve({
                        success: false,
                        message: errorMessage
                    });
                }
            })
            .catch(function(error) {
                console.error('[AUTH] Login error:', error);
                resolve({
                    success: false,
                    message: 'Network error. Please check your connection and try again.'
                });
            });
        });
    }

    // Logout function
    function logout() {
        var apiUrl = getApiUrl(API_CONFIG.ENDPOINTS.LOGOUT);

        console.log('[AUTH] Logging out...');

        // Call logout API
        fetch(apiUrl, {
            method: 'POST',
            headers: getAuthHeaders()
        })
        .then(function(response) {
            console.log('[AUTH] Logout response:', response.status);
        })
        .catch(function(error) {
            console.error('[AUTH] Logout error:', error);
        })
        .finally(function() {
            // Clear local data
            token = null;
            user = null;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');

            console.log('[AUTH] Logged out - redirecting to login');

            // Redirect to login
            window.location.href = 'index.html';
        });
    }

    // Get current user
    function getCurrentUser() {
        return user;
    }

    // Check if superuser
    function isSuperuser() {
        return user !== null && user.role === 'superuser';
    }

    // Apply role-based visibility to the UI
    function updateHeader() {
        const nameElem = document.getElementById('userName');
        if (nameElem && user) {
            nameElem.textContent = user.full_name || user.username;
        }
    }

    // Apply role-based visibility to the UI
    function applyRoleVisibility() {
        const adminElements = document.querySelectorAll('.superuser-only');
        const superuser = isSuperuser();
        
        adminElements.forEach(el => {
            if (superuser) {
                el.style.display = 'block';
                // If it's a list item, maintain layout
                if (el.tagName === 'LI') el.style.display = 'list-item';
            } else {
                el.style.display = 'none';
            }
        });
    }

    // Require authentication (redirect if not logged in)
    function requireAuth() {
        if (!isAuthenticated()) {
            console.warn('[AUTH] Not authenticated - redirecting to login');
            window.location.href = 'index.html';
            return false;
        }
        return true;
    }

    // Verify token is still valid
    function verifyToken() {
        if (!isAuthenticated()) {
            return Promise.resolve(false);
        }

        var apiUrl = getApiUrl(API_CONFIG.ENDPOINTS.VERIFY || '/api/auth/verify');

        return fetch(apiUrl, {
            method: 'GET',
            headers: getAuthHeaders()
        })
        .then(function(response) {
            if (response.status === 401) {
                console.error('[AUTH] Token verification failed - invalid token');
                logout();
                return false;
            }
            if (response.ok) {
                return response.json().then(function(data) {
                    // Update user info with latest from server
                    if (data.username) {
                        user = {
                            username: data.username,
                            full_name: data.full_name || (user ? user.full_name : null),
                            role: data.role || (user ? user.role : 'user')
                        };
                        localStorage.setItem('user', JSON.stringify(user));
                        updateHeader();
                    }
                    return true;
                });
            }
            return false;
        })
        .catch(function(error) {
            console.error('[AUTH] Token verification error:', error);
            return false;
        });
    }

    // Initialize on load
    init();

    // Public API
    return {
        isAuthenticated: isAuthenticated,
        getAuthHeaders: getAuthHeaders,
        getAuthHeadersForUpload: getAuthHeadersForUpload,
        handleApiError: handleApiError,
        login: login,
        logout: logout,
        getCurrentUser: getCurrentUser,
        isSuperuser: isSuperuser,
        applyRoleVisibility: applyRoleVisibility,
        updateHeader: updateHeader,
        requireAuth: requireAuth,
        verifyToken: verifyToken
    };
})();

// Auto-verify and apply visibility on page load
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.indexOf('index.html') === -1 && 
        window.location.pathname !== '/' && 
        window.location.pathname !== '') {
        
        if (auth.isAuthenticated()) {
            auth.updateHeader();
            auth.verifyToken().then(function(valid) {
                if (valid) {
                    auth.updateHeader();
                    auth.applyRoleVisibility(); // Re-apply after verification
                }
            });
        }
    }
});