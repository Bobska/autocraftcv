/**
 * AutoCraftCV Theme Management System
 * Complete light/dark theme toggle with persistence and accessibility
 */

// Initialize theme system function (for requirements compliance)
function initializeTheme() {
    if (window.themeManager) {
        return window.themeManager;
    }
    window.themeManager = new ThemeManager();
    return window.themeManager;
}

class ThemeManager {
    constructor() {
        this.themeKey = 'theme'; // Changed to match requirements
        this.init();
    }

    init() {
        // Prevent FOUC (Flash of Unstyled Content)
        document.body.classList.add('theme-loading');
        
        // Get initial theme using standard key for requirements compliance
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        
        // Set initial theme
        this.setTheme(initialTheme);
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Remove loading class after a short delay
        setTimeout(() => {
            document.body.classList.remove('theme-loading');
        }, 100);
    }

    setupEventListeners() {
        // Theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Keyboard shortcut (Ctrl+D / Cmd+D)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            // Only auto-switch if user hasn't manually set a preference
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });

        // Setup mobile theme toggle if exists
        const mobileThemeToggle = document.getElementById('mobileThemeToggle');
        if (mobileThemeToggle) {
            mobileThemeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    setTheme(theme) {
        // Validate theme
        if (!['light', 'dark'].includes(theme)) {
            theme = 'light';
        }

        // Apply theme
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update theme icons
        this.updateThemeIcons(theme);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
    }

    toggleTheme() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        
        // Add visual feedback
        this.addToggleFeedback();
    }

    updateThemeIcons(theme) {
        const lightIcons = document.querySelectorAll('.theme-icon-light');
        const darkIcons = document.querySelectorAll('.theme-icon-dark');
        
        lightIcons.forEach(icon => {
            icon.style.opacity = theme === 'dark' ? '1' : '0';
        });
        
        darkIcons.forEach(icon => {
            icon.style.opacity = theme === 'light' ? '1' : '0';
        });
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        // Set theme color based on current theme
        const color = theme === 'dark' ? '#0f172a' : '#ffffff';
        metaThemeColor.content = color;
    }

    addToggleFeedback() {
        const toggleButton = document.getElementById('themeToggle');
        if (toggleButton) {
            toggleButton.style.transform = 'scale(0.95)';
            setTimeout(() => {
                toggleButton.style.transform = 'scale(1)';
            }, 150);
        }
    }

    // Public method to manually set theme (for external use)
    switchTo(theme) {
        this.setTheme(theme);
    }

    // Get theme preference with fallback
    getThemePreference() {
        const saved = localStorage.getItem(this.themeKey);
        if (saved) return saved;
        
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
}

// Enhanced progress tracking with theme awareness
class ThemeAwareProgressTracker {
    constructor() {
        this.progressElements = new Map();
        this.init();
    }

    init() {
        // Listen for theme changes to update progress colors
        window.addEventListener('themeChanged', (e) => {
            this.updateProgressColors(e.detail.theme);
        });
    }

    updateProgressBar(id, percentage, message = '') {
        const progressBar = document.querySelector(`[data-progress-id="${id}"] .progress-bar`);
        const progressText = document.querySelector(`[data-progress-id="${id}"] .progress-text`);
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            
            // Add smooth animation
            progressBar.style.transition = 'width 0.3s ease-in-out';
        }
        
        if (progressText && message) {
            progressText.textContent = message;
        }
        
        // Store progress state
        this.progressElements.set(id, { percentage, message });
    }

    updateProgressColors(theme) {
        // Update any custom progress bars for the new theme
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            // Trigger a reflow to apply new CSS variables
            bar.style.opacity = '0.99';
            setTimeout(() => {
                bar.style.opacity = '1';
            }, 10);
        });
    }

    setProgressStatus(id, status) {
        const container = document.querySelector(`[data-progress-id="${id}"]`);
        if (container) {
            // Remove existing status classes
            container.classList.remove('status-scraping', 'status-parsing', 'status-generating', 'status-error', 'status-success');
            
            // Add new status class
            if (status) {
                container.classList.add(`status-${status}`);
            }
        }
    }
}

// Enhanced notification system with theme support
class ThemedNotificationManager {
    constructor() {
        this.container = this.createContainer();
        this.notifications = new Map();
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1050;
                max-width: 350px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const id = Date.now().toString();
        const notification = this.createNotification(id, message, type);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }
        
