import pytest
from backend.generate import generate_full_config

class TestFullPipeline:

    def _minimal_config(self, **overrides):
        defaults = dict(
            hostname="TestRouter",
            interfaces=["Gi0/0"],
            networks=[("192.168.1.1", "255.255.255.0")],
            ip_multicast=False,
            routing_protocol="None",
            router_id="",
            telephony_enabled=False,
            dn_list=[],
            enable_ssh=False,
            enable_secret="",
            console_password="",
            admin_username="",
            admin_password="",
            domain_name="",
            dhcp_network="",
            dhcp_mask="",
            dhcp_gateway="",
            dhcp_dns=""
        )
        defaults.update(overrides)
        return generate_full_config(**defaults)

    def test_starts_with_enable_and_conf_t(self):
        result = self._minimal_config()
        assert result[0] == "enable"
        assert result[1] == "configure terminal"

    def test_ends_with_end_and_write(self):
        result = self._minimal_config()
        assert "end" in result
        assert "write memory" in result
        assert result[-1] == "write memory"

    def test_hostname_present(self):
        result = self._minimal_config(hostname="Branch-R1")
        assert "hostname Branch-R1" in result

    def test_section_order(self):
        """Verify: base → interfaces → routing → security → dhcp → end"""
        result = self._minimal_config(
            routing_protocol="RIP",
            enable_secret="Secret123a",
            dhcp_network="192.168.1.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8"
        )
        text = "\n".join(result)
        idx_hostname = text.index("hostname")
        idx_interface = text.index("interface")
        idx_rip = text.index("router rip")
        idx_secret = text.index("enable algorithm-type")
        idx_dhcp = text.index("ip dhcp pool")
        idx_end = text.index("end")

        assert idx_hostname < idx_interface < idx_rip < idx_secret < idx_dhcp < idx_end

    def test_full_featured_config(self):
        result = generate_full_config(
            hostname="HQ-Router",
            interfaces=["Gi0/0", "Gi0/1"],
            networks=[("192.168.10.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252")],
            ip_multicast=True,
            routing_protocol="OSPF",
            router_id="1.1.1.1",
            telephony_enabled=True,
            dn_list=[{"number": "1001", "user": "Alice", "mac": "AABB.CCDD.0001"}],
            enable_ssh=True,
            enable_secret="C1sc0Secret",
            console_password="ConP4ssword",
            admin_username="admin",
            admin_password="AdminP4ss99",
            domain_name="corp.lab",
            dhcp_network="192.168.10.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.10.1",
            dhcp_dns="8.8.8.8",
            dhcp_excluded=["192.168.10.1", "192.168.10.10"],
            dhcp_option150="192.168.10.1",
            nat_type="PAT",
            nat_inside="Gi0/0",
            nat_outside="Gi0/1",
            snmp_enabled=True,
            snmp_community_ro="public",
            snmp_community_rw="private",
            snmp_location="Kyiv",
            snmp_contact="noc@corp.lab",
            snmp_trap_host="10.0.0.100",
            no_shutdown_interfaces=["Gi0/0", "Gi0/1"],
            pim_interfaces=["Gi0/0"]
        )
        text = "\n".join(result)

        # Core sections
        assert "hostname HQ-Router" in text
        assert "router ospf" in text
        assert "telephony-service" in text
        assert "ip dhcp pool LAN" in text
        assert "ip nat inside source list 1" in text
        assert "snmp-server community public RO" in text
        assert "option 150 ip 192.168.10.1" in text
        assert "mac-address AABB.CCDD.0001" in text
        assert "ip multicast-routing" in text
        assert "end" in text
        assert "write memory" in text
