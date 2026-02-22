/**
 * Handles the native HTML5 file input selection
 * When a directory is selected, this grabs the full file objects.
 * We extract the path from the first file to get its absolute folder path.
 */
document.addEventListener("DOMContentLoaded", () => {
    // Load storage info
    fetchStorage();

    // Start polling logs immediately
    pollLogs();
    setInterval(pollLogs, 1000); // Fetch logs every 1 second
});

/**
 * Fetches the system storage data and updates the widget bar.
 */
async function fetchStorage() {
    try {
        const response = await fetch('/api/system_storage');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                document.getElementById('storage-text').textContent = `Total: ${data.total_gb} GB`;

                // Add a small delay for the animation to be visible on load
                setTimeout(() => {
                    const percentText = document.getElementById('storage-percent');
                    if (percentText) percentText.textContent = `${data.used_percent}%`;

                    // Maximum circumference is 126. Empty is dashoffset=126, Full is dashoffset=0.
                    const circleCircumference = 126;
                    const dashoffset = circleCircumference - (data.used_percent / 100) * circleCircumference;

                    const bar = document.getElementById('storage-bar');
                    if (bar) {
                        bar.style.strokeDashoffset = dashoffset;

                        // Change color based on severity
                        if (data.used_percent > 90) {
                            bar.style.stroke = '#ef4444'; // Red
                        } else if (data.used_percent > 75) {
                            bar.style.stroke = '#f59e0b'; // Orange
                        } else {
                            bar.style.stroke = '#10b981'; // Green (safe)
                        }
                    }
                }, 300);
            }
        }
    } catch (e) {
        console.error("Storage fetch failed", e);
    }
}

// Listen for the native directory picker
const picker = document.getElementById('native-dir-picker');
if (picker) {
    picker.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            // Electron/Tauri injects physical absolute path via .path property
            // Standard browsers usually only provide .webkitRelativePath

            const file = e.target.files[0];
            let absolutePath = file.path;

            if (absolutePath) {
                // Extract directory by removing the filename from the path
                // e.g. /Users/name/Downloads/file.txt -> /Users/name/Downloads
                const isWin = absolutePath.includes('\\');
                const sep = isWin ? '\\' : '/';
                const dirPath = absolutePath.substring(0, absolutePath.lastIndexOf(sep));

                document.getElementById('target-path').value = dirPath;
                showToast("📁", "Folder selected successfully!");
            } else {
                // It's a standard web browser enforcing security rules.
                showToast("⚠️", "Browser security prevents automatic folder linking. Please paste the path directly.", true);
            }
        }
        // Reset input so it fires change again if they re-select the same folder
        e.target.value = '';
    });
}

const ENDPOINTS = {
    organize: "/api/organize",
    undo: "/api/undo",
    duplicates: "/api/clean/duplicates",
    empty_folders: "/api/clean/empty_folders",
};

/**
 * Main trigger function hooked to HTML buttons.
 */
async function triggerAction(actionName) {
    const pathInput = document.getElementById("target-path").value.trim();

    // Validate path for actions that require it
    if (actionName !== 'undo' && !pathInput) {
        showToast("⚠️", "Please paste an absolute directory path first!", true);
        document.getElementById("target-path").focus();
        return;
    }

    const payload = {
        path: pathInput,
    };

    // If organizing, determine method
    if (actionName === 'organize') {
        const methodRadios = document.getElementsByName('org-method');
        let selectedMethod = 'type';
        for (const radio of methodRadios) {
            if (radio.checked) {
                selectedMethod = radio.value;
                break;
            }
        }
        payload.method = selectedMethod;
    }

    const endpoint = ENDPOINTS[actionName];
    if (!endpoint) return;

    // Show loading state
    const btnId = getButtonId(actionName);
    const btn = document.getElementById(btnId);
    const originalText = btn.innerHTML;
    setButtonLoading(btn, true);

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            showToast("✅", data.message);
        } else {
            showToast("❌", data.message, true);
        }
    } catch (error) {
        showToast("❌", "Network error. Is the server running?", true);
        console.error("Fetch error:", error);
    } finally {
        // Restore button state
        setButtonLoading(btn, false, originalText);
        // Force an immediate log refresh instead of waiting for the 1s tick
        pollLogs();
    }
}

/**
 * Fetches the recent logs from the backend memory buffer
 */
async function pollLogs() {
    try {
        const response = await fetch("/api/logs");
        if (!response.ok) return;

        const data = await response.json();
        renderLogs(data.logs || []);
    } catch (error) {
        console.error("Failed to poll logs", error);
    }
}

/**
 * Renders the log text in the fake terminal
 */
