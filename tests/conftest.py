import pytest
import sys
import types
import os

# Додаємо корінь проєкту в sys.path, щоб тести бачили папку backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Глобальний мок для Eel 
@pytest.fixture(scope="session", autouse=True)
def mock_eel():
    if 'eel' not in sys.modules:
        eel_stub = types.SimpleNamespace(
            init=lambda *a, **k: None,
            expose=lambda f: f,  # Дозволяє декораторам @eel.expose працювати без помилок
            start=lambda *a, **k: None
        )
        sys.modules['eel'] = eel_stub

# 2. Фікстури з тестовими даними 
@pytest.fixture
def valid_networks_list():
    #Стандартний валідний список мереж для тестів
    return [
        ("192.168.1.1", "255.255.255.0"), 
        ("10.0.0.1", "255.255.255.252")
    ]

@pytest.fixture
def valid_interfaces_list():
    #Стандартний валідний список імен інтерфейсів
    return ["GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2"]

@pytest.fixture
def valid_telephony_data():
    #Дані для тестів телефонії 
    return [
        {"number": "1001", "user": "User 1", "mac": "0011.2233.4455"},
        {"number": "1002", "user": "User 2", "mac": "AABB.CCDD.EEFF"}
    ]

@pytest.fixture
def valid_bgp_data():
    #Дані для тестування протоколу BGP
    return {
        "router_id": "1.1.1.1",
        "local_as": "65000",
        "neighbors": [{"ip": "10.0.0.2", "remoteAs": "65001"}],
        "networks": [("192.168.1.0", "255.255.255.0")]
    }

@pytest.fixture
def valid_isis_data():
    #Дані для тестування протоколу IS-IS
    return {
        "area_id": "49.0001",
        "system_id": "0000.0000.0001",
        "router_type": "level-2-only",
        "interfaces": ["GigabitEthernet0/0"]
    }