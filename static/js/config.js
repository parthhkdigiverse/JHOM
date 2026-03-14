// API Configuration
var API_CONFIG = {
    BASE_URL: 'http://127.0.0.1:5000',
    ENDPOINTS: {
        // Auth
        LOGIN: '/api/auth/login',
        LOGOUT: '/api/auth/logout',
        VERIFY: '/api/auth/verify',
        ME: '/api/auth/me',
        
        // Buyers
        BUYERS: '/api/buyers',
        
        // Manufacturers
        MANUFACTURERS: '/api/manufacturers',
        
        // Tasks
        TASKS: '/api/tasks',
        
        // Calendar
        CALENDAR: '/api/calendar',
        
        // Upload
        UPLOAD: '/api/upload'
    }
};

// Helper function to get full API URL
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + endpoint;
}