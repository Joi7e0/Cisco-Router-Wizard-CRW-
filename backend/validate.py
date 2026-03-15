import ipaddress
import re

# Загальна валідація рядкових полів (дозволяє літери, цифри та основні роздільники)
def validate_general(value: str) -> str:
    """Перевіряє загальний рядок на допустимі символи.

    Дозволяє літери, цифри та символи ```. / - _```. Використовується
    для полів, які можуть містити як IP-адреси, так і назви (hostname,
    description тощо).

    Args:
        value (str): Рядок для перевірки.

    Returns:
        str: Порожній рядок якщо валідний, або повідомлення про помилку
             що починається з ``❌ Error:``.

    Examples:
        >>> validate_general("192.168.1.1")
        ''
        >>> validate_general("bad value!")
        "❌ Error: 'bad value!' містить недопустимі символи (дозволено: a-z, 0-9, ., /, -, _)."
    """
    if not isinstance(value, str):
        return "❌ Error: Value must be a string."

    if " " in value:
        return f"❌ Error: '{value}' містить пробіли."

    # Дозволені символи для мережевих налаштувань та імен
    if not all(c.isalnum() or c in "./-_" for c in value):
        return f"❌ Error: '{value}' містить недопустимі символи (дозволено: a-z, 0-9, ., /, -, _)."

    return ""

# Валідація Hostname за правилами Cisco IOS
def validate_hostname(hostname: str) -> str:
    """Перевіряє hostname відповідно до правил Cisco IOS.

    Cisco IOS вимагає, щоб hostname:
    - Починався з літери (не цифри).
    - Містив лише літери, цифри, ``-``, ``_``, ``.``.
    - Мав довжину не більше 63 символів.

    Args:
        hostname (str): Ім'я пристрою для перевірки.

    Returns:
        str: Порожній рядок якщо валідний, або повідомлення про помилку.

    Examples:
        >>> validate_hostname("Branch-Router")
        ''
        >>> validate_hostname("1Router")
        "❌ Error: Hostname повинен починатися з літери."
    """
    if not hostname:
        return "❌ Error: Hostname не може бути порожнім."

    if len(hostname) > 63:
        return "❌ Error: Hostname занадто довгий (макс. 63 символи)."

    if not re.match(r'^[a-zA-Z]', hostname):
        return "❌ Error: Hostname повинен починатися з літери."

    if not re.match(r'^[a-zA-Z0-9\-_\.]+$', hostname):
        return f"❌ Error: Hostname '{hostname}' містить недопустимі символи."

    return ""

# Валідація IP-адреси
def validate_ip(ip: str) -> str:
    """Перевіряє коректність IPv4-адреси для конфігурацій Cisco.

    Функція дозволяє broadcast-адресу ``255.255.255.255``, але блокує
    loopback (``127.x.x.x``), multicast (``224-239.x.x.x``) та інші
    зарезервовані діапазони, оскільки вони не можуть бути використані
    на інтерфейсах або як gateway Cisco-пристрою.

    Args:
        ip (str): IPv4-адреса для перевірки.

    Returns:
        str: Порожній рядок якщо адреса коректна, або повідомлення про помилку.

    Examples:
        >>> validate_ip("192.168.1.1")
        ''
        >>> validate_ip("127.0.0.1")
        "❌ Error: IP '127.0.0.1' є зарезервованим (multicast, loopback тощо)."
        >>> validate_ip("255.255.255.255")  # broadcast дозволений
        ''
    """
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
    """Перевіряє Router ID залежно від протоколу маршрутизації.

    Для OSPF Router ID є обов'язковим та не може бути ``0.0.0.0`` або
    ``255.255.255.255``. Для інших протоколів (EIGRP, BGP, RIP) поле
    опціональне, але якщо вказане — має бути коректною IP-адресою.

    Args:
        router_id (str): Router ID у форматі IPv4 (наприклад, ``"1.1.1.1"``).
        routing_protocol (str): Назва протоколу (``"OSPF"``, ``"EIGRP"``,
            ``"BGP"``, ``"RIP"``). Регістронезалежний.

    Returns:
        str: Порожній рядок якщо валідний, або повідомлення про помилку.

    Examples:
        >>> validate_router_id("1.1.1.1", "OSPF")
        ''
        >>> validate_router_id("", "OSPF")
        '❌ Error: Для OSPF потрібно вказати Router ID.'
        >>> validate_router_id("", "RIP")  # для RIP опціонально
        ''
    """
    try:
        if not isinstance(routing_protocol, str):
            raise TypeError("routing_protocol must be a string")

        if routing_protocol.upper() == "OSPF":
            if not router_id:
                return "❌ Error: Для OSPF потрібно вказати Router ID."
            error = validate_ip(router_id)
            if error:
                return error
            if router_id == "0.0.0.0" or router_id == "255.255.255.255":
                return f"❌ Error: Router ID не може бути {router_id}."
        elif router_id:  # Опціонально для інших, але якщо вказано — валідне
            error = validate_ip(router_id)
            if error:
                return error
            if router_id == "0.0.0.0" or router_id == "255.255.255.255":
                return f"❌ Error: Router ID не може бути {router_id}."
        return ""
    except (ValueError, TypeError) as e:
        print(f"Validate router_id error: {e}")
        return f"❌ Error: Некоректний Router ID: {router_id}"

