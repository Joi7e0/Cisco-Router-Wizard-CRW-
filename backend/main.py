import eel
import os
import traceback

try:
    from .generate import generate_full_config
    from .validate import validate_inputs
except ImportError:
    from generate import generate_full_config
    from validate import validate_inputs


# Ініціалізація eel
eel.init(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web")))


@eel.expose
def process_text(config_data: dict = None) -> str:
    if config_data is None:
        config_data = {}

    try:
        # Екстрагування значень із JSON об'єкта
        routing_protocol = config_data.get("routingProtocol", "")
        router_id = config_data.get("routerId", "")
        ip_multicast = config_data.get("ipMulticast", False)
        telephony_enabled = config_data.get("telephonyEnabled", False)
        dn_list = config_data.get("dnList", [])
        enable_ssh = config_data.get("enableSsh", False)
        hostname = config_data.get("hostname", "")
        enable_secret = config_data.get("enableSecret", "")
        console_password = config_data.get("consolePassword", "")
        admin_username = config_data.get("adminUsername", "admin")
        admin_password = config_data.get("adminPassword", "")
        domain_name = config_data.get("domainName", "local.lab")
        dhcp_network = config_data.get("dhcpNetwork", "")
        dhcp_mask = config_data.get("dhcpMask", "")
        dhcp_gateway = config_data.get("dhcpGateway", "")
        dhcp_dns = config_data.get("dhcpDns", "")
        interfaces = config_data.get("interfaces", [])
        networks = config_data.get("networks", [])
        no_shutdown_interfaces = config_data.get("noShutdownInterfaces", [])
        descriptions = config_data.get("descriptions", [])
        max_ephones = config_data.get("maxEphones", 3)
        max_dn = config_data.get("maxDn", 3)
        auto_assign_range = config_data.get("autoAssignRange", "1 to 3")
        
        # Dynamic calculations for 2.5
        ip_source_address = dhcp_gateway if dhcp_gateway else ""
        if not ip_source_address and interfaces:
            # Fallback to the first configured interface IP if available
            for ip, mask in networks:
                if ip:
                    ip_source_address = ip
                    break
        if not ip_source_address:
            ip_source_address = "10.0.0.1"  # ultimate fallback

        dhcp_excluded = config_data.get("dhcpExcluded", [])
        dhcp_excluded_from = config_data.get("dhcpExcludedFrom", "").strip()
        dhcp_excluded_to = config_data.get("dhcpExcludedTo", "").strip()
        dhcp_option150 = config_data.get("dhcpOption150", "").strip()
        cme_source_ip_raw = config_data.get("cmeSourceIp", "").strip()
        # Build dhcp_excluded from explicit From/To UI fields (overrides old logic)
        if dhcp_excluded_from and dhcp_excluded_to:
            dhcp_excluded = [dhcp_excluded_from, dhcp_excluded_to]
        elif dhcp_excluded_from:
            dhcp_excluded = [dhcp_excluded_from]
        elif not dhcp_excluded and dhcp_gateway:
            # Legacy auto-derive: gateway to gateway+9
            try:
                octets = dhcp_gateway.split('.')
                last_octet = int(octets[-1])
                if last_octet <= 245:
                    end_ip = f"{octets[0]}.{octets[1]}.{octets[2]}.{last_octet + 9}"
                    dhcp_excluded = [dhcp_gateway, end_ip]
                else:
                    dhcp_excluded = [dhcp_gateway]
            except (ValueError, IndexError):
                dhcp_excluded = [dhcp_gateway]

        # CME source IP: use explicit field, fallback to DHCP gateway
        cme_source_ip = cme_source_ip_raw or dhcp_gateway or ip_source_address or "10.0.0.1"

        nat_type = config_data.get("natType", "None")
        nat_inside = config_data.get("natInside", "")
        nat_outside = config_data.get("natOutside", "")
        nat_inside_local = config_data.get("natInsideLocal", "")
        nat_inside_global = config_data.get("natInsideGlobal", "")
        snmp_enabled = config_data.get("snmpEnabled", False)
        snmp_community_ro = config_data.get("snmpCommunityRo", "")
        snmp_community_rw = config_data.get("snmpCommunityRw", "")
        snmp_location = config_data.get("snmpLocation", "")
        snmp_contact = config_data.get("snmpContact", "")
        snmp_trap_host = config_data.get("snmpTrapHost", "")
        routing_config = config_data.get("routingConfig", {})

        # Захист від None
        if dn_list is None:
            dn_list = []
        if interfaces is None:
            interfaces = []
        if networks is None:
            networks = []
        if no_shutdown_interfaces is None:
            no_shutdown_interfaces = []
        if descriptions is None:
            descriptions = []

        # Мінімальна перевірка
        if not interfaces:
            return "❌ Помилка: не передано жодного інтерфейсу"

        # Нормалізація/валідація `networks`
        if isinstance(networks, int):
            try:
                if networks < 0:
                    raise ValueError("Networks count cannot be negative")
                networks = [("192.168.1.1", "255.255.255.0")] * networks
            except ValueError as e:
                return f"❌ Error: {e}"

        elif isinstance(networks, tuple):
            networks = [networks]

        elif not isinstance(networks, list):
            return "❌ Error: Некоректний формат параметра `networks` — очікується список або tuple або int"

        # Якщо `networks` не передали — заповнюємо дефолтними значеннями
        if not networks and interfaces:
            networks = [("192.168.1.1", "255.255.255.0")] * len(interfaces)

        # Перевірка відповідності довжин
        try:
            if len(networks) != len(interfaces):
                return (
                    f"❌ кількість мереж ({len(networks)}) не відповідає "
                    f"кількості інтерфейсів ({len(interfaces)})"
                )
        except TypeError:
            return "❌ Error: Некоректний формат параметра `networks` — очікується список мереж"

        # Базова валідація для OSPF
        # Захищено: routing_protocol може бути неправильного типу
        if not isinstance(routing_protocol, str):
            routing_protocol = str(routing_protocol)

        # Комлексна валідація вхідних даних
        validation_error = validate_inputs(
            networks=networks,
            hostname=hostname.strip() or "R1",
            routing_protocol=routing_protocol.strip(),
            router_id=str(router_id).strip() if router_id else "",
            enable_secret=str(enable_secret).strip() if enable_secret else "",
            console_password=str(console_password).strip() if console_password else "",
            admin_password=str(admin_password).strip() if admin_password else "",
            dhcp_network=str(dhcp_network).strip() if dhcp_network else "",
            dhcp_mask=str(dhcp_mask).strip() if dhcp_mask else "",
            dhcp_gateway=str(dhcp_gateway).strip() if dhcp_gateway else "",
            dhcp_dns=str(dhcp_dns).strip() if dhcp_dns else ""
        )
        
        if validation_error:
            return validation_error

        # Safeguard for max_ephones/max_dn receiving lists due to argument shifts
        if isinstance(max_ephones, list):
            max_ephones = 3
        if isinstance(max_dn, list):
            max_dn = 3

        # Fallbacks for optional parameters
        final_ip_source = cme_source_ip if cme_source_ip else (ip_source_address.strip() if ip_source_address else "10.0.0.1")
        final_auto_assign = auto_assign_range.strip() if auto_assign_range else "1 to 3"
        
        # Ensure dhcp_excluded is at least a tuple of strings
        if not dhcp_excluded:
            if dhcp_gateway:
                final_dhcp_excluded = (dhcp_gateway,)
            else:
                final_dhcp_excluded = ()
        else:
            final_dhcp_excluded = tuple(str(x).strip() for x in dhcp_excluded)

        # Виклик генерації конфігурації
        try:
            config_lines = generate_full_config(
                hostname=hostname.strip() or "R1",
                interfaces=[str(i).strip() for i in interfaces],
                networks=networks,
                ip_multicast=bool(ip_multicast),
                routing_protocol=routing_protocol.strip(),
                router_id=str(router_id).strip(),
                telephony_enabled=bool(telephony_enabled),
                dn_list=dn_list,
                enable_ssh=bool(enable_ssh),
                enable_secret=enable_secret.strip(),
                console_password=console_password.strip(),
                admin_username=admin_username.strip(),
                admin_password=admin_password.strip(),
                domain_name=domain_name.strip(),
                dhcp_network=dhcp_network.strip(),
                dhcp_mask=dhcp_mask.strip(),
                dhcp_gateway=dhcp_gateway.strip(),
                dhcp_dns=dhcp_dns.strip(),
                nat_type=nat_type.strip(),
                nat_inside=nat_inside.strip(),
                nat_outside=nat_outside.strip(),
                nat_inside_local=nat_inside_local.strip(),
                nat_inside_global=nat_inside_global.strip(),
                snmp_enabled=snmp_enabled,
                snmp_community_ro=snmp_community_ro.strip(),
                snmp_community_rw=snmp_community_rw.strip(),
                snmp_location=snmp_location.strip(),
                snmp_contact=snmp_contact.strip(),
                snmp_trap_host=snmp_trap_host.strip(),
                no_shutdown_interfaces=[str(i).strip() for i in no_shutdown_interfaces],
                descriptions=[str(d).strip() for d in descriptions],
                max_ephones=int(max_ephones),
                max_dn=int(max_dn),
                ip_source_address=final_ip_source,
                auto_assign_range=final_auto_assign,
                dhcp_excluded=final_dhcp_excluded,
                dhcp_option150=dhcp_option150,
                routing_config=routing_config
            )

            return "\n".join(config_lines)

        except Exception as e:
            error_details = traceback.format_exc()
            return (
                "❌ Критична помилка генерації конфігурації\n\n"
                f"Повідомлення: {str(e)}\n\n"
                f"Деталі:\n{error_details}"
            )

    except Exception as e:
        error_details = traceback.format_exc()
        return (
            "❌ Критична помилка: " + str(e) + "\nДеталі:\n" + error_details
        )


if __name__ == "__main__":
    window_size = (1180, 920)

    # Спробуємо різні режими браузерів
    for mode in ["edge", "chrome", None]:
        try:
            eel.start(
                "home.html",
                size=window_size,
                mode=mode,
                port=0,           
                block=True
            )
            break
        except Exception as e:
            print(f"Не вдалося запустити в режимі {mode}: {e}")
    else:
        print("Не вдалося запустити додаток у жодному браузері")
