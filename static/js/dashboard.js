// Check authentication
auth.requireAuth();

// Display user name
const user = auth.getCurrentUser();
if (user) {
    document.getElementById('userName').textContent = user.full_name || user.username;
}

/**
 * Load all dashboard data
 */
async function loadDashboard() {
    try {
        // Global stats are handled by api.js auto-loader if elements exist
        // So we focus on recent data here
        await Promise.all([
            loadRecentBuyers(),
            loadRecentTasks(),
            loadDriveStatus()
        ]);
        
    } catch (error) {
        console.error('Dashboard load error:', error);
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

        container.innerHTML = html;
        
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
                    </tr>
                </thead>
                <tbody>
                    ${recentTasks.map(task => `
                        <tr>
                            <td>${task.title}</td>
                            <td><span class="badge badge-${task.status}">${task.status}</span></td>
                            <td><span class="badge badge-${task.priority}">${task.priority}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
        
    } catch (error) {
        console.error('Recent tasks error:', error);
        if (document.getElementById('recentTasks')) {
            document.getElementById('recentTasks').innerHTML = '<p class="error">Failed to load tasks</p>';
        }
    }
}

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