# Валідація паролів
def validate_password(password: str, field_name: str) -> str:
    if not isinstance(password, str):
        return f"❌ Error: {field_name} повинен бути рядком."
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
def validate_inputs(
        networks: list,
        hostname: str = "",
        routing_protocol: str = "",
        router_id: str = "",
        enable_secret: str = "",
        console_password: str = "",
        admin_password: str = "",
        dhcp_network: str = "",
        dhcp_mask: str = "",
        dhcp_gateway: str = "",
        dhcp_dns: str = ""
) -> str:
    """Головна функція валідації всіх вхідних даних конфігурації.

    Послідовно перевіряє hostname, список мереж, Router ID, паролі
    та DHCP-налаштування. Повертає першу знайдену помилку або
    порожній рядок якщо всі дані коректні.

    Args:
        networks (list): Список кортежів ``(ip: str, mask: str)`` для
            інтерфейсів. Обов'язковий, не може бути порожнім.
        hostname (str, optional): Hostname пристрою. Якщо вказаний,
            перевіряється за правилами Cisco IOS. Defaults to ``""``.
        routing_protocol (str, optional): Протокол маршрутизації
            (``"OSPF"``, ``"RIP"`` тощо). Defaults to ``""``.
        router_id (str, optional): Router ID у форматі IPv4.
            Обов'язковий для OSPF. Defaults to ``""``.
        enable_secret (str, optional): Enable secret пароль (8-32 символи).
            Defaults to ``""``.
        console_password (str, optional): Console пароль. Defaults to ``""``.
        admin_password (str, optional): SSH admin пароль. Defaults to ``""``.
        dhcp_network (str, optional): Мережа DHCP-пулу. Defaults to ``""``.
        dhcp_mask (str, optional): Маска DHCP-пулу. Defaults to ``""``.
        dhcp_gateway (str, optional): Default gateway для DHCP. Defaults to ``""``.
        dhcp_dns (str, optional): DNS-сервер для DHCP. Defaults to ``""``.

    Returns:
        str: Порожній рядок якщо всі дані валідні, або рядок з повідомленням
             про першу знайдену помилку (починається з ``❌ Error:``).

    Raises:
        Exception: Внутрішні винятки перехоплюються та повертаються як
            ``❌ Error: Внутрішня помилка валідації.``

    Examples:
        >>> validate_inputs([("192.168.1.1", "255.255.255.0")])
        ''
        >>> validate_inputs([])
        '❌ Error: Будь ласка, вкажіть хоча б одну мережу (IP та маску).'
        >>> validate_inputs(
        ...     [("192.168.1.1", "255.255.255.0")],
        ...     routing_protocol="OSPF",
        ...     router_id=""
        ... )
        '❌ Error: Для OSPF потрібно вказати Router ID.'
    """
    try:
        # Валідація Hostname
        if hostname:
            error = validate_hostname(hostname)
            if error: return error

        if not networks:
            return "❌ Error: Будь ласка, вкажіть хоча б одну мережу (IP та маску)."
        
        for item in networks:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                continue
            ip, mask = item
            if not ip or not mask:
                return "❌ Error: Будь ласка, заповніть усі поля IP та маски."
            
            error = validate_general(ip) or validate_general(mask)
            if error: return error
            
            error = validate_ip(ip) or validate_mask(mask)
            if error: return error
        
        # Валідація router_id
        error = validate_router_id(router_id, routing_protocol)
        if error:
            return error
        
        # Валідація паролів
        for pwd, name in [(enable_secret, "Enable secret"), (console_password, "Console password"), (admin_password, "Admin password")]:
            if pwd:  # Якщо вказано
                error = validate_password(pwd, name)
                if error:
                    return error
        
        # Валідація DHCP
        error = validate_dhcp(dhcp_network, dhcp_mask, dhcp_gateway, dhcp_dns)
        if error:
            return error

        return ""
    except Exception as e:
        print(f"Unexpected error in validate_inputs: {e}")
        return "❌ Error: Внутрішня помилка валідації."