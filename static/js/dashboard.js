// Check authentication
auth.requireAuth();

// Display user name
auth.updateHeader();

let editingTaskId = null;

/**
 * Load all dashboard data
 */
async function loadDashboard() {
    try {
        await Promise.all([
            loadAdmins(),
            loadRecentBuyers(),
            loadRecentTasks(),
            loadDriveStatus()
        ]);
        
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

async function loadAdmins() {
    try {
        const admins = await AdminsAPI.getAll();
        const dropdown = document.getElementById('assigned_to');
        if (dropdown) {
            const defaultOption = dropdown.options[0];
            dropdown.innerHTML = '';
            dropdown.appendChild(defaultOption);
            admins.forEach(admin => {
                const option = document.createElement('option');
                option.value = admin.username;
                option.textContent = `${admin.full_name || admin.username}`;
                dropdown.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load admins:', error);
    }
}

// Load recent buyers
async function loadRecentBuyers() {
    try {
        const buyers = await BuyersAPI.getAll();
        const recentBuyers = buyers.slice(0, 5);

        const container = document.getElementById('recentBuyers');

        if (!recentBuyers || recentBuyers.length === 0) {
            container.innerHTML = '<p class="no-data">No buyers found</p>';
            return;
        }

        const html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Company</th>
                        <th>Phone</th>
                    </tr>
                </thead>
                <tbody>
                    ${recentBuyers.map(buyer => `
                        <tr>
                            <td>${buyer.name}</td>
                            <td>${buyer.company_name || '-'}</td>
                            <td>${buyer.phone || '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = `<div class="table-container">${html}</div>`;
        
    } catch (error) {
        console.error('Recent buyers error:', error);
        if (document.getElementById('recentBuyers')) {
            document.getElementById('recentBuyers').innerHTML = '<p class="error">Failed to load buyers</p>';
        }
    }
}

// Load recent tasks
async function loadRecentTasks() {
    try {
        const tasks = await TasksAPI.getAll();
        const recentTasks = tasks.slice(0, 5);

        const container = document.getElementById('recentTasks');

        if (!recentTasks || recentTasks.length === 0) {
            container.innerHTML = '<p class="no-data">No tasks found</p>';
            return;
        }

        const html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th style="text-align: right">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${recentTasks.map(task => `
                        <tr>
                            <td>${task.title}</td>
                            <td><span class="badge badge-${task.status}">${task.status.replace('_', ' ')}</span></td>
                            <td><span class="badge badge-${task.priority}">${task.priority}</span></td>
                            <td class="table-actions">
                                <button onclick="editTask('${task.id}')" class="btn btn-icon-only btn-secondary" title="Edit">
                                    <i data-lucide="edit-3"></i>
                                </button>
                                <button onclick="deleteTask('${task.id}')" class="btn btn-icon-only btn-danger" title="Delete">
                                    <i data-lucide="trash-2"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = `<div class="table-container">${html}</div>`;
        if (window.lucide) lucide.createIcons();
        
    } catch (error) {
        console.error('Recent tasks error:', error);
        if (document.getElementById('recentTasks')) {
            document.getElementById('recentTasks').innerHTML = '<p class="error">Failed to load tasks</p>';
        }
    }
}

async function editTask(id) {
    try {
        const task = await TasksAPI.getById(id);
        editingTaskId = id;
        document.getElementById('modalTitle').textContent = 'Edit Task';
        document.getElementById('title').value = task.title || '';
        document.getElementById('description').value = task.description || '';
        document.getElementById('status').value = task.status || 'pending';
        document.getElementById('priority').value = task.priority || 'medium';
        document.getElementById('due_date').value = task.due_date ? task.due_date.split(' ')[0] : '';
        document.getElementById('assigned_to').value = task.assigned_to || '';
        document.getElementById('taskModal').style.display = 'block';
    } catch (error) {
        console.error('Edit task error:', error);
        alert('Failed to load task details');
    }
}

async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        await TasksAPI.delete(id);
        alert('Task deleted successfully');
        loadRecentTasks();
    } catch (error) {
        console.error('Delete task error:', error);
        alert('Failed to delete task');
    }
}

function closeModal() {
    document.getElementById('taskModal').style.display = 'none';
    editingTaskId = null;
}

document.getElementById('taskForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value || null,
        status: document.getElementById('status').value,
        priority: document.getElementById('priority').value,
        due_date: document.getElementById('due_date').value || null,
        assigned_to: document.getElementById('assigned_to').value || null
    };

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';

    try {
        if (editingTaskId) {
            await TasksAPI.update(editingTaskId, formData);
            alert('Task updated successfully');
            closeModal();
            loadRecentTasks();
        }
    } catch (error) {
        console.error('Save task error:', error);
        alert('Failed to save task');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Changes';
    }
});

// Load Google Drive status
async function loadDriveStatus() {
    try {
        const status = await UploadAPI.getDriveStatus();
        const driveElem = document.getElementById('driveStatus');
        
        if (driveElem) {
            if (status && status.status === 'success') {
                driveElem.textContent = '✅ Connected';
            } else {
                driveElem.textContent = '❌ Disconnected';
            }
        }
        
    } catch (error) {
        console.error('Drive status error:', error);
        const driveElem = document.getElementById('driveStatus');
        if (driveElem) driveElem.textContent = '⚠️ Error';
    }
}

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', loadDashboard);

window.onclick = function(event) {
    const modal = document.getElementById('taskModal');
    if (event.target === modal) closeModal();
}