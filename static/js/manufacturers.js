// Check authentication
auth.requireAuth();

// Display user name
auth.updateHeader();

let allManufacturers = [];
let editingManufacturerId = null;

// Load all manufacturers
async function loadManufacturers() {
    try {
        const manufacturers = await ManufacturersAPI.getAll();
        allManufacturers = manufacturers;
        displayManufacturers(manufacturers);
    } catch (error) {
        console.error('Load manufacturers error:', error);
        document.getElementById('manufacturersContainer').innerHTML = '<p class="error">Failed to load manufacturers</p>';
    }
}

// Display manufacturers in table
function displayManufacturers(manufacturers) {
    const container = document.getElementById('manufacturersContainer');

    if (!manufacturers || manufacturers.length === 0) {
        container.innerHTML = '<p class="no-data">No manufacturers found. Click "Add Manufacturer" to create one.</p>';
        return;
    }

    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Company</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Category</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${manufacturers.map(manufacturer => `
                    <tr>
                        <td>${manufacturer.id}</td>
                        <td>${manufacturer.name}</td>
                        <td>${manufacturer.company_name || '-'}</td>
                        <td>${manufacturer.email || '-'}</td>
                        <td>${manufacturer.phone || '-'}</td>
                        <td>${manufacturer.product_category || '-'}</td>
                        <td class="table-actions">
                            <button onclick="editManufacturer('${manufacturer.id}')" class="btn btn-icon-only btn-secondary" title="Edit">
                                <i data-lucide="edit-3"></i>
                            </button>
                            <button onclick="deleteManufacturer('${manufacturer.id}')" class="btn btn-icon-only btn-danger" title="Delete">
                                <i data-lucide="trash-2"></i>
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = `<div class="table-container">${html}</div>`;
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Search functionality
document.getElementById('searchInput').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const filtered = allManufacturers.filter(manufacturer => 
        manufacturer.name.toLowerCase().includes(searchTerm) ||
        (manufacturer.company_name && manufacturer.company_name.toLowerCase().includes(searchTerm)) ||
        (manufacturer.email && manufacturer.email.toLowerCase().includes(searchTerm)) ||
        (manufacturer.product_category && manufacturer.product_category.toLowerCase().includes(searchTerm))
    );
    displayManufacturers(filtered);
});

// Show add modal
function showAddModal() {
    editingManufacturerId = null;
    document.getElementById('modalTitle').textContent = 'Add Manufacturer';
    document.getElementById('manufacturerForm').reset();
    document.getElementById('manufacturerModal').style.display = 'block';
}

// Edit manufacturer
async function editManufacturer(id) {
    try {
        const manufacturer = await ManufacturersAPI.getById(id);
        
        editingManufacturerId = id;
        document.getElementById('modalTitle').textContent = 'Edit Manufacturer';
        
        // Fill form
        document.getElementById('name').value = manufacturer.name || '';
        document.getElementById('company_name').value = manufacturer.company_name || '';
        document.getElementById('email').value = manufacturer.email || '';
        document.getElementById('phone').value = manufacturer.phone || '';
        document.getElementById('address').value = manufacturer.address || '';
        document.getElementById('city').value = manufacturer.city || '';
        document.getElementById('state').value = manufacturer.state || '';
        document.getElementById('country').value = manufacturer.country || '';
        document.getElementById('gst_number').value = manufacturer.gst_number || '';
        document.getElementById('product_category').value = manufacturer.product_category || '';
        
        document.getElementById('manufacturerModal').style.display = 'block';
        
    } catch (error) {
        console.error('Edit manufacturer error:', error);
        alert('Failed to load manufacturer details');
    }
}

// Delete manufacturer
async function deleteManufacturer(id) {
    if (!confirm('Are you sure you want to delete this manufacturer?')) {
        return;
    }

    try {
        await ManufacturersAPI.delete(id);
        alert('Manufacturer deleted successfully');
        loadManufacturers();
    } catch (error) {
        console.error('Delete manufacturer error:', error);
        alert('Failed to delete manufacturer');
    }
}

// Close modal
function closeModal() {
    document.getElementById('manufacturerModal').style.display = 'none';
    editingManufacturerId = null;
}

// Handle form submit
document.getElementById('manufacturerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        company_name: document.getElementById('company_name').value || null,
        email: document.getElementById('email').value || null,
        phone: document.getElementById('phone').value || null,
        address: document.getElementById('address').value || null,
        city: document.getElementById('city').value || null,
        state: document.getElementById('state').value || null,
        country: document.getElementById('country').value || null,
        gst_number: document.getElementById('gst_number').value || null,
        product_category: document.getElementById('product_category').value || null
    };

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';

    try {
        if (editingManufacturerId) {
            await ManufacturersAPI.update(editingManufacturerId, formData);
            alert('Manufacturer updated successfully');
        } else {
            await ManufacturersAPI.create(formData);
            alert('Manufacturer created successfully');
        }

        closeModal();
        loadManufacturers();
        
    } catch (error) {
        console.error('Save manufacturer error:', error);
        alert('Failed to save manufacturer');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Manufacturer';
    }
});

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('manufacturerModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Initialize
loadManufacturers();