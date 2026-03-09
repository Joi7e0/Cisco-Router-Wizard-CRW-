// ui.js
const MAX_INTERFACES = 3;
let currentStep = 1;

// --- STEP NAVIGATION ---
function updateStepUI() {
    document.querySelectorAll('.step-content').forEach(step => {
        const stepNum = parseInt(step.id.split('-')[1]);
        const isActive = stepNum === currentStep;
        step.classList.toggle('active', isActive);

        if (isActive && stepNum === 3) {
            updateISISInterfaceChecklist();
        }
    });

    const steps = document.querySelectorAll('.stepper .step');
    steps.forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.toggle('active', stepNum === currentStep);
        step.classList.toggle('completed', stepNum < currentStep);

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

    const totalSteps = steps.length;
    const progressPercent = ((currentStep - 1) / (totalSteps - 1));
    const progressBar = document.getElementById('stepper-progress');
    if (progressBar) {
        progressBar.style.width = `calc(${progressPercent} * (100% - 90px))`;
    }

    const backBtn = document.getElementById('back-btn');
    if (backBtn) backBtn.disabled = (currentStep === 1);

    const nextBtn = document.getElementById('next-btn');
    if (nextBtn) {
        if (currentStep === 6) {
            nextBtn.disabled = true;
            nextBtn.style.opacity = '0.5';
            nextBtn.style.cursor = 'not-allowed';
            nextBtn.style.pointerEvents = 'none';
        } else {
            nextBtn.disabled = false;
            nextBtn.style.opacity = '1';
            nextBtn.style.cursor = 'pointer';
            nextBtn.style.pointerEvents = 'auto';
        }
    }
}

window.nextStep = function () {
    if (currentStep < 6) {
        currentStep++;
        updateStepUI();
    }
};

window.prevStep = function () {
    if (currentStep > 1) {
        currentStep--;
        updateStepUI();
    }
};

window.goToStep = function (step) {
    currentStep = step;
    updateStepUI();
};

window.switchTab = function (tabId) {
    document.getElementById('device-info-pane').classList.remove('hidden');
};

window.updateEncryptionSecurityBadge = function () {
    const select = document.getElementById('password_encryption_type');
    const badge = document.getElementById('encryption_security_badge');
    if (!select || !badge) return;

    const val = parseInt(select.value);
    badge.className = 'security-badge';

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
};

