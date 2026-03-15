// Check authentication
auth.requireAuth();

// Display user name
auth.updateHeader();

// Global variables
var currentBuyerId = null;
var isEditMode = false;

// Load all buyers
function loadBuyers() {
    var container = document.getElementById('buyersContainer');
    container.innerHTML = '<p class="loading">Loading buyers...</p>';

    console.log('[BUYERS] Loading buyers...');

    BuyersAPI.getAll()
        .then(function(buyers) {
            console.log('[BUYERS] Loaded:', buyers.length, 'buyers');
            displayBuyers(buyers);
        })
        .catch(function(error) {
            console.error('[BUYERS] Load error:', error);
            container.innerHTML = '<p class="error">Failed to load buyers. Please refresh the page.</p>';
        });
}

// Display buyers in table
function displayBuyers(buyers) {
    var container = document.getElementById('buyersContainer');
    var countBadge = document.getElementById('buyerCount');

    if (!buyers || buyers.length === 0) {
        container.innerHTML = '<p class="no-data">No buyers found. Add your first buyer to get started!</p>';
        countBadge.textContent = '0 buyers';
        return;
    }

    countBadge.textContent = buyers.length + ' buyer' + (buyers.length !== 1 ? 's' : '');

    var html = '<table class="table">';
    html += '<thead>';
    html += '<tr>';
    html += '<th>Name</th>';
    html += '<th>Company</th>';
    html += '<th>Email</th>';
    html += '<th>Phone</th>';
    html += '<th>Location</th>';
    html += '<th>Payment Terms</th>';
    html += '<th>Actions</th>';
    html += '</tr>';
    html += '</thead>';
    html += '<tbody>';

    for (var i = 0; i < buyers.length; i++) {
        var buyer = buyers[i];
        html += '<tr>';
        html += '<td><strong>' + (buyer.name || 'N/A') + '</strong></td>';
        html += '<td>' + (buyer.company_name || 'N/A') + '</td>';
        html += '<td>' + (buyer.email || 'N/A') + '</td>';
        html += '<td>' + (buyer.phone || 'N/A') + '</td>';
        html += '<td>' + (buyer.city ? buyer.city + ', ' : '') + (buyer.state || 'N/A') + '</td>';
        html += '<td><span class="badge badge-primary">' + (buyer.payment_terms || 'N/A') + '</span></td>';
        html += '<td class="action-buttons">';
        html += '<button onclick="editBuyer(' + buyer.id + ')" class="btn-icon" title="Edit">✏️</button>';
        html += '<button onclick="deleteBuyer(' + buyer.id + ')" class="btn-icon" title="Delete">🗑️</button>';
        html += '</td>';
        html += '</tr>';
    }

    html += '</tbody>';
    html += '</table>';

    container.innerHTML = html;
}

// Show add modal
function showAddModal() {
    isEditMode = false;
    currentBuyerId = null;
    document.getElementById('modalTitle').textContent = 'Add New Buyer';
    document.getElementById('buyerForm').reset();
    document.getElementById('buyerModal').style.display = 'block';
}

// Show edit modal
function editBuyer(id) {
    isEditMode = true;
    currentBuyerId = id;
    document.getElementById('modalTitle').textContent = 'Edit Buyer';

    BuyersAPI.getById(id)
        .then(function(buyer) {
            document.getElementById('name').value = buyer.name || '';
            document.getElementById('company_name').value = buyer.company_name || '';
            document.getElementById('email').value = buyer.email || '';
            document.getElementById('phone').value = buyer.phone || '';
            document.getElementById('address').value = buyer.address || '';
            document.getElementById('city').value = buyer.city || '';
            document.getElementById('state').value = buyer.state || '';
            document.getElementById('country').value = buyer.country || '';
            document.getElementById('gst_number').value = buyer.gst_number || '';
            document.getElementById('payment_terms').value = buyer.payment_terms || '';
            
            document.getElementById('buyerModal').style.display = 'block';
        })
        .catch(function(error) {
            console.error('[BUYERS] Edit load error:', error);
            alert('Failed to load buyer details');
        });
}

// Close modal
function closeModal() {
    document.getElementById('buyerModal').style.display = 'none';
    document.getElementById('buyerForm').reset();
    currentBuyerId = null;
    isEditMode = false;
}

// Delete buyer
function deleteBuyer(id) {
    if (!confirm('Are you sure you want to delete this buyer?')) {
        return;
    }

    BuyersAPI.delete(id)
        .then(function(result) {
            alert('Buyer deleted successfully');
            loadBuyers();
        })
        .catch(function(error) {
            console.error('[BUYERS] Delete error:', error);
            alert('Failed to delete buyer');
        });
}

// Handle form submission
document.getElementById('buyerForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Saving...';

    var data = {
        name: document.getElementById('name').value,
        company_name: document.getElementById('company_name').value,
        email: document.getElementById('email').value || null,
        phone: document.getElementById('phone').value || null,
        address: document.getElementById('address').value || null,
        city: document.getElementById('city').value || null,
        state: document.getElementById('state').value || null,
        country: document.getElementById('country').value || null,
        gst_number: document.getElementById('gst_number').value || null,
        payment_terms: document.getElementById('payment_terms').value
    };

    var apiCall;
    if (isEditMode) {
        apiCall = BuyersAPI.update(currentBuyerId, data);
    } else {
        apiCall = BuyersAPI.create(data);
    }

    apiCall
        .then(function(result) {
            alert(isEditMode ? 'Buyer updated successfully' : 'Buyer created successfully');
            closeModal();
            loadBuyers();
        })
        .catch(function(error) {
            console.error('[BUYERS] Save error:', error);
            alert('Failed to save buyer: ' + (error.message || 'Unknown error'));
        })
        .finally(function() {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span class="btn-icon">💾</span> Save Buyer';
        });
});

// Search functionality
document.getElementById('searchInput').addEventListener('input', function(e) {
    var searchTerm = e.target.value.toLowerCase();
    var rows = document.querySelectorAll('.table tbody tr');

    for (var i = 0; i < rows.length; i++) {
        var text = rows[i].textContent.toLowerCase();
        if (text.indexOf(searchTerm) > -1) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
});

// Close modal when clicking outside
window.onclick = function(event) {
    var modal = document.getElementById('buyerModal');
    if (event.target == modal) {
        closeModal();
    }
};

// Initialize
console.log('[BUYERS] Initializing page...');
loadBuyers();