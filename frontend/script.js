/**
 * Audio Steganography - Global JavaScript
 * Shared functionality for all pages
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    styleRangeInputs();
});

/**
 * Initialize navigation highlighting
 */
function initializeNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Style range inputs for better appearance
 */
function styleRangeInputs() {
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    
    rangeInputs.forEach(input => {
        // Webkit browsers (Chrome, Safari)
        const style = `
            ::-webkit-slider-thumb {
                appearance: none;
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                cursor: pointer;
                box-shadow: 0 0 10px rgba(0, 255, 136, 0.4);
                border: 2px solid var(--primary-bg);
            }
            
            ::-webkit-slider-thumb:hover {
                box-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
            }
            
            ::-moz-range-thumb {
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                cursor: pointer;
                box-shadow: 0 0 10px rgba(0, 255, 136, 0.4);
                border: 2px solid var(--primary-bg);
            }
            
            ::-moz-range-thumb:hover {
                box-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
            }
        `;
    });
}

/**
 * Format file size in human-readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Validate WAV file
 */
function isValidWAV(file) {
    return file && file.type === 'audio/wav' && file.name.endsWith('.wav');
}

/**
 * Validate alphanumeric message
 */
function isValidMessage(text) {
    return /^[a-zA-Z0-9\s]*$/.test(text);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    return navigator.clipboard.writeText(text);
}

/**
 * Download text file
 */
function downloadTextFile(content, filename) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        background: var(--card-bg);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, duration);
}

/**
 * Debounce function for input events
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Throttle function for frequent events
 */
function throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastCall >= delay) {
            lastCall = now;
            func(...args);
        }
    };
}

/**
 * Format time duration
 */
function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
    } else {
        return `${seconds}s`;
    }
}

/**
 * Generate unique ID
 */
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Check browser support for audio API
 */
function checkAudioSupport() {
    const audioContext = window.AudioContext || window.webkitAudioContext;
    return audioContext ? true : false;
}

/**
 * Smooth scroll to element
 */
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Show loading state on button
 */
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = '⏳ Processing...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

/**
 * Form validation helper
 */
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--error-color)';
            isValid = false;
        } else {
            input.style.borderColor = '';
        }
    });
    
    return isValid;
}

/**
 * Reset form and clear validation styles
 */
function resetFormValidation(formElement) {
    const inputs = formElement.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.style.borderColor = '';
    });
}

/**
 * Analytics event tracking (placeholder for future implementation)
 */
function trackEvent(eventName, eventData = {}) {
    if (window.gtag) {
        gtag('event', eventName, eventData);
    }
    // Fallback: log to console in development
    if (process.env.NODE_ENV === 'development') {
        console.log('Event:', eventName, eventData);
    }
}

/**
 * Create a simple bar chart using CSS
 */
function createBarChart(containerId, data, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const maxValue = Math.max(...data.map(d => d.value));
    const chartHTML = data.map(item => `
        <div style="margin-bottom: 1rem;">
            <div style="color: var(--text-secondary); margin-bottom: 0.5rem;">${item.label}</div>
            <div style="background: var(--border-color); border-radius: 4px; height: 20px; overflow: hidden;">
                <div style="
                    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
                    height: 100%;
                    width: ${(item.value / maxValue) * 100}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <div style="color: var(--accent-primary); margin-top: 0.3rem; font-weight: bold;">${item.value}${options.unit || ''}</div>
        </div>
    `).join('');
    
    container.innerHTML = chartHTML;
}

/**
 * Create a progress indicator
 */
function updateProgressBar(progressBarId, percentage) {
    const progressFill = document.getElementById(progressBarId);
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
}

/**
 * Format percentage with decimal places
 */
function formatPercentage(value, decimals = 1) {
    return (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals) + '%';
}

/**
 * Create table from data
 */
function createTable(containerId, headers, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let tableHTML = '<table style="width: 100%; border-collapse: collapse;">';
    
    // Headers
    tableHTML += '<thead><tr>';
    headers.forEach(header => {
        tableHTML += `<th style="padding: 0.5rem; text-align: left; border-bottom: 2px solid var(--border-color); color: var(--accent-primary);">${header}</th>`;
    });
    tableHTML += '</tr></thead>';
    
    // Body
    tableHTML += '<tbody>';
    data.forEach((row, index) => {
        const bgColor = index % 2 === 0 ? 'transparent' : 'rgba(0, 255, 136, 0.05)';
        tableHTML += `<tr style="background: ${bgColor};">`;
        row.forEach(cell => {
            tableHTML += `<td style="padding: 0.5rem; border-bottom: 1px solid var(--border-color); color: var(--text-secondary);">${cell}</td>`;
        });
        tableHTML += '</tr>';
    });
    tableHTML += '</tbody></table>';
    
    container.innerHTML = tableHTML;
}

/**
 * Simple state manager for pages
 */
class PageState {
    constructor(storageKey) {
        this.storageKey = storageKey;
        this.data = JSON.parse(localStorage.getItem(storageKey) || '{}');
    }
    
    set(key, value) {
        this.data[key] = value;
        this.save();
    }
    
    get(key, defaultValue = null) {
        return this.data[key] !== undefined ? this.data[key] : defaultValue;
    }
    
    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.data));
    }
    
    clear() {
        this.data = {};
        localStorage.removeItem(this.storageKey);
    }
}

// Export for use in other scripts
window.AudioStegUtils = {
    formatFileSize,
    isValidWAV,
    isValidMessage,
    copyToClipboard,
    downloadTextFile,
    showToast,
    debounce,
    throttle,
    formatDuration,
    generateId,
    checkAudioSupport,
    smoothScrollTo,
    setButtonLoading,
    validateForm,
    resetFormValidation,
    trackEvent,
    createBarChart,
    updateProgressBar,
    formatPercentage,
    createTable,
    PageState
};
