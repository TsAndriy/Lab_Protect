document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeEncryption();
    initializeDecryption();
});

// ==================== Вкладки ====================
function initializeTabs() {
    const buttons = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Деактивуємо все
            buttons.forEach(b => b.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            // Активуємо вибране
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// ==================== Шифрування ====================
function initializeEncryption() {
    const fileInput = document.getElementById('encrypt-file-input');
    const dropZone = document.getElementById('encrypt-drop-zone');
    const textInput = document.getElementById('encrypt-text-input');
    const passwordInput = document.getElementById('encrypt-password');
    const encryptBtn = document.getElementById('btn-encrypt');
    let selectedFile = null;

    // Обробка вибору файлу
    const handleFile = (file) => {
        selectedFile = file;
        document.getElementById('encrypt-file-name').textContent = file.name;
        document.getElementById('encrypt-file-size').textContent = formatBytes(file.size);
        document.getElementById('encrypt-file-info').style.display = 'flex';
        document.querySelector('#encrypt-drop-zone .file-upload-content').style.display = 'none';
        textInput.disabled = true; // Блокуємо ввід тексту, якщо вибрано файл
    };

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) handleFile(e.target.files[0]);
    });

    // Drag & Drop
    setupDragAndDrop(dropZone, handleFile);

    // Очистка файлу, якщо почали вводити текст
    textInput.addEventListener('input', () => {
        if (textInput.value.length > 0 && selectedFile) {
            selectedFile = null;
            fileInput.value = '';
            document.getElementById('encrypt-file-info').style.display = 'none';
            document.querySelector('#encrypt-drop-zone .file-upload-content').style.display = 'block';
            textInput.disabled = false;
        }
    });

    // Клік по кнопці Шифрувати
    encryptBtn.addEventListener('click', async () => {
        const password = passwordInput.value;
        if (!password) {
            showNotification('Введіть пароль!', 'error');
            return;
        }
        if (!selectedFile && !textInput.value) {
            showNotification('Оберіть файл або введіть текст!', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('password', password);

        if (selectedFile) {
            formData.append('file', selectedFile);
        } else {
            formData.append('text', textInput.value);
        }

        try {
            showLoader();
            const response = await fetch('/lab3/encrypt/', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            hideLoader();

            if (result.error) {
                showNotification(result.error, 'error');
            } else {
                displayEncryptResult(result);
                showNotification('Шифрування успішне!', 'success');
            }
        } catch (e) {
            hideLoader();
            showNotification('Помилка з\'єднання: ' + e.message, 'error');
        }
    });
}

function displayEncryptResult(data) {
    const container = document.getElementById('encrypt-result');
    container.style.display = 'block';

    document.getElementById('encrypt-hex-preview').textContent = data.encrypted_hex;
    document.getElementById('encrypt-original-size').textContent = formatBytes(data.original_size);
    document.getElementById('encrypt-output-size').textContent = formatBytes(data.encrypted_size);
    document.getElementById('encrypt-time').textContent = data.execution_time_ms.toFixed(2) + ' мс';

    // Логіка скачування
    const downloadBtn = document.getElementById('btn-download-encrypted');
    downloadBtn.onclick = () => {
        // Викликаємо нову функцію збереження з діалогом
        saveFileWithDialog(data.encrypted_data_full_hex, data.filename, 'hex');
    };
}

// ==================== Дешифрування ====================
function initializeDecryption() {
    const fileInput = document.getElementById('decrypt-file-input');
    const dropZone = document.getElementById('decrypt-drop-zone');
    const hexInput = document.getElementById('decrypt-hex-input');
    const passwordInput = document.getElementById('decrypt-password');
    const decryptBtn = document.getElementById('btn-decrypt');
    let selectedFile = null;

    const handleFile = (file) => {
        selectedFile = file;
        document.getElementById('decrypt-file-name').textContent = file.name;
        document.getElementById('decrypt-file-size').textContent = formatBytes(file.size);
        document.getElementById('decrypt-file-info').style.display = 'flex';
        document.querySelector('#decrypt-drop-zone .file-upload-content').style.display = 'none';
        hexInput.disabled = true;
    };

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) handleFile(e.target.files[0]);
    });

    setupDragAndDrop(dropZone, handleFile);

    hexInput.addEventListener('input', () => {
        if (hexInput.value.length > 0 && selectedFile) {
            selectedFile = null;
            fileInput.value = '';
            document.getElementById('decrypt-file-info').style.display = 'none';
            document.querySelector('#decrypt-drop-zone .file-upload-content').style.display = 'block';
            hexInput.disabled = false;
        }
    });

    decryptBtn.addEventListener('click', async () => {
        const password = passwordInput.value;
        if (!password) {
            showNotification('Введіть пароль!', 'error');
            return;
        }
        if (!selectedFile && !hexInput.value) {
            showNotification('Оберіть файл або введіть HEX!', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('password', password);

        if (selectedFile) {
            formData.append('file', selectedFile);
        } else {
            formData.append('encrypted_hex', hexInput.value.replace(/\s+/g, '')); // Видаляємо пробіли
        }

        try {
            showLoader();
            const response = await fetch('/lab3/decrypt/', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            hideLoader();

            if (result.error) {
                showNotification(result.error, 'error');
            } else {
                displayDecryptResult(result);
                showNotification('Дешифрування успішне!', 'success');
            }
        } catch (e) {
            hideLoader();
            showNotification('Помилка з\'єднання: ' + e.message, 'error');
        }
    });
}

function displayDecryptResult(data) {
    const container = document.getElementById('decrypt-result');
    container.style.display = 'block';

    // Текстове або бінарне прев'ю
    const textContainer = document.getElementById('decrypt-text-container');
    const hexContainer = document.getElementById('decrypt-hex-container');

    if (data.is_text) {
        textContainer.style.display = 'block';
        hexContainer.style.display = 'none';
        document.getElementById('decrypt-text-preview').textContent = data.text_preview;
    } else {
        textContainer.style.display = 'none';
        hexContainer.style.display = 'block';
        document.getElementById('decrypt-hex-full').textContent = data.decrypted_hex.substring(0, 500) + (data.decrypted_hex.length > 500 ? '...' : '');
    }

    document.getElementById('decrypt-size').textContent = formatBytes(data.decrypted_size);
    document.getElementById('decrypt-time').textContent = data.execution_time_ms.toFixed(2) + ' мс';

    // Завантаження
    const downloadBtn = document.getElementById('btn-download-decrypted');
    downloadBtn.onclick = () => {
        if (data.is_text) {
            // Викликаємо функцію збереження для тексту
            saveFileWithDialog(data.decrypted_text_full, data.filename + '.txt', 'text');
        } else {
            // Викликаємо функцію збереження для бінарних даних (hex)
            saveFileWithDialog(data.decrypted_hex, data.filename, 'hex');
        }
    };
}


// ==================== Допоміжні функції ====================

function setupDragAndDrop(zone, callback) {
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files[0]) callback(e.dataTransfer.files[0]);
    });
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function showNotification(msg, type) {
    const notif = document.getElementById('notification');
    const span = document.getElementById('notification-message');
    span.textContent = msg;
    notif.className = `notification ${type} show`;
    setTimeout(() => {
        notif.classList.remove('show');
    }, 3000);
}

