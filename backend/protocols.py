import os
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

def render_template_to_lines(template_name, context):
    # Відрендерить Jinja2-шаблон і повертає непорожні рядки.
    #
    # Універсальна допоміжня функція для всіх генераторів. Автоматично
    # видаляє порожні рядки (інденти, порожні рядки Jinja2).
    #
    # Args:
    #     template_name (str): Назва шаблону.
    #     context (dict): Дані для шаблону.
    #
    # Returns:
    #     list[str]: Список очищених рядків.
    template = env.get_template(template_name)

    rendered = template.render(**context)
    return [line for line in rendered.splitlines() if line.strip()]

def _mask_to_wildcard(mask: str) -> str:
    # Конвертує subnet mask або CIDR-префікс в wildcard mask.
    #
    # Приймає dotted-decimal (наприклад, "255.255.255.0"),
    # CIDR без префіксу ("24") або з префіксом ("/24").
    # Використовується для Jinja2 шаблонів OSPF, EIGRP, NAT.
    #
    # Args:
    #     mask (str): Subnet mask або CIDR-префікс.
    #
    # Returns:
    #     str: Wildcard mask у dotted-decimal форматі.

    try:
        if not mask or not isinstance(mask, str):
            return "0.0.0.0"
        mask = mask.strip()
        
        # ЛОГІКА CIDR: Якщо передано число (наприклад 24 або /22)
        # 1. Визначаємо кількість хостових бітів: 32 - префікс
        # 2. Створюємо бітову маску хостової частини: (1 << host_bits) - 1
        # 3. Розбиваємо 32-бітне число на 4 октети
        if mask.isdigit() or (mask.startswith('/') and mask[1:].isdigit()):
            cidr_str = mask[1:] if mask.startswith('/') else mask
            cidr = int(cidr_str)
            if 0 <= cidr <= 32:
                host_bits = (1 << (32 - cidr)) - 1
                return f"{(host_bits >> 24) & 0xFF}.{(host_bits >> 16) & 0xFF}.{(host_bits >> 8) & 0xFF}.{host_bits & 0xFF}"
        
        # ЛОГІКА MASK: Якщо передано 255.255.255.0
        # 1. Розбиваємо на октети
        # 2. Для кожного октета: wildcard = 255 - mask_octet
        parts = mask.split('.')
        if len(parts) == 4:
            try:
                vals = [int(p) for p in parts]
                if all(0 <= v <= 255 for v in vals):
                    return ".".join(str(255 - v) for v in vals)
            except ValueError:
                pass
            
        return "0.0.0.0"
    except Exception:
        return "0.0.0.0"

