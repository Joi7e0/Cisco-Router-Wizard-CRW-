def _mask_to_wildcard(mask: str) -> str:
    """Convert subnet mask like '255.255.255.252' to wildcard '0.0.0.3'."""
    parts = mask.split('.')
    wildcard_parts = [str(255 - int(p)) for p in parts]
    return '.'.join(wildcard_parts)


def generate_protocol_config(protocol: str, router_id: str, networks: list[tuple[str, str]]) -> list[str]:
    """Генерація конфігурації для протоколу маршрутизації."""
    proto = protocol.upper().strip()
    cfg = []

    if proto == "OSPF":
        cfg.append("!")
        cfg.append("router ospf 1")
        cfg.append(f" router-id {router_id}")
        for net_ip, net_mask in networks:
            wildcard = _mask_to_wildcard(net_mask)
            cfg.append(f" network {net_ip} {wildcard} area 0")
        cfg.append(" exit")
    elif proto == "RIP":
        cfg.append("!")
        cfg.append("router rip")
        cfg.append(" version 2")
        for net_ip, _ in networks:
            cfg.append(f" network {net_ip}")
        cfg.append(" no auto-summary")
        cfg.append(" exit")
    elif proto == "EIGRP":
        cfg.append("!")
        cfg.append("router eigrp 100")
        for net_ip, _ in networks:
            cfg.append(f" network {net_ip}")
        cfg.append(" no auto-summary")
        cfg.append(" exit")
    elif proto == "BGP":
        cfg.append("!")
        cfg.append("router bgp 65000")
        cfg.append(" bgp log-neighbor-changes")
        cfg.append(" neighbor 1.1.1.2 remote-as 65001")
        cfg.append(" exit")
    elif proto == "IS-IS":
        cfg.append("!")
        cfg.append("router isis")
        cfg.append(" net 49.0001.0000.0000.0001.00")
        cfg.append(" is-type level-2-only")
        cfg.append(" exit")
    else:
        cfg.append("! No routing protocol selected")
    
    return cfg