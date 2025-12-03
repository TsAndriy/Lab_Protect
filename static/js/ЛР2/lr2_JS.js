// ==================== Глобальні змінні ====================

let selectedFile = null;
let verifyFile = null;

// ==================== Ініціалізація ====================
// Tabs are automatically initialized by common-utils.js

document.addEventListener('DOMContentLoaded', function() {
    initializeTextHash();
    initializeFileHash();
    initializeVerifyFile();
    initializeCopyButtons();
});

// Видалена функція initializeTabs - tabs auto-initialize in common-utils.js

// ==================== Хешування тексту ====================

function initializeTextHash() {
    const inputText = document.getElementById('input-text');
    const textLength = document.getElementById('text-length');
    const btnHashText = document.getElementById('btn-hash-text');
    const btnClearText = document.getElementById('btn-clear-text');

    // Оновлення довжини тексту
    inputText.addEventListener('input', () => {
        textLength.textContent = inputText.value.length;
    });

    // Хешування тексту
    btnHashText.addEventListener('click', async () => {
        const text = inputText.value;

        try {
            showLoader();

            const response = await fetch('/lab2/hash-text/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();
            hideLoader();

            if (data.success) {
                displayTextResult(data);
                showNotification('Хеш успішно обчислено!', 'success');
            } else {
                showNotification(data.error || 'Помилка обчислення хешу', 'error');
            }
        } catch (error) {
            hideLoader();
            showNotification('Помилка з\'єднання з сервером', 'error');
            console.error('Error:', error);
        }
    });

    // Очищення
    btnClearText.addEventListener('click', () => {
        inputText.value = '';
        textLength.textContent = '0';
        document.getElementById('text-result').style.display = 'none';
    });
}

function displayTextResult(data) {
    document.getElementById('text-hash-value').textContent = data.hash;
    document.getElementById('text-result-length').textContent = `${data.text_length} символів`;
    document.getElementById('text-execution-time').textContent = `${data.execution_time_ms.toFixed(2)} мс`;
    document.getElementById('text-result').style.display = 'block';

    // Експорт
    document.getElementById('btn-export-text-hash').onclick = () => {
        exportHash(data.hash, 'text_hash');
    };
}

// ==================== Хешування файлу ====================

function initializeFileHash() {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('file-drop-zone');
    const fileInfo = document.getElementById('file-info');
    const btnHashFile = document.getElementById('btn-hash-file');
    // const btnRemoveFile = document.getElementById('btn-remove-file');

    // Обробка вибору файлу
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // Drag and Drop - використовуємо функцію з common-utils.js
    setupDragAndDrop(dropZone, handleFileSelect);

    // Видалення файлу
    // btnRemoveFile.addEventListener('click', (e) => {
    //     e.stopPropagation();
    //     clearFileSelection();
    // });

    // Хешування файлу
    btnHashFile.addEventListener('click', async () => {
        if (!selectedFile) return;

        try {
            showLoader();

            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await fetch('/lab2/hash-file/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            hideLoader();

            if (data.success) {
                displayFileResult(data);
                showNotification('Хеш файлу успішно обчислено!', 'success');
            } else {
                showNotification(data.error || 'Помилка обчислення хешу', 'error');
            }
        } catch (error) {
            hideLoader();
            showNotification('Помилка з\'єднання з сервером', 'error');
            console.error('Error:', error);
        }
    });

    function handleFileSelect(file) {
        selectedFile = file;
        document.querySelector('.file-upload-content').style.display = 'none';
        fileInfo.style.display = 'flex';
        document.getElementById('file-name').textContent = file.name;
        document.getElementById('file-size').textContent = formatBytes(file.size);
        btnHashFile.disabled = false;
        document.getElementById('file-result').style.display = 'none';
    }

    function clearFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        document.querySelector('.file-upload-content').style.display = 'block';
        fileInfo.style.display = 'none';
        btnHashFile.disabled = true;
        document.getElementById('file-result').style.display = 'none';
    }
}

function displayFileResult(data) {
    document.getElementById('file-hash-value').textContent = data.hash;
    document.getElementById('file-result-name').textContent = data.filename;
    document.getElementById('file-result-size').textContent = formatBytes(data.file_size);
    document.getElementById('file-execution-time').textContent = `${data.execution_time_ms.toFixed(2)} мс`;
    document.getElementById('file-result').style.display = 'block';

    // Експорт
    document.getElementById('btn-export-file-hash').onclick = () => {
        exportHash(data.hash, data.filename);
    };
}

// ==================== Перевірка цілісності ====================

function initializeVerifyFile() {
    const verifyFileInput = document.getElementById('verify-file-input');
    const verifyDropZone = document.getElementById('verify-drop-zone');
    const verifyFileInfo = document.getElementById('verify-file-info');
    const expectedHash = document.getElementById('expected-hash');
    const hashLength = document.getElementById('hash-length');
    const btnVerifyFile = document.getElementById('btn-verify-file');
    // const btnRemoveVerifyFile = document.getElementById('btn-remove-verify-file');

    // Оновлення довжини хешу
    expectedHash.addEventListener('input', () => {
        const value = expectedHash.value.toUpperCase();
        expectedHash.value = value;
        hashLength.textContent = value.length;
        updateVerifyButton();
    });

    // Обробка вибору файлу
    verifyFileInput.addEventListener('change', (e) => {
        handleVerifyFileSelect(e.target.files[0]);
    });

    // Drag and Drop
    // Drag and Drop - використовуємо функцію з common-utils.js
    setupDragAndDrop(verifyDropZone, handleVerifyFileSelect);

    // Видалення файлу
    // btnRemoveVerifyFile.addEventListener('click', (e) => {
    //     e.stopPropagation();
    //     clearVerifyFileSelection();
    // });

    // Перевірка
    btnVerifyFile.addEventListener('click', async () => {
        if (!verifyFile || !expectedHash.value) return;

        try {
            showLoader();

            const formData = new FormData();
            formData.append('file', verifyFile);
            formData.append('expected_hash', expectedHash.value);

            const response = await fetch('/lab2/verify-file/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            hideLoader();

            if (data.success) {
                displayVerifyResult(data);
                showNotification(
                    data.match ? 'Файл не змінювався!' : 'Файл було змінено!',
                    data.match ? 'success' : 'error'
                );
            } else {
                showNotification(data.error || 'Помилка перевірки', 'error');
            }
        } catch (error) {
            hideLoader();
            showNotification('Помилка з\'єднання з сервером', 'error');
            console.error('Error:', error);
        }
    });

    function handleVerifyFileSelect(file) {
        verifyFile = file;
        document.querySelector('#verify-drop-zone .file-upload-content').style.display = 'none';
        verifyFileInfo.style.display = 'flex';
        document.getElementById('verify-file-name').textContent = file.name;
        document.getElementById('verify-file-size').textContent = formatFileSize(file.size);
        updateVerifyButton();
        document.getElementById('verify-result').style.display = 'none';
    }

    function clearVerifyFileSelection() {
        verifyFile = null;
        verifyFileInput.value = '';
        document.querySelector('#verify-drop-zone .file-upload-content').style.display = 'block';
        verifyFileInfo.style.display = 'none';
        updateVerifyButton();
        document.getElementById('verify-result').style.display = 'none';
    }

    function updateVerifyButton() {
        btnVerifyFile.disabled = !(verifyFile && expectedHash.value.length === 32);
    }
}

function displayVerifyResult(data) {
    const verificationStatus = document.getElementById('verification-status');
    const statusIcon = document.getElementById('status-icon');
    const statusMessage = document.getElementById('status-message');

    // Встановлюємо статус
    verificationStatus.className = 'verification-status ' + (data.match ? 'success' : 'error');
    statusMessage.textContent = data.message;

    // Відображаємо хеші
    document.getElementById('expected-hash-display').textContent = data.expected_hash;
    document.getElementById('actual-hash-display').textContent = data.actual_hash;

    // Інформація про файл
    document.getElementById('verify-result-name').textContent = data.filename;
    document.getElementById('verify-result-size').textContent = formatBytes(data.file_size);
    document.getElementById('verify-execution-time').textContent = `${data.execution_time_ms.toFixed(2)} мс`;

    document.getElementById('verify-result').style.display = 'block';
}

// ==================== Допоміжні функції ====================

function initializeCopyButtons() {
    document.querySelectorAll('.btn-copy').forEach(button => {
        button.addEventListener('click', async () => {
            const targetId = button.dataset.copy;
            // Використовуємо функцію copyText з common-utils.js
            copyText(targetId);
        });
    });
}

async function exportHash(hash, filename) {
    try {
        const response = await fetch('/lab2/export-hash/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                hash: hash,
                filename: filename
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            // Використовуємо функцію downloadBlob з common-utils.js
            downloadBlob(blob, `${filename}.md5.txt`);
            showNotification('Хеш успішно експортовано!', 'success');
        } else {
            showNotification('Помилка експорту', 'error');
        }
    } catch (error) {
        showNotification('Помилка з\'єднання з сервером', 'error');
        console.error('Error:', error);
    }
}

// Видалені дублюючі функції - використовуємо з common-utils.js:
// - formatBytes (було formatFileSize)
// - showLoader
// - hideLoader
// - showNotification
// - setupDragAndDrop (замість окремих обробників dragover, dragleave, drop)
// - copyText (в initializeCopyButtons)
// - downloadBlob (в exportHash)
}