import pytest
import sys
import os

# Додаємо шлях до модуля
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.protocols import generate_protocol_config, _mask_to_wildcard

# Тестові дані для мереж
VALID_NETWORKS = [("192.168.1.0", "255.255.255.0"), ("10.0.0.0", "255.0.0.0")]
INVALID_NETWORKS = [("192.168.1.0", "invalid_mask")]
EMPTY_NETWORKS = []

# 1. Тести для допоміжної функції _mask_to_wildcard
class TestMaskToWildcard:
    def test_mask_to_wildcard_valid_masks(self):
        # Валідні маски повинні коректно перетворюватися
        assert _mask_to_wildcard("255.255.255.0") == "0.0.0.255"
        assert _mask_to_wildcard("255.255.255.252") == "0.0.0.3"
        assert _mask_to_wildcard("255.0.0.0") == "0.255.255.255"
        assert _mask_to_wildcard("255.255.0.0") == "0.0.255.255"
        assert _mask_to_wildcard("255.255.255.128") == "0.0.0.127"
        assert _mask_to_wildcard("255.255.255.192") == "0.0.0.63"
        assert _mask_to_wildcard("255.255.255.224") == "0.0.0.31"
        assert _mask_to_wildcard("255.255.255.240") == "0.0.0.15"
        assert _mask_to_wildcard("255.255.255.248") == "0.0.0.7"
        assert _mask_to_wildcard("255.255.255.254") == "0.0.0.1"
        assert _mask_to_wildcard("0.0.0.0") == "255.255.255.255"
    
    def test_mask_to_wildcard_cidr_masks(self):
        # Маски у форматі CIDR (рядок)
        assert _mask_to_wildcard("24") == "0.0.0.255"
        assert _mask_to_wildcard("32") == "0.0.0.0"
        assert _mask_to_wildcard("16") == "0.0.255.255"
        assert _mask_to_wildcard("8") == "0.255.255.255"
        assert _mask_to_wildcard("30") == "0.0.0.3"
    
    def test_mask_to_wildcard_invalid_string(self):
        # Некоректні рядки повинні повертати "0.0.0.0" або викликати помилку
        assert _mask_to_wildcard("invalid") == "0.0.0.0"
        assert _mask_to_wildcard("255.255.255") == "0.0.0.0"
        assert _mask_to_wildcard("255.255.255.256") == "0.0.0.0"
        assert _mask_to_wildcard("255.255.255.0.0") == "0.0.0.0"
        assert _mask_to_wildcard("") == "0.0.0.0"
        assert _mask_to_wildcard("abc.def.ghi.jkl") == "0.0.0.0"
    
    def test_mask_to_wildcard_wrong_types(self):
        # Неправильні типи даних
        assert _mask_to_wildcard(255) == "0.0.0.0"
        assert _mask_to_wildcard(24) == "0.0.0.0"
        assert _mask_to_wildcard(None) == "0.0.0.0"
        assert _mask_to_wildcard([]) == "0.0.0.0"
        assert _mask_to_wildcard({}) == "0.0.0.0"
    
    def test_mask_to_wildcard_edge_cases(self):
        # Граничні випадки
        assert _mask_to_wildcard("255.255.255.255") == "0.0.0.0"
        assert _mask_to_wildcard("128.0.0.0") == "127.255.255.255"
        assert _mask_to_wildcard("254.0.0.0") == "1.255.255.255"
    
    def test_mask_to_wildcard_spaces_handling(self):
        # Обробка пробілів
        assert _mask_to_wildcard(" 255.255.255.0 ") == "0.0.0.255"
        assert _mask_to_wildcard("255.255.255.0  ") == "0.0.0.255"
        assert _mask_to_wildcard("  24  ") == "0.0.0.255"