function createInterfaceField(name = "", ip = "", mask = "", description = "", noShutdown = false, index = 0) {
    const container = document.createElement("div");
    container.className = "interface-item";

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <strong class="interface-label"><span data-i18n="interfaceNum"></span>${index + 1}</strong>
            <button type="button" class="btn-remove" onclick="removeInterface(this)" title="Remove interface">&times;</button>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <div style="flex: 1; min-width: 200px;">
                <label data-i18n="name">Name</label><br>
                <input type="text" class="interface-name interface-input" value="${name}" placeholder="GigabitEthernet0/0" style="width: 100%;">
            </div>

            <div style="flex: 1; min-width: 150px;">
                <label data-i18n="ipAddress">IP Address</label><br>
                <input type="text" class="interface-ip interface-input" value="${ip}" placeholder="192.168.1.1" style="width: 100%;">
            </div>

            <div style="flex: 1; min-width: 150px;">
                <label data-i18n="subnetMask">Subnet Mask</label><br>
                <input type="text" class="interface-mask interface-input" value="${mask}" placeholder="255.255.255.0" style="width: 100%;">
            </div>
        </div>

        <div style="margin-top: 15px;">
            <label data-i18n="description">Description</label><br>
            <input type="text" class="interface-description interface-input" value="${description}" placeholder="Connection to...">
        </div>

        <div style="margin-top: 5px;">
            <label class="toggle-group">
                <div class="switch">
                    <input type="checkbox" class="interface-no-shutdown" ${noShutdown ? 'checked' : ''}>
                    <span class="slider"></span>
                </div>
                <span class="toggle-label" data-i18n="noShutdown">no shutdown (Enable interface)</span>
            </label>
        </div>
    `;

    // Reapply translations specifically for the newly injected HTML
    const lang = window.crw_i18n.getCurrentLanguage();
    window.crw_i18n.loadLocale(lang).then(trans => {
        const ctx = trans["wizard"];
        if (ctx) {
            container.querySelectorAll("[data-i18n]").forEach(element => {
                const key = element.getAttribute("data-i18n");
                if (ctx[key]) {
                    element.innerHTML = ctx[key];
                }
            });
            // Update the combined text logic for interface label explicitly
            const lbl = container.querySelector(".interface-label");
            if (lbl && ctx["interfaceNum"]) {
                lbl.innerHTML = `<span data-i18n="interfaceNum">${ctx["interfaceNum"]}</span>${index + 1}`;
            }
        }
    });

    return container;
}

function updateAddButtonState() {
    const addBtn = document.querySelector("#step-2 button.btn-secondary");
    if (!addBtn) return;

    const currentCount = document.querySelectorAll(".interface-item").length;

    if (currentCount >= MAX_INTERFACES) {
        addBtn.disabled = true;
        // The text might be overridden by translation eventually, but give immediate feedback
        addBtn.setAttribute("data-i18n", "interfaceLimit");
        addBtn.style.opacity = "0.5";
    } else {
        addBtn.disabled = false;
        addBtn.setAttribute("data-i18n", "addInterface");
        addBtn.style.opacity = "1";
    }

    // Trigger i18n
    window.crw_i18n.setLanguage(window.crw_i18n.getCurrentLanguage(), "wizard");
}

window.renumberInterfaces = function () {
    const items = document.querySelectorAll('.interface-item');
    items.forEach((item, idx) => {
        const labelspan = item.querySelector('.interface-label span');
        const text = labelspan ? labelspan.textContent : 'Interface #';
        const label = item.querySelector('.interface-label');
        if (label) {
            label.innerHTML = `<span data-i18n="interfaceNum">${text}</span>${idx + 1}`;
        }
    });
};

window.removeInterface = function (btn) {
    btn.closest('.interface-item').remove();
    window.renumberInterfaces();
    updateAddButtonState();
};

window.addInterfaceField = function (name = "", ip = "", mask = "", description = "", noShutdown = false) {
    const currentCount = document.querySelectorAll(".interface-item").length;
    if (currentCount >= MAX_INTERFACES) return;

    const list = document.getElementById("interfaces-list");
    const field = createInterfaceField(name, ip, mask, description, noShutdown, currentCount);
    list.appendChild(field);

    updateAddButtonState();
};

window.initDefaultInterfaces = function () {
    document.getElementById("interfaces-list").innerHTML = "";
    addInterfaceField("GigabitEthernet0/0", "192.168.1.1", "255.255.255.0", "Local LAN", true);
    addInterfaceField("GigabitEthernet0/1", "172.16.0.1", "255.255.0.0", "WAN Connection", false);
    addInterfaceField("GigabitEthernet0/2", "10.0.0.1", "255.255.255.252", "Point-to-Point Link", true);
};

window.selectProtocol = function (protocolName) {
    const oldRadio = document.getElementById(`radio-${protocolName}`);
    if (oldRadio) oldRadio.checked = true;

    document.querySelectorAll('.protocol-btn').forEach(btn => {
        btn.classList.toggle('active', btn.id === `btn-${protocolName}`);
    });

    document.querySelectorAll('.protocol-pane').forEach(pane => {
        pane.classList.add('hidden');
    });

    const activePane = document.getElementById(`pane-${protocolName}`);
    if (activePane) activePane.classList.remove('hidden');

    if (protocolName === 'IS-IS') updateISISInterfaceChecklist();
};

window.updateISISInterfaceChecklist = function () {
    const container = document.getElementById("isis-interfaces-checklist");
    if (!container || !window.crw_state) return;

    const { interfaces } = window.crw_state.getInterfacesData();
    if (interfaces.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic; font-size: 0.8rem;">Add interfaces in Step 2 first...</p>';
        return;
    }

    container.innerHTML = interfaces.map((inf) => `
        <div class="checklist-item">
            <label class="checkbox-container">
                <input type="checkbox" class="isis-participation-check" value="${inf}">
                <span class="checkmark"></span>
                <span class="label-text" style="font-size: 0.85rem;">${inf}</span>
            </label>
        </div>
    `).join('');
};

window.autoFillForm = function () {
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
};

// Orchestration
window.triggerGenerateConfig = async function () {
    if (!window.crw_state || !window.crw_api) return;

    const { interfaces } = window.crw_state.getInterfacesData();
    if (interfaces.length === 0) {
        alert("❌ Please add at least one interface!");
        goToStep(2);
        return;
    }

    const data = window.crw_state.buildConfigData();
    await window.crw_api.sendToPython(data);
};

// Lifecycle
document.addEventListener("DOMContentLoaded", () => {
    // Basic Theme hook-up checking
    const savedTheme = localStorage.getItem('crw_theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    // Load translations globally
    const lang = window.crw_i18n.getCurrentLanguage();
    window.crw_i18n.setLanguage(lang, "wizard");

    document.getElementById("interfaces-list").innerHTML = "";
    updateStepUI();
    selectProtocol('Static');
});