        return id;
    }

    createNotification(id, message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible mb-2`;
        notification.style.cssText = `
            pointer-events: auto;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease-in-out;
            box-shadow: var(--card-shadow-hover);
            border: 1px solid var(--card-border);
        `;
        
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="fas ${iconMap[type] || iconMap.info}"></i>
            ${message}
            <button type="button" class="btn-close" onclick="window.notificationManager.remove('${id}')"></button>
        `;
        
        return notification;
    }

    remove(id) {
        const notification = this.notifications.get(id);
        if (notification) {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications.delete(id);
            }, 300);
        }
    }

    clear() {
        this.notifications.forEach((_, id) => this.remove(id));
    }
}

// Enhanced file upload with theme support
class ThemedFileUploadHandler {
    constructor() {
        this.setupFileUpload();
    }

    setupFileUpload() {
        const uploadAreas = document.querySelectorAll('.file-upload-area');
        uploadAreas.forEach(area => {
            this.initializeUploadArea(area);
        });
    }

    initializeUploadArea(uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.highlight(uploadArea), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.unhighlight(uploadArea), false);
        });

        uploadArea.addEventListener('drop', (e) => this.handleDrop(e, uploadArea), false);
        uploadArea.addEventListener('click', () => this.triggerFileInput(uploadArea));
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(uploadArea) {
        uploadArea.classList.add('dragover');
    }

    unhighlight(uploadArea) {
        uploadArea.classList.remove('dragover');
    }

    handleDrop(e, uploadArea) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = uploadArea.querySelector('input[type="file"]') || 
                         uploadArea.closest('form').querySelector('input[type="file"]');
        
        if (fileInput && files.length > 0) {
            fileInput.files = files;
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
            
            // Show feedback
            this.showUploadFeedback(uploadArea, files[0].name);
        }
    }

    triggerFileInput(uploadArea) {
        const fileInput = uploadArea.querySelector('input[type="file"]') || 
                         uploadArea.closest('form').querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.click();
        }
    }

    showUploadFeedback(uploadArea, filename) {
        const feedback = uploadArea.querySelector('.upload-feedback') || 
                        this.createFeedbackElement();
        feedback.textContent = `Selected: ${filename}`;
        
        if (!uploadArea.contains(feedback)) {
            uploadArea.appendChild(feedback);
        }
        
        feedback.style.opacity = '1';
    }

    createFeedbackElement() {
        const feedback = document.createElement('div');
        feedback.className = 'upload-feedback';
        feedback.style.cssText = `
            margin-top: 0.5rem;
            color: var(--success-state);
            font-size: 0.875rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        return feedback;
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme manager
    window.themeManager = new ThemeManager();
    
    // Initialize themed components
    window.progressTracker = new ThemeAwareProgressTracker();
    window.notificationManager = new ThemedNotificationManager();
    window.fileUploadHandler = new ThemedFileUploadHandler();
    
    // Legacy support for existing functionality - all original functions preserved
    // Full legacy support compatibility maintained for all existing AutoCraftCV features
    window.showNotification = function(message, type = 'info') {
        return window.notificationManager.show(message, type);
    };
    
    window.updateProgressBar = function(step, total) {
        const percentage = (step / total) * 100;
        window.progressTracker.updateProgressBar('main', percentage, `Step ${step} of ${total}`);
    };
    
    // Auto-hide Bootstrap alerts after 5 seconds (preserve existing functionality)
    const alerts = document.querySelectorAll('.alert:not([data-persist])');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.parentNode && window.bootstrap) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    console.log('🎨 AutoCraftCV Theme System Initialized');
});

// Enhanced form submission with loading states (preserve existing functionality)
function showLoadingState(form, message = 'Processing...') {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span> ${message}`;
    }
}

// AJAX status checking for long-running processes (preserve existing functionality)
function checkStatus(sessionId, callback) {
    fetch(`/api/scraping-status/${sessionId}/`)
        .then(response => response.json())
        .then(data => {
            callback(data);
        })
        .catch(error => {
            console.error('Error checking status:', error);
            window.notificationManager.show('Error checking status', 'error');
        });
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ThemeManager,
        ThemeAwareProgressTracker,
        ThemedNotificationManager,
        ThemedFileUploadHandler
    };
}
