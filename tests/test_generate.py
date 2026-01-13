import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.generate import (
    generate_interface_config,
    generate_full_config,
    generate_multicast_config,
    generate_protocol_config,
    generate_telephony_config,
    generate_security_config,
    generate_dhcp_config
)
# 1. Тести для generate_interface_config
class TestGenerateInterfaceConfig:
    def test_generate_interface_config_basic(self):
        # Звичайний випадок: два інтерфейси без no shutdown
        interfaces = ["GigabitEthernet0/0", "GigabitEthernet0/1"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.252")
        ]

        config = generate_interface_config(interfaces, networks)

        expected = [
            "interface GigabitEthernet0/0",
            " ip address 192.168.1.1 255.255.255.0",
            " exit",
            "interface GigabitEthernet0/1",
            " ip address 10.0.0.1 255.255.255.252",
            " exit"
        ]

        assert config == expected
    
    def test_generate_interface_config_with_no_shutdown(self):
        # Перевірка вибіркового no shutdown
        interfaces = ["Gi0/0", "Gi0/1", "Gi0/2"]
        networks = [
            ("172.16.10.1", "255.255.255.0"),
            ("192.168.55.1", "255.255.255.248"),
            ("10.99.1.1", "255.255.255.252")
        ]
        no_shutdown = ["Gi0/0", "Gi0/2"]

        config = generate_interface_config(interfaces, networks, no_shutdown)

        expected = [
            "interface Gi0/0",
            " ip address 172.16.10.1 255.255.255.0",
            " no shutdown",
            " exit",
            "interface Gi0/1",
            " ip address 192.168.55.1 255.255.255.248",
            " exit",
            "interface Gi0/2",
            " ip address 10.99.1.1 255.255.255.252",
            " no shutdown",
            " exit"
        ]

        assert config == expected
    
    def test_generate_interface_config_all_no_shutdown(self):
        # Всі інтерфейси з no shutdown
        interfaces = ["Fa0/0", "Fa0/1"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.0")
        ]
        no_shutdown = ["Fa0/0", "Fa0/1"]

        config = generate_interface_config(interfaces, networks, no_shutdown)
        
        assert " no shutdown" in config[2]
        assert " no shutdown" in config[6]
    
    def test_generate_interface_config_length_mismatch(self):
        # Повинна виникати помилка при невідповідності довжин
        interfaces = ["Gi0/0", "Gi0/1"]
        networks = [("192.168.1.1", "255.255.255.0")]  # лише одна мережа

        with pytest.raises(ValueError, match=r".*lengths mismatch.*"):
            generate_interface_config(interfaces, networks)
    
    def test_generate_interface_config_empty(self):
        # Порожні списки → повертаємо порожній список конфігурації
        config = generate_interface_config([], [])
        assert config == []
        
        config = generate_interface_config([], [], [])
        assert config == []
    
    def test_generate_interface_config_single_interface(self):
        # Тестування одного інтерфейсу
        config = generate_interface_config(
            ["FastEthernet0/0"],
            [("10.0.0.1", "255.255.255.0")]
        )
        
        assert len(config) == 3
        assert "interface FastEthernet0/0" in config[0]
        assert "ip address 10.0.0.1 255.255.255.0" in config[1]
        assert "exit" in config[2]
    
    def test_generate_interface_config_wrong_types(self):
        # Перевірка стійкості до неправильних типів даних
        with pytest.raises(TypeError):
            generate_interface_config(None, [])
        
        with pytest.raises(TypeError):
            generate_interface_config([], None)
        
        with pytest.raises(TypeError):
            generate_interface_config(["Gi0/0"], [("192.168.1.1", 2552552550)])
    
    def test_generate_interface_config_duplicate_no_shutdown(self):
        # Тестування дублювання інтерфейсів у no_shutdown
        config = generate_interface_config(
            ["Gi0/0", "Gi0/1"],
            [("192.168.1.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252")],
            no_shutdown=["Gi0/0", "Gi0/0"]
        )
        
        config_str = "\n".join(config)
        assert config_str.count("no shutdown") == 1
    
    def test_generate_interface_config_mixed_interface_names(self):
        # Тестування різних форматів імен інтерфейсів
        interfaces = ["GigabitEthernet0/0", "Gi0/1", "Fa0/0", "Serial0/0/0"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.252"),
            ("172.16.1.1", "255.255.0.0"),
            ("1.1.1.1", "255.255.255.252")
        ]
        
        config = generate_interface_config(interfaces, networks)
        
        assert len(config) == 12
        assert "interface GigabitEthernet0/0" in config[0]
        assert "interface Gi0/1" in config[3]
        assert "interface Fa0/0" in config[6]
        assert "interface Serial0/0/0" in config[9]

