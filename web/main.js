// main.js

const MAX_INTERFACES = 3;
let interfaceCounter = 0;

// Створення одного блоку інтерфейсу
function createInterfaceField(name = "", ip = "", mask = "", noShutdown = false, index = interfaceCounter) {
    const container = document.createElement("div");
    container.className = "interface-field";
    container.dataset.index = index;
    container.style.marginBottom = "20px";
    container.style.padding = "16px";
    container.style.border = "1px solid #415a77";
    container.style.borderRadius = "8px";
    container.style.background = "rgba(27, 38, 59, 0.5)";

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <strong>Інтерфейс #${index + 1}</strong>
            <button type="button" class="remove-interface-btn"
                    style="background:#e74c3c; color:white; border:none; padding:6px 12px; border-radius:6px; cursor:pointer;">
                Видалити
            </button>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <div style="flex: 1; min-width: 220px;">
                <label>Назва інтерфейсу</label><br>
                <input type="text" class="interface-name" value="${name}" placeholder="GigabitEthernet0/0">
            </div>

            <div style="flex: 1; min-width: 180px;">
                <label>IP-адреса</label><br>
                <input type="text" class="interface-ip" value="${ip}" placeholder="192.168.1.1">
            </div>

            <div style="flex: 1; min-width: 180px;">
                <label>Маска підмережі</label><br>
                <input type="text" class="interface-mask" value="${mask}" placeholder="255.255.255.0">
            </div>
        </div>

        <div style="margin-top: 12px;">
            <label style="user-select: none; cursor: pointer;">
                <input type="checkbox" class="interface-no-shutdown" ${noShutdown ? 'checked' : ''}>
                no shutdown (увімкнути інтерфейс)
            </label>
        </div>
    `;

    // Обробник видалення
    container.querySelector(".remove-interface-btn").addEventListener("click", () => {
        container.remove();
        updateAddButtonState();
    });

    return container;
}

// Додавання нового інтерфейсу з перевіркою ліміту
function addInterfaceField(name = "", ip = "", mask = "", noShutdown = false) {
    const currentCount = document.querySelectorAll(".interface-field").length;
    
    if (currentCount >= MAX_INTERFACES) {
        alert(`На цій моделі роутера максимум ${MAX_INTERFACES} інтерфейси!`);
        return;
    }

    const list = document.getElementById("interfaces-list");
    const field = createInterfaceField(name, ip, mask, noShutdown, interfaceCounter);
    list.appendChild(field);
    interfaceCounter++;

    updateAddButtonState();
}

// Оновлення стану кнопки "Додати інтерфейс"
function updateAddButtonState() {
    const addBtn = document.querySelector("#interfaces-container button");
    if (!addBtn) return;

    const currentCount = document.querySelectorAll(".interface-field").length;

    if (currentCount >= MAX_INTERFACES) {
        addBtn.disabled = true;
        addBtn.textContent = `Максимум ${MAX_INTERFACES} інтерфейси`;
        addBtn.style.opacity = "0.6";
        addBtn.style.cursor = "not-allowed";
    } else {
        addBtn.disabled = false;
        addBtn.textContent = "+ Додати інтерфейс";
        addBtn.style.opacity = "1";
        addBtn.style.cursor = "pointer";
    }
}

// Ініціалізація дефолтних 3 інтерфейсів
function initDefaultInterfaces() {
    interfaceCounter = 0;
    document.getElementById("interfaces-list").innerHTML = "";

    addInterfaceField("GigabitEthernet0/0", "192.168.1.1",   "255.255.255.0", true);
    addInterfaceField("GigabitEthernet0/1", "172.16.0.1",    "255.255.0.0",   false);
    addInterfaceField("GigabitEthernet0/2", "10.0.0.1",      "255.255.255.252", true);

    updateAddButtonState();
}

// Збір усіх даних інтерфейсів
function getInterfacesData() {
    const fields = document.querySelectorAll(".interface-field");
    const interfaces = [];
    const networks = [];
    const noShutdownList = [];

    fields.forEach(field => {
        const name = field.querySelector(".interface-name").value.trim();
        const ip = field.querySelector(".interface-ip").value.trim();
        const mask = field.querySelector(".interface-mask").value.trim();
        const noShutdown = field.querySelector(".interface-no-shutdown").checked;

        // Додаємо, якщо є назва та хоча б один з IP/маски
        if (name && (ip || mask)) {
            interfaces.push(name);
            // Якщо чогось бракує — підставляємо типові значення
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

// Показ/приховування поля Router ID для OSPF
document.querySelectorAll('input[name="routing-protocol"]').forEach(radio => {
    radio.addEventListener('change', () => {
        const ospfOptions = document.getElementById("ospf-options");
        ospfOptions.classList.toggle("hidden", radio.value !== "OSPF");
    });
});

// Автозаповнення всієї форми
function autoFillForm() {
    initDefaultInterfaces();

    // Routing Protocol - OSPF за замовчуванням
    document.querySelector('input[value="OSPF"]').checked = true;
    document.getElementById("ospf-options").classList.remove("hidden");
    document.getElementById("router-id").value = "1.1.1.1";

    // Multicast
    document.getElementById("multicast-checkbox").checked = true;

    // Telephony
    document.getElementById("telephony-checkbox").checked = true;
    document.getElementById("dn1-number").value = "1001";
    document.getElementById("dn1-user").value = "user1";
    document.getElementById("dn2-number").value = "1002";
    document.getElementById("dn2-user").value = "user2";
    document.getElementById("dn3-number").value = "1003";
    document.getElementById("dn3-user").value = "user3";

    // Security
    document.getElementById("ssh").checked = true;
    document.querySelector('input[placeholder="Router"]').value = "MyRouter";
    document.querySelector('input[placeholder="type"]').value = "cisco123";
    document.querySelectorAll('input[placeholder="******"]')[0].value = "consolepass";
    document.querySelectorAll('input[placeholder="******"]')[1].value = "vtypass";

    // DHCP
    document.getElementById("dhcp-network").value = "192.168.10.0";
    document.getElementById("dhcp-mask").value = "255.255.255.0";
    document.getElementById("dhcp-gateway").value = "192.168.10.1";
    document.getElementById("dhcp-dns").value = "8.8.8.8";

    alert("Форма заповнена типовими тестовими значеннями!");
}

// Головна функція відправки в Python
async function sendToPython() {
    const { interfaces, networks, noShutdownList } = getInterfacesData();

    if (interfaces.length === 0) {
        alert("Додайте хоча б один інтерфейс з назвою та IP/маскою!");
        return;
    }

    const routingProtocol = document.querySelector('input[name="routing-protocol"]:checked')?.value || "";
    const routerId = document.getElementById("router-id").value.trim();
    const ipMulticast = document.getElementById("multicast-checkbox").checked;

    const telephonyEnabled = document.getElementById("telephony-checkbox").checked;
    const dnList = [
        { number: document.getElementById("dn1-number").value.trim(), user: document.getElementById("dn1-user").value.trim() },
        { number: document.getElementById("dn2-number").value.trim(), user: document.getElementById("dn2-user").value.trim() },
        { number: document.getElementById("dn3-number").value.trim(), user: document.getElementById("dn3-user").value.trim() }
    ];

    const enableSSH = document.getElementById("ssh").checked;
    const hostname = document.querySelector('input[placeholder="Router"]').value.trim();
    const enableSecret = document.querySelector('input[placeholder="type"]').value.trim();
    const consolePassword = document.querySelectorAll('input[placeholder="******"]')[0].value.trim();
    const vtyPassword = document.querySelectorAll('input[placeholder="******"]')[1].value.trim();

    const dhcpNetwork = document.getElementById("dhcp-network").value.trim();
    const dhcpMask = document.getElementById("dhcp-mask").value.trim();
    const dhcpGateway = document.getElementById("dhcp-gateway").value.trim();
    const dhcpDns = document.getElementById("dhcp-dns").value.trim();

    try {
        const res = await eel.process_text(
            routingProtocol,            // routing_protocol
            "",                       // proto (left empty)
            routerId,                  // router_id
            ipMulticast,               // ip_multicast
            telephonyEnabled,          // telephony_enabled
            dnList,                    // dn_list
            enableSSH,                 // enable_ssh
            hostname,                  // hostname
            enableSecret,              // enable_secret
            consolePassword,           // console_password
            vtyPassword,               // vty_password
            dhcpNetwork,               // dhcp_network
            dhcpMask,                  // dhcp_mask
            dhcpGateway,               // dhcp_gateway
            dhcpDns,                   // dhcp_dns
            interfaces,                // interfaces
            networks,                  // networks
            noShutdownList,            // no_shutdown_interfaces
            3,                         // max_ephones
            3,                         // max_dn
            "10.0.0.1",              // ip source-address telephony
            "1 to 3",                // auto assign range
            ["10.0.0.1", "10.0.0.10"]  // dhcp excluded
        )();

        const responseDiv = document.getElementById("response");
        responseDiv.innerText = res;
        responseDiv.style.color = res.startsWith("❌") ? "#ff6b6b" : "#00ffcc";
    } catch (err) {
        console.error("Помилка:", err);
        document.getElementById("response").innerText = 
            "❌ Виникла помилка при генерації конфігурації\n" + err.message;
        document.getElementById("response").style.color = "#ff6b6b";
    }
}

// Ініціалізація при завантаженні сторінки
document.addEventListener("DOMContentLoaded", () => {
    initDefaultInterfaces();
    updateAddButtonState();
});