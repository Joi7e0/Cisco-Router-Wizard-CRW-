// state.js

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

function buildConfigData() {
    const { interfaces, networks, descriptions, noShutdownList } = getInterfacesData();

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

    const dnList = [
        { number: document.getElementById("dn1-number")?.value.trim(), user: document.getElementById("dn1-user")?.value.trim() },
        { number: document.getElementById("dn2-number")?.value.trim(), user: document.getElementById("dn2-user")?.value.trim() },
        { number: document.getElementById("dn3-number")?.value.trim(), user: document.getElementById("dn3-user")?.value.trim() }
    ];

    const configData = {
        routingProtocol: routingProtocol,
        routerId: routingConfig.routerId,
        ipMulticast: document.getElementById("multicast-checkbox")?.checked || false,
        telephonyEnabled: document.getElementById("telephony-checkbox")?.checked || false,
        dnList: dnList,
        enableSsh: document.getElementById("enable_ssh")?.checked || false,
        hostname: document.getElementById("hostname")?.value.trim() || "",
        enableSecret: document.getElementById("enable_secret")?.value.trim() || "",
        consolePassword: document.getElementById("console_password")?.value.trim() || "",
        vtyPassword: document.getElementById("vty_password")?.value.trim() || "",
        passwordEncryptionType: document.getElementById("password_encryption_type")?.value || "5",
        dhcpNetwork: document.getElementById("dhcp-network")?.value.trim() || "",
        dhcpMask: document.getElementById("dhcp-mask")?.value.trim() || "",
        dhcpGateway: document.getElementById("dhcp-gateway")?.value.trim() || "",
        dhcpDns: document.getElementById("dhcp-dns")?.value.trim() || "",
        interfaces: interfaces,
        networks: networks,
        noShutdownInterfaces: noShutdownList,
        descriptions: descriptions,
        maxEphones: 3,
        maxDn: 3,
        ipSourceAddress: "10.0.0.1",
        autoAssignRange: "1 to 3",
        dhcpExcluded: ["10.0.0.1", "10.0.0.10"],
        routingConfig: routingConfig
    };

    return configData;
}

window.crw_state = {
    getInterfacesData,
    buildConfigData
};
