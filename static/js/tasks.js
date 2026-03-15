// Check authentication
auth.requireAuth();

// Display user name
const user = auth.getCurrentUser();
if (user) {
    document.getElementById('userName').textContent = user.username;
}

let allTasks = [];
let editingTaskId = null;

// Load all tasks
async function loadTasks() {
    try {
        const tasks = await TasksAPI.getAll();
        allTasks = tasks;
        
        // Update count badge
        const countBadge = document.getElementById('taskCount');
        if (countBadge) {
            countBadge.textContent = `${tasks.length} tasks`;
        }
        
        displayTasks(tasks);
    } catch (error) {
        console.error('Load tasks error:', error);
        document.getElementById('tasksContainer').innerHTML = '<p class="error">Failed to load tasks</p>';
    }
}

// Display tasks in table
function displayTasks(tasks) {
    const container = document.getElementById('tasksContainer');

    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p class="no-data">No tasks found. Click "Add Task" to create one.</p>';
        return;
    }

    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Due Date</th>
                    <th>Assigned To</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${tasks.map(task => `
                    <tr>
                        <td>${task.id}</td>
                        <td>${task.title}</td>
                        <td>${task.description ? (task.description.length > 50 ? task.description.substring(0, 50) + '...' : task.description) : '-'}</td>
                        <td><span class="badge badge-${task.status}">${task.status.replace('_', ' ')}</span></td>
                        <td><span class="badge badge-${task.priority}">${task.priority}</span></td>
                        <td>${task.due_date || '-'}</td>
                        <td>${task.assigned_to || '-'}</td>
                        <td>
                            <button onclick="editTask('${task.id}')" class="btn-icon" title="Edit">
                                ✏️
                            </button>
                            <button onclick="deleteTask('${task.id}')" class="btn-icon" title="Delete">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// Filter tasks
function filterTasks() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const priorityFilter = document.getElementById('priorityFilter').value;

    let filtered = allTasks;

    // Search
    if (searchTerm) {
        filtered = filtered.filter(task => 
            task.title.toLowerCase().includes(searchTerm) ||
            (task.description && task.description.toLowerCase().includes(searchTerm)) ||
            (task.assigned_to && task.assigned_to.toLowerCase().includes(searchTerm))
        );
    }

    // Status filter
    if (statusFilter) {
        filtered = filtered.filter(task => task.status === statusFilter);
    }

    // Priority filter
    if (priorityFilter) {
        filtered = filtered.filter(task => task.priority === priorityFilter);
    }

    displayTasks(filtered);
}

// Add event listeners for filters
document.getElementById('searchInput').addEventListener('input', filterTasks);
document.getElementById('statusFilter').addEventListener('change', filterTasks);
document.getElementById('priorityFilter').addEventListener('change', filterTasks);

// Show add modal
function showAddModal() {
    editingTaskId = null;
    document.getElementById('modalTitle').textContent = 'Add Task';
    document.getElementById('taskForm').reset();
    document.getElementById('taskModal').style.display = 'block';
}

// Edit task
async function editTask(id) {
    try {
        const task = await TasksAPI.getById(id);
        
        editingTaskId = id;
        document.getElementById('modalTitle').textContent = 'Edit Task';
        
        // Fill form
        document.getElementById('title').value = task.title || '';
        document.getElementById('description').value = task.description || '';
        document.getElementById('status').value = task.status || 'pending';
        document.getElementById('priority').value = task.priority || 'medium';
        document.getElementById('due_date').value = task.due_date || '';
        document.getElementById('assigned_to').value = task.assigned_to || '';
        
        document.getElementById('taskModal').style.display = 'block';
        
    } catch (error) {
        console.error('Edit task error:', error);
        alert('Failed to load task details');
    }
}

// Delete task
async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        await TasksAPI.delete(id);
        alert('Task deleted successfully');
        loadTasks();
    } catch (error) {
        console.error('Delete task error:', error);
        alert('Failed to delete task');
    }
}

// Close modal
function closeModal() {
    document.getElementById('taskModal').style.display = 'none';
    editingTaskId = null;
}

// Handle form submit
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
        } else {
            await TasksAPI.create(formData);
            alert('Task created successfully');
        }

        closeModal();
        loadTasks();
        
    } catch (error) {
        console.error('Save task error:', error);
        alert('Failed to save task');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Task';
    }
});

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('taskModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Initialize
loadTasks();