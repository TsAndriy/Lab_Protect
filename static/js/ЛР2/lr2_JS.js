// ==================== Lab 2: MD5 Hashing ====================
// Uses common utilities from common.js

let selectedFile = null;
let verifyFile = null;

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeTextHash();
    initializeFileHash();
    initializeVerifyFile();
});

// ==================== Text Hashing ====================
function initializeTextHash() {
    const inputText = document.getElementById('input-text');
    const textLength = document.getElementById('text-length');
    const btnHashText = document.getElementById('btn-hash-text');
    const btnClearText = document.getElementById('btn-clear-text');

    inputText.addEventListener('input', () => {
        textLength.textContent = inputText.value.length;
    });

    btnHashText.addEventListener('click', async () => {
        const text = inputText.value;

        try {
            const data = await fetchJSON('/lab2/hash-text/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            if (data.success) {
                displayTextResult(data);
                showNotification('Хеш успішно обчислено!', 'success');
            } else {
                showNotification(data.error || 'Помилка обчислення хешу', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

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

    document.getElementById('btn-export-text-hash').onclick = () => {
        exportHash(data.hash, 'text_hash');
    };
}

// ==================== File Hashing ====================
function initializeFileHash() {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('file-drop-zone');
    const fileInfo = document.getElementById('file-info');
    const btnHashFile = document.getElementById('btn-hash-file');

    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    setupDragAndDrop(dropZone, handleFileSelect);

    btnHashFile.addEventListener('click', async () => {
        if (!selectedFile) return;

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            showLoader();
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
        document.getElementById('file-size').textContent = formatFileSize(file.size);
        btnHashFile.disabled = false;
        document.getElementById('file-result').style.display = 'none';
    }
}

function displayFileResult(data) {
    document.getElementById('file-hash-value').textContent = data.hash;
    document.getElementById('file-result-name').textContent = data.filename;
    document.getElementById('file-result-size').textContent = formatFileSize(data.file_size);
    document.getElementById('file-execution-time').textContent = `${data.execution_time_ms.toFixed(2)} мс`;
    document.getElementById('file-result').style.display = 'block';

    document.getElementById('btn-export-file-hash').onclick = () => {
        exportHash(data.hash, data.filename);
    };
}

// ==================== File Verification ====================
function initializeVerifyFile() {
    const verifyFileInput = document.getElementById('verify-file-input');
    const verifyDropZone = document.getElementById('verify-drop-zone');
    const verifyFileInfo = document.getElementById('verify-file-info');
    const expectedHash = document.getElementById('expected-hash');
    const hashLength = document.getElementById('hash-length');
    const btnVerifyFile = document.getElementById('btn-verify-file');

    expectedHash.addEventListener('input', () => {
        const value = expectedHash.value.toUpperCase();
        expectedHash.value = value;
        hashLength.textContent = value.length;
        updateVerifyButton();
    });

    verifyFileInput.addEventListener('change', (e) => {
        handleVerifyFileSelect(e.target.files[0]);
    });

    setupDragAndDrop(verifyDropZone, handleVerifyFileSelect);

    btnVerifyFile.addEventListener('click', async () => {
        if (!verifyFile || !expectedHash.value) return;

        try {
            const formData = new FormData();
            formData.append('file', verifyFile);
            formData.append('expected_hash', expectedHash.value);

            showLoader();
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

    function updateVerifyButton() {
        btnVerifyFile.disabled = !(verifyFile && expectedHash.value.length === 32);
    }
}

function displayVerifyResult(data) {
    const verificationStatus = document.getElementById('verification-status');
    const statusMessage = document.getElementById('status-message');

    verificationStatus.className = 'verification-status ' + (data.match ? 'success' : 'error');
    statusMessage.textContent = data.message;

    document.getElementById('expected-hash-display').textContent = data.expected_hash;
    document.getElementById('actual-hash-display').textContent = data.actual_hash;
    document.getElementById('verify-result-name').textContent = data.filename;
    document.getElementById('verify-result-size').textContent = formatFileSize(data.file_size);
    document.getElementById('verify-execution-time').textContent = `${data.execution_time_ms.toFixed(2)} мс`;

    document.getElementById('verify-result').style.display = 'block';
}

// ==================== Export Hash ====================
async function exportHash(hash, filename) {
    try {
        const response = await fetch('/lab2/export-hash/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hash: hash, filename: filename })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.md5.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Хеш успішно експортовано!', 'success');
        } else {
            showNotification('Помилка експорту', 'error');
        }
    } catch (error) {
        showNotification('Помилка з\'єднання з сервером', 'error');
        console.error('Error:', error);
    }
}
