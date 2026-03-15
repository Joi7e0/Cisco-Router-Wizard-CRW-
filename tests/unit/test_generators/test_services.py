import pytest
from backend.generate import generate_dhcp_config, generate_telephony_config, generate_snmp_config

class TestDhcpConfig:

    def test_basic_dhcp(self):
        result = generate_dhcp_config("192.168.1.0", "255.255.255.0", "192.168.1.1", "8.8.8.8")
        text = "\n".join(result)
        assert "ip dhcp pool LAN" in text
        assert "network 192.168.1.0 255.255.255.0" in text
        assert "default-router 192.168.1.1" in text
        assert "dns-server 8.8.8.8" in text

    def test_excluded_range(self):
        result = generate_dhcp_config("192.168.1.0", "255.255.255.0", "192.168.1.1", "",
                                      excluded=["192.168.1.1", "192.168.1.10"])
        text = "\n".join(result)
        assert "ip dhcp excluded-address 192.168.1.1 192.168.1.10" in text

    def test_excluded_single(self):
        result = generate_dhcp_config("192.168.1.0", "255.255.255.0", "192.168.1.1", "",
                                      excluded=["192.168.1.1"])
        text = "\n".join(result)
        assert "ip dhcp excluded-address 192.168.1.1" in text
        assert "192.168.1.10" not in text

    def test_option150(self):
        result = generate_dhcp_config("192.168.1.0", "255.255.255.0", "192.168.1.1", "",
                                      dhcp_option150="192.168.1.1")
        text = "\n".join(result)
        assert "option 150 ip 192.168.1.1" in text

    def test_empty_network_returns_nothing(self):
        result = generate_dhcp_config("", "", "", "")
        assert result == []

class TestTelephonyConfig:

    def test_basic_telephony(self):
        dn_list = [{"number": "1001", "user": "Alice", "mac": ""}]
        result = generate_telephony_config(True, dn_list, ip_source_address="192.168.1.1")
        text = "\n".join(result)
        assert "telephony-service" in text
        assert "ip source-address 192.168.1.1 port 2000" in text
        assert "ephone-dn 1" in text
        assert "number 1001" in text

    def test_telephony_with_mac(self):
        dn_list = [{"number": "1001", "user": "Alice", "mac": "0011.2233.4455"}]
        result = generate_telephony_config(True, dn_list)
        text = "\n".join(result)
        assert "mac-address 0011.2233.4455" in text
        assert "button 1:1" in text

    def test_telephony_name_not_username(self):
        """BUG-4 regression test: ephone must use 'name' not 'username'"""
        dn_list = [{"number": "1001", "user": "Alice", "mac": ""}]
        result = generate_telephony_config(True, dn_list)
        text = "\n".join(result)
        assert "name Alice" in text
        assert "username" not in text

    def test_telephony_disabled(self):
        result = generate_telephony_config(False, [])
        assert result == []

class TestSnmpConfig:

    def test_snmp_basic(self):
        result = generate_snmp_config(True, "public", "private", "Kyiv", "admin@lab", "10.0.0.100")
        text = "\n".join(result)
        assert "snmp-server community public RO" in text
        assert "snmp-server community private RW" in text
        assert "snmp-server location Kyiv" in text
        assert "snmp-server contact admin@lab" in text
        assert "snmp-server host 10.0.0.100" in text

    def test_snmp_disabled(self):
        result = generate_snmp_config(False, "", "", "", "", "")
        assert result == []
