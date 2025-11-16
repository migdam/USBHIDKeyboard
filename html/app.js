// Pico Multi-Input Agent - Web UI JavaScript

const API_BASE = '';
let apiKey = localStorage.getItem('apiKey') || '';

// Theme Management
const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

if (currentTheme === 'dark') {
    document.body.classList.add('dark-mode');
    themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
});

// Tab Navigation
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const panelId = tab.dataset.panel + '-panel';

        tabs.forEach(t => t.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));

        tab.classList.add('active');
        document.getElementById(panelId).classList.add('active');
    });
});

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// API Helper
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (apiKey && options.method === 'POST') {
        headers['X-API-Key'] = apiKey;
    }

    try {
        const response = await fetch(API_BASE + endpoint, {
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        showToast(`API Error: ${error.message}`, 'error');
        throw error;
    }
}

// Keyboard Panel
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const sendTextBtn = document.getElementById('send-text');
const sendEnterBtn = document.getElementById('send-enter');
const sendTabBtn = document.getElementById('send-tab');
const keyBtns = document.querySelectorAll('.key-btn');

textInput.addEventListener('input', () => {
    charCount.textContent = textInput.value.length;
});

sendTextBtn.addEventListener('click', async () => {
    const text = textInput.value;
    if (!text) {
        showToast('Please enter some text', 'warning');
        return;
    }

    try {
        await apiCall('/api/type', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
        showToast(`Queued ${text.length} characters`, 'success');
        textInput.value = '';
        charCount.textContent = '0';
    } catch (error) {
        // Error already shown
    }
});

sendEnterBtn.addEventListener('click', async () => {
    await sendKey('ENTER');
});

sendTabBtn.addEventListener('click', async () => {
    await sendKey('TAB');
});

keyBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        await sendKey(btn.dataset.key);
    });
});

async function sendKey(key) {
    try {
        await apiCall('/api/key', {
            method: 'POST',
            body: JSON.stringify({ key })
        });
        showToast(`Sent ${key}`, 'success');
    } catch (error) {
        // Error already shown
    }
}

// Ctrl+Enter shortcut
textInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        sendTextBtn.click();
    }
});

// Mouse Panel
const dpadBtns = document.querySelectorAll('.dpad-btn');
const leftClickBtn = document.getElementById('left-click');
const middleClickBtn = document.getElementById('middle-click');
const rightClickBtn = document.getElementById('right-click');
const scrollUpBtn = document.getElementById('scroll-up');
const scrollDownBtn = document.getElementById('scroll-down');

dpadBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        if (btn.dataset.move) {
            const [dx, dy] = btn.dataset.move.split(',').map(Number);
            await moveMouse(dx, dy);
        } else if (btn.dataset.click) {
            await clickMouse(btn.dataset.click);
        }
    });
});

leftClickBtn.addEventListener('click', () => clickMouse('left'));
middleClickBtn.addEventListener('click', () => clickMouse('middle'));
rightClickBtn.addEventListener('click', () => clickMouse('right'));

scrollUpBtn.addEventListener('click', () => scrollMouse(5));
scrollDownBtn.addEventListener('click', () => scrollMouse(-5));

async function moveMouse(dx, dy) {
    try {
        await apiCall('/api/mouse/move', {
            method: 'POST',
            body: JSON.stringify({ dx, dy })
        });
    } catch (error) {
        // Error already shown
    }
}

async function clickMouse(button) {
    try {
        await apiCall('/api/mouse/click', {
            method: 'POST',
            body: JSON.stringify({ button })
        });
        showToast(`${button} click`, 'success');
    } catch (error) {
        // Error already shown
    }
}

async function scrollMouse(amount) {
    try {
        await apiCall('/api/mouse/scroll', {
            method: 'POST',
            body: JSON.stringify({ amount })
        });
    } catch (error) {
        // Error already shown
    }
}

// Jitter Panel
const jitterEnableBtn = document.getElementById('jitter-enable');
const jitterDisableBtn = document.getElementById('jitter-disable');
const jitterIntervalSlider = document.getElementById('jitter-interval-slider');
const jitterIntervalDisplay = document.getElementById('jitter-interval-display');

jitterEnableBtn.addEventListener('click', async () => {
    try {
        await apiCall('/api/jitter/on', { method: 'POST' });
        showToast('Jitter enabled', 'success');
        updateJitterStatus();
    } catch (error) {
        // Error already shown
    }
});

jitterDisableBtn.addEventListener('click', async () => {
    try {
        await apiCall('/api/jitter/off', { method: 'POST' });
        showToast('Jitter disabled', 'success');
        updateJitterStatus();
    } catch (error) {
        // Error already shown
    }
});

jitterIntervalSlider.addEventListener('input', () => {
    jitterIntervalDisplay.textContent = `${jitterIntervalSlider.value}s`;
});

async function updateJitterStatus() {
    try {
        const data = await apiCall('/api/jitter/status');
        document.getElementById('jitter-state').textContent = data.enabled ? 'Enabled' : 'Disabled';
        document.getElementById('jitter-state').classList.toggle('active', data.enabled);
        document.getElementById('jitter-interval').textContent = `${data.interval}s`;
        document.getElementById('jitter-count').textContent = data.jitter_count || 0;
    } catch (error) {
        // Error already shown
    }
}

// Macros Panel
const macroList = document.getElementById('macro-list');
const refreshMacrosBtn = document.getElementById('refresh-macros');

refreshMacrosBtn.addEventListener('click', loadMacros);

