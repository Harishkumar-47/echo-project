// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    registerServiceWorker();
});

// Register service worker for PWA
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('Service Worker registered successfully');
            })
            .catch(function(error) {
                console.log('Service Worker registration failed:', error);
            });
    }
}

function initializeApp() {
    // Initialize bottom navigation
    initBottomNav();
    
    // Set up event listeners
    setupEventListeners();
    
    // Hide loading indicator initially
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    // Hide history section initially
    const historySection = document.getElementById('historySection');
    if (historySection) historySection.style.display = 'none';
}

function initBottomNav() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Handle navigation
            const tab = this.dataset.tab;
            handleNavigation(tab);
        });
    });
}

function handleNavigation(tab) {
    switch(tab) {
        case 'dashboard':
            showDashboard();
            break;
        case 'history':
            showHistory();
            break;
        case 'settings':
            showSettings();
            break;
    }
}

function showDashboard() {
    // Show main dashboard content
    document.querySelector('.quick-actions').style.display = 'block';
    hideAdvancedSearch();
    hideResults();
    // Hide history section
    const historySection = document.getElementById('historySection');
    if (historySection) historySection.style.display = 'none';
}

function showHistory() {
    // Hide other main sections
    document.querySelector('.quick-actions').style.display = 'none';
    hideAdvancedSearch();
    hideResults();
    // Show history section
    const historySection = document.getElementById('historySection');
    if (historySection) historySection.style.display = 'block';
}

function showSettings() {
    // Show settings section, no alert
    document.querySelector('.quick-actions').style.display = 'none';
    hideAdvancedSearch();
    hideResults();
    const historySection = document.getElementById('historySection');
    if (historySection) historySection.style.display = 'none';
    const settingsSection = document.getElementById('settingsSection');
    if (settingsSection) settingsSection.style.display = 'block';
}

function setupEventListeners() {
    // Add event listeners for various interactions
    document.addEventListener('click', handleClicks);
    
    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

function handleClicks(event) {
    const target = event.target;
    
    // Handle action card clicks
    if (target.closest('.action-card')) {
        const card = target.closest('.action-card');
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);
    }
}

function handleFormSubmit(event) {
    event.preventDefault();
    // Handle form submissions here
}

// Quick scan functions
function quickScan(type) {
    showResults();
    showLoading();
    
    // Simulate API call
    setTimeout(() => {
        hideLoading();
        populateResults(type);
    }, 2000);
}

function showAdvancedSearch() {
    const advancedSearch = document.getElementById('advancedSearch');
    const quickActions = document.querySelector('.quick-actions');
    
    if (advancedSearch) {
        advancedSearch.style.display = 'block';
        advancedSearch.scrollIntoView({ behavior: 'smooth' });
    }
}

function hideAdvancedSearch() {
    const advancedSearch = document.getElementById('advancedSearch');
    if (advancedSearch) {
        advancedSearch.style.display = 'none';
    }
}

function startAdvancedScan() {
    // Get form values
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const fileName = document.getElementById('fileName').value;
    
    // Get selected file types
    const selectedTypes = [];
    const checkboxes = document.querySelectorAll('.chip input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
        selectedTypes.push(checkbox.value);
    });
    
    console.log('Advanced scan parameters:', {
        dateFrom,
        dateTo,
        fileName,
        selectedTypes
    });
    
    showResults();
    showLoading();
    
    // Simulate API call
    setTimeout(() => {
        hideLoading();
        populateAdvancedResults({ dateFrom, dateTo, fileName, selectedTypes });
    }, 3000);
}

function showResults() {
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function hideResults() {
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
}

function showLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
    }
}

function populateResults(type) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    
    // Sample data based on scan type
    let sampleData = getSampleData(type);
    
    resultsContainer.innerHTML = '';
    
    if (sampleData.length === 0) {
        let message = getNoResultsMessage(type);
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="${message.icon}" style="font-size: 48px; margin-bottom: 16px; color: #ddd;"></i>
                <h3>${message.title}</h3>
                <p>${message.description}</p>
            </div>
        `;
        return;
    }
    
    sampleData.forEach(file => {
        const fileItem = createFileItem(file);
        resultsContainer.appendChild(fileItem);
    });
}

function populateAdvancedResults(searchParams) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    
    // Generate results based on advanced search parameters
    let sampleData = getAdvancedSampleData(searchParams);
    
    resultsContainer.innerHTML = '';
    
    if (sampleData.length === 0) {
        let message = getNoResultsMessage('default');
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="${message.icon}" style="font-size: 48px; margin-bottom: 16px; color: #ddd;"></i>
                <h3>${message.title}</h3>
                <p>${message.description}</p>
            </div>
        `;
        return;
    }
    
    sampleData.forEach(file => {
        const fileItem = createFileItem(file);
        resultsContainer.appendChild(fileItem);
    });
}

function getSampleData(type) {
    // Return empty array for all types to show "no files found" message
    return [];
}

function getNoResultsMessage(type) {
    const messages = {
        recent: {
            icon: 'fas fa-clock',
            title: 'No Recent Deletions',
            description: 'No files have been deleted from your cloud storage in the last 7 days.'
        },
        images: {
            icon: 'fas fa-image',
            title: 'No Deleted Images',
            description: 'No deleted image files were found in your cloud storage.'
        },
        documents: {
            icon: 'fas fa-file-alt',
            title: 'No Deleted Documents',
            description: 'No deleted document files (PDF, DOC, TXT) were found in your cloud storage.'
        },
        default: {
            icon: 'fas fa-search',
            title: 'No Files Found',
            description: 'No files matching your search criteria were found in the cloud storage.'
        }
    };
    
    return messages[type] || messages.default;
}

function getAdvancedSampleData(searchParams) {
    // Return empty array to show "no files found" message
    return [];
}

function createFileItem(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    
    fileItem.innerHTML = `
        <div class="file-icon">
            <i class="${file.icon}"></i>
        </div>
        <div class="file-info">
            <h4>${file.name}</h4>
            <p>Deleted: ${file.deleted}</p>
            <small>Size: ${file.size}</small>
        </div>
        <button class="recover-btn" onclick="recoverFile('${file.name}')">
            <i class="fas fa-download"></i>
        </button>
    `;
    
    return fileItem;
}

function recoverFile(fileName) {
    // Show recovery animation
    const button = event.target.closest('.recover-btn');
    const originalHTML = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;
    
    // Simulate recovery process
    setTimeout(() => {
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.style.background = '#4CAF50';
        
        // Show success message
        showRecoverySuccess(fileName);
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.disabled = false;
            button.style.background = '';
        }, 2000);
    }, 1500);
}

function showRecoverySuccess(fileName) {
    // Create and show a toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${fileName} recovered successfully!</span>
    `;
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: #4CAF50;
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 12px rgba(76,175,80,0.3);
        animation: slideDown 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // Simulate logout
        window.location.href = 'login.html';
    }
}

// Add CSS for toast animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
`;
document.head.appendChild(style);