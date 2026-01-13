from .protocols import generate_protocol_config


def generate_interface_config(
    interfaces: list[str],
    networks: list[tuple[str, str]],
    no_shutdown_interfaces: list[str] = None
) -> list[str]:
    """
    Генерація команд для налаштування інтерфейсів
    """
    if no_shutdown_interfaces is None:
        no_shutdown_interfaces = []

    cfg = []
    for intf, (ip, mask) in zip(interfaces, networks):
        cfg.append(f"interface {intf}")
        cfg.append(f" ip address {ip} {mask}")
        if intf in no_shutdown_interfaces:
            cfg.append(" no shutdown")
        cfg.append(" exit")
    return cfg


def generate_base_config(
    hostname: str,
    interfaces: list[str],
    networks: list[tuple[str, str]],
    no_shutdown_interfaces: list[str] = None
) -> list[str]:
    """Базова частина конфігурації + інтерфейси"""
    cfg = [
        "enable",
        "configure terminal",
        f"hostname {hostname or 'R1'}",
        "!"
    ]
    cfg.extend(generate_interface_config(interfaces, networks, no_shutdown_interfaces))
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


def generate_telephony_config(
    telephony_enabled: bool,
    dn_list: list[dict],
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3"
) -> list[str]:
    """Конфігурація telephony-service та ephone-dn/ephone"""
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


def generate_security_config(
    enable_ssh: bool,
    enable_secret: str,
    console_password: str,
    vty_password: str
) -> list[str]:
    """Безпека: паролі, enable secret, SSH"""
    cfg = ["!"]

    if enable_secret:
        cfg.append(f"enable secret {enable_secret}")

    if console_password:
        cfg.extend([
            "line console 0",
            f" password {console_password}",
            " login",
            " exit",
            "!"
        ])

    if vty_password:
        cfg.extend([
            "line vty 0 4",
            f" password {vty_password}",
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


def generate_dhcp_config(
    dhcp_network: str,
    dhcp_mask: str,
    dhcp_gateway: str,
    dhcp_dns: str,
    excluded: tuple[str, str] = ("10.0.0.1", "10.0.0.10")
) -> list[str]:
    """Налаштування DHCP-сервера"""
    if not dhcp_network or not dhcp_mask:
        return []

    cfg = ["!"]
    cfg.append(f"ip dhcp excluded-address {excluded[0]} {excluded[1]}")
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
    dhcp_network: str,
    dhcp_mask: str,
    dhcp_gateway: str,
    dhcp_dns: str,
    no_shutdown_interfaces: list[str] = None,
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3",
    dhcp_excluded: tuple[str, str] = ("10.0.0.1", "10.0.0.10")
) -> list[str]:
    """
    Збирає всю конфігурацію разом
    Повертає список рядків (кожний рядок — окрема команда)
    """
    if no_shutdown_interfaces is None:
        no_shutdown_interfaces = []

    config = []

    # 1. Базова частина + інтерфейси
    config.extend(generate_base_config(hostname, interfaces, networks, no_shutdown_interfaces))

    # 2. Multicast (якщо потрібно)
    config.extend(generate_multicast_config(ip_multicast, interfaces))

    # 3. Протокол маршрутизації
    config.extend(generate_protocol_config(routing_protocol, router_id, networks))

    # 4. Telephony
    config.extend(generate_telephony_config(
        telephony_enabled, dn_list, max_ephones, max_dn,
        ip_source_address, auto_assign_range
    ))

    # 5. Безпека
    config.extend(generate_security_config(
        enable_ssh, enable_secret, console_password, vty_password
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