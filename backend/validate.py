import ipaddress
import re

def validate_general(value: str) -> str:
    """Загальна перевірка: довжина, пробіли, символи."""
    if len(value) < 7:
        return f"❌ Error: '{value}' занадто коротке."
    if len(value) > 18:
        return f"❌ Error: '{value}' занадто довге."
    if " " in value:
        return f"❌ Error: '{value}' містить пробіли."
    if not all(c.isalnum() or c in ".:/" for c in value):
        return f"❌ Error: '{value}' містить недопустимі символи."
    return ""

def validate_ip(ip: str) -> str:
    """Валідація IP-адреси."""
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_multicast or addr.is_loopback or addr.is_reserved:
            return f"❌ Error: IP '{ip}' є зарезервованим (multicast, loopback тощо)."
        return ""
    except ValueError:
        return f"❌ Error: Неправильний формат IP-адреси '{ip}'."

def validate_mask(mask: str) -> str:
    """Валідація маски підмережі."""
    try:
        ipaddress.ip_network(f"0.0.0.0/{mask}")
        return ""
    except ValueError:
        return f"❌ Error: Неправильний формат маски '{mask}'."

def validate_router_id(router_id: str, routing_protocol: str) -> str:
    """Валідація Router ID (R1.16)."""
    if routing_protocol.upper() == "OSPF":
        if not router_id:
            return "❌ Error: Для OSPF потрібно вказати Router ID."
        error = validate_ip(router_id)
        if error:
            return error
        if router_id == "0.0.0.0":
            return "❌ Error: Router ID не може бути 0.0.0.0."
    elif router_id:  # Опціонально для інших, але якщо вказано — валідне
        error = validate_ip(router_id)
        if error:
            return error
    return ""

def validate_password(password: str, field_name: str) -> str:
    """Валідація паролів (R1.17)."""
    if not password:
        return f"❌ Error: {field_name} не може бути порожнім."
    if len(password) < 8 or len(password) > 32:
        return f"❌ Error: {field_name} повинен бути 8-32 символи."
    if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
        return f"❌ Error: {field_name} повинен містити мінімум 1 цифру та 1 літеру."
    return ""

def validate_dhcp(dhcp_network: str, dhcp_mask: str, dhcp_gateway: str, dhcp_dns: str) -> str:
    """Валідація DHCP (R1.18)."""
    if dhcp_network and dhcp_mask:
        error = validate_ip(dhcp_network) or validate_mask(dhcp_mask)
        if error:
            return error
        try:
            network = ipaddress.ip_network(f"{dhcp_network}/{dhcp_mask}")
            if dhcp_gateway and ipaddress.ip_address(dhcp_gateway) not in network:
                return "❌ Error: Gateway не в межах DHCP мережі."
        except ValueError:
            return "❌ Error: Некоректна DHCP мережа/маска."
    if dhcp_dns:
        return validate_ip(dhcp_dns)
    return ""

def validate_inputs(ip: str, mask: str, ip1: str, mask1: str, ip2: str, mask2: str,
                    routing_protocol: str = "", router_id: str = "",
                    enable_secret: str = "", console_password: str = "", vty_password: str = "",
                    dhcp_network: str = "", dhcp_mask: str = "", dhcp_gateway: str = "", dhcp_dns: str = "") -> str:
    """Комплексна валідація всіх обов'язкових полів (розширена)."""
    if not all([ip, mask, ip1, mask1, ip2, mask2]):
        return "❌ Error: Будь ласка, заповніть усі поля IP та маски."
    
    for value in [ip, mask, ip1, mask1, ip2, mask2]:
        error = validate_general(value)
        if error:
            return error
    
    for ip_val in [ip, ip1, ip2]:
        error = validate_ip(ip_val)
        if error:
            return error
    
    for mask_val in [mask, mask1, mask2]:
        error = validate_mask(mask_val)
        if error:
            return error
    
    # Нова: Валідація router_id
    error = validate_router_id(router_id, routing_protocol)
    if error:
        return error
    
    # Нова: Валідація паролів
    for pwd, name in [(enable_secret, "Enable secret"), (console_password, "Console password"), (vty_password, "VTY password")]:
        if pwd:  # Якщо вказано
            error = validate_password(pwd, name)
            if error:
                return error
    
    # Нова: Валідація DHCP
    error = validate_dhcp(dhcp_network, dhcp_mask, dhcp_gateway, dhcp_dns)
    if error:
        return error
    
    return ""