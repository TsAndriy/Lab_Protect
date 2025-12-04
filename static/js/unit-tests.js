/**
 * Unit Tests Visualization JavaScript
 * Handles running and displaying unit test results
 */

// Global state for test results
let currentTestResults = null;
let currentFilter = 'all';

/**
 * Run unit tests for a specific lab
 * @param {number} labNumber - Lab number (1, 2, 3, or 4)
 */
async function runUnitTests(labNumber) {
    const container = document.getElementById('unit-tests-content');
    if (!container) return;
    
    // Show loading state
    container.innerHTML = `
        <div class="test-loading">
            <div class="spinner"></div>
            <p>Запуск тестів для ЛР${labNumber}...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/lab${labNumber}/run-tests/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentTestResults = data;
        displayTestResults(data);
        
    } catch (error) {
        console.error('Error running tests:', error);
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Помилка запуску тестів</h3>
                <p>${error.message}</p>
                <button class="btn" onclick="runUnitTests(${labNumber})">Спробувати знову</button>
            </div>
        `;
    }
}

/**
 * Display test results in the UI
 * @param {Object} data - Test results data
 */
function displayTestResults(data) {
    const container = document.getElementById('unit-tests-content');
    if (!container) return;
    
    const passRate = data.total_tests > 0 
        ? ((data.passed / data.total_tests) * 100).toFixed(1) 
        : 0;
    
    container.innerHTML = `
        <div class="unit-tests-container">
            <!-- Summary Statistics -->
            <div class="test-summary">
                <div class="test-stat-card total">
                    <div class="test-stat-label">Всього тестів</div>
                    <div class="test-stat-number">${data.total_tests}</div>
                </div>
                <div class="test-stat-card passed">
                    <div class="test-stat-label">Успішно</div>
                    <div class="test-stat-number">${data.passed}</div>
                </div>
                <div class="test-stat-card failed">
                    <div class="test-stat-label">Невдало</div>
                    <div class="test-stat-number">${data.failed}</div>
                </div>
                <div class="test-stat-card errors">
                    <div class="test-stat-label">Помилки</div>
                    <div class="test-stat-number">${data.errors}</div>
                </div>
            </div>
            
            <!-- Progress Bar -->
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${passRate}%"></div>
            </div>
            <p style="text-align: center; margin-top: 10px; color: #6b7280;">
                Успішність: ${passRate}%
            </p>
            
            <!-- Test Results List -->
            <div class="test-results-list">
                <div class="test-results-header">
                    <h3>Результати тестів</h3>
                    <div class="test-filter">
                        <button class="filter-btn ${currentFilter === 'all' ? 'active' : ''}" 
                                onclick="filterTests('all')">
                            Всі (${data.total_tests})
                        </button>
                        <button class="filter-btn ${currentFilter === 'passed' ? 'active' : ''}" 
                                onclick="filterTests('passed')">
                            ✓ Успішні (${data.passed})
                        </button>
                        <button class="filter-btn ${currentFilter === 'failed' ? 'active' : ''}" 
                                onclick="filterTests('failed')">
                            ✗ Невдалі (${data.failed + data.errors})
                        </button>
                    </div>
                </div>
                
                <div id="test-items-container">
                    ${renderTestItems(data.tests, currentFilter)}
                </div>
            </div>
            
            <!-- Raw Output (Collapsible) -->
            ${data.output ? `
                <div class="test-output">
                    <div class="test-output-header">
                        <h4>Детальний вивід тестів</h4>
                        <button class="toggle-output-btn" onclick="toggleOutput()">
                            Показати/Сховати
                        </button>
                    </div>
                    <div id="test-output-content" style="display: none;">
                        ${escapeHtml(data.output)}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Render test items based on filter
 * @param {Array} tests - Array of test objects
 * @param {string} filter - Filter type ('all', 'passed', 'failed')
 * @returns {string} HTML string
 */
function renderTestItems(tests, filter) {
    if (!tests || tests.length === 0) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <p>Результати тестів недоступні</p>
            </div>
        `;
    }
    
    const filteredTests = tests.filter(test => {
        if (filter === 'all') return true;
        if (filter === 'passed') return test.status === 'passed';
        if (filter === 'failed') return test.status === 'failed' || test.status === 'error';
        return true;
    });
    
    if (filteredTests.length === 0) {
        return `
            <div class="empty-state">
                <p>Немає тестів для відображення</p>
            </div>
        `;
    }
    
    return filteredTests.map(test => `
        <div class="test-item ${test.status}">
            <div class="test-item-header">
                <div class="test-name">${escapeHtml(test.name)}</div>
                <span class="test-status ${test.status}">
                    ${test.status === 'passed' ? '✓ Passed' : 
                      test.status === 'failed' ? '✗ Failed' : '⚠ Error'}
                </span>
            </div>
            ${test.message ? `
                <div class="test-message">${escapeHtml(test.message)}</div>
            ` : ''}
        </div>
    `).join('');
}

/**
 * Filter tests by status
 * @param {string} filter - Filter type
 */
function filterTests(filter) {
    currentFilter = filter;
    if (currentTestResults) {
        displayTestResults(currentTestResults);
    }
}

/**
 * Toggle test output visibility
 */
function toggleOutput() {
    const output = document.getElementById('test-output-content');
    if (output) {
        output.style.display = output.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Initialize unit tests tab
 */
function initializeUnitTestsTab(labNumber) {
    const container = document.getElementById('unit-tests-content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="unit-tests-container">
            <div class="empty-state">
                <div class="empty-state-icon">🧪</div>
                <h3>Unit Тести для ЛР${labNumber}</h3>
                <p>Натисніть кнопку нижче, щоб запустити автоматичні тести</p>
                <div class="test-controls">
                    <button class="btn btn-primary" onclick="runUnitTests(${labNumber})">
                        ▶ Запустити тести
                    </button>
                </div>
            </div>
        </div>
    `;
}
