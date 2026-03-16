from .protocols import generate_protocol_config
import os
from jinja2 import Environment, FileSystemLoader

# Set up Jinja2 environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

def render_template_to_lines(template_name: str, context: dict) -> list[str]:
    # Відрендерить Jinja2-шаблон і повертає непорожні рядки.
    #
    # Універсальна допоміжня функція для всіх генераторів. Автоматично
    # видаляє порожні рядки (інденти, порожні рядки Jinja2).
    #
    # Args:
    # template_name (str): Відносний шлях до шаблону (наприклад,
    # ``"interfaces.j2"`` або ``"routing/ospf.j2"``). Шлях відносно
    # ``backend/templates/``.
    # context (dict): Змінні для підстановки в шаблон.
    #
    # Returns:
    # list[str]: Список рядків з відрендереного шаблону (без порожніх).
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
    # Генерує Cisco IOS команди для налаштування інтерфейсів.
    #
    # Для кожного інтерфейсу генерує блок: ``interface``, ``ip address``,
    # опціональні ``description``, ``no shutdown``, ``ip nat inside/outside``,
    # ``ip router isis``. Використовує шаблон ``interfaces.j2``.
    #
    # Args:
    # interfaces (list[str]): Список імен інтерфейсів
    # (``["Gi0/0", "Gi0/1"]``).
    # networks (list[tuple[str, str]]): Список кортежів ``(ip, mask)``
    # у тому ж порядку, що й ``interfaces``.
    # no_shutdown_interfaces (list[str], optional): Інтерфейси, які
    # отримають ``no shutdown``. ``None`` = всі.
    # Defaults to ``None``.
    # descriptions (list[str], optional): Описи для кожного
    # інтерфейсу (по порядку). Defaults to ``None``.
    # routing_config (dict, optional): Конфігурація протоколу
    # маршрутизації (для визначення IS-IS інтерфейсів).
    # Defaults to ``None``.
    # nat_inside (str, optional): Назва інтерфейсу ``ip nat inside``.
    # Defaults to ``""``.
    # nat_outside (str, optional): Назва інтерфейсу ``ip nat outside``.
    # Defaults to ``""``.
    #
    # Returns:
    # list[str]: Список Cisco IOS команд для всіх інтерфейсів.
    # Якщо список не передано або він порожній — всі інтерфейси будуть no shutdown
    if not no_shutdown_interfaces:
        no_shutdown_interfaces = interfaces.copy() if interfaces else []
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
    # Генерує початкову (базову) частину конфігурації.
    #
    # Генерує ``enable``, ``configure terminal`` та ``hostname``
    # (обробник ``base.j2``), а потім повну конфігурацію
    # інтерфейсів через :func:`generate_interface_config`.
    #
    # Args:
    # hostname (str): Ім'я пристрою. Якщо порожне — використовується
    # fallback ``"R1"``.
    # interfaces (list[str]): Список імен інтерфейсів.
    # networks (list[tuple[str, str]]): Список кортежів ``(ip, mask)``.
    # no_shutdown_interfaces (list[str], optional): Defaults to ``None``.
    # descriptions (list[str], optional): Defaults to ``None``.
    # routing_config (dict, optional): Defaults to ``None``.
    # nat_inside (str, optional): Defaults to ``""``.
    # nat_outside (str, optional): Defaults to ``""``.
    #
    # Returns:
    # list[str]: Список команд: ``enable``, ``configure terminal``,
    # ``hostname ...``, блоки інтерфейсів.
    cfg = render_template_to_lines('base.j2', {'hostname': hostname or 'R1'})
    cfg.extend(generate_interface_config(interfaces, networks, no_shutdown_interfaces, descriptions, routing_config, nat_inside, nat_outside))
    return cfg