function showLoader() {
    document.getElementById('loader').style.display = 'block';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

/**
 * Універсальна функція збереження файлу з діалогом "Зберегти як".
 * @param {string} data - Дані для збереження (HEX-рядок або текст).
 * @param {string} filename - Пропоноване ім'я файлу.
 * @param {string} type - Тип даних: 'hex' (для бінарних файлів) або 'text' (для текстових).
 */
async function saveFileWithDialog(data, filename, type) {
    let blob;

    if (type === 'hex') {
        // Конвертуємо HEX у байти
        const bytes = new Uint8Array(data.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
        blob = new Blob([bytes], { type: "application/octet-stream" });
    } else {
        // Текстові дані
        blob = new Blob([data], { type: "text/plain;charset=utf-8" });
    }

    try {
        // Перевірка підтримки File System Access API
        if ('showSaveFilePicker' in window) {
            const options = {
                suggestedName: filename,
                types: [{
                    description: type === 'hex' ? 'Binary File' : 'Text File',
                    accept: type === 'hex' ? {'application/octet-stream': ['.rc5', '.bin']} : {'text/plain': ['.txt']}
                }],
            };

            const handle = await window.showSaveFilePicker(options);
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            showNotification('Файл успішно збережено!', 'success');
        } else {
            // Fallback для браузерів без підтримки API (автоматичне завантаження)
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href); // Очистка пам'яті
        }
    } catch (err) {
        // Ігноруємо помилку, якщо користувач скасував діалог
        if (err.name !== 'AbortError') {
            console.error('Помилка збереження:', err);
            showNotification('Не вдалося зберегти файл', 'error');
        }
    }
}

// Старі функції downloadHexAsBinary та downloadTextFile більше не потрібні,
// оскільки їх логіку об'єднано в saveFileWithDialog