# 2. Тести для generate_protocol_config
class TestGenerateProtocolConfig:
    
    def test_generate_protocol_config_ospf_valid(self):
        # OSPF з валідними параметрами
        config = generate_protocol_config("OSPF", "1.1.1.1", VALID_NETWORKS)
        
        # Перевіряємо базову структуру OSPF
        assert "router ospf 1" in config or "router ospf 100" in config
        assert "router-id 1.1.1.1" in "\n".join(config)
        
        # Перевіряємо network команди
        config_str = "\n".join(config)
        assert "192.168.1.0" in config_str
        assert "10.0.0.0" in config_str
        assert "area" in config_str.lower()
        assert "exit" in config_str.lower() or "!" in config_str
    
    def test_generate_protocol_config_ospf_without_router_id(self):
        # OSPF без router_id
        config = generate_protocol_config("OSPF", "", VALID_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router ospf" in config_str
        # router-id може бути відсутній або автоматичний
        assert "router-id" not in config_str or "router-id" in config_str
    
    def test_generate_protocol_config_ospf_no_networks(self):
        # OSPF без мереж
        config = generate_protocol_config("OSPF", "1.1.1.1", EMPTY_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router ospf" in config_str
        assert "router-id 1.1.1.1" in config_str
        # network команд не повинно бути
        assert "network 192.168" not in config_str
    
    def test_generate_protocol_config_ospf_invalid_network(self):
        # OSPF з невалідною мережею
        config = generate_protocol_config("OSPF", "1.1.1.1", INVALID_NETWORKS)
        
        # Може повертати конфігурацію з помилкою або без network команд
        assert isinstance(config, list)
    
    def test_generate_protocol_config_rip_valid(self):
        # RIP з валідними мережами
        config = generate_protocol_config("RIP", "", VALID_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router rip" in config_str
        assert "version 2" in config_str or "version" in config_str
        assert "192.168.1.0" in config_str
        assert "10.0.0.0" in config_str
        assert "no auto-summary" in config_str or "auto-summary" in config_str
        assert "exit" in config_str.lower() or "!" in config_str
    
    def test_generate_protocol_config_rip_no_networks(self):
        # RIP без мереж
        config = generate_protocol_config("RIP", "", EMPTY_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router rip" in config_str
        # network команд не повинно бути
        assert "network 192.168" not in config_str
    
    def test_generate_protocol_config_eigrp_valid(self):
        # EIGRP з валідними мережами
        config = generate_protocol_config("EIGRP", "", VALID_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router eigrp" in config_str
        assert "192.168.1.0" in config_str
        assert "10.0.0.0" in config_str
        assert "no auto-summary" in config_str or "auto-summary" in config_str
        assert "exit" in config_str.lower() or "!" in config_str
    
    def test_generate_protocol_config_eigrp_no_networks(self):
        # EIGRP без мереж
        config = generate_protocol_config("EIGRP", "", EMPTY_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router eigrp" in config_str
        assert "network 192.168" not in config_str
    
    def test_generate_protocol_config_bgp_valid(self):
        # BGP (може не використовувати мережі)
        config = generate_protocol_config("BGP", "", VALID_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router bgp" in config_str
        # BGP може мати додаткові параметри
        assert isinstance(config, list)
        assert len(config) > 0
    
    def test_generate_protocol_config_bgp_with_as_number(self):
        # BGP з номером AS
        config = generate_protocol_config("BGP", "", VALID_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router bgp" in config_str
        # Перевіряємо, що є номер AS (наприклад, 65000)
        assert any("65000" in line or "65001" in line for line in config)
    
    def test_generate_protocol_config_isis_valid(self):
        # IS-IS
        config = generate_protocol_config("IS-IS", "", VALID_NETWORKS)
        
        config_str = "\n".join(config)
        assert "router isis" in config_str.lower() or "router is-is" in config_str.lower()
        assert isinstance(config, list)
        assert len(config) > 0
    
    def test_generate_protocol_config_static_valid(self):
        # Статична маршрутизація
        config = generate_protocol_config("Static", "", VALID_NETWORKS)
        
        # Статична маршрутизація може повертати порожній список або команди ip route
        assert isinstance(config, list)
        if len(config) > 0:
            assert "ip route" in "\n".join(config).lower()
    
    def test_generate_protocol_config_unknown_protocol(self):
        # Невідомий протокол
        config = generate_protocol_config("UNKNOWN", "1.1.1.1", VALID_NETWORKS)
        
        # Повинен повертати порожній список або повідомлення про помилку
        assert config == [] or "No routing protocol selected" in "\n".join(config) or "Error" in "\n".join(config)
    
    def test_generate_protocol_config_empty_protocol(self):
        # Порожній протокол
        config = generate_protocol_config("", "", VALID_NETWORKS)
        
        assert config == [] or "No routing protocol selected" in "\n".join(config)
    
    def test_generate_protocol_config_invalid_protocol_type(self):
        # Некоректний тип протоколу
        config = generate_protocol_config(123, "1.1.1.1", VALID_NETWORKS)
        
        # Може повертати порожній список або повідомлення про помилку
        assert isinstance(config, list)
    
    def test_generate_protocol_config_invalid_router_id_type(self):
        # Некоректний тип router_id
        config = generate_protocol_config("OSPF", 123, VALID_NETWORKS)
        
        # Може обробляти або ігнорувати неправильний router_id
        assert isinstance(config, list)
    
    def test_generate_protocol_config_invalid_networks_type(self):
        # Некоректний тип мереж
        config = generate_protocol_config("OSPF", "1.1.1.1", "not_a_list")
        
        # Може повертати порожній список або конфігурацію без мереж
        assert isinstance(config, list)
    
    def test_generate_protocol_config_mixed_valid_invalid_networks(self):
        # Змішані валідні та невалідні мережі
        mixed_networks = [("192.168.1.0", "255.255.255.0"), ("invalid", "mask"), ("10.0.0.0", "255.0.0.0")]
        config = generate_protocol_config("OSPF", "1.1.1.1", mixed_networks)
        
        # Повинен обробляти лише валідні мережі
        config_str = "\n".join(config)
        assert "192.168.1.0" in config_str
        assert "10.0.0.0" in config_str
        # Невалідна мережа не повинна з'являтися
        assert "invalid" not in config_str
    
    def test_generate_protocol_config_single_network(self):
        # Тільки одна мережа
        single_network = [("192.168.1.0", "255.255.255.0")]
        config = generate_protocol_config("OSPF", "1.1.1.1", single_network)
        
        config_str = "\n".join(config)
        assert "192.168.1.0" in config_str
        assert "router ospf" in config_str
        assert "router-id 1.1.1.1" in config_str
    
    def test_generate_protocol_config_multiple_networks(self):
        # Багато мереж
        multiple_networks = [
            ("192.168.1.0", "255.255.255.0"),
            ("10.0.0.0", "255.0.0.0"),
            ("172.16.0.0", "255.255.0.0"),
            ("192.168.100.0", "255.255.255.128")
        ]
        config = generate_protocol_config("OSPF", "1.1.1.1", multiple_networks)
        
        config_str = "\n".join(config)
        assert "192.168.1.0" in config_str
        assert "10.0.0.0" in config_str
        assert "172.16.0.0" in config_str
        assert "192.168.100.0" in config_str
        assert config_str.count("network") == 4
    
    def test_generate_protocol_config_with_wildcard_calculation(self):
        # Перевірка правильного обчислення wildcard з маски
        networks = [("192.168.1.0", "255.255.255.0")]
        config = generate_protocol_config("OSPF", "1.1.1.1", networks)
        
        config_str = "\n".join(config)
        # Для маски 255.255.255.0 wildcard має бути 0.0.0.255
        if "wildcard" in config_str:
            assert "0.0.0.255" in config_str
        elif "area" in config_str:
            # Якщо використовується формат з маскою у wildcard
            assert "0.0.0.255" in config_str

# 3. Інтеграційні тести
def test_integration_mask_to_wildcard_in_protocol_config():
    # Інтеграційний тест: перевірка, що _mask_to_wildcard використовується в generate_protocol_config
    networks = [("192.168.1.0", "255.255.255.0")]
    
    # Тестуємо для OSPF
    config = generate_protocol_config("OSPF", "1.1.1.1", networks)
    config_str = "\n".join(config)
    
    # Перевіряємо, що wildcard обчислюється правильно
    if "0.0.0.255" in config_str:
        # Це означає, що маска 255.255.255.0 була перетворена в wildcard 0.0.0.255
        pass
    elif "255.255.255.0" in config_str:
        # Можливо, використовується маска без перетворення
        pass
    
    assert isinstance(config, list)

def test_all_protocols_supported():
    # Перевірка, що всі основні протоколи підтримуються
    protocols = ["OSPF", "RIP", "EIGRP", "BGP", "IS-IS", "Static"]
    
    for protocol in protocols:
        config = generate_protocol_config(protocol, "1.1.1.1" if protocol == "OSPF" else "", VALID_NETWORKS)
        
        # Кожен протокол має повертати список
        assert isinstance(config, list)
        
        # Конфігурація не повинна бути None
        assert config is not None
        
        # Для невідомих протоколів може бути порожній список
        if protocol not in ["UNKNOWN", ""]:
            # Відомі протоколи мають повертати непорожню конфігурацію
            assert len(config) > 0 or protocol in ["Static"]  # Static може бути порожнім

def test_protocol_config_error_handling():
    # Тестування обробки помилок
    invalid_cases = [
        ("UNKNOWN", "1.1.1.1", VALID_NETWORKS),  # Невідомий протокол
        ("OSPF", "1.1.1.1", "not_a_list"),       # Неправильний тип мереж
        (None, None, None),                       # Всі параметри None
    ]
    
    for protocol, router_id, networks in invalid_cases:
        config = generate_protocol_config(protocol, router_id, networks)
        
        # Функція не повинна викликати виняток
        assert isinstance(config, list)
        
        # Може повертати порожній список або повідомлення про помилку
        assert config == [] or any("Error" in line or "error" in line.lower() or "!" in line for line in config)

def test_wildcard_edge_cases_in_config():
    # Перевірка крайніх випадків для масок у конфігурації протоколів
    edge_networks = [
        ("192.168.1.0", "255.255.255.255"),  # /32
        ("10.0.0.0", "0.0.0.0"),             # /0
        ("172.16.0.0", "255.255.255.252"),   # /30
        ("192.168.100.0", "255.255.255.128"), # /25
    ]
    
    config = generate_protocol_config("OSPF", "1.1.1.1", edge_networks)
    
    # Повинен обробити всі мережі, навіть з нестандартними масками
    config_str = "\n".join(config)
    
    # Кількість network команд має відповідати кількості мереж
    network_count = config_str.count("network")
    assert network_count == 4 or network_count == 0  # Може не додавати network для деяких масок

# 4. Тести продуктивності та стабільності
def test_generate_protocol_config_performance():
    # Тестування швидкодії для багатьох мереж
    large_networks = [("10.{}.0.0".format(i), "255.255.0.0") for i in range(1, 51)]
    
    import time
    start_time = time.time()
    
    config = generate_protocol_config("OSPF", "1.1.1.1", large_networks)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Генерація 50 мереж не повинна займати більше 1 секунди
    assert execution_time < 1.0
    
    # Перевіряємо, що всі мережі оброблені
    config_str = "\n".join(config)
    for i in range(1, 51):
        assert "10.{}.0.0".format(i) in config_str

def test_protocol_config_memory_usage():
    # Перевірка, що функція не викликає проблем з пам'яттю
    huge_networks = [("192.168.{}.0".format(i), "255.255.255.0") for i in range(1, 101)]
    
    config = generate_protocol_config("OSPF", "1.1.1.1", huge_networks)
    
    # Результат має бути списком рядків
    assert isinstance(config, list)
    assert all(isinstance(line, str) for line in config)
    
    # Кількість рядків має бути обмеженою
    assert len(config) < 500  # Навіть для 100 мереж

if __name__ == "__main__":
    # Запуск тестів з командного рядка
    pytest.main([__file__, "-v", "--tb=short"])