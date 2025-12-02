// Main JavaScript file for NutriScan UI

document.addEventListener('DOMContentLoaded', function() {
    console.log('NutriScan UI loaded');
    initializeUI();
});

function initializeUI() {
    // Initialize event listeners
    initializeFormHandlers();
    initializeImagePreview();
}

function initializeFormHandlers() {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Form submission will be handled by Django
            console.log('Form submitted');
        });
    }
}

function initializeImagePreview() {
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && isValidImageFile(file)) {
                console.log('Valid image file selected:', file.name);
            } else {
                alert('Please select a valid image file');
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
        const response = await fetchWithCSRF('/api/upload/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Upload successful:', data);
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

// Export functions for use in templates
window.NutriScan = {
    showNotification,
    uploadImage,
    fetchWithCSRF
};
