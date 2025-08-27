/**
 * AutoCraftCV Progress Tracking
 * Real-time progress bars for long-running operations
 */

class ProgressTracker {
    constructor() {
        this.activePollers = new Map();
        this.defaultOptions = {
            pollInterval: 2000, // 2 seconds
            maxRetries: 3,
            timeout: 600000 // 10 minutes (increased for longer operations)
        };
    }

    /**
     * Start tracking progress for a task
     * @param {string} taskId - Unique task identifier
     * @param {Object} options - Configuration options
     * @param {Function} options.onProgress - Callback for progress updates
     * @param {Function} options.onComplete - Callback when task completes
     * @param {Function} options.onError - Callback for errors
     * @param {HTMLElement} options.progressContainer - Container for progress elements
     */
    track(taskId, options = {}) {
        const config = { ...this.defaultOptions, ...options };
        
        // Create progress UI if container provided
        if (config.progressContainer) {
            this.createProgressUI(config.progressContainer, taskId);
        }

        // Start polling
        this.startPolling(taskId, config);
    }

    /**
     * Create progress UI elements
     */
    createProgressUI(container, taskId) {
        const progressHtml = `
            <div id="progress-${taskId}" class="progress-tracker">
                <div class="progress-header">
                    <h5 class="progress-title">Processing...</h5>
                    <span class="progress-stage">1/1</span>
                </div>
                <div class="progress mb-3">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 0%">
                        <span class="progress-text">0%</span>
                    </div>
                </div>
                <div class="progress-status">
                    <small class="text-muted">Initializing...</small>
                </div>
                <div class="progress-time">
                    <small class="text-muted">
                        <span class="elapsed-time">0s elapsed</span>
                        <span class="estimated-time" style="display: none;">• ~30s remaining</span>
                    </small>
                </div>
                <div class="progress-actions mt-2" style="display: none;">
                    <button type="button" class="btn btn-outline-secondary btn-sm cancel-btn">
                        Cancel
                    </button>
                </div>
            </div>
        `;
        
        container.innerHTML = progressHtml;
        
        // Add cancel handler
        const cancelBtn = container.querySelector('.cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelTask(taskId);
            });
        }
    }

    /**
     * Start polling for progress updates
     */
    startPolling(taskId, config) {
        const startTime = Date.now();
        let retryCount = 0;

        const poller = {
            intervalId: null,
            config: config,
            startTime: startTime
        };

        const poll = () => {
            fetch(`/api/progress/${taskId}/`)
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 404) {
                            throw new Error(`Task ${taskId} not found - it may have expired or been cleaned up`);
                        } else if (response.status === 500) {
                            throw new Error(`Server error - please try again later`);
                        } else {
                            throw new Error(`HTTP ${response.status} - ${response.statusText}`);
                        }
                    }
                    return response.json();
                })
                .then(data => {
                    retryCount = 0; // Reset retry count on success
                    this.updateProgress(taskId, data, config);

                    if (data.completed || data.error) {
                        this.stopPolling(taskId);
                        
                        if (data.error) {
                            if (config.onError) {
                                config.onError(data);
                            }
                        } else if (config.onComplete) {
                            config.onComplete(data);
                        }
                    }
                })
                .catch(error => {
                    console.error('Progress polling error:', error);
                    
                    // Special handling for 404 errors (task not found)
                    if (error.message.includes('not found') || error.message.includes('404')) {
                        // Try recovery before giving up
                        fetch(`/api/recover-progress/${taskId}/`)
                            .then(response => response.json())
                            .then(recoveryData => {
                                if (recoveryData.status === 'found' || recoveryData.status === 'recovered') {
                                    console.log('Progress recovery successful:', recoveryData);
                                    // Update with recovery data
                                    this.updateProgress(taskId, recoveryData.progress_data, config);
                                    return;
                                }
                                
                                // Still failed, stop polling
                                this.stopPolling(taskId);
                                if (config.onError) {
                                    config.onError({
                                        error: 'Task not found',
                                        details: error.message + '. Recovery also failed.',
                                        is404: true,
                                        recovery_attempted: true
                                    });
                                }
                            })
                            .catch(recoveryError => {
                                console.error('Progress recovery failed:', recoveryError);
                                this.stopPolling(taskId);
                                if (config.onError) {
                                    config.onError({
                                        error: 'Task not found',
                                        details: error.message + '. Recovery failed: ' + recoveryError.message,
                                        is404: true,
                                        recovery_attempted: true
                                    });
                                }
                            });
                        return;
                    }
                    
                    retryCount++;
                    
                    if (retryCount >= config.maxRetries) {
                        this.stopPolling(taskId);
                        if (config.onError) {
                            config.onError({
                                error: 'Failed to get progress updates',
                                details: error.message
                            });
                        }
                    }
                });

            // Check timeout
            if (Date.now() - startTime > config.timeout) {
                this.stopPolling(taskId);
                if (config.onError) {
                    config.onError({
                        error: 'Operation timed out',
                        details: 'Task took longer than expected'
                    });
                }
            }
        };

        poller.intervalId = setInterval(poll, config.pollInterval);
        this.activePollers.set(taskId, poller);

        // Initial poll
        poll();
    }

    /**
     * Update progress UI
     */
    updateProgress(taskId, data, config) {
        // Update UI elements
        const progressContainer = document.getElementById(`progress-${taskId}`);
        if (progressContainer) {
            this.updateProgressUI(progressContainer, data);
        }

        // Call progress callback
        if (config.onProgress) {
            config.onProgress(data);
        }
    }

    /**
     * Update progress UI elements
     */
    updateProgressUI(container, data) {
        const progressBar = container.querySelector('.progress-bar');
        const progressText = container.querySelector('.progress-text');
        const progressStage = container.querySelector('.progress-stage');
        const progressStatus = container.querySelector('.progress-status small');
        const elapsedTime = container.querySelector('.elapsed-time');
        const estimatedTime = container.querySelector('.estimated-time');
        const cancelBtn = container.querySelector('.cancel-btn');

        // Update progress bar
        if (progressBar && progressText) {
            const percentage = Math.min(100, Math.max(0, data.progress || 0));
            progressBar.style.width = `${percentage}%`;
            progressText.textContent = `${percentage}%`;

            // Update colors based on status
            progressBar.className = 'progress-bar progress-bar-striped';
            if (data.error) {
                progressBar.classList.add('bg-danger');
            } else if (data.completed) {
                progressBar.classList.add('bg-success');
                progressBar.classList.remove('progress-bar-animated');
            } else {
                progressBar.classList.add('bg-primary', 'progress-bar-animated');
            }
        }

        // Update stage
        if (progressStage && data.stage) {
            progressStage.textContent = data.stage;
        }

        // Update status message
        if (progressStatus) {
            progressStatus.textContent = data.status || 'Processing...';
            if (data.error) {
                progressStatus.className = 'text-danger';
            } else if (data.completed) {
                progressStatus.className = 'text-success';
            } else {
                progressStatus.className = 'text-muted';
            }
        }

        // Update time information
        if (elapsedTime && data.elapsed_time) {
            elapsedTime.textContent = `${data.elapsed_time}s elapsed`;
        }

        if (estimatedTime && data.estimated_remaining) {
            estimatedTime.textContent = `• ~${data.estimated_remaining}s remaining`;
            estimatedTime.style.display = 'inline';
        }

        // Show/hide cancel button
        if (cancelBtn) {
            if (data.completed || data.error) {
                cancelBtn.style.display = 'none';
            } else {
                cancelBtn.style.display = 'inline-block';
            }
        }
    }

    /**
     * Stop polling for a task
     */
    stopPolling(taskId) {
        const poller = this.activePollers.get(taskId);
        if (poller && poller.intervalId) {
            clearInterval(poller.intervalId);
            this.activePollers.delete(taskId);
        }
    }

    /**
     * Cancel a task
     */
    cancelTask(taskId) {
        this.stopPolling(taskId);
        
        // Update UI to show cancelled state
        const progressContainer = document.getElementById(`progress-${taskId}`);
        if (progressContainer) {
            const progressStatus = progressContainer.querySelector('.progress-status small');
            if (progressStatus) {
                progressStatus.textContent = 'Cancelled by user';
                progressStatus.className = 'text-warning';
            }
            
            const progressBar = progressContainer.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.add('bg-warning');
            }
        }
    }

    /**
     * Clean up all active pollers
     */
    cleanup() {
        this.activePollers.forEach((poller, taskId) => {
            this.stopPolling(taskId);
        });
    }
}

