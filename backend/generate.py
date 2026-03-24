from .protocols import generate_protocol_config
import os
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

def render_template_to_lines(template_name, context):
    template = env.get_template(template_name)
    rendered = template.render(**context)
    return [line for line in rendered.splitlines() if line.strip()]

# Генерація конфігурації інтерфейсів
def generate_interface_config(
    interfaces: list[str],
    networks: list[tuple[str, str]],
    no_shutdown_interfaces: list[str] = None,
    descriptions: list[str] = None,
    routing_config: dict = None,
    nat_inside: str = "",
    nat_outside: str = ""
) -> list[str]:

    if no_shutdown_interfaces is None:
        no_shutdown_interfaces = interfaces
    if descriptions is None:
        descriptions = []

    interface_data = []
    for idx, (intf, (ip, mask)) in enumerate(zip(interfaces, networks)):
        desc = descriptions[idx] if idx < len(descriptions) and descriptions[idx] else ""
        isis = False
        if routing_config and routing_config.get("protocol") == "IS-IS":
            if intf in routing_config.get("participatingInterfaces", []):
                isis = True
                
        interface_data.append({
            'name': intf,
            'ip': ip,
            'mask': mask,
            'description': desc,
            'no_shutdown': intf in no_shutdown_interfaces,
            'isis': isis,
            'is_nat_inside': intf == nat_inside,
            'is_nat_outside': intf == nat_outside
        })

    return render_template_to_lines('interfaces.j2', {'interface_data': interface_data})

# Генерація базової конфігурації з hostname та інтерфейсами
def generate_base_config(
    hostname: str,
    interfaces: list[str],
    networks: list[tuple[str, str]],
    no_shutdown_interfaces: list[str] = None,
    descriptions: list[str] = None,
    routing_config: dict = None,
    nat_inside: str = "",
    nat_outside: str = ""
) -> list[str]:
    cfg = render_template_to_lines('base.j2', {'hostname': hostname or 'R1'})
    cfg.extend(generate_interface_config(interfaces, networks, no_shutdown_interfaces, descriptions, routing_config, nat_inside, nat_outside))
    return cfg

def generate_multicast_config(ip_multicast: bool, interfaces: list[str]) -> list[str]:
    """Конфігурація multicast, якщо увімкнено"""
    if not ip_multicast:
        return []
    
    return render_template_to_lines('multicast.j2', {
        'ip_multicast': ip_multicast,
        'pim_interfaces': interfaces
    })

# Генерація конфігурації телефонії
def generate_telephony_config(
    telephony_enabled: bool,
    dn_list: list[dict],
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3"
) -> list[str]:
    if not telephony_enabled:
        return []

    formatted_dn_list = []
    for idx, entry in enumerate(dn_list[:max_dn], start=1):
        formatted_dn_list.append({
            'idx': idx,
            'number': entry.get("number", "").strip(),
            'user': entry.get("user", "").strip(),
            'mac': entry.get("mac", "").strip()
        })

    return render_template_to_lines('telephony.j2', {
        'telephony_enabled': telephony_enabled,
        'max_ephones': max_ephones,
        'max_dn': max_dn,
        'ip_source_address': ip_source_address,
        'auto_assign_range': auto_assign_range,
        'dn_list': formatted_dn_list
    })

# Генерація конфігурації безпеки (SSH, паролі)
def generate_security_config(
    enable_ssh: bool,
    enable_secret: str,
    console_password: str,
    admin_username: str,
    admin_password: str,
    domain_name: str
) -> list[str]:
    # If SSH enabled, all SSH fields must be present to generate valid config
    effective_ssh = enable_ssh and bool(admin_username) and bool(admin_password) and bool(domain_name)
    
    return render_template_to_lines('security.j2', {
        'enable_secret': enable_secret,
        'console_password': console_password,
        'enable_ssh': effective_ssh,
        'admin_username': admin_username,
        'admin_password': admin_password,
        'domain_name': domain_name
    })

# Генерація конфігурації DHCP
def generate_dhcp_config(
    dhcp_network: str,
    dhcp_mask: str,
    dhcp_gateway: str,
    dhcp_dns: str,
    excluded: list[str] = None,
    dhcp_option150: str = ""
) -> list[str]:
    if not dhcp_network or not dhcp_mask:
        return []

    if isinstance(excluded, str):
        excluded = tuple(excluded.split())
    elif not excluded:
        excluded = []

    return render_template_to_lines('dhcp.j2', {
        'dhcp_network': dhcp_network,
        'dhcp_mask': dhcp_mask,
        'dhcp_gateway': dhcp_gateway,
        'dhcp_dns': dhcp_dns,
        'excluded': excluded,
        'dhcp_option150': dhcp_option150
    })

