// static/js/tabs.js

document.addEventListener('DOMContentLoaded', function () {
    const navItems = document.querySelectorAll('.nav-item');
    const dashboardSection = document.querySelector('.quick-actions');
    const historySection = document.getElementById('historySection');
    const settingsSection = document.getElementById('settingsSection');

    // Function to hide all tabs
    function hideAllSections() {
        dashboardSection.style.display = 'none';
        historySection.style.display = 'none';
        settingsSection.style.display = 'none';
    }

    navItems.forEach(btn => {
        btn.addEventListener('click', function () {
            // Remove active class from all nav items
            navItems.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Hide all sections
            hideAllSections();

            // Show the selected section
            const tab = btn.getAttribute('data-tab');
            if (tab === 'dashboard') dashboardSection.style.display = 'block';
            if (tab === 'history') historySection.style.display = 'block';
            if (tab === 'settings') settingsSection.style.display = 'block';
        });
    });

    // Default visible section → Dashboard
    hideAllSections();
    dashboardSection.style.display = 'block';
});
