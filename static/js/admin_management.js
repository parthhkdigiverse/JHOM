/**
 * Admin Management Logic
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Initial Access Check
    if (!auth.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    const currentUser = auth.getCurrentUser();
    if (currentUser.role !== 'superuser') {
        alert('Access denied. Superuser privileges required.');
        window.location.href = 'dashboard.html';
        return;
    }

    document.getElementById('userName').textContent = currentUser.full_name || currentUser.username;

    // 2. Load Initial Data
    loadStats();
    loadAdmins();

    // 3. Modal Controls
    const modal = document.getElementById('adminModal');
    const addBtn = document.getElementById('addAdminBtn');
    const closeBtn = document.querySelector('.close');
    const form = document.getElementById('adminForm');

    addBtn.onclick = () => {
        document.getElementById('modalTitle').textContent = 'Add New Admin';
        form.reset();
        document.getElementById('adminId').value = '';
        modal.style.display = 'block';
    };

    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // 4. Form Submission
    form.onsubmit = async (e) => {
        e.preventDefault();
        
        const adminId = document.getElementById('adminId').value;
        const data = {
            username: document.getElementById('username').value,
            full_name: document.getElementById('full_name').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            role: document.getElementById('role').value,
            is_active: document.getElementById('is_active').checked
        };

        try {
            let result;
            if (adminId) {
                result = await AdminsAPI.update(adminId, data);
            } else {
                result = await AdminsAPI.create(data);
            }
            
            modal.style.display = 'none';
            loadAdmins();
        } catch (error) {
            alert('Error saving admin: ' + error.message);
        }
    };
});

async function loadStats() {
    try {
        const stats = await StatsAPI.getGlobal();
        document.getElementById('statBuyers').textContent = stats.total_buyers;
        document.getElementById('statManufacturers').textContent = stats.total_manufacturers;
        document.getElementById('statTasks').textContent = stats.total_tasks;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadAdmins() {
    const container = document.getElementById('adminsContainer');
    container.innerHTML = '<p class="loading">Loading admin accounts...</p>';

    try {
        const admins = await AdminsAPI.getAll();
        
        if (admins.length === 0) {
            container.innerHTML = '<p class="no-data">No administrators found.</p>';
            return;
        }

        let html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>User / Email</th>
                        <th>Role</th>
                        <th>Password</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        admins.forEach(admin => {
            const roleClass = admin.role === 'superuser' ? 'badge-high' : 'badge-in-progress';
            const statusClass = admin.is_active ? 'badge-completed' : 'badge-pending';
            
            html += `
                <tr>
                    <td><strong>${admin.full_name}</strong></td>
                    <td>
                        <div>${admin.username}</div>
                        <small style="color: #64748b">${admin.email}</small>
                    </td>
                    <td><span class="badge ${roleClass}">${admin.role}</span></td>
                    <td><code style="background: #f1f5f9; padding: 2px 4px; border-radius: 4px;">${admin.password}</code></td>
                    <td><span class="badge ${statusClass}">${admin.is_active ? 'Active' : 'Disabled'}</span></td>
                    <td>
                        <div class="action-buttons">
                            <button onclick="editAdmin(${JSON.stringify(admin).replace(/"/g, '&quot;')})" class="btn-icon" title="Edit">
                                <i data-lucide="edit-3"></i>
                            </button>
                            <button onclick="deleteAdmin(${admin.id}, '${admin.username}')" class="btn-icon" title="Delete" style="color: var(--danger)">
                                <i data-lucide="trash-2"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
        lucide.createIcons();
        
    } catch (error) {
        container.innerHTML = `<p class="error">Error loading admins: ${error.message}</p>`;
    }
}

function editAdmin(admin) {
    document.getElementById('modalTitle').textContent = 'Edit Administrator';
    document.getElementById('adminId').value = admin.id;
    document.getElementById('username').value = admin.username;
    document.getElementById('full_name').value = admin.full_name;
    document.getElementById('email').value = admin.email;
    document.getElementById('password').value = admin.password;
    document.getElementById('role').value = admin.role;
    document.getElementById('is_active').checked = admin.is_active;
    
    document.getElementById('adminModal').style.display = 'block';
}

async function deleteAdmin(id, username) {
    if (confirm(`Are you sure you want to delete admin "${username}"?`)) {
        try {
            await AdminsAPI.delete(id);
            loadAdmins();
        } catch (error) {
            alert('Error deleting admin: ' + error.message);
        }
    }
}