def generate_multicast_config(ip_multicast: bool, pim_interfaces: list[str]) -> list[str]:
    # Генерує конфігурацію IP Multicast та PIM.
    #
    # Args:
    #     ip_multicast (bool): Увімкнути multicast.
    #     pim_interfaces (list[str]): Список інтерфейсів.
    #
    # Returns:
    #     list[str]: Команди Cisco IOS.

    # Генерує конфігурацію IP Multicast та PIM.
    #
    # Якщо multicast увімкнено, генерує ``ip multicast-routing``
    # та ``ip pim sparse-dense-mode`` на вказаних інтерфейсах.
    # Використовує шаблон ``multicast.j2``.
    #
    # Args:
    # ip_multicast (bool): Увімкнути multicast. ``False`` — повертає ``[]``.
    # pim_interfaces (list[str]): Інтерфейси для PIM
    # (``["Gi0/0", "Gi0/1"]``). Може бути порожним.
    #
    # Returns:
    # list[str]: Команди multicast або ``[]`` якщо
    # ``ip_multicast=False``.
    #
    # Examples:
    # >>> generate_multicast_config(True, ["Gi0/0"])
    # ['!', 'ip multicast-routing', 'interface Gi0/0', ' ip pim sparse-dense-mode', ' exit']
    # >>> generate_multicast_config(False, [])
    # []
    if not ip_multicast:
        return []
    
    if pim_interfaces is None:
        pim_interfaces = []
    
    return render_template_to_lines('multicast.j2', {
        'ip_multicast': ip_multicast,
        'pim_interfaces': pim_interfaces
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
    # Генерує конфігурацію Cisco CME (Telephony Service).
    #
    # Створює блок ``telephony-service`` з параметрами
    # ``max-ephones``, ``max-dn``, ``ip source-address`` та блоки
    # ``ephone-dn`` / ``ephone`` для кожного телефону.
    # Використовує шаблон ``telephony.j2``.
    #
    # Args:
    # telephony_enabled (bool): Увімкнути CME. ``False`` — повертає ``[]``.
    # dn_list (list[dict]): Список телефонних номерів. Кожен
    # елемент: ``{"number": str, "user": str, "mac": str}``.
    # max_ephones (int, optional): Максимальна кількість ephone.
    # Defaults to ``3``.
    # max_dn (int, optional): Максимальна кількість ephone-dn.
    # Defaults to ``3``.
    # ip_source_address (str, optional): CME source IP-адреса.
    # Defaults to ``"10.0.0.1"``.
    # auto_assign_range (str, optional): Діапазон auto assign
    # (``"1 to 3"``). Defaults to ``"1 to 3"``.
    #
    # Returns:
    # list[str]: Команди CME або ``[]`` якщо ``telephony_enabled=False``.
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
    # Генерує конфігурацію безпеки (SSH, паролі, шифрування).
    #
    # Генерує:
    # - ``service password-encryption`` (завжди)
    # - ``enable algorithm-type scrypt secret`` (якщо вказано)
    # - ``line console 0`` / ``password`` / ``login`` (якщо вказано)
    # - ``ip domain-name``, ``username``, ``crypto key generate rsa``,
    # ``ip ssh version 2``, ``line vty 0 4`` (якщо SSH увімкнено
    # і всі SSH-параметри непорожні)
    # Використовує шаблон ``security.j2``.
    #
    # Args:
    # enable_ssh (bool): Увімкнути SSH. Активний лише якщо
    # всі SSH-поля (користувач, пароль, домен) непорожні.
    # enable_secret (str): Enable secret пароль. Порожний — не
    # додається.
    # console_password (str): Console пароль. Порожний — не
    # додається.
    # admin_username (str): SSH користувач.
    # admin_password (str): SSH пароль.
    # domain_name (str): IP domain-name для генерації RSA-ключів.
    #
    # Returns:
    # list[str]: Команди безпеки або ``[]`` якщо жодне поле
    # не вказано.
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
    # Генерує конфігурацію DHCP-сервера.
    #
    # Генерує ``ip dhcp excluded-address`` (для gateway та фіксованих
    # адрес), ``ip dhcp pool LAN`` з ``network``, ``default-router``,
    # ``dns-server`` і опціонально ``option 150 ip`` для IP-телефонів.
    # Використовує шаблон ``dhcp.j2``.
    #
    # Args:
    # dhcp_network (str): Мережа DHCP-пулу (``"192.168.1.0"``).
    # Якщо порожна — повертає ``[]``.
    # dhcp_mask (str): Маска DHCP-пулу (``"255.255.255.0"``).
    # Якщо порожна — повертає ``[]``.
    # dhcp_gateway (str): Gateway для DHCP-клієнтів.
    # dhcp_dns (str): DNS-сервер для DHCP-клієнтів.
    # excluded (list[str], optional): 1 або 2 IP-адреси для
    # ``ip dhcp excluded-address``. 1 елемент = одна адреса,
    # 2 = діапазон. Defaults to ``None``.
    # dhcp_option150 (str, optional): IP-адреса TFTP-сервера для
    # Option 150 (Cisco IP Phones). Defaults to ``""``.
    #
    # Returns:
    # list[str]: Команди DHCP або ``[]`` якщо мережа/маска не
    # вказані.
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
    # Генерує конфігурацію NAT (PAT або Static).
    #
    # Args:
    #     nat_type (str): PAT/Static/None.
    #     nat_inside (str): Інтерфейс IN.
    #     nat_outside (str): Інтерфейс OUT.
    #     dhcp_network (str): Локальна мережа для PAT.
    #
    # Returns:
    #     list[str]: Команди NAT.

    #
    # Для PAT: ``access-list 1 permit`` + ``ip nat inside source list 1 ... overload``.
    # Для Static: ``ip nat inside source static``.
    # Використовує шаблон ``nat.j2``.
    #
    # Note:
    # Позначки ``ip nat inside`` / ``ip nat outside`` на інтерфейсах
    # генеруються в :func:`generate_interface_config`, не тут.
    #
    # Args:
    # nat_type (str): Тип NAT: ``"PAT"``, ``"Static"`` або ``"None"``.
    # nat_inside (str): Назва інтерфейсу inside (``"Gi0/0"``).
    # nat_outside (str): Назва інтерфейсу outside (``"Gi0/1"``).
    # nat_inside_local (str): Внутрішня IP для Static NAT.
    # nat_inside_global (str): Зовнішня IP для Static NAT.
    # dhcp_network (str): Внутрішня мережа для access-list (PAT).
    # dhcp_mask (str): Маска внутрішньої мережі (перетворюється
    # в wildcard mask).
    #
    # Returns:
    # list[str]: Команди NAT або ``[]`` якщо ``nat_type=="None"``.
    if nat_type == "None" or not nat_type:
        return []

    # ПІДГОТОВКА ДЛЯ PAT (Port Address Translation):
    # Обчислюємо Wildcard Mask з DHCP-маски для створення access-list.
    # Гіпотеза: Внутрішня мережа для NAT збігається з мережею DHCP-пулу.
    wildcard_mask = "0.0.0.0"
    if dhcp_mask:
        try:
            # Алгоритм інверсії октетів (255 - маска)
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
    # Генерує конфігурацію SNMP.
    #
    # Args:
    #     snmp_enabled (bool): Статус.
    #     snmp_community_ro (str): RO Community.
    #
    # Returns:
    #     list[str]: Команди SNMP.

    #
    # Генерує ``snmp-server community`` (RO/RW), ``snmp-server location``,
    # ``snmp-server contact`` та ``snmp-server host`` (trap).
    # Використовує шаблон ``snmp.j2``.
    #
    # Note:
    # SNMPv2c передає community string у незашифрованому вигляді.
    # Для продукційних середовищ розгляньте SNMPv3.
    #
    # Args:
    # snmp_enabled (bool): Увімкнути SNMP. ``False`` — повертає ``[]``.
    # snmp_community_ro (str): Community string для притання (RO).
    # snmp_community_rw (str): Community string для запису (RW).
    # snmp_location (str): Параметр ``snmp-server location``.
    # snmp_contact (str): Параметр ``snmp-server contact``.
    # snmp_trap_host (str): IP-адреса сервера SNMP trap.
    #
    # Returns:
    # list[str]: Команди SNMP або ``[]`` якщо ``snmp_enabled=False``.
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
    descriptions: list[str] = None,
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3",
    dhcp_excluded: list[str] = None,
    no_auto_summary: bool = True,
    routing_config: dict = None,
    pim_interfaces: list[str] = None,
    dhcp_option150: str = ""
) -> list[str]:
    # Збирає повну конфігурацію Cisco IOS з усіх секцій.
    #
    # Головна функція-оркестратор. Послідовно викликає генератори кожної
    # секції і збирає їх вивід в єдиний список команд, готовий для
    # копіювання на Cisco-пристрій через CLI або TFTP.
    #
    # Порядок секцій у конфігурації:
    # 1. Base config (``enable`` / ``configure terminal`` / hostname / interfaces)
    # 2. Multicast (якщо ``ip_multicast=True``)
    # 3. Routing protocol (RIP / OSPF / EIGRP / BGP / Static / IS-IS)
    # 4. Telephony service (CME ephone-dn / ephone)
    # 5. Security (enable secret / console password / SSH)
    # 6. DHCP server
    # 7. NAT (PAT or Static)
    # 8. SNMP
    # 9. ``end`` / ``write memory``
    #
    # Args:
    # hostname (str): Ім'я пристрою (Cisco IOS hostname). Якщо порожнє,
    # використовується ``"R1"`` як fallback.
    # interfaces (list[str]): Список імен інтерфейсів
    # (наприклад, ``["Gi0/0", "Gi0/1"]``).
    # networks (list[tuple[str, str]]): Список кортежів ``(ip, mask)``
    # відповідно до порядку в ``interfaces``.
    # ip_multicast (bool): Якщо ``True`` — генерує ``ip multicast-routing``
    # та PIM-конфігурацію.
    # routing_protocol (str): Протокол маршрутизації
    # (``"RIP"``, ``"OSPF"``, ``"EIGRP"``, ``"BGP"``, ``"STATIC"``,
    # ``"IS-IS"``, ``"None"``).
    # router_id (str): Router ID у форматі IPv4. Обов'язковий для OSPF.
    # telephony_enabled (bool): Якщо ``True`` — генерує блок
    # ``telephony-service`` та ephone.
    # dn_list (list[dict]): Список телефонних номерів. Кожен елемент:
    # ``{"number": str, "user": str, "mac": str}``.
    # enable_ssh (bool): Якщо ``True`` — генерує SSH/VTY конфігурацію.
    # enable_secret (str): Enable secret пароль (пустий — не додається).
    # console_password (str): Пароль для console 0.
    # admin_username (str): Ім'я SSH-користувача.
    # admin_password (str): Пароль SSH-користувача.
    # domain_name (str): IP domain-name для генерації RSA-ключів.
    # dhcp_network (str): Мережа DHCP-пулу (наприклад, ``"192.168.1.0"``).
    # dhcp_mask (str): Маска DHCP-пулу.
    # dhcp_gateway (str): Gateway для DHCP-клієнтів.
    # dhcp_dns (str): DNS-сервер для DHCP-клієнтів.
    # nat_type (str, optional): Тип NAT: ``"PAT"``, ``"Static"`` або
    # ``"None"``. Defaults to ``"None"``.
    # nat_inside (str, optional): Інтерфейс NAT inside. Defaults to ``""``.
    # nat_outside (str, optional): Інтерфейс NAT outside. Defaults to ``""``.
    # nat_inside_local (str, optional): Внутрішня IP для Static NAT.
    # nat_inside_global (str, optional): Зовнішня IP для Static NAT.
    # snmp_enabled (bool, optional): Якщо ``True`` — генерує SNMP.
    # Defaults to ``False``.
    # snmp_community_ro (str, optional): SNMP RO community. Defaults to ``""``.
    # snmp_community_rw (str, optional): SNMP RW community. Defaults to ``""``.
    # snmp_location (str, optional): snmp-server location. Defaults to ``""``.
    # snmp_contact (str, optional): snmp-server contact. Defaults to ``""``.
    # snmp_trap_host (str, optional): IP для SNMP trap. Defaults to ``""``.
    # no_shutdown_interfaces (list[str], optional): Список інтерфейсів для
    # ``no shutdown``. Defaults to ``None`` (всі).
    # descriptions (list[str], optional): Описи для кожного інтерфейсу.
    # Defaults to ``None``.
    # max_ephones (int, optional): max-ephones для telephony-service.
    # Defaults to ``3``.
    # max_dn (int, optional): max-dn для telephony-service. Defaults to ``3``.
    # ip_source_address (str, optional): CME source IP. Defaults to
    # ``"10.0.0.1"``.
    # auto_assign_range (str, optional): auto assign range. Defaults to
    # ``"1 to 3"``.
    # dhcp_excluded (list[str], optional): Список виключених DHCP-адрес
    # (1 або 2 елементи). Defaults to ``None``.
    # no_auto_summary (bool, optional): Якщо ``True`` — додає ``no
    # auto-summary`` для RIP/EIGRP. Defaults to ``True``.
    # routing_config (dict, optional): Розширена конфігурація протоколу
    # (ospfNetworks, eigrpNetworks тощо). Defaults to ``None``.
    # pim_interfaces (list[str], optional): Інтерфейси для PIM. Defaults
    # to ``None``.
    # dhcp_option150 (str, optional): TFTP-сервер для Option 150 (IP-
    # телефони). Defaults to ``""``.
    #
    # Returns:
    # list[str]: Список рядків Cisco IOS команд у правильному порядку.
    # Перший елемент — ``"enable"``, останній — ``"write memory"``.
    #
    # Examples:
    # >>> cfg = generate_full_config(
    # ...     hostname="HQ",
    # ...     interfaces=["Gi0/0"],
    # ...     networks=[("192.168.1.1", "255.255.255.0")],
    # ...     ip_multicast=False,
    # ...     routing_protocol="None",
    # ...     router_id="",
    # ...     telephony_enabled=False,
    # ...     dn_list=[],
    # ...     enable_ssh=False,
    # ...     enable_secret="",
    # ...     console_password="",
    # ...     admin_username="",
    # ...     admin_password="",
    # ...     domain_name="",
    # ...     dhcp_network="",
    # ...     dhcp_mask="",
    # ...     dhcp_gateway="",
    # ...     dhcp_dns=""
    # ... )
    # >>> cfg[0]
    # 'enable'
    # >>> cfg[-1]
    # 'write memory'
    if no_shutdown_interfaces is None:
        no_shutdown_interfaces = []

    config = []

    # ЛАНЦЮЖОК ГЕНЕРАЦІЇ:
    # Важливо підтримувати такий порядок для коректності Cisco IOS:
    # 1. Base (hostname/interfaces) - фундамент, на якому тримається решта
    config.extend(generate_base_config(hostname, interfaces, networks, no_shutdown_interfaces, descriptions, routing_config, nat_inside, nat_outside))

    # 2. Advanced features (опціональні розширення)
    config.extend(generate_multicast_config(ip_multicast, pim_interfaces))

    # 3. Маршрутизація (повинна завантажуватись після інтерфейсів, щоб прив'язки були валідні)
    config.extend(generate_protocol_config(routing_protocol, router_id, networks, no_auto_summary, routing_config))

    # 4. Сервіси та Безпека
    config.extend(generate_telephony_config(
        telephony_enabled, dn_list, max_ephones, max_dn,
        ip_source_address, auto_assign_range
    ))

    # 5. Безпека (SSH та паролі)
    config.extend(generate_security_config(
        enable_ssh, enable_secret, console_password,
        admin_username, admin_password, domain_name
    ))

    # 6. IP Infrastructure (DHCP та NAT)
    config.extend(generate_dhcp_config(
        dhcp_network, dhcp_mask, dhcp_gateway, dhcp_dns, dhcp_excluded,
        dhcp_option150=dhcp_option150
    ))

    # 7. NAT (залежить від DHCP-налаштувань для розрахунку Wildcard)
    config.extend(generate_nat_config(
        nat_type, nat_inside, nat_outside, nat_inside_local, nat_inside_global, dhcp_network, dhcp_mask
    ))

    # 8. Management
    config.extend(generate_snmp_config(
        snmp_enabled, snmp_community_ro, snmp_community_rw, snmp_location, snmp_contact, snmp_trap_host
    ))

    # 9. ФІНАЛІЗАЦІЯ:
    # Повернення в привілейований режим та збереження в енергонезалежну пам'ять (NVRAM).
    config.extend([
        "!",
        "end",
        "write memory"
    ])


    return config