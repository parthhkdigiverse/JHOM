// API wrapper with automatic error handling
function apiCall(url, options) {
    options = options || {};
    
    // Add auth headers if authenticated
    if (auth.isAuthenticated()) {
        if (!options.headers) {
            options.headers = auth.getAuthHeaders();
        }
    }
    
    console.log('[API] Calling:', url);
    
    return fetch(url, options)
        .then(function(response) {
            console.log('[API] Response status:', response.status);
            
            // Check for auth errors
            if (response.status === 401) {
                console.error('[API] 401 Unauthorized');
                alert('Your session has expired. Please login again.');
                window.location.href = 'index.html';
                throw new Error('Authentication required');
            }
            
            // Check for other errors
            if (!response.ok) {
                return response.json().then(function(data) {
                    throw new Error(data.detail || data.message || 'API error');
                }).catch(function() {
                    throw new Error('HTTP ' + response.status);
                });
            }
            
            return response.json();
        });
}

// Buyers API
var BuyersAPI = {
    getAll: function() {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.BUYERS));
    },
    
    getById: function(id) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.BUYERS + '/' + id));
    },
    
    create: function(data) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.BUYERS), {
            method: 'POST',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    update: function(id, data) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.BUYERS + '/' + id), {
            method: 'PUT',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    delete: function(id) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.BUYERS + '/' + id), {
            method: 'DELETE',
            headers: auth.getAuthHeaders()
        });
    }
};

// Manufacturers API
var ManufacturersAPI = {
    getAll: function() {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.MANUFACTURERS));
    },
    
    getById: function(id) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.MANUFACTURERS + '/' + id));
    },
    
    create: function(data) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.MANUFACTURERS), {
            method: 'POST',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    update: function(id, data) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.MANUFACTURERS + '/' + id), {
            method: 'PUT',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    delete: function(id) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.MANUFACTURERS + '/' + id), {
            method: 'DELETE',
            headers: auth.getAuthHeaders()
        });
    }
};

// Tasks API
var TasksAPI = {
    getAll: function(statusFilter, priorityFilter) {
        var url = getApiUrl(API_CONFIG.ENDPOINTS.TASKS);
        var params = [];
        
        if (statusFilter) params.push('status_filter=' + statusFilter);
        if (priorityFilter) params.push('priority_filter=' + priorityFilter);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        return apiCall(url);
    },
    
    getById: function(id) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.TASKS + '/' + id));
    },
    
    create: function(data) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.TASKS), {
            method: 'POST',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    update: function(id, data) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.TASKS + '/' + id), {
            method: 'PUT',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    delete: function(id) {
        return apiCall(getApiUrl(API_CONFIG.ENDPOINTS.TASKS + '/' + id), {
            method: 'DELETE',
            headers: auth.getAuthHeaders()
        });
    }
};

// Upload API
var UploadAPI = {
    getDriveStatus: function() {
        return apiCall(getApiUrl('/api/upload/google-drive/status'));
    },
    
    getDriveFiles: function(type) {
        return apiCall(getApiUrl('/api/upload/google-drive/files/' + type));
    },
    
    uploadBuyer: function(buyerId, file) {
        var formData = new FormData();
        formData.append('file', file);
        
        return fetch(getApiUrl('/api/upload/buyer/' + buyerId), {
            method: 'POST',
            headers: auth.getAuthHeadersForUpload(),
            body: formData
        })
        .then(function(response) {
            if (response.status === 401) {
                alert('Session expired. Please login again.');
                window.location.href = 'index.html';
                throw new Error('Authentication required');
            }
            return response.json();
        });
    },
    
    uploadManufacturer: function(manufacturerId, file) {
        var formData = new FormData();
        formData.append('file', file);
        
        return fetch(getApiUrl('/api/upload/manufacturer/' + manufacturerId), {
            method: 'POST',
            headers: auth.getAuthHeadersForUpload(),
            body: formData
        })
        .then(function(response) {
            if (response.status === 401) {
                alert('Session expired. Please login again.');
                window.location.href = 'index.html';
                throw new Error('Authentication required');
            }
            return response.json();
        });
    },
    
    uploadDirect: function(file) {
        var formData = new FormData();
        formData.append('file', file);
        
        return fetch(getApiUrl('/api/upload/direct'), {
            method: 'POST',
            headers: auth.getAuthHeadersForUpload(),
            body: formData
        })
        .then(function(response) {
            if (response.status === 401) {
                alert('Session expired. Please login again.');
                window.location.href = 'index.html';
                throw new Error('Authentication required');
            }
            return response.json();
        });
    }
};

// Admins API (Superuser only)
var AdminsAPI = {
    getAll: function() {
        return apiCall(getApiUrl('/api/auth/admins'));
    },
    
    create: function(data) {
        return apiCall(getApiUrl('/api/auth/admins'), {
            method: 'POST',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    update: function(id, data) {
        return apiCall(getApiUrl('/api/auth/admins/' + id), {
            method: 'PUT',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    delete: function(id) {
        return apiCall(getApiUrl('/api/auth/admins/' + id), {
            method: 'DELETE',
            headers: auth.getAuthHeaders()
        });
    }
};

// Stats API
var StatsAPI = {
    getGlobal: function() {
        return apiCall(getApiUrl('/api/auth/stats'));
    }
};