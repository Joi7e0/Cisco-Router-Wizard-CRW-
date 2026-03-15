import pytest
from backend.validate import (validate_general, validate_ip, validate_mask, validate_dhcp, validate_inputs)

class TestNetworkValidation:
    
    def test_validate_general_valid(self):
        assert validate_general("192.168.1.1") == ""
        assert validate_general("255.255.255.0") == ""
        assert validate_general("10.0.0.0/24") == ""

    def test_validate_general_invalid(self):
        assert "містить пробіли" in validate_general("192.168.1.1 ")
        assert "містить недопустимі символи" in validate_general("192.168.1.a@") # @ is still invalid
        assert "Value must be a string" in validate_general(123)

    def test_validate_hostname(self):
        from backend.validate import validate_hostname
        assert validate_hostname("Router-A") == ""
        assert "повинен починатися з літери" in validate_hostname("1Router")
        assert "Hostname не може бути порожнім" in validate_hostname("")
        assert "містить недопустимі символи" in validate_hostname("Router@A")

    def test_validate_ip_valid(self):
        assert validate_ip("192.168.1.1") == ""
        assert validate_ip("8.8.8.8") == ""
        assert validate_ip("255.255.255.255") == ""  # Special case: broadcast allowed

    def test_validate_ip_invalid(self):
        assert "Неправильний формат" in validate_ip("256.256.256.256")
        assert "Неправильний формат" in validate_ip("192.168.1")
        assert "є зарезервованим" in validate_ip("127.0.0.1")  # Loopback
        assert "є зарезервованим" in validate_ip("224.0.0.1")  # Multicast

    def test_validate_mask_valid(self):
        assert validate_mask("255.255.255.0") == ""
        assert validate_mask("255.255.255.252") == ""
        assert validate_mask("24") == ""
        assert validate_mask("30") == ""

    def test_validate_mask_invalid(self):
        assert "Неправильний формат" in validate_mask("255.255.255.1")
        assert "Неправильний формат" in validate_mask("33")
        assert "Неправильний формат" in validate_mask("invalid")

    def test_validate_dhcp_valid(self):
        # Gateway 192.168.1.1 is in 192.168.1.0/24 network
        assert validate_dhcp("192.168.1.0", "255.255.255.0", "192.168.1.1", "8.8.8.8") == ""
        # DNS is optional
        assert validate_dhcp("10.0.0.0", "255.255.255.252", "10.0.0.1", "") == ""

    def test_validate_dhcp_invalid(self):
        # Gateway outside network
        assert "Gateway не в межах" in validate_dhcp("192.168.1.0", "255.255.255.0", "10.0.0.1", "")
        # Invalid IP in DHCP settings
        assert "Неправильний формат IP" in validate_dhcp("invalid", "255.255.255.0", "", "")

    def test_validate_inputs_basic(self):
        valid_networks = [("192.168.1.1", "255.255.255.0")]
        assert validate_inputs(valid_networks) == ""

    def test_validate_inputs_empty(self):
        assert "вкажіть хоча б одну мережу" in validate_inputs([])

    def test_validate_inputs_missing_fields(self):
        invalid_networks = [("192.168.1.1", "")]
        assert "заповніть усі поля" in validate_inputs(invalid_networks)
