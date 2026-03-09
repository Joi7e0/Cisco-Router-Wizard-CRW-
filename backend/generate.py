from .protocols import generate_protocol_config
import hashlib
import base64

# Генерація конфігурації інтерфейсів
def generate_interface_config(
    interfaces: list[str],
    networks: list[tuple[str, str]],
    no_shutdown_interfaces: list[str] = None,
    descriptions: list[str] = None,
    routing_config: dict = None
) -> list[str]:

    if no_shutdown_interfaces is None:
        no_shutdown_interfaces = []
    if descriptions is None:
        descriptions = []

    cfg = []
    # Use zip with fillvalue or just assume same length since we validated in main.py
    for idx, (intf, (ip, mask)) in enumerate(zip(interfaces, networks)):
        cfg.append(f"interface {intf}")
        # Add description if available
        if idx < len(descriptions) and descriptions[idx]:
            cfg.append(f" description {descriptions[idx]}")
        cfg.append(f" ip address {ip} {mask}")
        if intf in no_shutdown_interfaces:
            cfg.append(" no shutdown")
        
        # IS-IS Participation
        if routing_config and routing_config.get("protocol") == "IS-IS":
            participating = routing_config.get("participatingInterfaces", [])
            if intf in participating:
                cfg.append(" ip router isis")
                
        cfg.append(" exit")
    return cfg

# Генерація базової конфігурації з hostname та інтерфейсами
def generate_base_config(
    hostname: str,
    interfaces: list[str],
    networks: list[tuple[str, str]],
    no_shutdown_interfaces: list[str] = None,
    descriptions: list[str] = None,
    routing_config: dict = None
) -> list[str]:
    cfg = [
        "enable",
        "configure terminal",
        f"hostname {hostname or 'R1'}",
        "!"
    ]
    cfg.extend(generate_interface_config(interfaces, networks, no_shutdown_interfaces, descriptions, routing_config))
    return cfg

def generate_multicast_config(ip_multicast: bool, interfaces: list[str]) -> list[str]:
    """Конфігурація multicast, якщо увімкнено"""
    if not ip_multicast:
        return []
    
    cfg = ["!", "ip multicast-routing"]
    for intf in interfaces:
        cfg.extend([
            f"interface {intf}",
            " ip pim sparse-dense-mode",
            " exit"
        ])
    return cfg

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

    cfg = ["!", "telephony-service"]
    cfg.extend([
        f" max-ephones {max_ephones}",
        f" max-dn {max_dn}",
        f" ip source-address {ip_source_address} port 2000",
        f" auto assign {auto_assign_range}",
        " exit",
        "!"
    ])

    # Обмежуємо кількість до max_dn
    for idx, entry in enumerate(dn_list[:max_dn], start=1):
        number = entry.get("number", "").strip()
        username = entry.get("user", "").strip()

        if number:
            cfg.extend([
                f"ephone-dn {idx}",
                f" number {number}",
                " exit",
                "!"
            ])

        if username:
            cfg.extend([
                f"ephone {idx}",
                f" username {username}",
                " exit",
                "!"
            ])

    return cfg

def encrypt_password(password: str, encryption_type: str) -> str:
    """
    Імітує або обчислює хеш пароля залежно від типу.
    """
    if not password:
        return ""
    
    if encryption_type == "0":
        return password
    elif encryption_type == "1":
        # Simulation for Type 1 (Microsoft)
        return f"MS-{hashlib.md5(password.encode()).hexdigest()[:8]}"
    elif encryption_type == "2":
        return f"T2-{hashlib.sha1(password.encode()).hexdigest()[:10]}"
    elif encryption_type == "3":
        return f"T3-{hashlib.md5(password.encode()).hexdigest()[:10]}"
    elif encryption_type == "4":
        # Legacy SHA-256
        return hashlib.sha256(password.encode()).hexdigest()[:12]
    elif encryption_type == "5":
        # MD5
        return hashlib.md5(password.encode()).hexdigest()
    elif encryption_type == "6":
        # AES (Simulation)
        return f"AES-{base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()[:16]}"
    elif encryption_type == "7":
        # Спрощена імітація Type 7 (Vigenère)
        return "08314D5D1A48"  # Приклад статичного обфускованого пароля
    elif encryption_type == "8":
        # SHA-256
        return hashlib.sha256(password.encode()).hexdigest()
    elif encryption_type == "9":
        # SCRYPT
        try:
            salt = b"salt"
            h = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
            return base64.b64encode(h).decode()
        except AttributeError:
            return hashlib.sha512(password.encode()).hexdigest()
    return password

