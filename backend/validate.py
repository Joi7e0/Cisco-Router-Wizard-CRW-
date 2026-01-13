import ipaddress
import re

# Загальна валідація рядкових полів (без специфіки IP/масок)
def validate_general(value: str) -> str:
    if not isinstance(value, str):
        return "❌ Error: Value must be a string."

    if " " in value:
        return f"❌ Error: '{value}' містить пробіли."

    # Дозволені символи: цифри, крапки (для IP/масок), слеш для CIDR (якщо маска в /24 форматі)
    if not all(c.isdigit() or c in "./" for c in value):
        return f"❌ Error: '{value}' містить недопустимі символи (дозволено: 0-9, ., /)."

    return ""

# Валідація IP-адреси
def validate_ip(ip: str) -> str:
    try:
        if not isinstance(ip, str):
            raise TypeError(f"IP must be str, got {type(ip)}")

        addr = ipaddress.ip_address(ip)

        # Змінено логіку: дозволяємо broadcast, але блокуємо інші зарезервовані
        if addr.is_multicast or addr.is_loopback or addr.is_reserved:
            # Дозволяємо broadcast-адресу
            if str(addr) == "255.255.255.255":
                return ""
            return f"❌ Error: IP '{ip}' є зарезервованим (multicast, loopback тощо)."

        return ""
    except (ValueError, TypeError) as e:
        print(f"Validate IP error: {e}")
        return f"❌ Error: Неправильний формат IP-адреси '{ip}'."

# Валідація маски підмережі
def validate_mask(mask: str) -> str:
    try:
        if not isinstance(mask, str):
            raise TypeError(f"Mask must be str, got {type(mask)}")
        ipaddress.ip_network(f"0.0.0.0/{mask}")
        return ""
    except (ValueError, TypeError) as e:
        print(f"Validate mask error: {e}")
        return f"❌ Error: Неправильний формат маски '{mask}'."

# Валідація Router ID залежно від протоколу маршрутизації
def validate_router_id(router_id: str, routing_protocol: str) -> str:
    try:
        if not isinstance(routing_protocol, str):
            raise TypeError("routing_protocol must be a string")

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
    except (ValueError, TypeError) as e:
        print(f"Validate router_id error: {e}")
        return f"❌ Error: Некоректний Router ID: {router_id}"

# Валідація паролів
def validate_password(password: str, field_name: str) -> str:
    if not password:
        return f"❌ Error: {field_name} не може бути порожнім."
    if len(password) < 8 or len(password) > 32:
        return f"❌ Error: {field_name} повинен бути 8-32 символи."
    if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
        return f"❌ Error: {field_name} повинен містити мінімум 1 цифру та 1 літеру."
    return ""

# Валідація DHCP налаштувань
def validate_dhcp(dhcp_network: str, dhcp_mask: str, dhcp_gateway: str, dhcp_dns: str) -> str:
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

# Головна функція валідації всіх вхідних даних
def validate_inputs(ip: str, mask: str, ip1: str, mask1: str, ip2: str, mask2: str,
                    routing_protocol: str = "", router_id: str = "",
                    enable_secret: str = "", console_password: str = "", vty_password: str = "",
                    dhcp_network: str = "", dhcp_mask: str = "", dhcp_gateway: str = "", dhcp_dns: str = "") -> str:
    try:
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
    except Exception as e:
        print(f"Unexpected error in validate_inputs: {e}")
        return "❌ Error: Внутрішня помилка валідації."