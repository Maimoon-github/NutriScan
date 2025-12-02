// Main JavaScript file for NutriScan UI

document.addEventListener('DOMContentLoaded', function() {
    console.log('NutriScan UI loaded');
    initializeUI();
});

function initializeUI() {
    // Initialize event listeners
    initializeFormHandlers();
    initializeImagePreview();
    logPageDebugInfo();
}

function logPageDebugInfo() {
    // Log page-specific debug info
    if (window.location.pathname.includes('/results/')) {
        console.group('NutriScan Results Page Debug Info');
        console.log('URL:', window.location.href);
        
        // Log all data attributes available on the page
        const dataElements = document.querySelectorAll('[data-*]');
        console.log('Elements with data attributes:', dataElements.length);
        
        // Log any visible JSON on the page
        const scripts = document.querySelectorAll('script');
        scripts.forEach((script, idx) => {
            if (script.textContent.includes('const fullResponse')) {
                console.log('Found fullResponse in script');
            }
        });
        
        console.groupEnd();
    }
}

function initializeFormHandlers() {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Log form submission
            console.log('Upload form submitted');
        });
    }
}

function initializeImagePreview() {
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && isValidImageFile(file)) {
                console.log('Valid image file selected:', file.name, '(' + (file.size / 1024).toFixed(2) + ' KB)');
            } else {
                alert('Please select a valid image file (JPG, PNG, GIF - max 5MB)');
            }
        });
    }
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    return validTypes.includes(file.type) && file.size <= maxSize;
}

// Utility function to fetch data with CSRF token
function fetchWithCSRF(url, options = {}) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      getCookie('csrftoken');
    
    const headers = {
        'X-CSRFToken': csrftoken,
        ...options.headers
    };

    return fetch(url, {
        ...options,
        headers
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API call examples
async function uploadImage(formData) {
    try {
        console.log('Starting image upload...');
        const response = await fetchWithCSRF('/upload/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Upload successful:', data);
        console.group('API Response Structure');
        console.log('Response keys:', Object.keys(data));
        console.log('Full response:', data);
        console.groupEnd();
        return data;
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const messagesContainer = document.querySelector('.messages') || document.querySelector('main');
    if (messagesContainer) {
        messagesContainer.insertBefore(notification, messagesContainer.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Expand/collapse detailed sections
function toggleDetails(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.toggle('expanded');
        console.log('Toggled details for:', elementId);
    }
}

// Export functions for use in templates
window.NutriScan = {
    showNotification,
    uploadImage,
    fetchWithCSRF,
    toggleDetails,
    debugLog: function(data) {
        console.group('NutriScan Debug');
        console.log('Debug data:', data);
        console.log('Data type:', typeof data);
        console.log('Data keys:', data && typeof data === 'object' ? Object.keys(data) : 'N/A');
        console.groupEnd();
    }
};