/**
 * Enhanced form handling with progress tracking
 */
class ProgressForm {
    constructor(formElement, options = {}) {
        this.form = formElement;
        this.options = {
            progressContainer: null,
            endpoint: '',
            method: 'POST',
            onSuccess: null,
            onError: null,
            ...options
        };
        
        this.tracker = new ProgressTracker();
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
    }

    async handleSubmit() {
        const formData = new FormData(this.form);
        const submitBtn = this.form.querySelector('button[type="submit"]');
        
        // Disable form
        this.setFormDisabled(true);
        if (submitBtn) {
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Processing...';
        }

        try {
            // Submit form and get task ID
            const response = await fetch(this.options.endpoint, {
                method: this.options.method,
                body: this.options.method === 'POST' ? formData : null,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            if (data.task_id) {
                // Start tracking progress
                this.tracker.track(data.task_id, {
                    progressContainer: this.options.progressContainer,
                    onComplete: (progressData) => {
                        this.handleSuccess(progressData);
                    },
                    onError: (errorData) => {
                        this.handleError(errorData);
                    }
                });
            } else {
                // Handle immediate response
                this.handleSuccess(data);
            }

        } catch (error) {
            this.handleError({ error: error.message });
        }
    }

    handleSuccess(data) {
        this.setFormDisabled(false);
        
        if (this.options.onSuccess) {
            this.options.onSuccess(data);
        } else {
            // Default success handling
            this.showMessage('Operation completed successfully!', 'success');
        }
    }

    handleError(data) {
        this.setFormDisabled(false);
        
        if (this.options.onError) {
            this.options.onError(data);
        } else {
            // Default error handling
            this.showMessage(data.error || 'An error occurred', 'error');
        }
    }

    setFormDisabled(disabled) {
        const inputs = this.form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            input.disabled = disabled;
        });

        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            if (disabled) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Processing...';
            } else {
                submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
            }
        }
    }

    showMessage(message, type) {
        // Create or update message element
        let messageEl = document.getElementById('form-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'form-message';
            this.form.insertBefore(messageEl, this.form.firstChild);
        }

        messageEl.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        messageEl.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
    }

    getCSRFToken() {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return csrfInput ? csrfInput.value : '';
    }
}

// Global progress tracker instance
window.progressTracker = new ProgressTracker();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.progressTracker && typeof window.progressTracker.cleanup === 'function') {
        window.progressTracker.cleanup();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProgressTracker, ProgressForm };
}
