import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.generate import (
    generate_interface_config,
    generate_full_config,
)

# 1. Тести для generate_interface_config
class TestGenerateInterfaceConfig:
    
    def test_generate_interface_config_basic(self):
        interfaces = ["GigabitEthernet0/0", "GigabitEthernet0/1"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.252")
        ]

        config = generate_interface_config(interfaces, networks)

        # Перевіряємо, що конфігурація містить основні елементи
        config_str = "\n".join(config)
        assert "interface GigabitEthernet0/0" in config_str
        assert " ip address 192.168.1.1 255.255.255.0" in config_str
        assert "interface GigabitEthernet0/1" in config_str
        assert " ip address 10.0.0.1 255.255.255.252" in config_str
        assert "exit" in config_str
    
    def test_generate_interface_config_with_no_shutdown(self):
        interfaces = ["Gi0/0", "Gi0/1", "Gi0/2"]
        networks = [
            ("172.16.10.1", "255.255.255.0"),
            ("192.168.55.1", "255.255.255.248"),
            ("10.99.1.1", "255.255.255.252")
        ]
        no_shutdown_interfaces = ["Gi0/0", "Gi0/2"]

        config = generate_interface_config(interfaces, networks, no_shutdown_interfaces)

        config_str = "\n".join(config)
        assert "interface Gi0/0" in config_str
        assert " no shutdown" in config_str
        assert "interface Gi0/1" in config_str
        # Перевіряємо, що Gi0/1 не має no shutdown
        sections = config_str.split("interface")
        for section in sections:
            if "Gi0/1" in section:
                assert "no shutdown" not in section
    
    def test_generate_interface_config_single_interface(self):
        config = generate_interface_config(
            ["FastEthernet0/0"],
            [("10.0.0.1", "255.255.255.0")]
        )
        
        config_str = "\n".join(config)
        assert "interface FastEthernet0/0" in config_str
        assert " ip address 10.0.0.1 255.255.255.0" in config_str
    
    def test_generate_interface_config_empty(self):
        config = generate_interface_config([], [])
        assert config == []
        
        config = generate_interface_config([], [], [])
        assert config == []
    
    def test_generate_interface_config_all_interfaces_no_shutdown(self):
        interfaces = ["Fa0/0", "Fa0/1"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.0")
        ]
        no_shutdown_interfaces = ["Fa0/0", "Fa0/1"]

        config = generate_interface_config(interfaces, networks, no_shutdown_interfaces)
        
        config_str = "\n".join(config)
        assert config_str.count("no shutdown") == 2
    
    def test_generate_interface_config_no_no_shutdown(self):
        interfaces = ["Gi0/0", "Gi0/1"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.252")
        ]

        config = generate_interface_config(interfaces, networks)
        
        config_str = "\n".join(config)
        assert "no shutdown" not in config_str
    
    def test_generate_interface_config_mixed_interface_names(self):
        interfaces = ["GigabitEthernet0/0", "Gi0/1", "Fa0/0", "Serial0/0/0"]
        networks = [
            ("192.168.1.1", "255.255.255.0"),
            ("10.0.0.1", "255.255.255.252"),
            ("172.16.1.1", "255.255.0.0"),
            ("1.1.1.1", "255.255.255.252")
        ]
        
        config = generate_interface_config(interfaces, networks)
        
        config_str = "\n".join(config)
        assert "interface GigabitEthernet0/0" in config_str
        assert "interface Gi0/1" in config_str
        assert "interface Fa0/0" in config_str
        assert "interface Serial0/0/0" in config_str