# Генерація конфігурації безпеки (SSH, паролі)
def generate_security_config(
    enable_ssh: bool,
    enable_secret: str,
    console_password: str,
    vty_password: str,
    password_encryption_type: str = "7"
) -> list[str]:
    cfg = ["!"]

    if password_encryption_type == "7":
        cfg.append("service password-encryption")

    if enable_secret:
        if password_encryption_type == "0":
            cfg.append(f"enable secret {enable_secret}")
        elif password_encryption_type == "7":
            # Для Type 7 використовуємо enable secret з сирим паролем (буде Type 5 за замовчуванням на пристрої)
            cfg.append(f"enable secret {enable_secret}")
        elif password_encryption_type in ["1", "2", "3", "4", "5", "6", "8", "9"]:
            enc_pwd = encrypt_password(enable_secret, password_encryption_type)
            # Cisco uses 'enable secret <type> <hash>' for most secure types
            # For 1-4 we'll use secret but note they are simulated
            cfg.append(f"enable secret {password_encryption_type} {enc_pwd}")
        else:
            cfg.append(f"enable secret {enable_secret}")

    if console_password:
        cfg.extend([
            "line console 0",
            f" password {password_encryption_type if password_encryption_type == '7' else ''} {encrypt_password(console_password, password_encryption_type) if password_encryption_type == '7' else console_password}".replace("  ", " "),
            " login",
            " exit",
            "!"
        ])

    if vty_password:
        cfg.extend([
            "line vty 0 4",
            f" password {password_encryption_type if password_encryption_type == '7' else ''} {encrypt_password(vty_password, password_encryption_type) if password_encryption_type == '7' else vty_password}".replace("  ", " "),
            " login",
            " exit",
            "!"
        ])

    if enable_ssh:
        cfg.extend([
            "ip domain-name local.lab",
            "crypto key generate rsa modulus 1024",
            "ip ssh version 2",
            "!"
        ])

    return cfg

# Генерація конфігурації DHCP
def generate_dhcp_config(
    dhcp_network: str,
    dhcp_mask: str,
    dhcp_gateway: str,
    dhcp_dns: str,
    excluded: tuple[str, str] = ("10.0.0.1", "10.0.0.10")
) -> list[str]:
    if not dhcp_network or not dhcp_mask:
        return []

    cfg = ["!"]
    if excluded and len(excluded) >= 2:
        cfg.append(f"ip dhcp excluded-address {excluded[0]} {excluded[1]}")
    elif excluded and len(excluded) == 1:
        cfg.append(f"ip dhcp excluded-address {excluded[0]}")
    cfg.extend([
        "ip dhcp pool LAN",
        f" network {dhcp_network} {dhcp_mask}"
    ])

    if dhcp_gateway:
        cfg.append(f" default-router {dhcp_gateway}")
    if dhcp_dns:
        cfg.append(f" dns-server {dhcp_dns}")

    cfg.append(" exit")
    cfg.append("!")

    return cfg

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
    vty_password: str,
    password_encryption_type: str,
    dhcp_network: str,
    dhcp_mask: str,
    dhcp_gateway: str,
    dhcp_dns: str,
    no_shutdown_interfaces: list[str] = None,
    descriptions: list[str] = None,
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3",
    dhcp_excluded: tuple[str, str] = ("10.0.0.1", "10.0.0.10"),
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
    config.extend(generate_base_config(hostname, interfaces, networks, no_shutdown_interfaces, descriptions, routing_config))

    # 2. Multicast (якщо потрібно)
    config.extend(generate_multicast_config(ip_multicast, interfaces))

    # 3. Протокол маршрутизації
    config.extend(generate_protocol_config(routing_protocol, router_id, networks, no_auto_summary, routing_config))

    # 4. Telephony
    config.extend(generate_telephony_config(
        telephony_enabled, dn_list, max_ephones, max_dn,
        ip_source_address, auto_assign_range
    ))

    # 5. Безпека
    config.extend(generate_security_config(
        enable_ssh, enable_secret, console_password, vty_password, password_encryption_type
    ))

    # 6. DHCP
    config.extend(generate_dhcp_config(
        dhcp_network, dhcp_mask, dhcp_gateway, dhcp_dns, dhcp_excluded
    ))

    # 7. Завершення конфігурації
    config.extend([
        "!",
        "end",
        "write memory"
    ])

    return config