async function loadMacros() {
    try {
        const data = await apiCall('/api/scripts/list');
        const scripts = data.scripts || [];

        if (scripts.length === 0) {
            macroList.innerHTML = '<p>No macros found</p>';
            return;
        }

        macroList.innerHTML = '';
        scripts.forEach(script => {
            const item = document.createElement('div');
            item.className = 'macro-item';
            item.innerHTML = `
                <h3>${script}</h3>
                <div class="macro-actions">
                    <button class="btn preview-btn" data-script="${script}">Preview</button>
                    <button class="btn success run-btn" data-script="${script}">Run</button>
                </div>
            `;
            macroList.appendChild(item);
        });

        // Attach event listeners
        document.querySelectorAll('.preview-btn').forEach(btn => {
            btn.addEventListener('click', () => previewScript(btn.dataset.script));
        });

        document.querySelectorAll('.run-btn').forEach(btn => {
            btn.addEventListener('click', () => runScript(btn.dataset.script));
        });
    } catch (error) {
        macroList.innerHTML = '<p class="error">Failed to load macros</p>';
    }
}

async function previewScript(name) {
    try {
        const data = await apiCall(`/api/scripts/get?name=${encodeURIComponent(name)}`);
        showModal(name, data.content);
    } catch (error) {
        // Error already shown
    }
}

async function runScript(name) {
    try {
        await apiCall('/api/macro/run', {
            method: 'POST',
            body: JSON.stringify({ script: name })
        });
        showToast(`Running ${name}`, 'success');
    } catch (error) {
        // Error already shown
    }
}

// Modal
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modal-title');
const scriptContent = document.getElementById('script-content');
const modalRunBtn = document.getElementById('modal-run');
const modalCloseBtns = document.querySelectorAll('.modal-close');

let currentScript = '';

function showModal(title, content) {
    modalTitle.textContent = title;
    scriptContent.textContent = content;
    currentScript = title;
    modal.classList.add('active');
}

modalCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        modal.classList.remove('active');
    });
});

modalRunBtn.addEventListener('click', () => {
    runScript(currentScript);
    modal.classList.remove('active');
});

// Status Panel
const refreshStatusBtn = document.getElementById('refresh-status');

refreshStatusBtn.addEventListener('click', updateStatus);

async function updateStatus() {
    try {
        const data = await apiCall('/api/status');

        // WiFi
        const wifiStatus = data.wifi || {};
        document.getElementById('wifi-status').textContent =
            `${wifiStatus.state || 'unknown'} - ${wifiStatus.ip || 'N/A'}`;

        // USB
        const usbStatus = data.usb || {};
        document.getElementById('usb-mode').textContent = usbStatus.mode || 'unknown';

        // Memory
        const memory = data.memory || 0;
        document.getElementById('memory-status').textContent = `${(memory / 1024).toFixed(1)} KB`;

        // Uptime
        const uptime = data.uptime || 0;
        document.getElementById('uptime').textContent = formatUptime(uptime);

    } catch (error) {
        // Error already shown
    }
}

function formatUptime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h}h ${m}m ${s}s`;
}

// Logs Panel
const logsContainer = document.getElementById('logs-container');
const autoScrollCheck = document.getElementById('auto-scroll');
const logLevelFilter = document.getElementById('log-level-filter');
const clearLogsBtn = document.getElementById('clear-logs');

clearLogsBtn.addEventListener('click', () => {
    logsContainer.innerHTML = '<div class="log-line">Logs cleared</div>';
});

async function updateLogs() {
    try {
        const data = await apiCall('/api/logs/tail');
        const logs = data.logs || [];

        logsContainer.innerHTML = '';
        logs.forEach(log => {
            const line = document.createElement('div');
            line.className = `log-line ${log.level}`;
            line.textContent = `[${log.time.toFixed(3)}] [${log.level}] ${log.message}`;
            logsContainer.appendChild(line);
        });

        if (autoScrollCheck.checked) {
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }
    } catch (error) {
        // Silent fail for logs
    }
}

// Settings Panel
const apiKeyInput = document.getElementById('api-key-input');
const toggleApiKeyBtn = document.getElementById('toggle-api-key');
const usbModeSelect = document.getElementById('usb-mode-select');
const logLevelSelect = document.getElementById('log-level-select');
const saveSettingsBtn = document.getElementById('save-settings');

apiKeyInput.value = apiKey;

toggleApiKeyBtn.addEventListener('click', () => {
    const type = apiKeyInput.type === 'password' ? 'text' : 'password';
    apiKeyInput.type = type;
    toggleApiKeyBtn.textContent = type === 'password' ? 'Show' : 'Hide';
});

saveSettingsBtn.addEventListener('click', async () => {
    apiKey = apiKeyInput.value;
    localStorage.setItem('apiKey', apiKey);

    try {
        await apiCall('/api/settings/set', {
            method: 'POST',
            body: JSON.stringify({
                usb_mode: usbModeSelect.value,
                log_level: logLevelSelect.value
            })
        });
        showToast('Settings saved', 'success');
    } catch (error) {
        // Error already shown
    }
});

async function loadSettings() {
    try {
        const data = await apiCall('/api/settings/get');
        usbModeSelect.value = data.usb_mode || 'keyboard_mouse';
        logLevelSelect.value = data.log_level || 'INFO';
    } catch (error) {
        // Error already shown
    }
}

// Auto-refresh
setInterval(() => {
    if (document.querySelector('#status-panel.active')) {
        updateStatus();
    }
    if (document.querySelector('#logs-panel.active')) {
        updateLogs();
    }
    if (document.querySelector('#jitter-panel.active')) {
        updateJitterStatus();
    }
}, 5000);

// Initial load
loadMacros();
updateStatus();
updateJitterStatus();
loadSettings();