# 2. Тести для generate_full_config
class TestGenerateFullConfig:
    
    def test_generate_full_config_minimal(self):
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
            no_shutdown_interfaces=["Gi0/0"]
        )

        config_str = "\n".join(config)

        # Обов'язкові елементи
        assert "hostname R-TestMinimal" in config_str
        assert "interface Gi0/0" in config_str
        assert " ip address 192.168.10.1 255.255.255.0" in config_str
        assert "interface Gi0/1" in config_str
        assert " ip address 10.0.0.1 255.255.255.252" in config_str
        assert "end" in config_str
    
    def test_generate_full_config_full_features(self):
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
            no_shutdown_interfaces=["GigabitEthernet0/0", "GigabitEthernet0/1"]
        )

        config_str = "\n".join(config)

        # Базові елементи
        assert "hostname Branch-R1" in config_str
        assert "interface GigabitEthernet0/0" in config_str
        assert "interface GigabitEthernet0/1" in config_str
        assert "interface Loopback0" in config_str
        
        # OSPF
        assert "router ospf" in config_str.lower()
        
        # Телефонія
        assert "telephony-service" in config_str.lower()
        
        # Безпека
        assert "enable secret" in config_str.lower()
        assert "line console" in config_str.lower()
        
        # DHCP
        assert "ip dhcp pool" in config_str.lower()
        assert "default-router" in config_str.lower()
        
        # Завершення
        assert "end" in config_str
    
    def test_generate_full_config_different_protocols(self):
        for protocol in ["RIP", "EIGRP", "OSPF", ""]:
            config = generate_full_config(
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
                no_shutdown_interfaces=[]
            )

            config_str = "\n".join(config)
            
            if protocol == "OSPF":
                assert "router ospf" in config_str.lower()
            elif protocol == "RIP":
                assert "router rip" in config_str.lower()
            elif protocol == "EIGRP":
                assert "router eigrp" in config_str.lower()
            else:
                # Для порожнього протоколу не повинно бути конфігурації маршрутизації
                pass
    
    def test_generate_full_config_with_dhcp(self):
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
            no_shutdown_interfaces=["Gi0/0"]
        )

        config_str = "\n".join(config)
        assert "ip dhcp pool" in config_str.lower()
        assert "192.168.1.0" in config_str
        assert "255.255.255.0" in config_str
        assert "default-router" in config_str.lower()
    
    def test_generate_full_config_with_ssh(self):
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
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        # SSH може конфігуруватися по-різному
        ssh_indicators = ["crypto key generate rsa", "ip ssh", "ssh version"]
        has_ssh = any(indicator in config_str.lower() for indicator in ssh_indicators)
        assert has_ssh
    
    def test_generate_full_config_with_multicast(self):
        config = generate_full_config(
            hostname="MulticastTest",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=True,
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
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "ip multicast-routing" in config_str.lower()
    
    def test_generate_full_config_with_telephony(self):
        config = generate_full_config(
            hostname="PhoneTest",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="",
            router_id="",
            telephony_enabled=True,
            dn_list=[
                {"number": "1001", "user": "alice"},
                {"number": "1002", "user": "bob"}
            ],
            enable_ssh=False,
            enable_secret="",
            console_password="",
            vty_password="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns="",
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "telephony-service" in config_str.lower()
        assert "ephone-dn" in config_str.lower()
    
    def test_generate_full_config_no_interfaces(self):
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
            no_shutdown_interfaces=[]
        )
        
        config_str = "\n".join(config)
        assert "hostname EmptyR" in config_str
        assert "end" in config_str

# 3. Інтеграційні тести
def test_integration_all_functions():
    # Перевіряємо, що основні функції повертають коректні типи даних
    config = generate_interface_config(["Gi0/0"], [("192.168.1.1", "255.255.255.0")])
    assert isinstance(config, list)
    assert all(isinstance(line, str) for line in config)
    
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
        no_shutdown_interfaces=[]
    )
    
    assert isinstance(full_config, list)
    assert all(isinstance(line, str) for line in full_config)
    assert len(full_config) > 0

def test_consistency_between_functions():
    # Перевіряємо консистентність між функціями
    interfaces = ["Gi0/0", "Gi0/1"]
    networks = [("192.168.1.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252")]
    
    # Генеруємо повну конфігурацію
    full_config = generate_full_config(
        hostname="TestRouter",
        interfaces=interfaces,
        networks=networks,
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
        no_shutdown_interfaces=["Gi0/0"]
    )
    
    full_config_str = "\n".join(full_config)
    
    # Перевіряємо, що всі основні секції присутні
    assert "hostname TestRouter" in full_config_str
    assert "interface Gi0/0" in full_config_str
    assert "interface Gi0/1" in full_config_str
    assert "ip multicast-routing" in full_config_str
    assert "router ospf" in full_config_str.lower()
    assert "telephony-service" in full_config_str.lower()
    assert "enable secret" in full_config_str.lower()
    assert "ip dhcp pool" in full_config_str.lower()
    assert "end" in full_config_str

if __name__ == "__main__":
    pytest.main([__file__, "-v"])