let lastLogCount = 0;
function renderLogs(logs) {
    const consoleDiv = document.getElementById("log-console");

    // Only update DOM if new logs arrived
    if (logs.length === lastLogCount) return;
    lastLogCount = logs.length;

    consoleDiv.innerHTML = "";

    if (logs.length === 0) {
        consoleDiv.innerHTML = "<span class='log-entry info'>System ready. Awaiting commands...</span>";
        return;
    }

    logs.forEach(logText => {
        const span = document.createElement("div");
        span.className = "log-entry";

        // Color coding for visual flair
        if (logText.includes("❌") || logText.includes("Error")) {
            span.classList.add("error");
        } else if (logText.includes("⚠️") || logText.includes("Warning")) {
            span.classList.add("warning");
        } else if (logText.includes("✅")) {
            span.classList.add("success");
        } else if (logText.includes("---")) {
            span.classList.add("info");
        }

        span.textContent = logText;
        consoleDiv.appendChild(span);
    });

    // Auto scroll to bottom
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

/**
 * Toast Notification System
 */
let toastTimeout;
function showToast(icon, message, isError = false) {
    const toast = document.getElementById("toast");
    const iconSpan = document.getElementById("toast-icon");
    const msgSpan = document.getElementById("toast-message");

    // Reset classes
    toast.className = "toast";

    if (isError) {
        toast.style.borderLeft = "4px solid var(--color-error)";
    } else {
        toast.style.borderLeft = "4px solid var(--color-success)";
    }

    iconSpan.textContent = icon;
    msgSpan.textContent = message;

    // Show toast
    setTimeout(() => {
        toast.classList.add("show");
    }, 10);

    // Hide after 3 seconds
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

/**
 * Utility matching action names to button IDs
 */
function getButtonId(action) {
    const map = {
        'organize': 'btn-organize',
        'undo': 'btn-undo',
        'duplicates': 'btn-duplicates',
        'empty_folders': 'btn-empty'
    };
    return map[action];
}

/**
 * Utility for disabling a button and showing a spinner
 */
function setButtonLoading(btn, isLoading, originalHTML = "") {
    if (!btn) return;

    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = `<span style="animation: spin 1s linear infinite; display: inline-block;">⏳</span> Working...`;

        // Add dynamic style if missing
        if (!document.getElementById('spin-anim')) {
            const style = document.createElement('style');
            style.id = 'spin-anim';
            style.innerHTML = `@keyframes spin { 100% { transform: rotate(360deg); } }`;
            document.head.appendChild(style);
        }
    } else {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}

/**
 * Executes a Local Search via the backend OS Walk API
 */
async function triggerSearch() {
    const pathInput = document.getElementById('target-path').value.trim();
    const queryInput = document.getElementById('search-query').value.trim();
    const btn = document.getElementById('btn-search');

    if (!pathInput || !queryInput) {
        showToast("⚠️", "Please provide both a Target Directory and a Search Query.", true);
        return;
    }

    const originalHTML = btn.innerHTML;
    setButtonLoading(btn, true, originalHTML);

    // Reset and show search table
    const resultsCard = document.getElementById('search-results-card');
    const tbody = document.getElementById('results-body');
    const statusText = document.getElementById('search-status');

    resultsCard.style.display = 'block';
    tbody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: var(--color-text-secondary); padding: 30px;">Searching, please wait...</td></tr>';
    statusText.textContent = `Searching inside ${pathInput}...`;

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path: pathInput, query: queryInput })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            tbody.innerHTML = ''; // Clear loading

            if (data.results.length === 0) {
                tbody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: var(--color-text-secondary); padding: 30px;">No files found matching your query.</td></tr>';
                statusText.textContent = `0 matches found.`;
            } else {
                data.results.forEach(file => {
                    const tr = document.createElement('tr');

                    const tdNamePath = document.createElement('td');
                    tdNamePath.innerHTML = `
                        <span class="file-name">${file.name}</span>
                        <span class="file-path">${file.path}</span>
                    `;

                    const tdSize = document.createElement('td');
                    tdSize.textContent = file.size;

                    tr.appendChild(tdNamePath);
                    tr.appendChild(tdSize);
                    tbody.appendChild(tr);
                });

                statusText.textContent = `Found ${data.results.length}${data.results.length >= 1000 ? '+' : ''} matches for "${queryInput}"`;
            }
        } else {
            showToast("❌", data.message || "Search failed. Please ensure the path exists.", true);
            tbody.innerHTML = `<tr><td colspan="2" style="text-align: center; color: var(--color-error); padding: 30px;">Error: ${data.message}</td></tr>`;
            statusText.textContent = "Search failed.";
        }
    } catch (error) {
        showToast("❌", "Network error occurred.", true);
        tbody.innerHTML = `<tr><td colspan="2" style="text-align: center; color: var(--color-error); padding: 30px;">Network Error: ${error}</td></tr>`;
        statusText.textContent = "Search failed.";
    } finally {
        setButtonLoading(btn, false, originalHTML);
    }
}