def generate_nat_config(
    nat_type: str,
    nat_inside: str,
    nat_outside: str,
    nat_inside_local: str,
    nat_inside_global: str,
    dhcp_network: str,
    dhcp_mask: str
) -> list[str]:
    if nat_type == "None" or not nat_type:
        return []

    # Calculate wildcard mask from DHCP mask
    # For a wizard, assuming DHCP network is the internal network
    wildcard_mask = "0.0.0.0"
    if dhcp_mask:
        try:
            octets = dhcp_mask.split('.')
            wildcard_octets = [str(255 - int(o)) for o in octets]
            wildcard_mask = ".".join(wildcard_octets)
        except ValueError:
            pass

    return render_template_to_lines('nat.j2', {
        'nat_type': nat_type,
        'nat_inside': nat_inside,
        'nat_outside': nat_outside,
        'nat_inside_local': nat_inside_local,
        'nat_inside_global': nat_inside_global,
        'local_network': dhcp_network,
        'wildcard_mask': wildcard_mask
    })

def generate_snmp_config(
    snmp_enabled: bool,
    snmp_community_ro: str,
    snmp_community_rw: str,
    snmp_location: str,
    snmp_contact: str,
    snmp_trap_host: str
) -> list[str]:
    if not snmp_enabled:
        return []
    
    return render_template_to_lines('snmp.j2', {
        'snmp_community_ro': snmp_community_ro,
        'snmp_community_rw': snmp_community_rw,
        'snmp_location': snmp_location,
        'snmp_contact': snmp_contact,
        'snmp_trap_host': snmp_trap_host
    })

# Збірка повної конфігурації
def generate_full_config(
    hostname: str,
    interfaces: list[str],
    networks: list[tuple[str, str]],
    ip_multicast: bool,
    routing_protocol: str,
    router_id: str,
    telephony_enabled: bool,
    dn_list: list[dict],
    enable_ssh: bool,
    enable_secret: str,
    console_password: str,
    admin_username: str,
    admin_password: str,
    domain_name: str,
    dhcp_network: str,
    dhcp_mask: str,
    dhcp_gateway: str,
    dhcp_dns: str,
    dhcp_option150: str = "",
    nat_type: str = "None",
    nat_inside: str = "",
    nat_outside: str = "",
    nat_inside_local: str = "",
    nat_inside_global: str = "",
    snmp_enabled: bool = False,
    snmp_community_ro: str = "",
    snmp_community_rw: str = "",
    snmp_location: str = "",
    snmp_contact: str = "",
    snmp_trap_host: str = "",
    no_shutdown_interfaces: list[str] = None,
    pim_interfaces: list[str] = None,
    descriptions: list[str] = None,
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3",
    dhcp_excluded: list[str] = None,
    no_auto_summary: bool = True,
    routing_config: dict = None
) -> list[str]:
    """
    Збирає всю конфігурацію разом
    Повертає список рядків (кожний рядок — окрема команда)
    """
    if no_shutdown_interfaces is None:
        no_shutdown_interfaces = []

    config = []

    # 1. Базова частина + інтерфейси
    config.extend(generate_base_config(hostname, interfaces, networks, no_shutdown_interfaces, descriptions, routing_config, nat_inside, nat_outside))

    # 2. Multicast (якщо потрібно)
    config.extend(generate_multicast_config(ip_multicast, pim_interfaces if pim_interfaces is not None else interfaces))

    # 3. Протокол маршрутизації
    config.extend(generate_protocol_config(routing_protocol, router_id, networks, no_auto_summary, routing_config))

    # 4. Telephony
    config.extend(generate_telephony_config(
        telephony_enabled, dn_list, max_ephones, max_dn,
        ip_source_address, auto_assign_range
    ))

    # 5. Безпека
    config.extend(generate_security_config(
        enable_ssh, enable_secret, console_password,
        admin_username, admin_password, domain_name
    ))

    # 6. DHCP
    config.extend(generate_dhcp_config(
        dhcp_network, dhcp_mask, dhcp_gateway, dhcp_dns, dhcp_excluded, dhcp_option150
    ))

    # 7. NAT
    config.extend(generate_nat_config(
        nat_type, nat_inside, nat_outside, nat_inside_local, nat_inside_global, dhcp_network, dhcp_mask
    ))

    # 8. SNMP
    config.extend(generate_snmp_config(
        snmp_enabled, snmp_community_ro, snmp_community_rw, snmp_location, snmp_contact, snmp_trap_host
    ))

    # 9. Завершення конфігурації
    config.extend([
        "!",
        "end",
        "write memory"
    ])

    return config