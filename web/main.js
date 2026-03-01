const MAX_INTERFACES = 3;
let interfaceCounter = 0;
let currentStep = 1;

// --- STEP NAVIGATION ---

function updateStepUI() {
    // Update step visibility
    document.querySelectorAll('.step-content').forEach(step => {
        step.classList.toggle('active', parseInt(step.id.split('-')[1]) === currentStep);
    });

    // Update stepper visibility and icons
    const steps = document.querySelectorAll('.stepper .step');
    steps.forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.toggle('active', stepNum === currentStep);
        step.classList.toggle('completed', stepNum < currentStep);

        // Update Icons (Cumulative active state)
        const img = step.querySelector('img');
        if (img) {
            const suffixes = {
                1: { suffix: "", ext: "jpg" },
                2: { suffix: "-activ", ext: "jpg" },
                3: { suffix: "-activity", ext: "jpg" },
                4: { suffix: "-activity", ext: "jpg" },
                5: { suffix: "-activ", ext: "jpg" },
                6: { suffix: "-activ", ext: "jpg" }
            };

            const config = suffixes[stepNum];
            let baseName = "";
            if (stepNum === 1) baseName = "account-settings";
            else if (stepNum === 2) baseName = "basic-settings";
            else if (stepNum === 3) baseName = "site-profile";
            else if (stepNum === 4) baseName = "switch-wide-settings";
            else if (stepNum === 5) baseName = "port-settings";
            else if (stepNum === 6) baseName = "summary";

            if (stepNum <= currentStep) {
                img.src = `photo/${baseName}${config.suffix}.${config.ext}`;
            } else {
                img.src = `photo/${baseName}.jpg`;
            }
        }
    });

    // Update progress bar
    const totalSteps = steps.length;
    const progressPercent = ((currentStep - 1) / (totalSteps - 1));
    const progressBar = document.getElementById('stepper-progress');
    if (progressBar) {
        progressBar.style.width = `calc(${progressPercent} * (100% - 90px))`;
    }

    // Update buttons
    const backBtn = document.getElementById('back-btn');
    if (backBtn) backBtn.disabled = (currentStep === 1);

    const nextBtn = document.getElementById('next-btn');
    if (nextBtn) {
        if (currentStep === 6) {
            nextBtn.style.display = 'none';
        } else {
            nextBtn.style.display = 'inline-block';
            nextBtn.textContent = 'Next Step >';
        }
    }
}

function nextStep() {
    if (currentStep < 6) {
        currentStep++;
        updateStepUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepUI();
    }
}

function goToStep(step) {
    currentStep = step;
    updateStepUI();
}

// --- INFO PANEL TABS ---

function switchTab(tabId) {
    document.querySelectorAll('.info-area .tab').forEach(tab => {
        tab.classList.toggle('active', tab.getAttribute('onclick').includes(tabId));
    });

    document.getElementById('device-info-pane').classList.toggle('hidden', tabId !== 'device-info');
    document.getElementById('help-tips-pane').classList.toggle('hidden', tabId !== 'help-tips');
}

// --- INTERFACES LOGIC ---

function createInterfaceField(name = "", ip = "", mask = "", noShutdown = false, index = 0) {
    const container = document.createElement("div");
    container.className = "interface-item";

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <strong class="interface-label">Interface #${index + 1}</strong>
            <button type="button" class="btn-remove" onclick="removeInterface(this)" title="Remove interface">&times;</button>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <div style="flex: 1; min-width: 200px;">
                <label>Name</label><br>
                <input type="text" class="interface-name" value="${name}" placeholder="GigabitEthernet0/0" style="width: 100%;">
            </div>

            <div style="flex: 1; min-width: 150px;">
                <label>IP Address</label><br>
                <input type="text" class="interface-ip" value="${ip}" placeholder="192.168.1.1" style="width: 100%;">
            </div>

            <div style="flex: 1; min-width: 150px;">
                <label>Subnet Mask</label><br>
                <input type="text" class="interface-mask" value="${mask}" placeholder="255.255.255.0" style="width: 100%;">
            </div>
        </div>

        <div style="margin-top: 15px;">
            <label class="toggle-group">
                <div class="switch">
                    <input type="checkbox" class="interface-no-shutdown" ${noShutdown ? 'checked' : ''}>
                    <span class="slider"></span>
                </div>
                <span class="toggle-label">no shutdown (Enable interface)</span>
            </label>
        </div>
    `;

    return container;
}

function renumberInterfaces() {
    const items = document.querySelectorAll('.interface-item');
    items.forEach((item, idx) => {
        const label = item.querySelector('.interface-label');
        if (label) {
            label.textContent = `Interface #${idx + 1}`;
        }
    });
}

