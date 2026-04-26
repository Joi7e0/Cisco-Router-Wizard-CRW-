import logging
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

logger = logging.getLogger(__name__)

# Глобальний стан з'єднання з роутером
_connection = None
_connection_info = {}


def get_connection_state() -> dict:
    # Повертає поточний стан підключення.
    #
    # Returns:
    #     dict: {"connected": bool, "host": str}
    return {
        "connected": _connection is not None and _connection.is_alive(),
        "host": _connection_info.get("host", "")
    }


def connect(
    host: str,
    port: int = 23,
    username: str = "",
    password: str = "",
    enable_secret: str = "",
    timeout: int = 15
) -> dict:
    # Встановлює Telnet-з'єднання з Cisco роутером через netmiko.
    #
    # Args:
    #     host (str): IP-адреса роутера.
    #     port (int): Telnet-порт (за замовчуванням 23).
    #     username (str): Ім'я користувача (може бути порожнім для no-auth VTY).
    #     password (str): Пароль для VTY-лінії.
    #     enable_secret (str): Enable secret для привілейованого режиму.
    #     timeout (int): Таймаут підключення у секундах.
    #
    # Returns:
    #     dict: {"ok": bool, "error": str}

    global _connection, _connection_info

    # Закриваємо попереднє з'єднання якщо є
    if _connection is not None:
        try:
            _connection.disconnect()
        except Exception:
            pass
        _connection = None
        _connection_info = {}

    device_params = {
        "device_type": "cisco_ios_telnet",
        "host": host.strip(),
        "port": int(port),
        "username": username.strip(),
        "password": password,
        "secret": enable_secret if enable_secret else password,
        "timeout": timeout,
        "session_timeout": 60,
        "conn_timeout": timeout,
        # Дозволяє підключення без username (no login / login local)
        "global_delay_factor": 2,
    }

    logger.info(f"Підключення до роутера {host}:{port} (user='{username or 'noauth'}')")

    try:
        conn = ConnectHandler(**device_params)

        # Входимо в privileged exec якщо є enable_secret
        if enable_secret:
            try:
                conn.enable()
                logger.info(f"Успішно активовано privileged exec на {host}")
            except Exception as e:
                logger.warning(f"Не вдалося увійти в enable mode: {e}")

        _connection = conn
        _connection_info = {"host": host, "port": port}
        logger.info(f"З'єднання з {host}:{port} встановлено успішно")
        return {"ok": True, "error": ""}

    except NetmikoAuthenticationException as e:
        logger.error(f"Помилка автентифікації при підключенні до {host}: {e}")
        return {"ok": False, "error": f"Authentication failed: {str(e)}"}

    except NetmikoTimeoutException as e:
        logger.error(f"Timeout при підключенні до {host}:{port}: {e}")
        return {"ok": False, "error": f"Connection timeout ({timeout}s): check IP and port"}

    except Exception as e:
        logger.error(f"Невідома помилка при підключенні до {host}: {e}")
        return {"ok": False, "error": str(e)}


def disconnect() -> dict:
    # Закриває поточне Telnet-з'єднання з роутером.
    #
    # Returns:
    #     dict: {"ok": bool}

    global _connection, _connection_info

    if _connection is None:
        return {"ok": True}

    try:
        _connection.disconnect()
        logger.info(f"З'єднання з {_connection_info.get('host', '?')} закрито")
    except Exception as e:
        logger.warning(f"Помилка при закритті з'єднання: {e}")
    finally:
        _connection = None
        _connection_info = {}

    return {"ok": True}


def deploy_config(config_lines: list[str]) -> dict:
    # Надсилає список команд конфігурації на підключений роутер.
    #
    # Використовує send_config_set() який автоматично входить у
    # configuration terminal і виходить після виконання всіх команд.
    # Рядки "end" та "write memory" виконуються окремо (поза conf t).
    #
    # Args:
    #     config_lines (list[str]): Список команд Cisco IOS.
    #
    # Returns:
    #     dict: {"ok": bool, "output": str, "error": str}

    global _connection

    if _connection is None or not _connection.is_alive():
        logger.error("Спроба деплою без активного з'єднання")
        return {"ok": False, "output": "", "error": "No active connection. Please connect to router first."}

    if not config_lines:
        return {"ok": False, "output": "", "error": "No configuration commands to send."}

    logger.info(f"Починаємо деплой {len(config_lines)} рядків конфігурації")

    try:
        # Відокремлюємо термінальні команди від основного конфігу
        # "end" і "write memory" не можна надсилати через send_config_set
        terminal_cmds = []
        config_body = []

        for line in config_lines:
            stripped = line.strip()
            if stripped in ("end", "write memory", "wr"):
                terminal_cmds.append(stripped)
            elif stripped == "!":
                continue  # Пропускаємо коментарі
            else:
                config_body.append(line)

        output_parts = []

        # Надсилаємо основну конфігурацію
        if config_body:
            output = _connection.send_config_set(
                config_body,
                enter_config_mode=True,
                exit_config_mode=True,
                delay_factor=2,
            )
            output_parts.append(output)
            logger.info("Основна конфігурація відправлена успішно")

        # Виконуємо термінальні команди (end, write memory)
        for cmd in terminal_cmds:
            out = _connection.send_command(cmd, expect_string=r"[>#]", delay_factor=3)
            output_parts.append(f"{cmd}\n{out}")
            logger.info(f"Виконано команду: {cmd}")

        full_output = "\n".join(output_parts)
        logger.info("Деплой завершено успішно")
        return {"ok": True, "output": full_output, "error": ""}

    except Exception as e:
        logger.error(f"Помилка деплою конфігурації: {e}")
        return {"ok": False, "output": "", "error": str(e)}
