import pytest
from backend.generate import generate_multicast_config

class TestMulticastConfig:

    def test_multicast_enabled(self):
        result = generate_multicast_config(True, ["Gi0/0", "Gi0/1"])
        text = "\n".join(result)
        assert "ip multicast-routing" in text
        assert "ip pim sparse-dense-mode" in text

    def test_multicast_with_interfaces(self):
        result = generate_multicast_config(True, ["Gi0/0"])
        text = "\n".join(result)
        assert "interface Gi0/0" in text
        assert "ip pim sparse-dense-mode" in text

    def test_multicast_disabled(self):
        result = generate_multicast_config(False, [])
        assert result == []

    def test_multicast_no_interfaces(self):
        result = generate_multicast_config(True, [])
        text = "\n".join(result)
        assert "ip multicast-routing" in text
        assert "ip pim" not in text
