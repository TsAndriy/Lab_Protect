// ==================== Lab 3: RC5 Encryption ====================
// Uses common utilities from common.js

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeEncryption();
    initializeDecryption();
});

// ==================== Encryption ====================
function initializeEncryption() {
    const fileInput = document.getElementById('encrypt-file-input');
    const dropZone = document.getElementById('encrypt-drop-zone');
    const textInput = document.getElementById('encrypt-text-input');
    const passwordInput = document.getElementById('encrypt-password');
    const encryptBtn = document.getElementById('btn-encrypt');
    let selectedFile = null;

    const handleFile = (file) => {
        selectedFile = file;
        document.getElementById('encrypt-file-name').textContent = file.name;
        document.getElementById('encrypt-file-size').textContent = formatBytes(file.size);
        document.getElementById('encrypt-file-info').style.display = 'flex';
        document.querySelector('#encrypt-drop-zone .file-upload-content').style.display = 'none';
        textInput.disabled = true;
    };

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) handleFile(e.target.files[0]);
    });

    setupDragAndDrop(dropZone, handleFile);

    textInput.addEventListener('input', () => {
        if (textInput.value.length > 0 && selectedFile) {
            selectedFile = null;
            fileInput.value = '';
            document.getElementById('encrypt-file-info').style.display = 'none';
            document.querySelector('#encrypt-drop-zone .file-upload-content').style.display = 'block';
            textInput.disabled = false;
        }
    });

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

    const downloadBtn = document.getElementById('btn-download-encrypted');
    downloadBtn.onclick = () => {
        saveFileWithDialog(data.encrypted_data_full_hex, data.filename, 'hex');
    };
}

// ==================== Decryption ====================
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
            formData.append('encrypted_hex', hexInput.value.replace(/\s+/g, ''));
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

    const downloadBtn = document.getElementById('btn-download-decrypted');
    downloadBtn.onclick = () => {
        if (data.is_text) {
            saveFileWithDialog(data.decrypted_text_full, data.filename + '.txt', 'text');
        } else {
            saveFileWithDialog(data.decrypted_hex, data.filename, 'hex');
        }
    };
}

// ==================== File Save with Dialog ====================
async function saveFileWithDialog(data, filename, type) {
    let blob;

    if (type === 'hex') {
        const bytes = new Uint8Array(data.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
        blob = new Blob([bytes], { type: "application/octet-stream" });
    } else {
        blob = new Blob([data], { type: "text/plain;charset=utf-8" });
    }

    try {
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
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);
        }
    } catch (err) {
        if (err.name !== 'AbortError') {
            console.error('Помилка збереження:', err);
            showNotification('Не вдалося зберегти файл', 'error');
        }
    }
}
