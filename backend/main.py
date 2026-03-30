import eel
import os
import traceback
import logging
from logging.handlers import RotatingFileHandler
import uuid
import json

# Налаштування мінімального рівня логування через змінну оточення LOG_LEVEL (за замовчуванням INFO)
log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Форматер для логів із розширеним контекстом
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - [USER:%(user)s] [SESSION:%(session)s] - %(message)s")

# Файловий обробник з ротацією за розміром (5 МБ, 3 бекапи)
# Для ротації за часом можна використати TimedRotatingFileHandler(filename, when="midnight", interval=1, backupCount=7)
# Це вбудований засіб Python `logging.handlers`, який реалізує ротацію без зовнішніх утиліт (типу logrotate).
# Якщо ж потрібне масштабування на рівні ОС, можна використовувати звичайний FileHandler і налаштувати logrotate у Linux.
file_handler = RotatingFileHandler("crw_app.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
file_handler.setLevel(log_level)
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
logger.addHandler(file_handler)

# Фільтр для глобальних подій (без конкретного контексту сесії)
class GlobalContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user'):
            record.user = 'System'
        if not hasattr(record, 'session'):
            record.session = 'Global'
        return True

logger.addFilter(GlobalContextFilter())

try:
    from .generate import generate_full_config
    from .validate import validate_inputs
    logger.debug("Успішний імпорт генератора та валідатора (relative)")
except ImportError:
    from generate import generate_full_config
    from validate import validate_inputs
    logger.debug("Успішний імпорт генератора та валідатора (absolute)")


# Ініціалізація eel
web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
logger.debug(f"Ініціалізація eel. Директорія web: {web_dir}")
eel.init(web_dir)


@eel.expose
def process_text(config_data: dict = None) -> str:
    # Ініціалізація унікальної сесії/запиту та адаптера логування
    req_id = str(uuid.uuid4()).split('-')[0].upper()
    admin_user = config_data.get("adminUsername", "GUEST") if config_data else "GUEST"
    req_logger = logging.LoggerAdapter(logger, {"user": admin_user, "session": req_id})

    req_logger.info("Початок обробки вхідних даних для генерації конфігурації")
    if config_data is None:
        req_logger.warning("Отримано порожні вхідні дані (None)")
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
            err_code = "ERR-VAL-001"
            err_id = str(uuid.uuid4()).split('-')[0].upper()
            req_logger.error(f"[{err_code}] [{err_id}] Помилка генерації: не передано жодного інтерфейсу. Контекст: hostname={hostname}")
            return json.dumps({
                "error": True,
                "code": err_code,
                "id": err_id,
                "messageKey": "errNoInterfaces",
                "defaultMessage": "Не передано жодного інтерфейсу",
                "instructionsKey": "instrNoInterfaces"
            })

        # Нормалізація/валідація `networks`
        if isinstance(networks, int):
            try:
                if networks < 0:
                    raise ValueError("Кількість мереж не може бути від'ємною")
                networks = [("192.168.1.1", "255.255.255.0")] * networks
            except ValueError as e:
                err_code = "ERR-VAL-002"
                err_id = str(uuid.uuid4()).split('-')[0].upper()
                req_logger.error(f"[{err_code}] [{err_id}] {e}. Контекст: networks={networks}")
                return json.dumps({
                    "error": True, "code": err_code, "id": err_id,
                    "messageKey": "errInvalidNetworkCount", "defaultMessage": f"{e}", "instructionsKey": "instrCheckForm"
                })

        elif not isinstance(networks, list):
            err_code = "ERR-VAL-003"
            err_id = str(uuid.uuid4()).split('-')[0].upper()
            req_logger.error(f"[{err_code}] [{err_id}] Некоректний формат параметра `networks`. Type: {type(networks)}")
            return json.dumps({
                "error": True, "code": err_code, "id": err_id,
                "messageKey": "errInvalidNetworkFormat", "defaultMessage": "Некоректний формат параметра `networks`", "instructionsKey": "instrContactSupport"
            })

        # Якщо `networks` не передали — заповнюємо дефолтними значеннями
        if not networks and interfaces:
            networks = [("192.168.1.1", "255.255.255.0")] * len(interfaces)

        # Перевірка відповідності довжин
        try:
            if len(networks) != len(interfaces):
                err_code = "ERR-VAL-004"
                err_id = str(uuid.uuid4()).split('-')[0].upper()
                req_logger.error(f"[{err_code}] [{err_id}] Невідповідність кількості мереж ({len(networks)}) та інтерфейсів ({len(interfaces)}). Контекст: interfaces={interfaces}")
                return json.dumps({
                    "error": True, "code": err_code, "id": err_id,
                    "messageKey": "errNetworkInterfaceMismatch", 
                    "defaultMessage": f"Кількість мереж ({len(networks)}) не відповідає кількості інтерфейсів ({len(interfaces)})",
                    "instructionsKey": "instrMatchNetworks"
                })
        except TypeError:
            err_code = "ERR-VAL-005"
            err_id = str(uuid.uuid4()).split('-')[0].upper()
            req_logger.error(f"[{err_code}] [{err_id}] Некоректний формат параметра `networks` — очікується список мереж")
            return json.dumps({
                "error": True, "code": err_code, "id": err_id,
                "messageKey": "errInvalidNetworkFormat", "defaultMessage": "Некоректний формат параметра `networks`", "instructionsKey": "instrContactSupport"
            })

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
            err_code = "ERR-VAL-006"
            err_id = str(uuid.uuid4()).split('-')[0].upper()
            req_logger.warning(f"[{err_code}] [{err_id}] Дані не пройшли валідацію: {validation_error}. Контекст: hostname={hostname}")
            return json.dumps({
                "error": True, "code": err_code, "id": err_id,
                "messageKey": "errValidationError", "defaultMessage": validation_error, "instructionsKey": "instrCheckValidation"
            })

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
            req_logger.info(f"Старт генерації конфігурації для пристрою: {hostname.strip() or 'R1'}")
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

            req_logger.info(f"Успішно згенеровано {len(config_lines)} рядків конфігурації")
            return "\n".join(config_lines)

        except Exception as e:
            err_code = "ERR-GEN-001"
            err_id = str(uuid.uuid4()).split('-')[0].upper()
            error_details = traceback.format_exc()
            # Контекст з основними безпечними параметрами
            safe_context = {
                "hostname": hostname,
                "routing_protocol": routing_protocol,
                "interfaces": interfaces,
                "telephony_enabled": telephony_enabled
            }
            req_logger.error(f"[{err_code}] [{err_id}] Критична помилка генерації: {str(e)}. Контекст: {safe_context}", exc_info=True)
            return json.dumps({
                "error": True, "code": err_code, "id": err_id,
                "messageKey": "errGenerationFailed", "defaultMessage": "Критична помилка генерації конфігурації.", "instructionsKey": "instrContactSupport"
            })

    except Exception as e:
        err_code = "ERR-SYS-001"
        err_id = str(uuid.uuid4()).split('-')[0].upper()
        error_details = traceback.format_exc()
        
        # Безпечний дамп параметрів для контексту
        safe_keys = ['hostname', 'routingProtocol', 'interfaces']
        context_data = {k: config_data.get(k) for k in safe_keys} if isinstance(config_data, dict) else "Invalid config_data format"
        
        # Тут не використовуємо req_logger, бо config_data може бути некоректним
        logger.critical(f"[{err_code}] [{err_id}] Глобальна помилка в process_text: {str(e)}. Контекст: {context_data}", exc_info=True)
        return json.dumps({
            "error": True, "code": err_code, "id": err_id,
            "messageKey": "errSystemGlobal", "defaultMessage": "Глобальна критична помилка системи.", "instructionsKey": "instrContactSupport"
        })


if __name__ == "__main__":
    logger.info("Запуск Cisco Router Wizard (Backend)")
    window_size = (1180, 920)

    # Спробуємо різні режими браузерів
    for mode in ["edge", "chrome", None]:
        try:
            logger.debug(f"Спроба запуску UI в режимі: {mode}")
            eel.start(
                "home.html",
                size=window_size,
                mode=mode,
                port=0,           
                block=True
            )
            logger.info("Роботу Eel завершено нормально")
            break
        except Exception as e:
            logger.warning(f"Не вдалося запустити в режимі {mode}: {e}")
            print(f"Не вдалося запустити в режимі {mode}: {e}")
    else:
        logger.error("Не вдалося запустити додаток у жодному браузері")
        print("Не вдалося запустити додаток у жодному браузері")
