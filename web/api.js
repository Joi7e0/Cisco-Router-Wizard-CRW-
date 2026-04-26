// api.js

// ===================== СТАН ПІДКЛЮЧЕННЯ =====================
let _isConnected = false;
let _configGenerated = false;

function _setConnectionState(connected) {
    _isConnected = connected;
    _updateConnectionIndicator();
    _updateDeployButton();
}

function _setConfigGenerated(generated) {
    _configGenerated = generated;
    _updateDeployButton();
}

function _updateConnectionIndicator() {
    const indicator = document.getElementById("conn-status-dot");
    const label = document.getElementById("conn-status-label");
    const disconnectBtn = document.getElementById("disconnect-btn");
    const connectBtn = document.getElementById("connect-btn");

    if (indicator) {
        indicator.className = _isConnected ? "status-dot connected" : "status-dot disconnected";
    }
    if (label) {
        label.textContent = _isConnected ? "🟢 Online" : "🔴 Offline";
    }
    if (disconnectBtn) disconnectBtn.disabled = !_isConnected;
    if (connectBtn) connectBtn.disabled = _isConnected;
}

function _updateDeployButton() {
    const deployBtn = document.getElementById("deploy-btn");
    if (!deployBtn) return;
    const canDeploy = _isConnected && _configGenerated;
    deployBtn.disabled = !canDeploy;
    deployBtn.style.opacity = canDeploy ? "1" : "0.5";
    deployBtn.style.cursor = canDeploy ? "pointer" : "not-allowed";
}

// ===================== ГЕНЕРАЦІЯ КОНФІГУРАЦІЇ =====================
async function sendToPython(configData) {
    try {
        const res = await eel.process_text(configData)();

        // Перевіряємо, чи повернув Python JSON-помилку
        try {
            const parsed = JSON.parse(res);
            if (parsed.error) {
                const downloadBtn = document.getElementById("download-btn");
                if (downloadBtn) downloadBtn.classList.add("hidden");

                const responseDiv = document.getElementById("response");
                if (responseDiv) {
                    responseDiv.innerText = "Error: " + (parsed.defaultMessage || "Generation failed.");
                    responseDiv.style.color = "#aa0000";
                }
                _setConfigGenerated(false);
                return res;
            }
        } catch (e) {
            // Звичайна успішна відповідь - не є JSON
        }

        const responseDiv = document.getElementById("response");
        if (responseDiv) {
            responseDiv.innerText = res;
            responseDiv.style.color = res.startsWith("❌") ? "#aa0000" : "#006600";
        }

        const downloadBtn = document.getElementById("download-btn");
        if (downloadBtn) {
            if (!res.startsWith("❌")) {
                downloadBtn.classList.remove("hidden");
                _setConfigGenerated(true);
            } else {
                downloadBtn.classList.add("hidden");
                _setConfigGenerated(false);
            }
        }

        return res;

    } catch (err) {
        console.error("Generation error:", err);
        const responseDiv = document.getElementById("response");
        if (responseDiv) {
            responseDiv.innerText = "❌ Error: " + err.message;
        }
        _setConfigGenerated(false);
        throw err;
    }
}

// ===================== ЗАВАНТАЖЕННЯ =====================
function downloadCommands() {
    const text = document.getElementById("response").innerText;
    if (!text || text.startsWith("❌") || text === "Output will appear here") {
        alert("Please generate configuration first!");
        return;
    }

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cisco_config_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ===================== TELNET ПІДКЛЮЧЕННЯ =====================
async function connectRouter() {
    const host     = (document.getElementById("conn-host")?.value || "").trim();
    const port     = parseInt(document.getElementById("conn-port")?.value || "23");
    const username = (document.getElementById("conn-user")?.value || "").trim();
    const password = document.getElementById("conn-pass")?.value || "";
    const secret   = document.getElementById("conn-secret")?.value || "";

    if (!host) {
        _showDeployLog("❌ Вкажіть IP-адресу роутера.", "error");
        return;
    }

    const connectBtn = document.getElementById("connect-btn");
    if (connectBtn) {
        connectBtn.disabled = true;
        connectBtn.textContent = "Підключення...";
    }

    _showDeployLog("⏳ Встановлення Telnet-з'єднання з " + host + ":" + port + " ...", "info");

    try {
        const res = await eel.connect_router(host, port, username, password, secret)();
        const parsed = JSON.parse(res);

        if (parsed.ok) {
            _setConnectionState(true);
            _showDeployLog("✅ З'єднання з " + host + " встановлено успішно!", "success");
        } else {
            _setConnectionState(false);
            _showDeployLog("❌ Не вдалося підключитися: " + (parsed.error || "Unknown error"), "error");
        }
    } catch (err) {
        _setConnectionState(false);
        _showDeployLog("❌ Помилка: " + err.message, "error");
    } finally {
        if (connectBtn) {
            connectBtn.textContent = "Підключитись";
            connectBtn.disabled = _isConnected;
        }
    }
}

async function disconnectRouter() {
    try {
        await eel.disconnect_router()();
    } catch (e) {
        console.warn("Disconnect error:", e);
    }
    _setConnectionState(false);
    _showDeployLog("🔌 З'єднання закрито.", "info");
}

// ===================== ДЕПЛОЙ НА РОУТЕР =====================
async function deployToRouter() {
    if (!_isConnected) {
        _showDeployLog("❌ Немає активного з'єднання. Спочатку підключіться до роутера.", "error");
        return;
    }

    const configText = document.getElementById("response")?.innerText || "";
    if (!configText || configText.startsWith("❌")) {
        _showDeployLog("❌ Немає згенерованої конфігурації. Спочатку натисніть Generate.", "error");
        return;
    }

    const deployBtn = document.getElementById("deploy-btn");
    if (deployBtn) {
        deployBtn.disabled = true;
        deployBtn.textContent = "⏳ Відправка...";
    }

    _showDeployLog("⏳ Відправка " + configText.split('\n').length + " команд на роутер...", "info");

    try {
        const res = await eel.deploy_config(configText)();
        const parsed = JSON.parse(res);

        if (parsed.ok) {
            _showDeployLog(
                "✅ Конфігурація успішно застосована!\n\n--- Вивід роутера ---\n" + (parsed.output || "(немає виводу)"),
                "success"
            );
        } else {
            _showDeployLog(
                "❌ Помилка деплою: " + (parsed.error || "Unknown error"),
                "error"
            );
        }
    } catch (err) {
        _showDeployLog("❌ Критична помилка: " + err.message, "error");
    } finally {
        if (deployBtn) {
            deployBtn.textContent = "🚀 Застосувати на роутері";
            _updateDeployButton();
        }
    }
}

// ===================== УТИЛІТИ =====================
function _showDeployLog(message, type = "info") {
    const logEl = document.getElementById("deploy-log");
    if (!logEl) return;

    logEl.classList.remove("hidden");
    logEl.innerText = message;

    const colors = { success: "#006600", error: "#aa0000", info: "#004899" };
    logEl.style.color = colors[type] || "#333";
}

window.crw_api = {
    sendToPython,
    downloadCommands,
    connectRouter,
    disconnectRouter,
    deployToRouter,
};

