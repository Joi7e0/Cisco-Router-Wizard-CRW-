import pytest
from backend.generate import generate_interface_config, generate_base_config

class TestInterfaceConfig:

    def test_basic_interface(self):
        result = generate_interface_config(["Gi0/0"], [("192.168.1.1", "255.255.255.0")])
        text = "\n".join(result)
        assert "interface Gi0/0" in text
        assert "ip address 192.168.1.1 255.255.255.0" in text
        assert "no shutdown" in text

    def test_interface_with_description(self):
        result = generate_interface_config(
            ["Gi0/0"], [("10.0.0.1", "255.255.255.252")],
            descriptions=["WAN Link"]
        )
        text = "\n".join(result)
        assert "description WAN Link" in text

    def test_nat_inside_outside(self):
        result = generate_interface_config(
            ["Gi0/0", "Gi0/1"],
            [("192.168.1.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252")],
            nat_inside="Gi0/0", nat_outside="Gi0/1"
        )
        text = "\n".join(result)
        assert "ip nat inside" in text
        assert "ip nat outside" in text

    def test_isis_interface(self):
        routing_config = {"protocol": "IS-IS", "participatingInterfaces": ["Gi0/0"]}
        result = generate_interface_config(
            ["Gi0/0"], [("10.0.0.1", "255.255.255.0")],
            routing_config=routing_config
        )
        text = "\n".join(result)
        assert "ip router isis" in text

    def test_no_shutdown_selective(self):
        result = generate_interface_config(
            ["Gi0/0", "Gi0/1"],
            [("192.168.1.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252")],
            no_shutdown_interfaces=["Gi0/0"]
        )
        text = "\n".join(result)
        lines = text.split("\n")
        # Gi0/0 should have no shutdown, Gi0/1 should not
        gi0_block = text.split("interface Gi0/1")[0]
        assert "no shutdown" in gi0_block

class TestBaseConfig:

    def test_hostname(self):
        result = generate_base_config("Router-HQ", ["Gi0/0"], [("10.0.0.1", "255.255.255.0")])
        text = "\n".join(result)
        assert "hostname Router-HQ" in text
        assert "enable" in text
        assert "configure terminal" in text

    def test_default_hostname(self):
        result = generate_base_config("", ["Gi0/0"], [("10.0.0.1", "255.255.255.0")])
        text = "\n".join(result)
        assert "hostname R1" in text
