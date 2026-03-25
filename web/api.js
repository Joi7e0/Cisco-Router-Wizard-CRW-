// api.js

let currentErrorContext = null;

async function sendToPython(configData) {
    try {
        const res = await eel.process_text(configData)();
        
        // Перевіряємо, чи повернув Python JSON-помилку
        try {
            const parsed = JSON.parse(res);
            if (parsed.error) {
                showErrorModal(parsed);
                // Ховаємо кнопку "завантажити"
                const downloadBtn = document.getElementById("download-btn");
                if (downloadBtn) downloadBtn.classList.add("hidden");
                
                const responseDiv = document.getElementById("response");
                if (responseDiv) {
                    responseDiv.innerText = "Generation failed. Please check the error details in the popup.";
                    responseDiv.style.color = "#aa0000";
                }
                return res;
            }
        } catch(e) {
            // Звичайна успішна відповідь - не є JSON
        }

        const responseDiv = document.getElementById("response");
        if (responseDiv) {
            responseDiv.innerText = res;
            responseDiv.style.color = res.startsWith("❌") ? "#aa0000" : "#006600";
        }

        // Show download button if success
        const downloadBtn = document.getElementById("download-btn");
        if (downloadBtn) {
            if (!res.startsWith("❌")) {
                downloadBtn.classList.remove("hidden");
            } else {
                downloadBtn.classList.add("hidden");
            }
        }

        return res;

    } catch (err) {
        console.error("Generation error:", err);
        const responseDiv = document.getElementById("response");
        if (responseDiv) {
            responseDiv.innerText = "❌ Error: " + err.message;
        }
        throw err;
    }
}

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

async function showErrorModal(errData) {
    currentErrorContext = errData;
    const lang = window.crw_i18n ? window.crw_i18n.getCurrentLanguage() : "en";
    let dict = {};
    if (window.crw_i18n && window.crw_i18n.loadLocale) {
        dict = await window.crw_i18n.loadLocale(lang);
    }
    const errDict = dict.errors || {};

    const modal = document.getElementById("error-modal");
    if (!modal) return;

    // Застосування перекладу
    document.getElementById("error-title").innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#a00" viewBox="0 0 256 256"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm-8-80V80a8,8,0,0,1,16,0v56a8,8,0,0,1-16,0Zm20,36a12,12,0,1,1-12-12A12,12,0,0,1,140,172Z"></path></svg> ` + (errDict.title || "Oops! Something went wrong");
    
    document.getElementById("error-message").innerText = errDict[errData.messageKey] || errData.defaultMessage;
    
    const instrText = errDict[errData.instructionsKey] || "Please check your configuration.";
    document.getElementById("error-instruction").innerHTML = `<strong>★ Action Required:</strong><br>${instrText}`;

    const lblCode = errDict.lblErrorCode || "Error Code: ";
    const lblId = errDict.lblErrorId || "Error ID: ";
    document.getElementById("error-code-display").innerText = `${lblCode}${errData.code}`;
    document.getElementById("error-id-display").innerText = `${lblId}${errData.id}`;

    const btnDismiss = document.getElementById("btn-dismiss-error");
    if (btnDismiss) btnDismiss.innerText = errDict.btnDismiss || "Dismiss";
    
    const btnCopy = document.getElementById("btn-copy-error");
    if (btnCopy) {
        btnCopy.innerText = errDict.btnReport || "Copy Details";
        btnCopy.style.backgroundColor = ""; // reset success style if any
    }

    modal.style.display = "flex"; // Оскільки ми використовуємо display:flex
    modal.classList.remove("hidden");
}

function closeErrorModal() {
    const modal = document.getElementById("error-modal");
    if (modal) {
        modal.style.display = "none";
        modal.classList.add("hidden");
    }
}

async function copyErrorDetails() {
    if (!currentErrorContext) return;
    const details = `Error Code: ${currentErrorContext.code}\nError ID: ${currentErrorContext.id}\nMessage: ${currentErrorContext.defaultMessage}`;
    try {
        await navigator.clipboard.writeText(details);
        const btn = document.getElementById("btn-copy-error");
        
        const lang = window.crw_i18n ? window.crw_i18n.getCurrentLanguage() : "en";
        const dict = (window.crw_i18n && window.crw_i18n.loadLocale) ? await window.crw_i18n.loadLocale(lang) : {};
        const successMsg = (dict.errors && dict.errors.reportSuccess) ? dict.errors.reportSuccess : "Copied!";
        
        if (btn) {
            btn.innerText = successMsg;
            btn.style.backgroundColor = "#2e7d32"; // green
            btn.style.color = "white";
        }
    } catch(err) {
        console.error("Failed to copy", err);
    }
}

window.crw_api = {
    sendToPython,
    downloadCommands,
    closeErrorModal,
    copyErrorDetails
};

