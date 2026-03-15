import pytest
from backend.protocols import _mask_to_wildcard, _cidr_to_mask
from backend.generate import generate_nat_config

class TestMaskToWildcard:

    @pytest.mark.parametrize("mask, expected", [
        ("255.255.255.0", "0.0.0.255"),
        ("255.255.0.0", "0.0.255.255"),
        ("255.255.255.252", "0.0.0.3"),
        ("255.0.0.0", "0.255.255.255"),
        ("24", "0.0.0.255"),
        ("/24", "0.0.0.255"),
        ("30", "0.0.0.3"),
    ])
    def test_valid_conversions(self, mask, expected):
        assert _mask_to_wildcard(mask) == expected

    def test_invalid_mask(self):
        assert _mask_to_wildcard("invalid") == "0.0.0.0"
        assert _mask_to_wildcard("") == "0.0.0.0"
        assert _mask_to_wildcard(None) == "0.0.0.0"

class TestCidrToMask:

    @pytest.mark.parametrize("cidr, expected", [
        (24, "255.255.255.0"),
        (30, "255.255.255.252"),
        (16, "255.255.0.0"),
        (8, "255.0.0.0"),
        (0, "0.0.0.0"),
        (32, "255.255.255.255"),
    ])
    def test_valid_cidr(self, cidr, expected):
        assert _cidr_to_mask(cidr) == expected

    def test_invalid_cidr(self):
        assert _cidr_to_mask(33) == "255.255.255.0"
        assert _cidr_to_mask(-1) == "255.255.255.0"

class TestNatConfig:

    def test_pat_config(self):
        result = generate_nat_config("PAT", "Gi0/0", "Gi0/1", "", "", "192.168.1.0", "255.255.255.0")
        text = "\n".join(result)
        assert "access-list 1 permit 192.168.1.0 0.0.0.255" in text
        assert "ip nat inside source list 1 interface Gi0/1 overload" in text

    def test_static_nat(self):
        result = generate_nat_config("Static", "", "", "192.168.1.100", "203.0.113.5", "", "")
        text = "\n".join(result)
        assert "ip nat inside source static 192.168.1.100 203.0.113.5" in text

    def test_nat_none(self):
        result = generate_nat_config("None", "", "", "", "", "", "")
        assert result == []
