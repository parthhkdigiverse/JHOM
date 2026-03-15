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

// Calendar API
var CalendarAPI = {
    getAll: function(start, end) {
        var url = getApiUrl('/api/calendar/events/fullcalendar');
        var params = [];
        if (start) params.push('start=' + start);
        if (end) params.push('end=' + end);
        if (params.length > 0) url += '?' + params.join('&');
        return apiCall(url);
    },
    
    getById: function(id) {
        return apiCall(getApiUrl('/api/calendar/events/' + id));
    },
    
    create: function(data) {
        return apiCall(getApiUrl('/api/calendar/events'), {
            method: 'POST',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    update: function(id, data) {
        return apiCall(getApiUrl('/api/calendar/events/' + id), {
            method: 'PUT',
            headers: auth.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    },
    
    delete: function(id) {
        return apiCall(getApiUrl('/api/calendar/events/' + id), {
            method: 'DELETE',
            headers: auth.getAuthHeaders()
        });
    },
    
    getToday: function() {
        return apiCall(getApiUrl('/api/calendar/events/today/list'));
    },
    
    getUpcoming: function(days) {
        return apiCall(getApiUrl('/api/calendar/events/upcoming/list?days=' + (days || 7)));
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

// PDF API
var PDFAPI = {
    generateProforma: function(data) {
        return this._downloadPDF(getApiUrl('/api/proforma/generate-pdf'), data, 'Proforma_Invoice.pdf');
    },
    
    generateQuotation: function(data) {
        return this._downloadPDF(getApiUrl('/api/quotation/generate-pdf'), data, 'Quotation.pdf');
    },
    
    _downloadPDF: function(url, data, defaultFilename) {
        console.log('[PDF] Generating:', url);
        
        return fetch(url, {
            method: 'POST',
            headers: Object.assign({
                'Content-Type': 'application/json'
            }, auth.getAuthHeaders()),
            body: JSON.stringify(data)
        })
        .then(function(response) {
            if (!response.ok) {
                return response.json().then(function(err) {
                    throw new Error(err.detail || err.message || 'Failed to generate PDF');
                }).catch(function() {
                    throw new Error('Server error (' + response.status + ')');
                });
            }
            
            // Get filename from header if possible
            var filename = defaultFilename;
            var disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = matches[1].replace(/['"]/g, '');
                }
            }
            
            return response.blob().then(function(blob) {
                return { blob: blob, filename: filename };
            });
        })
        .then(function(result) {
            // Trigger download
            var url = window.URL.createObjectURL(result.blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = result.filename;
            document.body.appendChild(a);
            a.click();
            setTimeout(function() {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 100);
            return true;
        });
    }
};

// --- GLOBAL INITIALIZATION ---
// Auto-load stats on any page that has the stat elements
document.addEventListener('DOMContentLoaded', async function() {
    const buyerElem = document.getElementById('statBuyers');
    const mfrElem = document.getElementById('statManufacturers');
    const taskElem = document.getElementById('statTasks');
    
    // Only fetch if at least one element exists and user is logged in
    if ((buyerElem || mfrElem || taskElem) && auth.isAuthenticated()) {
        try {
            console.log('[GLOBAL] Loading project-wide stats...');
            const stats = await StatsAPI.getGlobal();
            
            if (buyerElem) buyerElem.textContent = stats.total_buyers || 0;
            if (mfrElem) mfrElem.textContent = stats.total_manufacturers || 0;
            if (taskElem) taskElem.textContent = stats.total_tasks || 0;
            
            console.log('[GLOBAL] Stats loaded successfully');

        } catch (error) {
            console.error('[GLOBAL] Failed to load stats:', error);
        }
    }
});