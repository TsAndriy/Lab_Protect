// Глобальні змінні для пагінації
let generatedSequence = [];
let currentPage = 1;
const itemsPerPage = 5000;

// Функція для відображення поточної сторінки послідовності
function renderSequencePage() {
    const seqDiv = document.getElementById('gen-sequence');
    const paginationControls = document.getElementById('pagination-controls');
    const sequenceInfo = document.getElementById('sequence-info');

    if (generatedSequence.length === 0) {
        seqDiv.innerHTML = '';
        paginationControls.innerHTML = '';
        sequenceInfo.innerHTML = '';
        return;
    }

    const totalPages = Math.ceil(generatedSequence.length / itemsPerPage);
    if (currentPage < 1) currentPage = 1;
    if (currentPage > totalPages) currentPage = totalPages;

    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = generatedSequence.slice(start, end);

    seqDiv.innerHTML = pageItems.join(', ');

    const endItem = Math.min(end, generatedSequence.length);
    sequenceInfo.innerHTML = `(Показано ${start + 1} - ${endItem} з ${generatedSequence.length})`;

    let paginationHTML = '';
    if (totalPages > 1) {
        paginationHTML += `<button class="btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(1)">« Перша</button>`;
        paginationHTML += `<button class="btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">‹ Попередня</button>`;
        paginationHTML += `<span style="padding: 0 10px;">Сторінка ${currentPage} з ${totalPages}</span>`;
        paginationHTML += `<button class="btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Наступна ›</button>`;
        paginationHTML += `<button class="btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${totalPages})">Остання »</button>`;
    }
    paginationControls.innerHTML = paginationHTML;
}

function goToPage(page) {
    currentPage = page;
    renderSequencePage();
    document.getElementById('gen-sequence').scrollTop = 0;
}