function removeInterface(btn) {
    btn.closest('.interface-item').remove();
    renumberInterfaces();
    updateAddButtonState();
}

function updateAddButtonState() {
    const addBtn = document.querySelector("#step-2 button.btn-secondary");
    if (!addBtn) return;

    const currentCount = document.querySelectorAll(".interface-item").length;

    if (currentCount >= MAX_INTERFACES) {
        addBtn.disabled = true;
        addBtn.textContent = `Limit reached (${MAX_INTERFACES})`;
        addBtn.style.opacity = "0.5";
    } else {
        addBtn.disabled = false;
        addBtn.textContent = "+ Add Interface";
        addBtn.style.opacity = "1";
    }
}

function addInterfaceField(name = "", ip = "", mask = "", noShutdown = false) {
    const currentCount = document.querySelectorAll(".interface-item").length;

    if (currentCount >= MAX_INTERFACES) {
        alert(`Maximum ${MAX_INTERFACES} interfaces allowed!`);
        return;
    }

    const list = document.getElementById("interfaces-list");
    const field = createInterfaceField(name, ip, mask, noShutdown, currentCount);
    list.appendChild(field);

    updateAddButtonState();
}

function initDefaultInterfaces() {
    interfaceCounter = 0;
    document.getElementById("interfaces-list").innerHTML = "";

    addInterfaceField("GigabitEthernet0/0", "192.168.1.1", "255.255.255.0", true);
    addInterfaceField("GigabitEthernet0/1", "172.16.0.1", "255.255.0.0", false);
    addInterfaceField("GigabitEthernet0/2", "10.0.0.1", "255.255.255.252", true);
}

function getInterfacesData() {
    const fields = document.querySelectorAll(".interface-item");
    const interfaces = [];
    const networks = [];
    const noShutdownList = [];

    fields.forEach(field => {
        const name = field.querySelector(".interface-name").value.trim();
        const ip = field.querySelector(".interface-ip").value.trim();
        const mask = field.querySelector(".interface-mask").value.trim();
        const noShutdown = field.querySelector(".interface-no-shutdown").checked;

        if (name && (ip || mask)) {
            interfaces.push(name);
            const finalIp = ip || "192.168.1.1";
            const finalMask = mask || "255.255.255.0";
            networks.push([finalIp, finalMask]);
            if (noShutdown) {
                noShutdownList.push(name);
            }
        }
    });

    return { interfaces, networks, noShutdownList };
}

// --- OSPF Logic ---
document.querySelectorAll('input[name="routing-protocol"]').forEach(radio => {
    radio.addEventListener('change', () => {
        const ospfOptions = document.getElementById("ospf-options");
        if (ospfOptions) {
            ospfOptions.classList.toggle("hidden", radio.value !== "OSPF");
        }
    });
});

