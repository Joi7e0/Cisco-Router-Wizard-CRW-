// api.js

async function sendToPython(configData) {
    try {
        const res = await eel.process_text(configData)();

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
                if (responseDiv) responseDiv.innerText = "❌ Error: " + res;
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

window.crw_api = {
    sendToPython,
    downloadCommands
};
