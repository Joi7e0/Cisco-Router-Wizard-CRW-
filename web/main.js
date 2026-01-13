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
    document.querySelectorAll('input[placeholder="******"]')[0].value = "consolepass1";
    document.querySelectorAll('input[placeholder="******"]')[1].value = "vtypass1";

    // DHCP
    document.getElementById("dhcp-network").value = "192.168.10.0";
    document.getElementById("dhcp-mask").value = "255.255.255.0";
    document.getElementById("dhcp-gateway").value = "192.168.10.1";
    document.getElementById("dhcp-dns").value = "8.8.8.8";

    alert("Форма заповнена типовими тестовими значеннями!");
}

// Головна функція відправки в Python з розширеною клієнтською валідацією
async function sendToPython() {
    const { interfaces, networks, noShutdownList } = getInterfacesData();

    // ───────────────────────────────────────────────
    // 1. Перевірка наявності хоча б одного інтерфейсу
    // ───────────────────────────────────────────────
    if (interfaces.length === 0) {
        alert("❌ Додайте хоча б один інтерфейс!");
        return;
    }

    // Перевіряємо, що кожен інтерфейс має IP та маску
    for (let i = 0; i < interfaces.length; i++) {
        if (!interfaces[i] || !networks[i][0] || !networks[i][1]) {
            alert(`❌ Інтерфейс #${i + 1} неповний!\nВкажіть назву, IP-адресу та маску.`);
            return;
        }
    }

    // ───────────────────────────────────────────────
    // 2. Вибір протоколу та Router ID (для OSPF)
    // ───────────────────────────────────────────────
    const routingProtocol = document.querySelector('input[name="routing-protocol"]:checked')?.value || "";
    const routerId = document.getElementById("router-id").value.trim();

    if (routingProtocol === "OSPF") {
        if (!routerId) {
            alert("❌ Для OSPF обов'язково потрібно вказати Router ID!");
            document.getElementById("router-id").focus();
            return;
        }

        // Простий regex для IPv4
        const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        if (!ipv4Regex.test(routerId)) {
            alert("❌ Некоректний формат Router ID!\nОчікується валідна IPv4-адреса (наприклад: 1.1.1.1)");
            document.getElementById("router-id").focus();
            return;
        }

        if (routerId === "0.0.0.0") {
            alert("❌ Router ID не може бути 0.0.0.0!");
            document.getElementById("router-id").focus();
            return;
        }
    }

    // ───────────────────────────────────────────────
    // 3. Перевірка паролів (якщо заповнені)
    // ───────────────────────────────────────────────
    const hostname = document.querySelector('input[placeholder="Router"]').value.trim();
    const enableSecret = document.querySelector('input[placeholder="type"]').value.trim();
    const consolePass = document.querySelectorAll('input[placeholder="******"]')[0]?.value.trim() || "";
    const vtyPass = document.querySelectorAll('input[placeholder="******"]')[1]?.value.trim() || "";

    const passwordFields = [
        { value: enableSecret, name: "Enable secret" },
        { value: consolePass, name: "Console password" },
        { value: vtyPass, name: "VTY password" }
    ];

    for (const field of passwordFields) {
        if (field.value && field.value.length > 0) {
            if (field.value.length < 8) {
                alert(`❌ ${field.name} занадто короткий!\nМінімум 8 символів.`);
                return;
            }
            if (!/[A-Za-z]/.test(field.value) || !/\d/.test(field.value)) {
                alert(`❌ ${field.name} повинен містити хоча б одну літеру та одну цифру!`);
                return;
            }
        }
    }

    // ───────────────────────────────────────────────
    // 4. Базова перевірка DHCP (якщо заповнено)
    // ───────────────────────────────────────────────
    const dhcpNetwork = document.getElementById("dhcp-network").value.trim();
    const dhcpMask = document.getElementById("dhcp-mask").value.trim();
    const dhcpGateway = document.getElementById("dhcp-gateway").value.trim();

    if (dhcpNetwork && dhcpMask) {
        const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

        if (!ipv4Regex.test(dhcpNetwork)) {
            alert("❌ Некоректний формат DHCP Network!");
            document.getElementById("dhcp-network").focus();
            return;
        }

        if (!ipv4Regex.test(dhcpMask)) {
            alert("❌ Некоректний формат DHCP Subnet Mask!");
            document.getElementById("dhcp-mask").focus();
            return;
        }

        if (dhcpGateway && !ipv4Regex.test(dhcpGateway)) {
            alert("❌ Некоректний формат Default Gateway для DHCP!");
            document.getElementById("dhcp-gateway").focus();
            return;
        }
    }

    // ───────────────────────────────────────────────
    // Якщо всі перевірки пройдено — відправляємо на бекенд
    // ───────────────────────────────────────────────
    const telephonyEnabled = document.getElementById("telephony-checkbox").checked;
    const dnList = [
        { number: document.getElementById("dn1-number").value.trim(), user: document.getElementById("dn1-user").value.trim() },
        { number: document.getElementById("dn2-number").value.trim(), user: document.getElementById("dn2-user").value.trim() },
        { number: document.getElementById("dn3-number").value.trim(), user: document.getElementById("dn3-user").value.trim() }
    ];

    const enableSSH = document.getElementById("ssh").checked;
    const ipMulticast = document.getElementById("multicast-checkbox").checked;

    try {
        const res = await eel.process_text(
            routingProtocol,
            "",                       // proto (залишаємо для сумісності)
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
            document.getElementById("dhcp-dns").value.trim(),
            interfaces,
            networks,
            noShutdownList,
            3,                        // max_ephones
            3,                        // max_dn
            "10.0.0.1",              // ip source-address telephony
            "1 to 3",                // auto assign range
            ["10.0.0.1", "10.0.0.10"] // dhcp excluded
        )();

        const responseDiv = document.getElementById("response");
        responseDiv.innerText = res;
        responseDiv.style.color = res.startsWith("❌") ? "#ff6b6b" : "#00ffcc";
    } catch (err) {
        console.error("Помилка генерації:", err);
        document.getElementById("response").innerText = 
            "❌ Критична помилка при генерації конфігурації\n" + err.message;
        document.getElementById("response").style.color = "#ff6b6b";
    }
}

// Ініціалізація при завантаженні сторінки
document.addEventListener("DOMContentLoaded", () => {
    initDefaultInterfaces();
    updateAddButtonState();
});
