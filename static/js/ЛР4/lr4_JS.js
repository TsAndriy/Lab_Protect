// ==================== Lab 4: RSA Encryption ====================
// Uses common utilities from common.js

let encryptedBlobUrl = null;
let decryptedBlobUrl = null;

document.addEventListener('DOMContentLoaded', () => {
    setupFileUploads();
});

// ==================== Tab and Input Management ====================
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    const btns = document.querySelectorAll('.tab-btn');
    if(tabId === 'keys-tab') btns[0].classList.add('active');
    if(tabId === 'encrypt-tab') btns[1].classList.add('active');
    if(tabId === 'decrypt-tab') btns[2].classList.add('active');
}

function toggleKeyInput(mode, type) {
    const textContainer = document.getElementById(`${mode}-key-text-container`);
    const fileContainer = document.getElementById(`${mode}-key-file-container`);

    if (type === 'text') {
        textContainer.style.display = 'block';
        fileContainer.style.display = 'none';
    } else {
        textContainer.style.display = 'none';
        fileContainer.style.display = 'block';
    }
}

function setupFileUploads() {
    const encInput = document.getElementById('encrypt-file');
    encInput.addEventListener('change', (e) => {
        if(e.target.files[0]) {
            document.getElementById('encrypt-filename').textContent = e.target.files[0].name;
            document.getElementById('encrypt-text').disabled = true;
            document.getElementById('encrypt-text').placeholder = "Вибрано файл. Очистіть вибір файлу, щоб вводити текст.";
        }
    });

    const decInput = document.getElementById('decrypt-file');
    decInput.addEventListener('change', (e) => {
        if(e.target.files[0]) {
            document.getElementById('decrypt-filename').textContent = e.target.files[0].name;
            document.getElementById('decrypt-hex').disabled = true;
            document.getElementById('decrypt-hex').placeholder = "Вибрано файл. Очистіть вибір файлу, щоб вводити HEX.";
        }
    });
}

// ==================== Key Generation ====================
async function generateKeys() {
    const keySize = document.getElementById('key-size').value;
    const password = document.getElementById('key-password').value;

    showLoader();
    try {
        const data = await fetchJSON('/lab4/generate-keys/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                key_size: keySize,
                password: password
            })
        });

        if(data.success) {
            document.getElementById('private-key-display').value = data.private_key;
            document.getElementById('public-key-display').value = data.public_key;
            document.getElementById('keys-result').style.display = 'block';
        } else {
            alert('Помилка: ' + data.error);
        }
    } catch (e) {
        alert('Помилка з\'єднання: ' + e);
    }
}

// ==================== Encryption ====================
async function encryptData() {
    const fileInput = document.getElementById('encrypt-file');
    const textInput = document.getElementById('encrypt-text');
    const keySource = document.querySelector('input[name="enc-key-source"]:checked').value;
    const keyTextInput = document.getElementById('encrypt-pub-key');
    const keyFileInput = document.getElementById('encrypt-pub-key-file');

    const formData = new FormData();

    if (fileInput.files[0]) {
        formData.append('file', fileInput.files[0]);
    } else if (textInput.value) {
        formData.append('text', textInput.value);
    } else {
        alert('Виберіть файл або введіть текст!');
        return;
    }

    if (keySource === 'text') {
        if (!keyTextInput.value.trim()) { alert('Введіть публічний ключ!'); return; }
        formData.append('public_key_text', keyTextInput.value);
    } else {
        if (!keyFileInput.files[0]) { alert('Виберіть файл ключа!'); return; }
        formData.append('public_key_file', keyFileInput.files[0]);
    }

    showLoader();
    try {
        const response = await fetch('/lab4/encrypt/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        hideLoader();

        if (result.success) {
            document.getElementById('encrypt-result').style.display = 'block';
            document.getElementById('enc-orig-size').textContent = formatBytes(result.original_size);
            document.getElementById('enc-res-size').textContent = formatBytes(result.encrypted_size);
            document.getElementById('enc-time').textContent = result.execution_time_ms.toFixed(2) + ' ms';
            document.getElementById('enc-hex-preview').textContent = result.encrypted_hex.substring(0, 100) + '...';

            const byteCharacters = atob(hexToBase64(result.encrypted_hex));
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], {type: "application/octet-stream"});

            if (encryptedBlobUrl) window.URL.revokeObjectURL(encryptedBlobUrl);
            encryptedBlobUrl = window.URL.createObjectURL(blob);

            const dlBtn = document.getElementById('btn-download-enc');
            dlBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = encryptedBlobUrl;
                a.download = result.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };
        } else {
            alert('Error: ' + result.error);
        }
    } catch (e) {
        hideLoader();
        alert('Error: ' + e);
    }
}

// ==================== Decryption ====================
async function decryptData() {
    const fileInput = document.getElementById('decrypt-file');
    const hexInput = document.getElementById('decrypt-hex');
    const passwordInput = document.getElementById('decrypt-key-pass');
    const keySource = document.querySelector('input[name="dec-key-source"]:checked').value;
    const keyTextInput = document.getElementById('decrypt-priv-key');
    const keyFileInput = document.getElementById('decrypt-priv-key-file');

    const formData = new FormData();

    if (fileInput.files[0]) {
        formData.append('file', fileInput.files[0]);
    } else if (hexInput.value) {
        formData.append('encrypted_hex', hexInput.value);
    } else {
        alert('Виберіть файл або вставте HEX!');
        return;
    }

    if (keySource === 'text') {
        if (!keyTextInput.value.trim()) { alert('Введіть приватний ключ!'); return; }
        formData.append('private_key_text', keyTextInput.value);
    } else {
        if (!keyFileInput.files[0]) { alert('Виберіть файл ключа!'); return; }
        formData.append('private_key_file', keyFileInput.files[0]);
    }

    if (passwordInput.value) {
        formData.append('password', passwordInput.value);
    }

    showLoader();
    try {
        const response = await fetch('/lab4/decrypt/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        hideLoader();

        if (result.success) {
            document.getElementById('decrypt-result').style.display = 'block';
            document.getElementById('dec-res-size').textContent = formatBytes(result.decrypted_size);
            document.getElementById('dec-time').textContent = result.execution_time_ms.toFixed(2) + ' ms';
            document.getElementById('dec-type').textContent = result.is_text ? 'Текст (UTF-8)' : 'Бінарні дані';

            const previewArea = document.getElementById('dec-text-preview');
            if (result.is_text) {
                previewArea.value = result.text_preview;
            } else {
                previewArea.value = "Увага: Дані бінарні. Показано HEX:\n" + result.decrypted_hex;
            }

            let blob;
            if (result.is_text) {
                blob = new Blob([result.text_preview], {type: "text/plain"});
            } else {
                const byteCharacters = atob(hexToBase64(result.decrypted_hex));
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                blob = new Blob([byteArray], {type: "application/octet-stream"});
            }

            if (decryptedBlobUrl) window.URL.revokeObjectURL(decryptedBlobUrl);
            decryptedBlobUrl = window.URL.createObjectURL(blob);

            const dlBtn = document.getElementById('btn-download-dec');
            dlBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = decryptedBlobUrl;
                a.download = result.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };

        } else {
            alert('Error: ' + result.error);
        }
    } catch (e) {
        alert('Error: ' + e);
    }
}

// ==================== Helper Functions ====================
function copyText(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999);
    copyToClipboard(element.value, "Скопійовано!");
}

function downloadKey(type) {
    const text = document.getElementById(`${type}-key-display`).value;
    if(!text) return;
    downloadFile(text, `${type}_key.pem`, 'text/plain');
}
