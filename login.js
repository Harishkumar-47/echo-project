// Login functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeLoginForm();
});

function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Add interactive effects to form elements
    setupInputEffects();
    setupCloudProviderSelection();
}

function setupInputEffects() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
}

function setupCloudProviderSelection() {
    const cloudOptions = document.querySelectorAll('input[name="cloudProvider"]');
    
    cloudOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Remove selected class from all options
            document.querySelectorAll('.cloud-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Add selected class to current option
            if (this.checked) {
                this.closest('.cloud-option').classList.add('selected');
            }
        });
    });
}

function handleLogin(event) {
    event.preventDefault();
    
    // Get form values
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const cloudProvider = document.querySelector('input[name="cloudProvider"]:checked');
    
    // Basic validation
    if (!username || !password) {
        showError('Please enter both username and password.');
        return;
    }
    
    if (!cloudProvider) {
        showError('Please select a cloud provider.');
        return;
    }
    
    // Show loading state
    showLoginLoading();
    
    // Simulate login process
    setTimeout(() => {
        hideLoginLoading();
        
        // For demo purposes, always "succeed" the login
        showSuccess(`Connecting to ${cloudProvider.value}...`);
        
        // Redirect to dashboard after success
        setTimeout(() => {
            window.location.href = '../demo.html';
        }, 2000);
        
    }, 2000);
}

function showLoginLoading() {
    const loginBtn = document.querySelector('.login-btn');
    const originalHTML = loginBtn.innerHTML;
    
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
    loginBtn.dataset.originalHtml = originalHTML;
}

function hideLoginLoading() {
    const loginBtn = document.querySelector('.login-btn');
    const originalHTML = loginBtn.dataset.originalHtml;
    
    loginBtn.disabled = false;
    loginBtn.innerHTML = originalHTML;
}

function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showNotification(message, type) {
    // Remove existing notifications
    const existingNotif = document.querySelector('.notification');
    if (existingNotif) {
        existingNotif.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'error' ? '#f44336' : '#4CAF50'};
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideDown 0.3s ease;
        font-size: 14px;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.remove();
    }, 4000);
}

// Add animation CSS
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
    
    .input-group.focused {
        transform: scale(1.02);
    }
    
    .cloud-option.selected {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
    }
`;
document.head.appendChild(style);