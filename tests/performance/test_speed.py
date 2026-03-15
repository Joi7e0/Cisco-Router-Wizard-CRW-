import pytest
from backend.generate import generate_full_config

class TestPerformance:

    def _full_config(self):
        return generate_full_config(
            hostname="PerfTest",
            interfaces=["Gi0/0", "Gi0/1", "Gi0/2"],
            networks=[("192.168.1.1", "255.255.255.0"), ("10.0.0.1", "255.255.255.252"), ("172.16.0.1", "255.255.0.0")],
            ip_multicast=True,
            routing_protocol="OSPF",
            router_id="1.1.1.1",
            telephony_enabled=True,
            dn_list=[{"number": "1001", "user": "test", "mac": "AABB.CCDD.0001"}],
            enable_ssh=True,
            enable_secret="PerfSecret1",
            console_password="ConP4ssword",
            admin_username="admin",
            admin_password="AdminP4ss99",
            domain_name="perf.lab",
            dhcp_network="192.168.1.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8",
            nat_type="PAT",
            nat_inside="Gi0/0",
            nat_outside="Gi0/1",
            snmp_enabled=True,
            snmp_community_ro="public",
            snmp_community_rw="private",
            snmp_location="Test",
            snmp_contact="test@lab",
            snmp_trap_host="10.0.0.100",
            no_shutdown_interfaces=["Gi0/0", "Gi0/1"],
            pim_interfaces=["Gi0/0"]
        )

    def test_config_generation_speed(self, benchmark):
        """Full config generation should complete in under 100ms"""
        result = benchmark(self._full_config)
        assert isinstance(result, list)
        assert len(result) > 0
