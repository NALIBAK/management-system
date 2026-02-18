/* ============================================================
   Shared Sidebar HTML — injected by sidebar.js
   ============================================================ */

function renderSidebar(activePage) {
    const nav = [
        {
            label: 'Main', items: [
                { href: '../dashboard.html', icon: '🏠', text: 'Dashboard', id: 'dashboard' },
                { href: '../students/index.html', icon: '👨‍🎓', text: 'Students', id: 'students' },
                { href: '../staff/index.html', icon: '👨‍🏫', text: 'Staff', id: 'staff' },
            ]
        },
        {
            label: 'Academics', items: [
                { href: '../departments/index.html', icon: '🏛️', text: 'Departments', id: 'departments' },
                { href: '../courses/index.html', icon: '📚', text: 'Courses', id: 'courses' },
                { href: '../timetable/index.html', icon: '🗓️', text: 'Timetable', id: 'timetable' },
                { href: '../attendance/index.html', icon: '✅', text: 'Attendance', id: 'attendance' },
                { href: '../marks/index.html', icon: '📝', text: 'Marks & Results', id: 'marks' },
            ]
        },
        {
            label: 'Administration', items: [
                { href: '../fees/index.html', icon: '💰', text: 'Fees', id: 'fees' },
                { href: '../reports/index.html', icon: '📊', text: 'Reports', id: 'reports' },
                { href: '../notifications/index.html', icon: '🔔', text: 'Notifications', id: 'notifications' },
            ]
        },
        {
            label: 'System', items: [
                { href: '../settings/index.html', icon: '⚙️', text: 'Settings', id: 'settings' },
            ]
        },
    ];

    const html = nav.map(section => `
    <div class="nav-section-label">${section.label}</div>
    ${section.items.map(item => `
      <a href="${item.href}" class="nav-item ${item.id === activePage ? 'active' : ''}">
        <span class="nav-icon">${item.icon}</span> ${item.text}
      </a>`).join('')}
  `).join('');

    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.querySelector('.sidebar-nav').innerHTML = html;
}

function renderHeader(title, subtitle = '') {
    const user = auth.getUser();
    const header = document.getElementById('page-header');
    if (header) {
        header.innerHTML = `
      <div>
        <div class="header-title">${title}</div>
        ${subtitle ? `<div class="header-subtitle">${subtitle}</div>` : ''}
      </div>
      <div class="header-actions">
        <button class="theme-toggle" onclick="theme.toggle()">🌙</button>
        <div class="avatar">${auth.getUserInitials()}</div>
        <span style="font-size:13px;color:var(--text-muted)">${user?.username || ''}</span>
        <button class="btn btn-ghost btn-sm" onclick="auth.logout()">Logout</button>
      </div>`;
    }
}

window.renderSidebar = renderSidebar;
window.renderHeader = renderHeader;
