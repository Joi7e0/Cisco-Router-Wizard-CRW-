# backend/protocols.py
# Генерація конфігурації протоколів маршрутизації

def _mask_to_wildcard(mask: str) -> str:
    try:
        if not mask or not isinstance(mask, str):
            return "0.0.0.255"
        mask = mask.strip()
        
        # Якщо це префікс (н-д, 24)
        if mask.isdigit() or (mask.startswith('/') and mask[1:].isdigit()):
            cidr_str = mask[1:] if mask.startswith('/') else mask
            cidr = int(cidr_str)
            if 0 <= cidr <= 32:
                host_bits = (1 << (32 - cidr)) - 1
                return f"{(host_bits >> 24) & 0xFF}.{(host_bits >> 16) & 0xFF}.{(host_bits >> 8) & 0xFF}.{host_bits & 0xFF}"
        
        # Якщо це повноцінна маска (н-д, 255.255.255.0)
        parts = mask.split('.')
        if len(parts) == 4:
            return ".".join(str(255 - int(p)) for p in parts)
            
        return "0.0.0.255"
    except Exception:
        return "0.0.0.255"

def _cidr_to_mask(cidr: int) -> str:
    try:
        if not (0 <= cidr <= 32):
            return "255.255.255.0"
        mask_bits = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
        return f"{(mask_bits >> 24) & 0xFF}.{(mask_bits >> 16) & 0xFF}.{(mask_bits >> 8) & 0xFF}.{mask_bits & 0xFF}"
    except Exception:
        return "255.255.255.0"

def generate_protocol_config(
    protocol: str,
    router_id: str,
    networks: list,
    no_auto_summary: bool = True,
    routing_config: dict = None
) -> list[str]:
    """
    Генерує команди для протоколів маршрутизації
    """
    if not protocol or protocol.upper() == "NONE":
        return []

    proto = protocol.upper().strip()
    cfg = []
    rc = routing_config or {}

    if proto == "STATIC":
        routes = rc.get("staticRoutes", [])
        if routes:
            cfg.append("!")
            for r in routes:
                dest = r.get("dest")
                mask = r.get("mask", "")
                next_hop = r.get("nextHop", "")
                intf = r.get("interface", "")
                ad = r.get("ad", "")
                metric = r.get("metric", "")
                
                # Convert prefix to mask if needed
                if mask.isdigit() or mask.startswith('/'):
                    m_val = mask[1:] if mask.startswith('/') else mask
                    mask_final = _cidr_to_mask(int(m_val))
                else:
                    mask_final = mask or "255.255.255.0"
                
                cmd = f"ip route {dest} {mask_final}"
                if next_hop: cmd += f" {next_hop}"
                if intf: cmd += f" {intf}"
                if ad: cmd += f" {ad}"
                if metric: cmd += f" {metric}" # Metric in static is usually AD but keeping it
                cfg.append(cmd)

    elif proto == "RIP":
        cfg.append("!")
        cfg.append("router rip")
        cfg.append(" version 2")
        for item in networks:
            net_ip = item[0] if isinstance(item, (list, tuple)) else item
            if net_ip and net_ip != "invalid":
                cfg.append(f"  network {net_ip}")
        if rc.get("noAutoSummary", no_auto_summary):
            cfg.append("  no auto-summary")
        cfg.append(" exit")

    elif proto == "OSPF":
        pid = rc.get("processId", "1")
        area = rc.get("area", "0")
        rid = rc.get("routerId") or router_id
        
        cfg.append("!")
        cfg.append(f"router ospf {pid}")
        if rid:
            cfg.append(f"  router-id {rid}")
            
        # OSPF Networks are now handled differently or removed from UI but keeping for backend consistency
        for item in networks:
            net_ip = item[0] if isinstance(item, (list, tuple)) else item
            net_mask = item[1] if isinstance(item, (list, tuple)) and len(item) > 1 else "24"
            if net_ip and net_ip != "invalid":
                wildcard = _mask_to_wildcard(net_mask)
                cfg.append(f"  network {net_ip} {wildcard} area {area}")
        cfg.append(" exit")

    elif proto == "EIGRP":
        asn = rc.get("asNumber", "100")
        no_auto = rc.get("noAutoSummary", True)
        
        cfg.append("!")
        cfg.append(f"router eigrp {asn}")
        for item in networks:
            net_ip = item[0] if isinstance(item, (list, tuple)) else item
            if net_ip and net_ip != "invalid":
                cfg.append(f"  network {net_ip}")
        if no_auto:
            cfg.append("  no auto-summary")
        cfg.append(" exit")

    elif proto == "BGP":
        local_as = rc.get("localAs", "65001")
        rid = rc.get("routerId") or router_id
        neighbor = rc.get("neighborIp")
        remote_as = rc.get("remoteAs")
        
        cfg.append("!")
        cfg.append(f"router bgp {local_as}")
        if rid:
            cfg.append(f"  bgp router-id {rid}")
        if neighbor and remote_as:
            cfg.append(f"  neighbor {neighbor} remote-as {remote_as}")
            
        for item in networks:
            net_ip = item[0] if isinstance(item, (list, tuple)) else item
            net_mask = item[1] if isinstance(item, (list, tuple)) and len(item) > 1 else "24"
            if net_ip and net_ip != "invalid":
                if net_mask.isdigit():
                    mask = _cidr_to_mask(int(net_mask))
                    cfg.append(f"  network {net_ip} mask {mask}")
                else:
                    cfg.append(f"  network {net_ip} mask {net_mask}")
        cfg.append(" exit")

    elif proto == "IS-IS":
        area_id = rc.get("areaId", "49.0001")
        system_id = rc.get("systemId", "0000.0000.0001")
        r_type = rc.get("routerType", "level-1-2")
        
        cfg.append("!")
        cfg.append("router isis")
        cfg.append(f"  net {area_id}.{system_id}.00")
        cfg.append(f"  is-type {r_type}")
        cfg.append("  no auto-summary")
        cfg.append(" exit")

    return cfg
