const MAX_INTERFACES = 3;
let interfaceCounter = 0;
let currentStep = 1;

// --- STEP NAVIGATION ---

function updateStepUI() {
    // Update step visibility
    document.querySelectorAll('.step-content').forEach(step => {
        const stepNum = parseInt(step.id.split('-')[1]);
        const isActive = stepNum === currentStep;
        step.classList.toggle('active', isActive);

        // Initialize Step 3 data when it becomes active
        if (isActive && stepNum === 3) {
            updateISISInterfaceChecklist();
        }
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

// --- PASSWORD ENCRYPTION LOGIC ---

function updateEncryptionSecurityBadge() {
    const select = document.getElementById('password_encryption_type');
    const badge = document.getElementById('encryption_security_badge');
    if (!select || !badge) return;

    const val = parseInt(select.value);

    badge.className = 'security-badge'; // Reset classes

    if (val <= 4) {
        badge.classList.add('sec-low');
        badge.textContent = 'low';
    } else if (val <= 7) {
        badge.classList.add('sec-medium');
        badge.textContent = 'medium';
    } else {
        badge.classList.add('sec-high');
        badge.textContent = 'high';
    }
}

// --- INTERFACES LOGIC ---

function createInterfaceField(name = "", ip = "", mask = "", description = "", noShutdown = false, index = 0) {
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
                <input type="text" class="interface-name interface-input" value="${name}" placeholder="GigabitEthernet0/0" style="width: 100%;">
            </div>

            <div style="flex: 1; min-width: 150px;">
                <label>IP Address</label><br>
                <input type="text" class="interface-ip interface-input" value="${ip}" placeholder="192.168.1.1" style="width: 100%;">
            </div>

            <div style="flex: 1; min-width: 150px;">
                <label>Subnet Mask</label><br>
                <input type="text" class="interface-mask interface-input" value="${mask}" placeholder="255.255.255.0" style="width: 100%;">
            </div>
        </div>

        <div style="margin-top: 15px;">
            <label>Description</label><br>
            <input type="text" class="interface-description interface-input" value="${description}" placeholder="Connection to...">
        </div>

        <div style="margin-top: 5px;">
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

function addInterfaceField(name = "", ip = "", mask = "", description = "", noShutdown = false) {
    const currentCount = document.querySelectorAll(".interface-item").length;

    if (currentCount >= MAX_INTERFACES) {
        alert(`Maximum ${MAX_INTERFACES} interfaces allowed!`);
        return;
    }

    const list = document.getElementById("interfaces-list");
    const field = createInterfaceField(name, ip, mask, description, noShutdown, currentCount);
    list.appendChild(field);

    updateAddButtonState();
}

function initDefaultInterfaces() {
    interfaceCounter = 0;
    document.getElementById("interfaces-list").innerHTML = "";

    addInterfaceField("GigabitEthernet0/0", "192.168.1.1", "255.255.255.0", "Local LAN", true);
    addInterfaceField("GigabitEthernet0/1", "172.16.0.1", "255.255.0.0", "WAN Connection", false);
    addInterfaceField("GigabitEthernet0/2", "10.0.0.1", "255.255.255.252", "Point-to-Point Link", true);
}

function getInterfacesData() {
    const fields = document.querySelectorAll(".interface-item");
    const interfaces = [];
    const networks = [];
    const descriptions = [];
    const noShutdownList = [];

    fields.forEach(field => {
        const name = field.querySelector(".interface-name").value.trim();
        const ip = field.querySelector(".interface-ip").value.trim();
        const mask = field.querySelector(".interface-mask").value.trim();
        const description = field.querySelector(".interface-description").value.trim();
        const noShutdown = field.querySelector(".interface-no-shutdown").checked;

        if (name && (ip || mask)) {
            interfaces.push(name);
            const finalIp = ip || "192.168.1.1";
            const finalMask = mask || "255.255.255.0";
            networks.push([finalIp, finalMask]);
            descriptions.push(description);
            if (noShutdown) {
                noShutdownList.push(name);
            }
        }
    });

    return { interfaces, networks, descriptions, noShutdownList };
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
    document.getElementById("password_encryption_type").value = "5";
    updateEncryptionSecurityBadge();
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

// --- Routing Protocol Selection (Enterprise Refactor) ---
let staticRoutes = [];

function selectProtocol(protocolName) {
    // Update hidden radio for compatibility
    const oldRadio = document.getElementById(`radio-${protocolName}`);
    if (oldRadio) oldRadio.checked = true;

    // Update active state of buttons
    document.querySelectorAll('.protocol-btn').forEach(btn => {
        btn.classList.toggle('active', btn.id === `btn-${protocolName}`);
    });

    // Switch Panes
    document.querySelectorAll('.protocol-pane').forEach(pane => {
        pane.classList.add('hidden');
    });

    const activePane = document.getElementById(`pane-${protocolName}`);
    if (activePane) {
        activePane.classList.remove('hidden');
    }

    // Special logic for specific protocols
    if (protocolName === 'IS-IS') {
        updateISISInterfaceChecklist();
    }
}

// Static Routes logic removed as per simplification request

// Dynamic Checklist for IS-IS (Participation)
function updateISISInterfaceChecklist() {
    const container = document.getElementById("isis-interfaces-checklist");
    if (!container) return;

    const { interfaces } = getInterfacesData();
    if (interfaces.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic; font-size: 0.8rem;">Add interfaces in Step 2 first...</p>';
        return;
    }

    container.innerHTML = interfaces.map((inf, index) => `
        <div class="checklist-item">
            <label class="checkbox-container">
                <input type="checkbox" class="isis-participation-check" value="${inf}">
                <span class="checkmark"></span>
                <span class="label-text" style="font-size: 0.85rem;">${inf}</span>
            </label>
        </div>
    `).join('');
}

// Smart Wildcard Calculation
function calculateWildcard(maskOrCidr) {
    if (!maskOrCidr) return "";

    // Check if it's CIDR (/24)
    if (maskOrCidr.includes('/')) {
        const promo = maskOrCidr.split('/')[1];
        const cidr = parseInt(promo);
        if (isNaN(cidr)) return "Invalid CIDR";

        // Calculate Wildcard for CIDR
        let bits = (0xFFFFFFFF << (32 - cidr)) >>> 0;
        let wildcard = (~bits) >>> 0;

        return [
            (wildcard >> 24) & 0xFF,
            (wildcard >> 16) & 0xFF,
            (wildcard >> 8) & 0xFF,
            wildcard & 0xFF
        ].join('.');
    }

    // Check if it's Subnet Mask
    const parts = maskOrCidr.split('.');
    if (parts.length === 4) {
        return parts.map(p => 255 - parseInt(p)).join('.');
    }

    return "";
}

// --- Standalone Multicast Toggle ---
function toggleMulticastInSidebar() {
    const checkbox = document.getElementById("multicast-checkbox");
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
    }
}

// --- GENERATE ---
async function sendToPython() {
    const { interfaces, networks, descriptions, noShutdownList } = getInterfacesData();

    if (interfaces.length === 0) {
        alert("❌ Please add at least one interface!");
        goToStep(2);
        return;
    }

    // Collect Routing Configuration
    const routingProtocol = document.querySelector('input[name="routing-protocol"]:checked')?.value || "None";
    const routingConfig = {
        protocol: routingProtocol,
        networks: networks,
        staticRoutes: [],
        routerId: document.getElementById("router-id")?.value.trim() ||
            document.getElementById("bgp-router-id")?.value.trim() || "",
        ripNoAuto: document.getElementById("rip-no-auto")?.checked || false,
        eigrpAs: document.getElementById("eigrp-as")?.value.trim() || "100",
        eigrpNoAuto: document.getElementById("eigrp-no-auto")?.checked || false,
        ospfProcessId: document.getElementById("ospf-process-id")?.value.trim() || "1",
        ospfArea: document.getElementById("ospf-area")?.value.trim() || "0",
        bgpLocalAs: document.getElementById("bgp-local-as")?.value.trim() || "65000",
        bgpNeighborIp: document.getElementById("bgp-neighbor-ip")?.value.trim() || "",
        bgpRemoteAs: document.getElementById("bgp-remote-as")?.value.trim() || "",
        isisAreaId: document.getElementById("isis-area-id")?.value.trim() || "49.0001",
        isisSystemId: document.getElementById("isis-system-id")?.value.trim() || "0000.0000.0001.00",
        isisRouterType: document.getElementById("isis-type")?.value || "level-1-2",
        participatingInterfaces: Array.from(document.querySelectorAll(".isis-participation-check:checked")).map(el => el.value)
    };

    // Collect simplified Static Route
    const sDest = document.getElementById("static-dest")?.value.trim();
    const sMask = document.getElementById("static-mask")?.value.trim();
    const sNext = document.getElementById("static-next-hop")?.value.trim();
    if (sDest && sMask) {
        routingConfig.staticRoutes.push({
            dest: sDest,
            mask: sMask,
            nextHop: sNext
        });
    }

    const hostname = document.getElementById("hostname").value.trim();
    const enableSecret = document.getElementById("enable_secret").value.trim();
    const consolePass = document.getElementById("console_password").value.trim();
    const vtyPass = document.getElementById("vty_password").value.trim();
    const encryptionType = document.getElementById("password_encryption_type").value;

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
            "", // Legacy argument
            routingConfig.routerId || "", // Legacy position
            ipMulticast,
            telephonyEnabled,
            dnList,
            enableSSH,
            hostname,
            enableSecret,
            consolePass,
            vtyPass,
            encryptionType,
            dhcpNetwork,
            dhcpMask,
            dhcpGateway,
            dhcpDns,
            interfaces,
            networks,
            noShutdownList,
            descriptions,
            3, // max_ephones
            3, // max_dn
            "", // ip_source (empty to let backend handle)
            "", // auto_assign (empty to let backend handle)
            [], // dhcp_excluded (empty to let backend handle)
            routingConfig // Send the whole config object as the last argument
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
    // Apply Theme and Language Synergy
    const savedTheme = localStorage.getItem('crw_theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    const savedMode = localStorage.getItem('crw_mode');
    if (savedMode) {
        updateStatus(savedMode === 'connect' ? 'online' : 'offline');
    }

    const savedLang = localStorage.getItem('crw_lang');
    if (savedLang) {
        console.log("Active Language:", savedLang);
    }

    // Start with 0 interfaces as per request
    document.getElementById("interfaces-list").innerHTML = "";
    updateStepUI();

    // Default to Static on load
    selectProtocol('Static');
});

function updateStatus(status) {
    const text = document.getElementById('statusText');
    const dot = document.querySelector('.status-dot');
    if (!text || !dot) return;

    if (status === 'online') {
        text.textContent = "Status: Online";
        dot.className = 'status-dot green';
    } else {
        text.textContent = "Status: Offline";
        dot.className = 'status-dot orange';
    }
}
