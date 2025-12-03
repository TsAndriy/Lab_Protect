/**
 * Спільні утиліти для всіх лабораторних робіт
 * Містить повторювані функції для роботи з вкладками, завантаженням файлів, 
 * сповіщеннями та іншими загальними операціями
 */

// ==================== Управління вкладками ====================

/**
 * Ініціалізує систему вкладок
 * Працює з елементами класів .tab-btn та .tab-content
 */
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            
            if (!tabId) return;

            // Деактивуємо всі вкладки
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Активуємо вибрану вкладку
            button.classList.add('active');
            const targetContent = document.getElementById(tabId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

/**
 * Переключає вкладку програмно
 * @param {string} tabId - ID вкладки для активації
 */
function switchTab(tabId) {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => btn.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));

    const targetButton = Array.from(tabButtons).find(btn => 
        btn.dataset.tab === tabId
    );
    
    if (targetButton) {
        targetButton.classList.add('active');
    }

    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// ==================== Завантажувач (Loader) ====================

/**
 * Показує індикатор завантаження
 */
function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'block';
        loader.classList.add('show');
    }
}

/**
 * Приховує індикатор завантаження
 */
function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
        loader.classList.remove('show');
    }
}

// ==================== Повідомлення (Notifications) ====================

/**
 * Показує сповіщення користувачу
 * @param {string} message - Текст повідомлення
 * @param {string} type - Тип повідомлення: 'success', 'error', 'info'
 * @param {number} duration - Тривалість показу в мілісекундах (за замовчуванням 3000)
 */
function showNotification(message, type = 'success', duration = 3000) {
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notification-message');

    if (!notification || !notificationMessage) return;

    notificationMessage.textContent = message;
    notification.className = `notification ${type} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, duration);
}

// ==================== Робота з файлами ====================

/**
 * Налаштовує Drag & Drop для завантаження файлів
 * @param {HTMLElement} dropZone - Елемент зони для перетягування
 * @param {Function} handleFileCallback - Callback функція для обробки файлу
 */
function setupDragAndDrop(dropZone, handleFileCallback) {
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0 && handleFileCallback) {
            handleFileCallback(files[0]);
        }
    }, false);
}

/**
 * Форматує розмір файлу в читабельний формат
 * @param {number} bytes - Розмір в байтах
 * @param {number} decimals - Кількість знаків після коми
 * @returns {string} Форматований рядок розміру
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Завантажує текст як файл
 * @param {string} content - Вміст файлу
 * @param {string} filename - Ім'я файлу
 * @param {string} mimeType - MIME тип файлу
 */
function downloadTextAsFile(content, filename, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Завантажує бінарні дані як файл
 * @param {Blob} blob - Об'єкт Blob з даними
 * @param {string} filename - Ім'я файлу
 */
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// ==================== Робота з буфером обміну ====================

/**
 * Копіює текст у буфер обміну
 * @param {string} text - Текст для копіювання
 * @returns {Promise<boolean>} Promise з результатом операції
 */
async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return true;
        } else {
            // Fallback для старих браузерів
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return true;
            } catch (err) {
                document.body.removeChild(textArea);
                return false;
            }
        }
    } catch (err) {
        console.error('Помилка копіювання:', err);
        return false;
    }
}

/**
 * Копіює текст з елемента за ID
 * @param {string} elementId - ID елемента з текстом
 */
async function copyText(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const text = element.textContent || element.value;
    const success = await copyToClipboard(text);

    if (success) {
        showNotification('Скопійовано в буфер обміну!', 'success');
    } else {
        showNotification('Помилка копіювання', 'error');
    }
}

// ==================== Конвертація даних ====================

/**
 * Конвертує ArrayBuffer в HEX рядок
 * @param {ArrayBuffer} buffer - Буфер для конвертації
 * @returns {string} HEX рядок
 */
function arrayBufferToHex(buffer) {
    return Array.from(new Uint8Array(buffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

/**
 * Конвертує HEX рядок в ArrayBuffer
 * @param {string} hexString - HEX рядок
 * @returns {ArrayBuffer} Буфер
 */
function hexToArrayBuffer(hexString) {
    const hex = hexString.replace(/\s/g, '');
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
    }
    return bytes.buffer;
}

/**
 * Конвертує ArrayBuffer в Base64 рядок
 * @param {ArrayBuffer} buffer - Буфер для конвертації
 * @returns {string} Base64 рядок
 */
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

/**
 * Конвертує Base64 рядок в ArrayBuffer
 * @param {string} base64 - Base64 рядок
 * @returns {ArrayBuffer} Буфер
 */
function base64ToArrayBuffer(base64) {
    const binary = window.atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

// ==================== HTTP запити ====================

/**
 * Виконує POST запит до серверу
 * @param {string} url - URL ендпоінту
 * @param {Object|FormData} data - Дані для відправки
 * @param {boolean} isFormData - Чи є дані FormData
 * @returns {Promise<Object>} Promise з відповіддю сервера
 */
async function postRequest(url, data, isFormData = false) {
    const options = {
        method: 'POST',
        body: isFormData ? data : JSON.stringify(data)
    };

    if (!isFormData) {
        options.headers = {
            'Content-Type': 'application/json'
        };
    }

    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('Помилка запиту:', error);
        throw error;
    }
}

// ==================== Валідація ====================

/**
 * Перевіряє чи є рядок валідним HEX
 * @param {string} hex - HEX рядок для перевірки
 * @returns {boolean} true якщо валідний
 */
function isValidHex(hex) {
    const cleanHex = hex.replace(/\s/g, '');
    return /^[0-9A-Fa-f]+$/.test(cleanHex) && cleanHex.length % 2 === 0;
}

/**
 * Перевіряє чи є рядок валідним Base64
 * @param {string} str - Base64 рядок для перевірки
 * @returns {boolean} true якщо валідний
 */
function isValidBase64(str) {
    try {
        return btoa(atob(str)) === str;
    } catch (err) {
        return false;
    }
}

// ==================== Автоматична ініціалізація ====================

// Автоматично ініціалізуємо вкладки при завантаженні сторінки
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initializeTabs);
}

// ==================== Експорт модулів (для сумісності) ====================

// Якщо використовується як модуль
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeTabs,
        switchTab,
        showLoader,
        hideLoader,
        showNotification,
        setupDragAndDrop,
        formatBytes,
        downloadTextAsFile,
        downloadBlob,
        copyToClipboard,
        copyText,
        arrayBufferToHex,
        hexToArrayBuffer,
        arrayBufferToBase64,
        base64ToArrayBuffer,
        postRequest,
        isValidHex,
        isValidBase64
    };
}
