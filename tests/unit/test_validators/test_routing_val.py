import pytest
from backend.validate import validate_router_id

class TestRoutingValidation:
    
    @pytest.mark.parametrize("protocol", ["OSPF", "EIGRP", "BGP", "RIP"])
    def test_router_id_valid_ip(self, protocol):
        # Valid IP should pass for any protocol if provided
        assert validate_router_id("1.1.1.1", protocol) == ""
        assert validate_router_id("192.168.255.254", protocol) == ""

    def test_ospf_mandatory_router_id(self):
        # OSPF MUST have a router ID
        result = validate_router_id("", "OSPF")
        assert "❌ Error" in result
        assert "потрібно вказати Router ID" in result

    @pytest.mark.parametrize("protocol", ["EIGRP", "BGP", "RIP"])
    def test_optional_router_id(self, protocol):
        # Non-OSPF protocols can have empty router ID
        assert validate_router_id("", protocol) == ""

    @pytest.mark.parametrize("invalid_id", ["0.0.0.0", "255.255.255.255"])
    def test_router_id_blocked_ips(self, invalid_id):
        # 0.0.0.0 and 255.255.255.255 are blocked for OSPF
        assert "не може бути" in validate_router_id(invalid_id, "OSPF")
        # And blocked for others if provided
        assert "не може бути" in validate_router_id(invalid_id, "BGP")

    @pytest.mark.parametrize("bad_format", ["1.1.1", "256.1.1.1", "abc.def.ghi.jkl"])
    def test_router_id_invalid_format(self, bad_format):
        result = validate_router_id(bad_format, "OSPF")
        assert "Error" in result
        assert ("Некоректний Router ID" in result or "Неправильний формат IP" in result)

    def test_case_insensitivity(self):
        # Should work with lowercase 'ospf' if logic allows (backend uses .upper())
        assert validate_router_id("", "ospf") == "❌ Error: Для OSPF потрібно вказати Router ID."
