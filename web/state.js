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

    const pimInterfaces = Array.from(document.querySelectorAll(".multicast-participation-check:checked")).map(el => el.value);

    // Collect Routing Configuration
    const routingProtocol = document.querySelector('input[name="routing-protocol"]:checked')?.value || "None";
    const routingConfig = {
        protocol: routingProtocol,
        networks: networks,
        staticRoutes: [],
        routerId: document.getElementById("router-id")?.value.trim() ||
            document.getElementById("bgp-router-id")?.value.trim() || "",
        ripNoAuto: document.getElementById("rip-no-auto")?.checked || false,
        asNumber: document.getElementById("eigrp-as")?.value.trim() || "100",
        eigrpNoAuto: document.getElementById("eigrp-no-auto")?.checked || false,
        processId: document.getElementById("ospf-process-id")?.value.trim() || "1",
        localAs: document.getElementById("bgp-local-as")?.value.trim() || "65000",
        isisAreaId: document.getElementById("isis-area-id")?.value.trim() || "49.0001",
        isisSystemId: document.getElementById("isis-system-id")?.value.trim() || "0000.0000.0001.00",
        isisRouterType: document.getElementById("isis-type")?.value || "level-1-2",
        participatingInterfaces: Array.from(document.querySelectorAll(".isis-participation-check:checked")).map(el => el.value)
    };

    // Collect Static Routes list
    const staticRows = document.querySelectorAll("#static-routes-list tr");
    Array.from(staticRows).forEach(tr => {
        routingConfig.staticRoutes.push({
            dest: tr.dataset.dest,
            mask: tr.dataset.mask,
            nextHop: tr.dataset.nextHop || "",
            interface: tr.dataset.intf || ""
        });
    });

    // Collect RIP Networks list
    const ripNetworks = [];
    const ripRows = document.querySelectorAll("#rip-networks-list tr");
    Array.from(ripRows).forEach(tr => {
        if (tr.dataset.network) {
            ripNetworks.push(tr.dataset.network);
        }
    });
    routingConfig.ripNetworks = ripNetworks;

    // Collect OSPF Networks list (with per-network area)
    const ospfNetworksData = [];
    const ospfRows = document.querySelectorAll("#ospf-networks-list tr");
    Array.from(ospfRows).forEach(tr => {
        if (tr.dataset.network) {
            ospfNetworksData.push({
                network: tr.dataset.network,
                wildcard: tr.dataset.wildcard || "0.0.0.255",
                area: tr.dataset.area || "0"
            });
        }
    });
    routingConfig.ospfNetworks = ospfNetworksData;

    // Collect EIGRP Networks list (with wildcard mask)
    const eigrpNetworksData = [];
    const eigrpRows = document.querySelectorAll("#eigrp-networks-list tr");
    Array.from(eigrpRows).forEach(tr => {
        if (tr.dataset.network) {
            eigrpNetworksData.push({
                network: tr.dataset.network,
                wildcard: tr.dataset.wildcard || ""
            });
        }
    });
    routingConfig.eigrpNetworks = eigrpNetworksData;

    // Collect BGP Neighbors list
    const bgpNeighbors = [];
    const bgpNeighborRows = document.querySelectorAll("#bgp-neighbors-list tr");
    Array.from(bgpNeighborRows).forEach(tr => {
        if (tr.dataset.neighborIp) {
            bgpNeighbors.push({
                ip: tr.dataset.neighborIp,
                remoteAs: tr.dataset.remoteAs || ""
            });
        }
    });
    routingConfig.bgpNeighbors = bgpNeighbors;

    // Collect BGP Advertised Networks
    const bgpAdvertisedNetworks = [];
    const bgpNetRows = document.querySelectorAll("#bgp-networks-list tr");
    Array.from(bgpNetRows).forEach(tr => {
        if (tr.dataset.network) {
            bgpAdvertisedNetworks.push({
                network: tr.dataset.network,
                mask: tr.dataset.mask || ""
            });
        }
    });
    routingConfig.bgpAdvertisedNetworks = bgpAdvertisedNetworks;

    const dnListRaw = [
        { number: document.getElementById("dn1-number")?.value.trim(), user: document.getElementById("dn1-user")?.value.trim(), mac: document.getElementById("dn1-mac")?.value.trim() },
        { number: document.getElementById("dn2-number")?.value.trim(), user: document.getElementById("dn2-user")?.value.trim(), mac: document.getElementById("dn2-mac")?.value.trim() },
        { number: document.getElementById("dn3-number")?.value.trim(), user: document.getElementById("dn3-user")?.value.trim(), mac: document.getElementById("dn3-mac")?.value.trim() }
    ];
    const dnList = dnListRaw.filter(dn => dn.number || dn.user);

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
        adminUsername: document.getElementById("admin_username")?.value.trim() || "admin",
        adminPassword: document.getElementById("admin_password")?.value.trim() || "",
        domainName: document.getElementById("domain_name")?.value.trim() || "local.lab",
        dhcpNetwork: document.getElementById("dhcp-network")?.value.trim() || "",
        dhcpMask: document.getElementById("dhcp-mask")?.value.trim() || "",
        dhcpGateway: document.getElementById("dhcp-gateway")?.value.trim() || "",
        dhcpDns: document.getElementById("dhcp-dns")?.value.trim() || "",
        dhcpExcludedFrom: document.getElementById("dhcp-excluded-from")?.value.trim() || "",
        dhcpExcludedTo: document.getElementById("dhcp-excluded-to")?.value.trim() || "",
        dhcpOption150: document.getElementById("dhcp-option150")?.value.trim() || "",
        cmeSourceIp: document.getElementById("cme-source-ip")?.value.trim() || "",
        interfaces: interfaces,
        networks: networks,
        noShutdownInterfaces: noShutdownList,
        pimInterfaces: pimInterfaces,
        descriptions: descriptions,
        maxEphones: 3,
        maxDn: 3,
        autoAssignRange: "1 to 3",
        routingConfig: routingConfig,
        natType: document.getElementById("nat-type")?.value || "None",
        natInside: document.getElementById("nat-inside")?.value.trim() || "",
        natOutside: document.getElementById("nat-outside")?.value.trim() || "",
        natInsideLocal: document.getElementById("nat-inside-local")?.value.trim() || "",
        natInsideGlobal: document.getElementById("nat-inside-global")?.value.trim() || "",
        snmpEnabled: document.getElementById("snmp-enabled")?.checked || false,
        snmpCommunityRo: document.getElementById("snmp-community-ro")?.value.trim() || "",
        snmpCommunityRw: document.getElementById("snmp-community-rw")?.value.trim() || "",
        snmpLocation: document.getElementById("snmp-location")?.value.trim() || "",
        snmpContact: document.getElementById("snmp-contact")?.value.trim() || "",
        snmpTrapHost: document.getElementById("snmp-trap-host")?.value.trim() || ""
    };

    return configData;
}

window.crw_state = {
    getInterfacesData,
    buildConfigData
};