// --- AUTO FILL ---
function autoFillForm() {
    initDefaultInterfaces();

    document.getElementById("hostname").value = "Branch-R1";
    document.getElementById("enable_secret").value = "Cisco123!";
    document.getElementById("console_password").value = "Console123!";
    document.getElementById("vty_password").value = "VtyPass123!";
    document.getElementById("enable_ssh").checked = true;

    const ospfRadio = document.querySelector('input[name="routing-protocol"][value="OSPF"]');
    if (ospfRadio) {
        ospfRadio.checked = true;
        const ospfOptions = document.getElementById("ospf-options");
        if (ospfOptions) ospfOptions.classList.remove("hidden");
    }
    document.getElementById("router-id").value = "1.1.1.1";

    document.getElementById("multicast-checkbox").checked = true;

    document.getElementById("dhcp-network").value = "192.168.10.0";
    document.getElementById("dhcp-mask").value = "255.255.255.0";
    document.getElementById("dhcp-gateway").value = "192.168.10.1";
    document.getElementById("dhcp-dns").value = "8.8.8.8";

    document.getElementById("telephony-checkbox").checked = true;
    document.getElementById("dn1-number").value = "1001";
    document.getElementById("dn1-user").value = "Alice";
    document.getElementById("dn2-number").value = "1002";
    document.getElementById("dn2-user").value = "Bob";

    document.getElementById("nat-inside").value = "GigabitEthernet0/0";
    document.getElementById("nat-outside").value = "GigabitEthernet0/1";

    alert("Default values populated!");
}

// --- GENERATE ---
async function sendToPython() {
    const { interfaces, networks, noShutdownList } = getInterfacesData();

    if (interfaces.length === 0) {
        alert("❌ Please add at least one interface!");
        goToStep(2);
        return;
    }

    const routingProtocol = document.querySelector('input[name="routing-protocol"]:checked')?.value || "";
    const routerId = document.getElementById("router-id").value.trim();

    const hostname = document.getElementById("hostname").value.trim();
    const enableSecret = document.getElementById("enable_secret").value.trim();
    const consolePass = document.getElementById("console_password").value.trim();
    const vtyPass = document.getElementById("vty_password").value.trim();

    const telephonyEnabled = document.getElementById("telephony-checkbox").checked;
    const dnList = [
        { number: document.getElementById("dn1-number").value.trim(), user: document.getElementById("dn1-user").value.trim() },
        { number: document.getElementById("dn2-number").value.trim(), user: document.getElementById("dn2-user").value.trim() },
        { number: document.getElementById("dn3-number").value.trim(), user: document.getElementById("dn3-user").value.trim() }
    ];

    const enableSSH = document.getElementById("enable_ssh").checked;
    const ipMulticast = document.getElementById("multicast-checkbox").checked;

    const dhcpNetwork = document.getElementById("dhcp-network").value.trim();
    const dhcpMask = document.getElementById("dhcp-mask").value.trim();
    const dhcpGateway = document.getElementById("dhcp-gateway").value.trim();
    const dhcpDns = document.getElementById("dhcp-dns").value.trim();

    try {
        const res = await eel.process_text(
            routingProtocol,
            "",
            routerId,
            ipMulticast,
            telephonyEnabled,
            dnList,
            enableSSH,
            hostname,
            enableSecret,
            consolePass,
            vtyPass,
            dhcpNetwork,
            dhcpMask,
            dhcpGateway,
            dhcpDns,
            interfaces,
            networks,
            noShutdownList
        )();

        const responseDiv = document.getElementById("response");
        responseDiv.innerText = res;
        responseDiv.style.color = res.startsWith("❌") ? "#aa0000" : "#006600";

        // Show download button if success
        const downloadBtn = document.getElementById("download-btn");
        if (!res.startsWith("❌")) {
            downloadBtn.classList.remove("hidden");
        } else {
            downloadBtn.classList.add("hidden");
            responseDiv.innerText = "❌ Error: " + res;
        }
    } catch (err) {
        console.error("Generation error:", err);
        document.getElementById("response").innerText = "❌ Error: " + err.message;
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

// --- INIT ---
document.addEventListener("DOMContentLoaded", () => {
    // Start with 0 interfaces as per request
    document.getElementById("interfaces-list").innerHTML = "";
    updateStepUI();
});
