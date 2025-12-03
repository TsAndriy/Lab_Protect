// ==================== Common Utility Functions ====================

// ==================== Tab Management ====================
function initializeTabs(tabButtonSelector = '.tab-btn', tabContentSelector = '.tab-content') {
    const tabButtons = document.querySelectorAll(tabButtonSelector);
    const tabContents = document.querySelectorAll(tabContentSelector);

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab || button.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
            
            // Deactivate all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Activate selected tab
            button.classList.add('active');
            if (tabId) {
                const targetContent = document.getElementById(tabId);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            }
        });
    });
}

// ==================== File Upload Handling ====================
function setupDragAndDrop(dropZone, handleFileCallback) {
    if (!dropZone) return;

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && handleFileCallback) {
            handleFileCallback(file);
        }
    });
}

// ==================== File Size Formatting ====================
function formatBytes(bytes, decimals = 2) {
    if (!+bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

// Alias for backwards compatibility
const formatFileSize = formatBytes;

// ==================== Loader Functions ====================
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'block';
    }
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// ==================== Notification System ====================
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notification-message');

    if (!notification || !notificationMessage) return;

    notificationMessage.textContent = message;
    notification.className = `notification ${type} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// ==================== Fetch Utility ====================
async function fetchJSON(url, options = {}) {
    try {
        showLoader();
        const response = await fetch(url, options);
        const data = await response.json();
        hideLoader();
        return data;
    } catch (error) {
        hideLoader();
        showNotification('Помилка з\'єднання з сервером', 'error');
        console.error('Fetch error:', error);
        throw error;
    }
}

// ==================== Copy to Clipboard ====================
async function copyToClipboard(text, successMessage = 'Скопійовано в буфер обміну!') {
    try {
        await navigator.clipboard.writeText(text);
        showNotification(successMessage, 'success');
        return true;
    } catch (error) {
        showNotification('Помилка копіювання', 'error');
        console.error('Copy error:', error);
        return false;
    }
}

function initializeCopyButtons(selector = '.btn-copy') {
    document.querySelectorAll(selector).forEach(button => {
        button.addEventListener('click', async () => {
            const targetId = button.dataset.copy;
            if (targetId) {
                const element = document.getElementById(targetId);
                if (element) {
                    await copyToClipboard(element.textContent || element.value);
                }
            }
        });
    });
}

// ==================== Animation Utilities ====================
function fadeIn(element, duration = 300) {
    if (!element) return;
    element.style.animation = `fadeIn ${duration}ms ease`;
    element.style.display = 'block';
}

function fadeOut(element, duration = 300) {
    if (!element) return;
    element.style.animation = `fadeOut ${duration}ms ease`;
    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

// ==================== Export to File ====================
function downloadFile(content, filename, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ==================== Hex Conversion Utilities ====================
function hexToBytes(hex) {
    const bytes = [];
    for (let i = 0; i < hex.length; i += 2) {
        bytes.push(parseInt(hex.substr(i, 2), 16));
    }
    return new Uint8Array(bytes);
}

function bytesToHex(bytes) {
    return Array.from(bytes)
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');
}

function hexToBase64(hex) {
    const bytes = hexToBytes(hex);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// ==================== Initialize Common Features ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize copy buttons if they exist
    if (document.querySelector('.btn-copy')) {
        initializeCopyButtons();
    }
});
