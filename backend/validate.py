import ipaddress

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
        ipaddress.ip_address(ip)
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

def validate_inputs(ip: str, mask: str, ip1: str, mask1: str, ip2: str, mask2: str,
                    routing_protocol: str = "", router_id: str = "") -> str:
    """Комплексна валідація всіх обов'язкових полів."""
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
    
    if routing_protocol.upper() == "OSPF" and not router_id:
        return "❌ Error: Для OSPF потрібно вказати Router ID."
    
    return ""  