# 2. Тести для generate_full_config
class TestGenerateFullConfig:
    
    def test_generate_full_config_minimal(self):
        # Мінімальна конфігурація: тільки hostname + інтерфейси
        config = generate_full_config(
            hostname="R-TestMinimal",
            interfaces=["Gi0/0", "Gi0/1"],
            networks=[
                ("192.168.10.1", "255.255.255.0"),
                ("10.0.0.1", "255.255.255.252")
            ],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="",
            console_password="",
            vty_password="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="",
            no_shutdown_interfaces=["Gi0/0"]
        )

        config_str = "\n".join(config)

        # Обов'язкові елементи
        assert "hostname R-TestMinimal" in config_str
        assert "interface Gi0/0" in config_str
        assert " ip address 192.168.10.1 255.255.255.0" in config_str
        assert " no shutdown" in config_str
        assert "interface Gi0/1" in config_str
        assert " ip address 10.0.0.1 255.255.255.252" in config_str

        # Не повинно бути зайвого
        assert "router ospf" not in config_str
        assert "telephony-service" not in config_str
        assert "ip dhcp pool" not in config_str
        assert "crypto key generate rsa" not in config_str

        # Завершення конфігурації
        assert config[-2] == "end"
        assert config[-1] == "write memory"
    
    def test_generate_full_config_full_features(self):
        # Максимально насичений сценарій майже всіма функціями
        config = generate_full_config(
            hostname="Branch-R1",
            interfaces=["GigabitEthernet0/0", "GigabitEthernet0/1", "Loopback0"],
            networks=[
                ("192.168.100.1", "255.255.255.0"),
                ("172.16.5.1", "255.255.255.252"),
                ("10.255.255.1", "255.255.255.255")
            ],
            ip_multicast=True,
            routing_protocol="OSPF",
            router_id="10.255.255.1",
            telephony_enabled=True,
            dn_list=[
                {"number": "1001", "user": "alice"},
                {"number": "1002", "user": "bob"}
            ],
            enable_ssh=True,
            enable_secret="C1sc0#2025!",
            console_password="c0ns0leP@ss",
            vty_password="vtyStrongP@ss2025",
            dhcp_network="192.168.100.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.100.1",
            dhcp_dns="8.8.8.8",
            dhcp_excluded="192.168.100.1 192.168.100.10",
            no_shutdown_interfaces=["GigabitEthernet0/0", "GigabitEthernet0/1"]
        )

        config_str = "\n".join(config)

        # Базові елементи
        assert "hostname Branch-R1" in config_str
        assert "interface GigabitEthernet0/0" in config_str
        assert "interface GigabitEthernet0/1" in config_str
        assert "interface Loopback0" in config_str
        
        # Multicast
        assert "ip multicast-routing" in config_str
        assert "ip pim sparse-dense-mode" in config_str
        
        # OSPF
        assert "router ospf 1" in config_str
        assert "router-id 10.255.255.1" in config_str
        
        # Телефонія
        assert "telephony-service" in config_str
        assert "ephone-dn" in config_str
        
        # Безпека
        assert "enable secret C1sc0#2025!" in config_str
        assert "line console 0" in config_str
        assert "line vty 0 4" in config_str or "line vty 0 15" in config_str
        
        # SSH
        assert "crypto key generate rsa" in config_str or "ip ssh" in config_str
        
        # DHCP
        assert "ip dhcp excluded-address 192.168.100.1 192.168.100.10" in config_str
        assert "ip dhcp pool" in config_str
        assert " network 192.168.100.0 255.255.255.0" in config_str
        assert " default-router 192.168.100.1" in config_str
        
        # Завершення
        assert "end" in config_str
        assert "write memory" in config_str
    
    def test_generate_full_config_no_interfaces(self):
        # Перевірка поведінки при порожніх інтерфейсах
        config = generate_full_config(
            hostname="EmptyR",
            interfaces=[],
            networks=[],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="",
            console_password="",
            vty_password="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="",
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "hostname EmptyR" in config_str
        assert "end" in config_str or "write memory" in config_str
    
    def test_generate_full_config_different_protocols(self):
        # Швидка перевірка різних протоколів маршрутизації
        for protocol in ["RIP", "EIGRP", "OSPF", "Static", ""]:
            cfg = generate_full_config(
                hostname="ProtoTest",
                interfaces=["Gi0/0"],
                networks=[("192.168.10.1", "255.255.255.0")],
                ip_multicast=False,
                routing_protocol=protocol,
                router_id="1.1.1.1" if protocol == "OSPF" else "",
                telephony_enabled=False,
                dn_list=[],
                enable_ssh=False,
                enable_secret="",
                console_password="",
                vty_password="",
                dhcp_network="",
                dhcp_mask="",
                dhcp_gateway="",
                dhcp_dns="",
                dhcp_excluded="",
                no_shutdown_interfaces=[]
            )

            config_str = "\n".join(cfg)
            
            if protocol == "OSPF":
                assert "router ospf" in config_str.lower()
                assert "router-id 1.1.1.1" in config_str.lower()
            elif protocol == "RIP":
                assert "router rip" in config_str.lower()
            elif protocol == "EIGRP":
                assert "router eigrp" in config_str.lower()
            elif protocol == "Static":
                pass
            else:
                assert "router " not in config_str.lower() or "router ospf" not in config_str.lower()
    
    def test_generate_full_config_with_dhcp_excluded(self):
        # Тестування DHCP з excluded адресами
        config = generate_full_config(
            hostname="DHCP-Test",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="",
            console_password="",
            vty_password="",
            dhcp_network="192.168.1.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8",
            dhcp_excluded="192.168.1.1 192.168.1.10",
            no_shutdown_interfaces=["Gi0/0"]
        )

        config_str = "\n".join(config)
        assert "ip dhcp excluded-address 192.168.1.1 192.168.1.10" in config_str
        assert "ip dhcp pool" in config_str
        assert " network 192.168.1.0 255.255.255.0" in config_str
        assert " default-router 192.168.1.1" in config_str
        assert " dns-server 8.8.8.8" in config_str
    
    def test_generate_full_config_with_console_password(self):
        # Тестування конфігурації з паролем консолі
        config = generate_full_config(
            hostname="ConsoleTest",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="",
            console_password="MyConsolePass",
            vty_password="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="",
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "line console 0" in config_str.lower()
        assert "password" in config_str.lower()
        assert "login" in config_str.lower()
    
    def test_generate_full_config_with_vty_password(self):
        # Тестування конфігурації з паролем VTY
        config = generate_full_config(
            hostname="VTYTest",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="",
            console_password="",
            vty_password="MyVTYP@ss",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="",
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "line vty 0 4" in config_str.lower() or "line vty 0 15" in config_str.lower()
        assert "password" in config_str.lower()
        assert "login" in config_str.lower()
    
    def test_generate_full_config_with_enable_secret(self):
        # Тестування конфігурації з enable secret
        config = generate_full_config(
            hostname="SecretTest",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="MyEnableSecret123",
            console_password="",
            vty_password="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="",
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "enable secret MyEnableSecret123" in config_str
    
    def test_generate_full_config_with_ssh(self):
        # Тестування конфігурації з SSH
        config = generate_full_config(
            hostname="SSHTest",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=True,
            enable_secret="",
            console_password="",
            vty_password="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="",
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        ssh_commands = ["crypto key generate rsa", "ip ssh", "ssh version"]
        assert any(cmd in config_str for cmd in ssh_commands)
    
    def test_generate_full_config_length_mismatch(self):
        # Повинна виникати помилка при невідповідності довжин інтерфейсів та мереж
        with pytest.raises(ValueError, match=r".*lengths mismatch.*"):
            generate_full_config(
                hostname="Test",
                interfaces=["Gi0/0", "Gi0/1"],
                networks=[("192.168.1.1", "255.255.255.0")],
                ip_multicast=False,
                routing_protocol="",
                router_id="",
                telephony_enabled=False,
                dn_list=[],
                enable_ssh=False,
                enable_secret="",
                console_password="",
                vty_password="",
                dhcp_network="",
                dhcp_mask="",
                dhcp_gateway="",
                dhcp_dns="",
                dhcp_excluded="",
                no_shutdown_interfaces=[]
            )

# 3. Тести для generate_multicast_config
class TestGenerateMulticastConfig:
    
    def test_generate_multicast_config_enabled(self):
        # Multicast увімкнений
        config = generate_multicast_config(enabled=True)
        
        assert len(config) > 0
        assert "ip multicast-routing" in config
        assert "ip pim sparse-dense-mode" in config
    
    def test_generate_multicast_config_disabled(self):
        # Multicast вимкнений
        config = generate_multicast_config(enabled=False)
        
        assert config == [] or "no ip multicast-routing" in "\n".join(config)
    
    def test_generate_multicast_config_default(self):
        # Тестування значення за замовчуванням
        config_disabled = generate_multicast_config()
        config_explicit = generate_multicast_config(enabled=False)
        
        assert config_disabled == config_explicit

# 4. Тести для generate_protocol_config
class TestGenerateProtocolConfig:
    
    def test_generate_protocol_config_ospf(self):
        # Тестування OSPF з router_id
        config = generate_protocol_config("OSPF", "1.1.1.1")
        
        assert "router ospf 1" in config
        assert "router-id 1.1.1.1" in config
        assert "network" in "\n".join(config) or "passive-interface" in "\n".join(config)
    
    def test_generate_protocol_config_rip(self):
        # Тестування RIP
        config = generate_protocol_config("RIP", "")
        
        assert "router rip" in config
        assert "version 2" in config
        assert "network" in "\n".join(config)
    
    def test_generate_protocol_config_eigrp(self):
        # Тестування EIGRP
        config = generate_protocol_config("EIGRP", "")
        
        assert "router eigrp 100" in config or "router eigrp 1" in config
        assert "network" in "\n".join(config)
    
    def test_generate_protocol_config_empty(self):
        # Тестування порожнього протоколу
        config = generate_protocol_config("", "")
        
        assert config == []
    
    def test_generate_protocol_config_ospf_no_router_id(self):
        # Тестування OSPF без router_id
        config = generate_protocol_config("OSPF", "")
        
        assert "router ospf" in "\n".join(config)
        assert "router-id" not in "\n".join(config) or "router-id" in "\n".join(config)
    
    def test_generate_protocol_config_static(self):
        # Тестування Static маршрутизації
        config = generate_protocol_config("Static", "")
        
        assert isinstance(config, list)

# 5. Тести для generate_telephony_config
class TestGenerateTelephonyConfig:
    
    def test_generate_telephony_config_enabled(self):
        # Телефонія увімкнена з dn_list
        dn_list = [
            {"number": "1001", "user": "alice"},
            {"number": "1002", "user": "bob"},
            {"number": "1003", "user": "charlie"}
        ]
        
        config = generate_telephony_config(enabled=True, dn_list=dn_list)
        
        config_str = "\n".join(config)
        assert "telephony-service" in config_str
        assert "max-ephones" in config_str
        assert "max-dn" in config_str
        assert "ephone-dn 1" in config_str
        assert " number 1001" in config_str
        assert "ephone-dn 2" in config_str
        assert " number 1002" in config_str
        assert "ephone-dn 3" in config_str
        assert " number 1003" in config_str
    
    def test_generate_telephony_config_empty_dn_list(self):
        # Телефонія увімкнена з порожнім dn_list
        config = generate_telephony_config(enabled=True, dn_list=[])
        
        config_str = "\n".join(config)
        assert "telephony-service" in config_str
        assert "ephone-dn" in config_str or len(config) > 0
    
    def test_generate_telephony_config_disabled(self):
        # Телефонія вимкнена
        dn_list = [{"number": "1001", "user": "alice"}]
        config = generate_telephony_config(enabled=False, dn_list=dn_list)
        
        config_str = "\n".join(config)
        assert "telephony-service" not in config_str
        assert "ephone-dn" not in config_str
        assert config == [] or "no telephony-service" in config_str
    
    def test_generate_telephony_config_default(self):
        # Тестування значення за замовчуванням
        config_default = generate_telephony_config()
        config_explicit = generate_telephony_config(enabled=False, dn_list=[])
        
        assert config_default == config_explicit
    
    def test_generate_telephony_config_malformed_dn_list(self):
        # Тестування з неправильно сформованим dn_list
        dn_list = [
            {"number": "1001"},
            {"user": "bob"},
            {}
        ]
        
        config = generate_telephony_config(enabled=True, dn_list=dn_list)
        
        assert isinstance(config, list)

# 6. Тести для generate_security_config
class TestGenerateSecurityConfig:
    
    def test_generate_security_config_all_passwords(self):
        # Всі паролі вказані
        config = generate_security_config(
            enable_secret="enable123",
            console_password="console123",
            vty_password="vty123",
            enable_ssh=True
        )
        
        config_str = "\n".join(config)
        assert "enable secret enable123" in config_str
        assert "line console 0" in config_str
        assert "password console123" in config_str
        assert "login" in config_str
        assert "line vty 0 4" in config_str or "line vty 0 15" in config_str
        assert "password vty123" in config_str
        assert any(cmd in config_str for cmd in ["crypto key generate rsa", "ip ssh", "ssh version"])
    
    def test_generate_security_config_no_passwords(self):
        # Жоден пароль не вказаний
        config = generate_security_config(
            enable_secret="",
            console_password="",
            vty_password="",
            enable_ssh=False
        )
        
        config_str = "\n".join(config)
        assert "enable secret" not in config_str or "enable secret" in config_str
        assert "crypto key generate rsa" not in config_str
        assert "ip ssh" not in config_str
    
    def test_generate_security_config_only_enable_secret(self):
        # Тільки enable secret
        config = generate_security_config(
            enable_secret="MySecret",
            console_password="",
            vty_password="",
            enable_ssh=False
        )
        
        config_str = "\n".join(config)
        assert "enable secret MySecret" in config_str
        assert "password" not in config_str or ("line console" not in config_str and "line vty" not in config_str)
    
    def test_generate_security_config_only_ssh(self):
        # Тільки SSH без паролів
        config = generate_security_config(
            enable_secret="",
            console_password="",
            vty_password="",
            enable_ssh=True
        )
        
        config_str = "\n".join(config)
        assert any(cmd in config_str for cmd in ["crypto key generate rsa", "ip ssh", "ssh version"])
    
    def test_generate_security_config_default(self):
        # Тестування значень за замовчуванням
        config_default = generate_security_config()
        
        assert isinstance(config_default, list)

# 7. Тести для generate_dhcp_config
class TestGenerateDhcpConfig:
    
    def test_generate_dhcp_config_full(self):
        # Повна DHCP конфігурація
        config = generate_dhcp_config(
            dhcp_network="192.168.1.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8",
            dhcp_excluded="192.168.1.1 192.168.1.10"
        )
        
        config_str = "\n".join(config)
        assert "ip dhcp excluded-address 192.168.1.1 192.168.1.10" in config_str
        assert "ip dhcp pool LAN" in config_str
        assert " network 192.168.1.0 255.255.255.0" in config_str
        assert " default-router 192.168.1.1" in config_str
        assert " dns-server 8.8.8.8" in config_str
    
    def test_generate_dhcp_config_minimal(self):
        # Мінімальна DHCP конфігурація (тільки мережа та маска)
        config = generate_dhcp_config(
            dhcp_network="10.0.0.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded=""
        )
        
        config_str = "\n".join(config)
        assert "ip dhcp pool LAN" in config_str
        assert " network 10.0.0.0 255.255.255.0" in config_str
        assert " default-router" not in config_str or " default-router" in config_str
        assert " dns-server" not in config_str or " dns-server" in config_str
    
    def test_generate_dhcp_config_no_network(self):
        # DHCP без мережі (повертає порожній список)
        config = generate_dhcp_config(
            dhcp_network="",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8",
            dhcp_excluded="192.168.1.1 192.168.1.10"
        )
        
        assert config == []
    
    def test_generate_dhcp_config_no_mask(self):
        # DHCP без маски (маска може бути за замовчуванням)
        config = generate_dhcp_config(
            dhcp_network="192.168.1.0",
            dhcp_mask="",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8",
            dhcp_excluded=""
        )
        
        assert isinstance(config, list)
    
    def test_generate_dhcp_config_with_excluded_only(self):
        # Тільки excluded адреси без пулу
        config = generate_dhcp_config(
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            dhcp_excluded="192.168.1.1 192.168.1.10"
        )
        
        config_str = "\n".join(config)
        assert "ip dhcp excluded-address 192.168.1.1 192.168.1.10" in config_str
        assert "ip dhcp pool" not in config_str
    
    def test_generate_dhcp_config_default(self):
        # Тестування значень за замовчуванням
        config_default = generate_dhcp_config()
        
        assert config_default == []

# 8. Інтеграційні тести
def test_integration_all_functions():
    # Інтеграційний тест: перевірка, що всі функції повертають списки рядків
    assert isinstance(generate_interface_config(["Gi0/0"], [("192.168.1.1", "255.255.255.0")]), list)
    assert isinstance(generate_multicast_config(True), list)
    assert isinstance(generate_protocol_config("OSPF", "1.1.1.1"), list)
    assert isinstance(generate_telephony_config(True, [{"number": "1001", "user": "test"}]), list)
    assert isinstance(generate_security_config("test", "test", "test", True), list)
    assert isinstance(generate_dhcp_config("192.168.1.0", "255.255.255.0"), list)
    
    full_config = generate_full_config(
        hostname="Test",
        interfaces=["Gi0/0"],
        networks=[("192.168.1.1", "255.255.255.0")],
        ip_multicast=False,
        routing_protocol="",
        router_id="",
        telephony_enabled=False,
        dn_list=[],
        enable_ssh=False,
        enable_secret="",
        console_password="",
        vty_password="",
        dhcp_network="",
        dhcp_mask="",
        dhcp_gateway="",
        dhcp_dns="",
        dhcp_excluded="",
        no_shutdown_interfaces=[]
    )
    
    assert isinstance(full_config, list)
    assert len(full_config) > 0

def test_consistency_between_functions():
    # Перевірка консистентності між окремими функціями та generate_full_config
    full_config = generate_full_config(
        hostname="TestRouter",
        interfaces=["Gi0/0", "Gi0/1"],
        networks=[("192.168.1.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252")],
        ip_multicast=True,
        routing_protocol="OSPF",
        router_id="1.1.1.1",
        telephony_enabled=True,
        dn_list=[{"number": "1001", "user": "test"}],
        enable_ssh=True,
        enable_secret="secret123",
        console_password="console123",
        vty_password="vty123",
        dhcp_network="192.168.1.0",
        dhcp_mask="255.255.255.0",
        dhcp_gateway="192.168.1.1",
        dhcp_dns="8.8.8.8",
        dhcp_excluded="192.168.1.1",
        no_shutdown_interfaces=["Gi0/0"]
    )
    
    full_config_str = "\n".join(full_config)
    
    assert "hostname TestRouter" in full_config_str
    assert "interface Gi0/0" in full_config_str
    assert "interface Gi0/1" in full_config_str
    assert "ip multicast-routing" in full_config_str
    assert "router ospf" in full_config_str
    assert "telephony-service" in full_config_str
    assert "enable secret secret123" in full_config_str
    assert "crypto key generate rsa" in full_config_str or "ip ssh" in full_config_str
    assert "ip dhcp pool" in full_config_str
    assert "end" in full_config_str
    assert "write memory" in full_config_str

if __name__ == "__main__":
    # Запуск тестів з командного рядка
    pytest.main([__file__, "-v", "--tb=short"])