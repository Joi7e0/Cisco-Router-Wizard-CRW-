import eel
import os
import traceback

from .generate import generate_full_config


# Ініціалізація eel
eel.init(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web")))


@eel.expose
def process_text(
    routing_protocol: str = "",
    proto: str = "",
    router_id: str = "",
    ip_multicast: bool = False,
    telephony_enabled: bool = False,
    dn_list: list = None,
    enable_ssh: bool = False,
    hostname: str = "",
    enable_secret: str = "",
    console_password: str = "",
    vty_password: str = "",
    dhcp_network: str = "",
    dhcp_mask: str = "",
    dhcp_gateway: str = "",
    dhcp_dns: str = "",
    interfaces: list = None,
    networks: list = None,
    no_shutdown_interfaces: list = None,
    max_ephones: int = 3,
    max_dn: int = 3,
    ip_source_address: str = "10.0.0.1",
    auto_assign_range: str = "1 to 3",
    dhcp_excluded: tuple = ("10.0.0.1", "10.0.0.10")
) -> str:
    try:
        # Захист від None
        if dn_list is None:
            dn_list = []
        if interfaces is None:
            interfaces = []
        if networks is None:
            networks = []
        if no_shutdown_interfaces is None:
            no_shutdown_interfaces = []

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
        # Підтримка короткого імені параметра `proto` в тестах
        if proto and not routing_protocol:
            routing_protocol = proto

        # Захищено: routing_protocol може бути неправильного типу
        if not isinstance(routing_protocol, str):
            routing_protocol = str(routing_protocol)

        if routing_protocol.upper() == "OSPF" and not str(router_id).strip():
            return "❌ Для OSPF обов'язково потрібно вказати Router ID"

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
                vty_password=vty_password.strip(),
                dhcp_network=dhcp_network.strip(),
                dhcp_mask=dhcp_mask.strip(),
                dhcp_gateway=dhcp_gateway.strip(),
                dhcp_dns=dhcp_dns.strip(),
                no_shutdown_interfaces=[str(i).strip() for i in no_shutdown_interfaces],
                max_ephones=int(max_ephones),
                max_dn=int(max_dn),
                ip_source_address=ip_source_address.strip(),
                auto_assign_range=auto_assign_range.strip(),
                dhcp_excluded=tuple(dhcp_excluded)
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
                port=0,           # автоматичний порт
                block=True
            )
            break
        except Exception as e:
            print(f"Не вдалося запустити в режимі {mode}: {e}")
    else:
        print("Не вдалося запустити додаток у жодному браузері")
