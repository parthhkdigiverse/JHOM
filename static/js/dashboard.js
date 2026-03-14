// Check authentication
auth.requireAuth();

// Display user name
const user = auth.getCurrentUser();
if (user) {
    document.getElementById('userName').textContent = user.full_name || user.username;
}

// Load dashboard data
async function loadDashboard() {
    try {
        // Load stats
        await loadStats();
        
        // Load recent data
        await loadRecentBuyers();
        await loadRecentTasks();
        await loadDriveStatus();
        
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        // Use Global Stats API if available (more efficient)
        const stats = await StatsAPI.getGlobal();
        
        document.getElementById('totalBuyers').textContent = stats.total_buyers;
        document.getElementById('totalManufacturers').textContent = stats.total_manufacturers;
        document.getElementById('totalTasks').textContent = stats.total_tasks;
        
    } catch (error) {
        console.error('Stats load error, falling back to manual count:', error);
        // Fallback for non-superusers or if API fails
        try {
            const [buyers, manufacturers, tasks] = await Promise.all([
                BuyersAPI.getAll(),
                ManufacturersAPI.getAll(),
                TasksAPI.getAll()
            ]);

            document.getElementById('totalBuyers').textContent = buyers?.length || 0;
            document.getElementById('totalManufacturers').textContent = manufacturers?.length || 0;
            document.getElementById('totalTasks').textContent = tasks?.length || 0;
        } catch (innerError) {
            console.error('Fallback stats load error:', innerError);
        }
    }
}

// Load recent buyers
async function loadRecentBuyers() {
    try {
        const buyers = await BuyersAPI.getAll();
        const recentBuyers = buyers.slice(0, 5);

        const container = document.getElementById('recentBuyers');

        if (recentBuyers.length === 0) {
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
        document.getElementById('recentBuyers').innerHTML = '<p class="error">Failed to load buyers</p>';
    }
}

// Load recent tasks
async function loadRecentTasks() {
    try {
        const tasks = await TasksAPI.getAll();
        const recentTasks = tasks.slice(0, 5);

        const container = document.getElementById('recentTasks');

        if (recentTasks.length === 0) {
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
        document.getElementById('recentTasks').innerHTML = '<p class="error">Failed to load tasks</p>';
    }
}

// Load Google Drive status
async function loadDriveStatus() {
    try {
        const status = await UploadAPI.getDriveStatus();
        
        if (status && status.status === 'success') {
            document.getElementById('driveStatus').textContent = '✅ Connected';
        } else {
            document.getElementById('driveStatus').textContent = '❌ Disconnected';
        }
        
    } catch (error) {
        console.error('Drive status error:', error);
        document.getElementById('driveStatus').textContent = '⚠️ Error';
    }
}

// Initialize dashboard
loadDashboard();