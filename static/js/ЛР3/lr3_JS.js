// Tabs are automatically initialized by common-utils.js

document.addEventListener('DOMContentLoaded', () => {
    initializeEncryption();
    initializeDecryption();
});

// Видалена функція initializeTabs - tabs auto-initialize in common-utils.js

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
        document.getElementById('decrypt-hex-full').textContent = data.decrypted_hex;
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

// Видалені дублюючі функції - використовуємо з common-utils.js:
// - formatBytes
// - showNotification
// - showLoader
// - hideLoader
// - setupDragAndDrop
// - saveFileWithDialog (тепер в common-utils.js)