def _cidr_to_mask(cidr: int) -> str:
    # Перетворює CIDR-префікс (ціле число) в dotted-decimal subnet mask.
    #
    # Args:
    #     cidr (int): Префікс в діапазоні 0–32.
    #
    # Returns:
    #     str: Subnet mask у dotted-decimal форматі.

    try:
        if not (0 <= cidr <= 32):
            return "255.255.255.0"
        # 1. Беремо 0xFFFFFFFF (всі одиниці)
        # 2. Зсуваємо вліво на (32 - cidr) нулів
        # 3. Накладаємо маску 0xFFFFFFFF для коректної роботи зі знаковими числами
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
    # Генерує Cisco IOS команди для заданого протоколу маршрутизації.
    #
    # Підтримувані протоколи: RIP, OSPF, EIGRP, BGP, STATIC, IS-IS.
    #
    # Args:
    #     protocol (str): Назва протоколу.
    #     router_id (str): Router ID (IPv4).
    #     networks (list): Мережі для RIP.
    #     routing_config (dict): Конфігурація конкретного протоколу.
    #
    # Returns:
    #     list[str]: Список команд.

    #
    # Фабрикний метод для всіх підтримуваних протоколів. Визначає потрібний
    # Jinja2-шаблон (наприклад, ``routing/ospf.j2``) і передає ньому
    # контекст з інформацією про мережі, роутер-ID та параметрами
    # протоколу.
    #
    # Підтримувані протоколи:
    # - ``RIP`` — RIP v2 з списком мереж цластерних мереж.
    # - ``OSPF`` — single/multi-area OSPF з wildcard masks та area per-network.
    # - ``EIGRP`` — EIGRP з AS number і опціональним wildcard.
    # - ``BGP`` — BGP з списком neighbor і advertised networks.
    # - ``STATIC`` — статичні маршрути з next-hop або exit interface.
    # - ``IS-IS`` — IS-IS з NET-адресою та рівнем маршрутизації.
    #
    # Args:
    # protocol (str): Назва протоколу (регістронезалежна).
    # Допустимі значення: ``"RIP"``, ``"OSPF"``, ``"EIGRP"``,
    # ``"BGP"``, ``"STATIC"``, ``"IS-IS"``, ``"None"``.
    # router_id (str): Router ID у форматі IPv4. Обов'язковий для OSPF.
    # networks (list): Список кортежів ``(ip: str, mask: str)``.
    # Використовується для RIP. OSPF/EIGRP/BGP читають з ``routing_config``.
    # no_auto_summary (bool, optional): Додає ``no auto-summary`` для
    # RIP і EIGRP. Defaults to ``True``.
    # routing_config (dict, optional): Розширена конфігурація протоколу.
    # Ключі залежать від протоколу:
    #
    # - OSPF: ``{"processId": str, "routerId": str,``
    # ``"ospfNetworks": [{"network", "wildcard", "area"}]}``
    # - EIGRP: ``{"asNumber": str, "eigrpNetworks": [{"network", "wildcard"}]}``
    # - BGP: ``{"localAs": str, "routerId": str,``
    # ``"bgpNeighbors": [{"ip", "remoteAs"}],``
    # ``"bgpAdvertisedNetworks": [{"network", "mask"}]}``
    # - STATIC: ``{"staticRoutes": [{"dest", "mask", "nextHop",``
    # ``"interface", "ad", "metric"}]}``
    # - IS-IS: ``{"areaId": str, "systemId": str, "routerType": str}``
    #
    # Returns:
    # list[str]: Список Cisco IOS команд. Порожний список, якщо
    # ``protocol`` дорівнює ``"None"`` або порожній.
    #
    # Examples:
    # >>> generate_protocol_config("RIP", "", [("192.168.1.0", "255.255.255.0")])
    # ['!', 'router rip', ' version 2', ' network 192.168.1.0', ' no auto-summary', ' exit']
    # >>> generate_protocol_config("None", "", [])
    # []
    if not isinstance(protocol, str) or not protocol or protocol.upper() == "NONE":
        return []

    proto = protocol.upper().strip()
    rc = routing_config or {}

    context = {
        'protocol': proto,
        'no_auto_summary': rc.get("noAutoSummary", no_auto_summary)
    }

    if proto == "STATIC":
        static_routes = []
        routes = rc.get("staticRoutes", [])
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
                
            static_routes.append({
                'dest': dest,
                'mask_final': mask_final,
                'nextHop': next_hop,
                'interface': intf,
                'ad': ad,
                'metric': metric
            })
        context['static_routes'] = static_routes

    elif proto == "RIP":
        rip_networks = []
        manual_rip_networks = rc.get("ripNetworks", [])
        
        if manual_rip_networks:
            for net in manual_rip_networks:
                if net and net != "invalid":
                    rip_networks.append(net)
        else:
            for item in networks:
                net_ip = item[0] if isinstance(item, (list, tuple)) else item
                if net_ip and net_ip != "invalid":
                    rip_networks.append(net_ip)
                    
        context['rip_networks'] = rip_networks

    elif proto == "OSPF":
        ospf_networks = []
        manual_ospf_networks = rc.get("ospfNetworks", [])
        if manual_ospf_networks:
            # Use per-network area from UI table
            for item in manual_ospf_networks:
                net_ip = item.get("network", "") if isinstance(item, dict) else ""
                wildcard = item.get("wildcard", "0.0.0.255") if isinstance(item, dict) else "0.0.0.255"
                area = item.get("area", "0") if isinstance(item, dict) else "0"
                if net_ip and net_ip != "invalid":
                    ospf_networks.append({'ip': net_ip, 'wildcard': wildcard, 'area': area})
        else:
            # Fallback: derive from interface networks with default area 0
            for item in networks:
                net_ip = item[0] if isinstance(item, (list, tuple)) else item
                net_mask = item[1] if isinstance(item, (list, tuple)) and len(item) > 1 else "24"
                if net_ip and net_ip != "invalid":
                    wildcard = _mask_to_wildcard(net_mask)
                    ospf_networks.append({'ip': net_ip, 'wildcard': wildcard, 'area': '0'})
        context.update({
            'ospf_pid': rc.get("processId", "1"),
            'ospf_rid': rc.get("routerId") or router_id,
            'ospf_networks': ospf_networks
        })

    elif proto == "EIGRP":
        eigrp_networks = []
        manual_eigrp_networks = rc.get("eigrpNetworks", [])
        if manual_eigrp_networks:
            for item in manual_eigrp_networks:
                net_ip = item.get("network", "") if isinstance(item, dict) else ""
                wildcard = item.get("wildcard", "") if isinstance(item, dict) else ""
                if net_ip and net_ip != "invalid":
                    eigrp_networks.append({'ip': net_ip, 'wildcard': wildcard})
        else:
            # Fallback: use interface networks (classful, no wildcard)
            for item in networks:
                net_ip = item[0] if isinstance(item, (list, tuple)) else item
                if net_ip and net_ip != "invalid":
                    eigrp_networks.append({'ip': net_ip, 'wildcard': ''})
        context.update({
            'eigrp_asn': rc.get("asNumber", rc.get("eigrpAs", "100")),
            'eigrp_networks': eigrp_networks
        })

    elif proto == "BGP":
        bgp_neighbors = []
        manual_neighbors = rc.get("bgpNeighbors", [])
        if manual_neighbors:
            for nb in manual_neighbors:
                ip = nb.get("ip", "") if isinstance(nb, dict) else ""
                remote_as = nb.get("remoteAs", "") if isinstance(nb, dict) else ""
                if ip and remote_as:
                    bgp_neighbors.append({'ip': ip, 'remote_as': remote_as})
        else:
            # Fallback: single neighbor from old fields
            nb_ip = rc.get("neighborIp", "")
            nb_as = rc.get("remoteAs", "")
            if nb_ip and nb_as:
                bgp_neighbors.append({'ip': nb_ip, 'remote_as': nb_as})

        bgp_adv_networks = []
        manual_bgp_nets = rc.get("bgpAdvertisedNetworks", [])
        if manual_bgp_nets:
            for item in manual_bgp_nets:
                net_ip = item.get("network", "") if isinstance(item, dict) else ""
                net_mask = item.get("mask", "") if isinstance(item, dict) else ""
                if net_ip and net_ip != "invalid":
                    if net_mask.isdigit():
                        mask_str = _cidr_to_mask(int(net_mask))
                    else:
                        mask_str = net_mask or "255.255.255.0"
                    bgp_adv_networks.append({'ip': net_ip, 'mask_str': mask_str})
        else:
            # Fallback: derive from interface networks
            for item in networks:
                net_ip = item[0] if isinstance(item, (list, tuple)) else item
                net_mask = item[1] if isinstance(item, (list, tuple)) and len(item) > 1 else "24"
                if net_ip and net_ip != "invalid":
                    if net_mask.isdigit():
                        mask_str = _cidr_to_mask(int(net_mask))
                    else:
                        mask_str = net_mask
                    bgp_adv_networks.append({'ip': net_ip, 'mask_str': mask_str})
        context.update({
            'bgp_local_as': rc.get("localAs", "65001"),
            'bgp_rid': rc.get("routerId") or router_id,
            'bgp_neighbors': bgp_neighbors,
            'bgp_networks': bgp_adv_networks
        })

    elif proto == "IS-IS":
        context.update({
            'isis_area_id': rc.get("areaId", "49.0001"),
            'isis_system_id': rc.get("systemId", "0000.0000.0001"),
            'isis_router_type': rc.get("routerType", "level-1-2")
        })

    # Normalize protocol name for template file (IS-IS → isis)
    template_name = proto.lower().replace('-', '')
    return render_template_to_lines(f'routing/{template_name}.j2', context)