// Функція перемикання вкладок (використовує спрощену логіку)
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Оновлена функція генерації чисел
async function generateNumbers() {
    const data = {
        m: parseInt(document.getElementById('gen-m').value),
        a: parseInt(document.getElementById('gen-a').value),
        c: parseInt(document.getElementById('gen-c').value),
        x0: parseInt(document.getElementById('gen-x0').value),
        count: parseInt(document.getElementById('gen-count').value)
    };

    const seqDiv = document.getElementById('gen-sequence');
    document.getElementById('gen-results').style.display = 'block';
    seqDiv.innerHTML = 'Генерація та завантаження...';
    document.getElementById('pagination-controls').innerHTML = '';
    document.getElementById('sequence-info').innerHTML = '';

    try {
        const result = await fetchJSON('/lab1/generate/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (result.success) {
            const stats = result.statistics;
            document.getElementById('gen-stats').innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Кількість</div>
                    <div class="stat-value">${stats.count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Середнє</div>
                    <div class="stat-value">${stats.mean.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Унікальних</div>
                    <div class="stat-value">${stats.unique_values}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Мін / Макс</div>
                    <div class="stat-value">${stats.min} / ${stats.max}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Час генерації (мс) (не враховує рендеринг значень)</div>
                    <div class="stat-value">${result.generation_time_ms.toFixed(2)}</div>
                </div>
            `;

            generatedSequence = result.sequence;
            currentPage = 1;
            renderSequencePage();
        } else {
            seqDiv.innerHTML = '';
            alert('Помилка: ' + result.error);
        }
    } catch (error) {
        seqDiv.innerHTML = '';
        alert('Помилка запиту: ' + error);
    }
}

// Функція тестування періоду
async function testPeriod() {
    const data = {
        m: parseInt(document.getElementById('gen-m').value),
        a: parseInt(document.getElementById('gen-a').value),
        c: parseInt(document.getElementById('gen-c').value),
        x0: parseInt(document.getElementById('gen-x0').value),
        max_iterations: 100000
    };

    try {
        const result = await fetchJSON('/lab1/period/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (result.success) {
            document.getElementById('period-results').style.display = 'block';

            let badgeClass = 'badge-success';
            if (result.quality === 'Добре') badgeClass = 'badge-pending';
            if (result.quality === 'Погано') badgeClass = 'badge-danger';

            document.getElementById('period-stats').innerHTML = `
                <table>
                    <tr>
                        <th>Параметр</th>
                        <th>Значення</th>
                    </tr>
                    <tr>
                        <td>Знайдений період</td>
                        <td><strong>${result.period}</strong></td>
                    </tr>
                    <tr>
                        <td>Максимально можливий період</td>
                        <td>${result.max_possible_period}</td>
                    </tr>
                    <tr>
                        <td>Відсоток від максимуму</td>
                        <td>${result.percentage.toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td>Оцінка якості</td>
                        <td><span class="badge ${badgeClass}">${result.quality}</span></td>
                    </tr>
                    <tr>
                        <td>Час виконання (мс)</td>
                        <td><strong>${result.execution_time_ms.toFixed(2)}</strong></td>
                    </tr>
                </table>
            `;
        } else {
            alert('Помилка: ' + result.error);
        }
    } catch (error) {
        alert('Помилка запиту: ' + error);
    }
}

// Функція тесту Чезаро
async function testCesaro() {
    const data = {
        m: parseInt(document.getElementById('gen-m').value),
        a: parseInt(document.getElementById('gen-a').value),
        c: parseInt(document.getElementById('gen-c').value),
        x0: parseInt(document.getElementById('gen-x0').value),
        num_pairs: parseInt(document.getElementById('cesaro-pairs').value)
    };

    try {
        const result = await fetchJSON('/lab1/cesaro/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (result.success) {
            document.getElementById('cesaro-results').style.display = 'block';

            const ourError = result.our_generator.error_percentage;
            const sysError = result.system_generator.error_percentage;

            document.getElementById('cesaro-stats').innerHTML = `
                <div class="grid">
                    <div class="card">
                        <h4>Генератор Лемера</h4>
                        <table>
                            <tr>
                                <td>Оцінка Чезера:</td>
                                <td><strong>${result.our_generator.pi_estimate.toFixed(6)}</strong></td>
                            </tr>
                            <tr>
                                <td>Похибка (Pi - Оцінка):</td>
                                <td>${result.our_generator.error.toFixed(6)}</td>
                            </tr>
                            <tr>
                                <td>Похибка % (Відносно Pi):</td>
                                <td>${ourError.toFixed(3)}%</td>
                            </tr>
                        </table>
                    </div>
                    <div class="card">
                        <h4>Системний генератор</h4>
                        <table>
                            <tr>
                                <td>Оцінка Чезера:</td>
                                <td><strong>${result.system_generator.pi_estimate.toFixed(6)}</strong></td>
                            </tr>
                            <tr>
                                <td>Похибка (Pi - Оцінка):</td>
                                <td>${result.system_generator.error.toFixed(6)}</td>
                            </tr>
                            <tr>
                                <td>Похибка % (Відносно Pi):</td>
                                <td>${sysError.toFixed(3)}%</td>
                            </tr>
                        </table>
                    </div>
                </div>
                <div class="alert alert-info" style="margin-top: 20px;">
                    <strong>Pi:</strong> ${result.actual_pi}
                    <br>
                    <strong>Кількість пар:</strong> ${result.num_pairs}
                    <br>
                    <strong>Час виконання:</strong> ${result.execution_time_ms.toFixed(2)} мс
                </div>
            `;
        } else {
            alert('Помилка: ' + result.error);
        }
    } catch (error) {
        alert('Помилка запиту: ' + error);
    }
}

// Функція тестування випадковості
async function testRandomness() {
    const data = {
        m: parseInt(document.getElementById('gen-m').value),
        a: parseInt(document.getElementById('gen-a').value),
        c: parseInt(document.getElementById('gen-c').value),
        x0: parseInt(document.getElementById('gen-x0').value),
        count: parseInt(document.getElementById('random-count').value)
    };

    try {
        const result = await fetchJSON('/lab1/randomness/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (result.success) {
            document.getElementById('random-results').style.display = 'block';

            const freq = result.tests.frequency;
            const runs = result.tests.runs;

            let html = '<div class="grid">';

            if (!freq.error) {
                html += `
                    <div class="card">
                        <h4>Частотний тест</h4>
                        <table>
                            <tr>
                                <td>Одиниці:</td>
                                <td>${freq.ones_count} (${(freq.ones_ratio * 100).toFixed(2)}%)</td>
                            </tr>
                            <tr>
                                <td>Нулі:</td>
                                <td>${freq.zeros_count} (${(freq.zeros_ratio * 100).toFixed(2)}%)</td>
                            </tr>
                            <tr>
                                <td>Ідеальне співвідношення:</td>
                                <td>${freq.chi_square.toFixed(4)}</td>
                            </tr>
                            <tr>
                                <td>Результат:</td>
                                <td>
                                    <span class="badge ${freq.is_random ? 'badge-success' : 'badge-danger'}">
                                        ${freq.is_random ? 'Пройдено' : 'Не пройдено'}
                                    </span>
                                </td>
                            </tr>
                        </table>
                    </div>
                `;
            }

            if (!runs.error) {
                html += `
                    <div class="card">
                        <h4>Тест послідовностей</h4>
                        <table>
                            <tr>
                                <td>Кількість послідовностей:</td>
                                <td>${runs.runs}</td>
                            </tr>
                            <tr>
                                <td>Очікувана кількість:</td>
                                <td>${runs.expected_runs.toFixed(2)}</td>
                            </tr>
                            <tr>
                                <td>Різниця:</td>
                                <td>${runs.z_statistic.toFixed(4)}</td>
                            </tr>
                            <tr>
                                <td>Результат:</td>
                                <td>
                                    <span class="badge ${runs.is_random ? 'badge-success' : 'badge-danger'}">
                                        ${runs.is_random ? 'Пройдено' : 'Не пройдено'}
                                    </span>
                                </td>
                            </tr>
                        </table>
                    </div>
                `;
            }

            html += '</div>';
            html += `<div class="alert alert-info" style="margin-top: 20px;">
                        <strong>Час виконання:</strong> ${result.execution_time_ms.toFixed(2)} мс
                     </div>`;

            document.getElementById('random-stats').innerHTML = html;
        } else {
            alert('Помилка: ' + result.error);
        }
    } catch (error) {
        alert('Помилка запиту: ' + error);
    }
}

// Функція експорту результатів
async function exportResults() {
    const data = {
        m: parseInt(document.getElementById('gen-m').value),
        a: parseInt(document.getElementById('gen-a').value),
        c: parseInt(document.getElementById('gen-c').value),
        x0: parseInt(document.getElementById('gen-x0').value),
        count: parseInt(document.getElementById('gen-count').value)
    };

    try {
        if ('showSaveFilePicker' in window) {
            const options = {
                suggestedName: 'lr1_lin.txt',
                types: [
                    {
                        description: 'Text file',
                        accept: { 'text/plain': ['.txt'] },
                    },
                ],
            };
            const handle = await window.showSaveFilePicker(options);

            const response = await fetch('/lab1/export/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorResult = await response.json();
                throw new Error(errorResult.error || 'Не вдалося отримати дані з сервера');
            }

            const fileContent = await response.text();

            const writable = await handle.createWritable();
            await writable.write(fileContent);
            await writable.close();
            alert('Файл успішно збережено!');
        }
    } catch (error) {
        if (error.name !== 'AbortError') {
            alert('Помилка експорту: ' + error.message);
        }
    }
}

