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
            updateMulticastInterfaceChecklist();
            updateStaticExitInterfaces();
            updateRipNetworks();
        }
        if (isActive && stepNum === 5) {
            toggleNatFields();
            toggleSnmpFields();
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
    if (currentStep === 1) {
        // Run validation and highlight errors, but still allow navigation
        validateStep1();
    }
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

window.toggleEncryptionTypeVisibility = function () {
    // This could be used to gray out the dropdown if we wanted to enforce a specific type when delegated,
    // but the requirement says "select type of encryption" in UI.
    // So we'll just use this as a hook for now.
    console.log("Delegation toggled:", document.getElementById('delegate_cryptography').checked);
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
    addInterfaceField("GigabitEthernet0/1", "172.16.0.1", "255.255.0.0", "WAN Connection", true);
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

window.updateStaticExitInterfaces = function() {
    const select = document.getElementById("static-exit-interface");
    if (!select || !window.crw_state) return;
    
    // Save current selection to restore it if possible
    const currentVal = select.value;
    
    const { interfaces } = window.crw_state.getInterfacesData();
    let optionsHTML = '<option value="">None</option>';
    interfaces.forEach(inf => {
        optionsHTML += `<option value="${inf}">${inf}</option>`;
    });
    select.innerHTML = optionsHTML;
    
    if (interfaces.includes(currentVal)) {
        select.value = currentVal;
    }
};

window.addStaticRoute = function() {
    const destInput = document.getElementById("static-dest");
    const maskInput = document.getElementById("static-mask");
    const nextHopInput = document.getElementById("static-next-hop");
    const intfInput = document.getElementById("static-exit-interface");
    
    const dest = destInput.value.trim();
    const mask = maskInput.value.trim();
    const nextHop = nextHopInput.value.trim();
    const intf = intfInput.value.trim();
    
    if (!dest || (!nextHop && !intf)) {
        alert("Destination network and either Next Hop OR Exit Interface are required.");
        return;
    }

    const tbody = document.getElementById("static-routes-list");
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #ddd";
    tr.dataset.dest = dest;
    tr.dataset.mask = mask;
    tr.dataset.nextHop = nextHop;
    tr.dataset.intf = intf;

    tr.innerHTML = `
        <td style="padding: 10px; font-size: 0.85rem;">${dest}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${mask}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${nextHop || '-'}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${intf || '-'}</td>
        <td style="padding: 10px; text-align: center;">
            <button type="button" class="btn-remove" onclick="removeStaticRoute(this)" style="position: static;" title="Remove route">&times;</button>
        </td>
    `;
    tbody.appendChild(tr);

    // Clear inputs
    destInput.value = "";
    maskInput.value = "";
    nextHopInput.value = "";
    intfInput.value = "";
};

window.removeStaticRoute = function(btn) {
    btn.closest('tr').remove();
};

window.updateRipNetworks = function() {
    const tbody = document.getElementById("rip-networks-list");
    if (!tbody || tbody.dataset.initialized) return;
    
    const { networks } = window.crw_state.getInterfacesData();
    networks.forEach(net => {
        const netIp = net[0];
        if(netIp && netIp !== "invalid") {
            const tr = document.createElement("tr");
            tr.style.borderBottom = "1px solid #ddd";
            tr.dataset.network = netIp;
            tr.innerHTML = `
                <td style="padding: 10px; font-size: 0.85rem;">${netIp}</td>
                <td style="padding: 10px;">
                    <button type="button" class="btn-remove" onclick="removeRipNetwork(this)" style="position: static;" title="Remove network">&times;</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    });
    tbody.dataset.initialized = "true";
};

window.addRipNetwork = function() {
    const input = document.getElementById("rip-network-input");
    const netIp = input.value.trim();
    if (!netIp) {
        alert("Network Address is required.");
        return;
    }

    const tbody = document.getElementById("rip-networks-list");
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #ddd";
    tr.dataset.network = netIp;

    tr.innerHTML = `
        <td style="padding: 10px; font-size: 0.85rem;">${netIp}</td>
        <td style="padding: 10px;">
            <button type="button" class="btn-remove" onclick="removeRipNetwork(this)" style="position: static;" title="Remove network">&times;</button>
        </td>
    `;
    tbody.appendChild(tr);
    input.value = "";
    tbody.dataset.initialized = "true"; // Ensure auto-population doesn't overwrite
};

window.removeRipNetwork = function(btn) {
    btn.closest('tr').remove();
};

// ===================== OSPF NETWORKS =====================
window.addOspfNetwork = function() {
    const netInput = document.getElementById("ospf-network-input");
    const wildcardInput = document.getElementById("ospf-wildcard-input");
    const areaInput = document.getElementById("ospf-area-input");

    const net = netInput.value.trim();
    const wildcard = wildcardInput.value.trim();
    const area = areaInput.value.trim();

    if (!net) {
        alert("Network Address is required.");
        return;
    }

    const tbody = document.getElementById("ospf-networks-list");
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #ddd";
    tr.dataset.network = net;
    tr.dataset.wildcard = wildcard;
    tr.dataset.area = area;

    tr.innerHTML = `
        <td style="padding: 10px; font-size: 0.85rem;">${net}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${wildcard || '-'}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${area || '0'}</td>
        <td style="padding: 10px; text-align: center;">
            <button type="button" class="btn-remove" onclick="removeOspfNetwork(this)" style="position: static;" title="Remove network">&times;</button>
        </td>
    `;
    tbody.appendChild(tr);

    netInput.value = "";
    wildcardInput.value = "";
    areaInput.value = "0";
};

window.removeOspfNetwork = function(btn) {
    btn.closest('tr').remove();
};

// ===================== EIGRP NETWORKS =====================
window.addEigrpNetwork = function() {
    const netInput = document.getElementById("eigrp-network-input");
    const wildcardInput = document.getElementById("eigrp-wildcard-input");

    const net = netInput.value.trim();
    const wildcard = wildcardInput.value.trim();

    if (!net) {
        alert("Network Address is required.");
        return;
    }

    const tbody = document.getElementById("eigrp-networks-list");
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #ddd";
    tr.dataset.network = net;
    tr.dataset.wildcard = wildcard;

    tr.innerHTML = `
        <td style="padding: 10px; font-size: 0.85rem;">${net}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${wildcard || '-'}</td>
        <td style="padding: 10px; text-align: center;">
            <button type="button" class="btn-remove" onclick="removeEigrpNetwork(this)" style="position: static;" title="Remove network">&times;</button>
        </td>
    `;
    tbody.appendChild(tr);

    netInput.value = "";
    wildcardInput.value = "";
};

window.removeEigrpNetwork = function(btn) {
    btn.closest('tr').remove();
};

// ===================== BGP NEIGHBORS =====================
window.addBgpNeighbor = function() {
    const ipInput = document.getElementById("bgp-neighbor-ip");
    const asInput = document.getElementById("bgp-remote-as");

    const ip = ipInput.value.trim();
    const remoteAs = asInput.value.trim();

    if (!ip || !remoteAs) {
        alert("Neighbor IP and Remote AS are required.");
        return;
    }

    const tbody = document.getElementById("bgp-neighbors-list");
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #ddd";
    tr.dataset.neighborIp = ip;
    tr.dataset.remoteAs = remoteAs;

    tr.innerHTML = `
        <td style="padding: 10px; font-size: 0.85rem;">${ip}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${remoteAs}</td>
        <td style="padding: 10px; text-align: center;">
            <button type="button" class="btn-remove" onclick="removeBgpNeighbor(this)" style="position: static;" title="Remove neighbor">&times;</button>
        </td>
    `;
    tbody.appendChild(tr);

    ipInput.value = "";
    asInput.value = "";
};

window.removeBgpNeighbor = function(btn) {
    btn.closest('tr').remove();
};

// ===================== BGP ADVERTISED NETWORKS =====================
window.addBgpNetwork = function() {
    const netInput = document.getElementById("bgp-network-input");
    const maskInput = document.getElementById("bgp-mask-input");

    const net = netInput.value.trim();
    const mask = maskInput.value.trim();

    if (!net) {
        alert("Network Address is required.");
        return;
    }

    const tbody = document.getElementById("bgp-networks-list");
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #ddd";
    tr.dataset.network = net;
    tr.dataset.mask = mask;

    tr.innerHTML = `
        <td style="padding: 10px; font-size: 0.85rem;">${net}</td>
        <td style="padding: 10px; font-size: 0.85rem;">${mask || '-'}</td>
        <td style="padding: 10px; text-align: center;">
            <button type="button" class="btn-remove" onclick="removeBgpNetwork(this)" style="position: static;" title="Remove network">&times;</button>
        </td>
    `;
    tbody.appendChild(tr);

    netInput.value = "";
    maskInput.value = "";
};

window.removeBgpNetwork = function(btn) {
    btn.closest('tr').remove();
};

window.toggleMulticastFields = function () {
    const isEnabled = document.getElementById("multicast-checkbox")?.checked;
    const group = document.getElementById("multicast-fields-group");
    if (group) {
        if (isEnabled) {
            group.classList.remove("hidden");
        } else {
            group.classList.add("hidden");
        }
    }
};

window.updateMulticastInterfaceChecklist = function () {
    const container = document.getElementById("multicast-interfaces-checklist");
    if (!container || !window.crw_state) return;

    const { interfaces, noShutdownList } = window.crw_state.getInterfacesData();
    if (interfaces.length === 0) {
        container.innerHTML = '<tr><td colspan="3" style="padding: 10px; text-align: center; color: #999; font-style: italic;">Add interfaces in Step 2 first...</td></tr>';
        return;
    }

    container.innerHTML = interfaces.map((inf) => {
        const isUp = noShutdownList.includes(inf);
        const statusText = isUp ? "Up" : "Down";
        return `
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;">${inf}</td>
                <td style="padding: 10px;">${statusText}</td>
                <td style="padding: 10px; text-align: center;">
                    <input type="checkbox" class="multicast-participation-check" value="${inf}" style="transform: scale(1.2); cursor: pointer;" checked>
                </td>
            </tr>
        `;
    }).join('');
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

window.toggleNatFields = function () {
    const natType = document.getElementById("nat-type")?.value;
    const interfacesGroup = document.getElementById("nat-interfaces-group");
    const staticGroup = document.getElementById("nat-static-group");

    if (!interfacesGroup || !staticGroup) return;

    if (natType === "None") {
        interfacesGroup.classList.add("hidden");
        staticGroup.classList.add("hidden");
    } else if (natType === "PAT") {
        interfacesGroup.classList.remove("hidden");
        staticGroup.classList.add("hidden");
    } else if (natType === "Static") {
        interfacesGroup.classList.remove("hidden");
        staticGroup.classList.remove("hidden");
    }
};

window.toggleSnmpFields = function () {
    const snmpEnabled = document.getElementById("snmp-enabled")?.checked;
    const snmpFields = document.getElementById("snmp-fields-group");

    if (snmpFields) {
        if (snmpEnabled) {
            snmpFields.classList.remove("hidden");
        } else {
            snmpFields.classList.add("hidden");
        }
    }
};

window.toggleSshFields = function () {
    const sshEnabled = document.getElementById("enable_ssh")?.checked;
    const sshFields = document.getElementById("ssh-fields-group");

    if (sshFields) {
        if (sshEnabled) {
            sshFields.classList.remove("hidden");
        } else {
            sshFields.classList.add("hidden");
        }
    }
    validateStep1();
};

window.toggleTelephonyFields = function () {
    const telephonyEnabled = document.getElementById("telephony-checkbox")?.checked;
    const telephonyFields = document.getElementById("telephony-options");

    if (telephonyFields) {
        if (telephonyEnabled) {
            telephonyFields.classList.remove("hidden");
        } else {
            telephonyFields.classList.add("hidden");
        }
    }
};

window.validateStep1 = function () {
    // Show inline validation errors. Does NOT block navigation.
    const nextBtn = document.getElementById('next-btn');
    if (!nextBtn) return;

    // Check enable_secret
    const enableSecret = document.getElementById('enable_secret');
    const confirmEnableSecret = document.getElementById('confirm_enable_secret');
    const consolePassword = document.getElementById('console_password');
    const confirmConsolePassword = document.getElementById('confirm_console_password');

    if (enableSecret && confirmEnableSecret) {
        const mismatch = enableSecret.value && confirmEnableSecret.value && enableSecret.value !== confirmEnableSecret.value;
        confirmEnableSecret.classList.toggle('input-error', !!mismatch);
    }

    if (consolePassword && confirmConsolePassword) {
        const mismatch = consolePassword.value && confirmConsolePassword.value && consolePassword.value !== confirmConsolePassword.value;
        confirmConsolePassword.classList.toggle('input-error', !!mismatch);
    }

    // Check SSH fields if enabled
    const sshEnabled = document.getElementById("enable_ssh")?.checked;
    if (sshEnabled) {
        const adminPassword = document.getElementById('admin_password');
        const confirmAdminPassword = document.getElementById('confirm_admin_password');
        if (adminPassword && confirmAdminPassword) {
            const mismatch = adminPassword.value && confirmAdminPassword.value && adminPassword.value !== confirmAdminPassword.value;
            confirmAdminPassword.classList.toggle('input-error', !!mismatch);
        }
    }
};


window.autoFillForm = function () {
    initDefaultInterfaces();

    document.getElementById("hostname").value = "Branch-R1";
    document.getElementById("enable_secret").value = "Cisco123!";
    document.getElementById("confirm_enable_secret").value = "Cisco123!";
    document.getElementById("console_password").value = "Console123!";
    document.getElementById("confirm_console_password").value = "Console123!";
    document.getElementById("password_encryption_type").value = "5";
    updateEncryptionSecurityBadge();
    document.getElementById("enable_ssh").checked = true;
    document.getElementById("admin_username").value = "admin";
    document.getElementById("admin_password").value = "Admin123!";
    document.getElementById("confirm_admin_password").value = "Admin123!";
    document.getElementById("domain_name").value = "local.lab";

    const ospfRadio = document.querySelector('input[name="routing-protocol"][value="OSPF"]');
    if (ospfRadio) {
        ospfRadio.checked = true;
        const ospfOptions = document.getElementById("ospf-options");
        if (ospfOptions) ospfOptions.classList.remove("hidden");
    }
    
    // Auto-fill test static route
    const staticBody = document.getElementById("static-routes-list");
    if (staticBody) {
        staticBody.innerHTML = `
            <tr style="border-bottom: 1px solid #ddd;" data-dest="0.0.0.0" data-mask="0.0.0.0" data-next-hop="192.168.1.254" data-intf="">
                <td style="padding: 10px; font-size: 0.85rem;">0.0.0.0</td>
                <td style="padding: 10px; font-size: 0.85rem;">0.0.0.0</td>
                <td style="padding: 10px; font-size: 0.85rem;">192.168.1.254</td>
                <td style="padding: 10px; font-size: 0.85rem;">-</td>
                <td style="padding: 10px; text-align: center;">
                    <button type="button" class="btn-remove" onclick="removeStaticRoute(this)" style="position: static;" title="Remove route">&times;</button>
                </td>
            </tr>
        `;
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
    document.getElementById("nat-type").value = "PAT";
    document.getElementById("nat-inside").value = "GigabitEthernet0/0";
    document.getElementById("nat-outside").value = "GigabitEthernet0/1";
    document.getElementById("nat-inside-local").value = "192.168.10.50";
    document.getElementById("nat-inside-global").value = "203.0.113.10";

    document.getElementById("snmp-enabled").checked = true;
    document.getElementById("snmp-community-ro").value = "publicRC";
    document.getElementById("snmp-community-rw").value = "privateRW";
    document.getElementById("snmp-location").value = "Headquarters Data Center";
    document.getElementById("snmp-contact").value = "admin@cisco-lab.com";
    document.getElementById("snmp-trap-host").value = "10.0.0.100";

    toggleNatFields();
    toggleSnmpFields();
    toggleSshFields();
    toggleMulticastFields();
    toggleTelephonyFields();

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
    toggleNatFields();
    toggleSnmpFields();
    toggleSshFields();
    toggleMulticastFields();
    toggleTelephonyFields();

    // Add real-time validation listeners for Step 1
    // Using event delegation on #step-1 to catch dynamically shown SSH fields too
    const step1Container = document.getElementById('step-1');
    if (step1Container) {
        step1Container.addEventListener('input', validateStep1);
        step1Container.addEventListener('change', validateStep1);
    }

    // Password toggle logic — works with SVG button
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', function () {
            const wrapper = this.closest('.password-input-wrapper');
            const input = wrapper?.querySelector('input');
            const eyeOpen = this.querySelector('.eye-open');
            const eyeClosed = this.querySelector('.eye-closed');
            if (!input) return;
            if (input.type === 'password') {
                input.type = 'text';
                if (eyeOpen) eyeOpen.style.display = 'none';
                if (eyeClosed) eyeClosed.style.display = '';
            } else {
                input.type = 'password';
                if (eyeOpen) eyeOpen.style.display = '';
                if (eyeClosed) eyeClosed.style.display = 'none';
            }
        });
    });

    // Initial validation
    validateStep1();
});
