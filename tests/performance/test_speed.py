"""
Performance benchmark suite for the Cisco Router Wizard backend.

Run with:
    pytest tests/performance/test_speed.py -v \
        --benchmark-sort=mean \
        --benchmark-columns=mean,stddev,rounds,iterations

All timings are wall-clock (process_time excluded) measured by pytest-benchmark.
Memory deltas are captured via memory_profiler.memory_usage.
"""

import pytest
from memory_profiler import memory_usage

from backend.generate import generate_full_config
from backend.validate import validate_inputs


# ---------------------------------------------------------------------------
# Shared test fixtures / helpers
# ---------------------------------------------------------------------------

MINIMAL_KWARGS = dict(
    hostname="MinTest",
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
    admin_username="admin",
    admin_password="",
    domain_name="local.lab",
    dhcp_network="",
    dhcp_mask="",
    dhcp_gateway="",
    dhcp_dns="",
)

FULL_KWARGS = dict(
    hostname="PerfTest",
    interfaces=["Gi0/0", "Gi0/1", "Gi0/2"],
    networks=[
        ("192.168.1.1", "255.255.255.0"),
        ("10.0.0.1",    "255.255.255.252"),
        ("172.16.0.1",  "255.255.0.0"),
    ],
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
    pim_interfaces=["Gi0/0"],
)

LARGE_KWARGS = dict(
    hostname="LargeTest",
    interfaces=[f"Gi0/{i}" for i in range(10)],
    networks=[(f"10.{i}.0.1", "255.255.255.0") for i in range(10)],
    ip_multicast=True,
    routing_protocol="OSPF",
    router_id="9.9.9.9",
    telephony_enabled=True,
    dn_list=[
        {"number": f"10{i:02d}", "user": f"user{i}", "mac": f"AABB.CCDD.{i:04d}"}
        for i in range(20)
    ],
    enable_ssh=True,
    enable_secret="LargeSecret1",
    console_password="ConP4sword1",
    admin_username="admin",
    admin_password="AdminP4ss01",
    domain_name="large.lab",
    dhcp_network="10.0.0.0",
    dhcp_mask="255.255.255.0",
    dhcp_gateway="10.0.0.1",
    dhcp_dns="8.8.8.8",
    nat_type="PAT",
    nat_inside="Gi0/0",
    nat_outside="Gi0/1",
    snmp_enabled=True,
    snmp_community_ro="public",
    snmp_community_rw="private",
    snmp_location="DataCenter",
    snmp_contact="noc@lab",
    snmp_trap_host="10.0.0.200",
    no_shutdown_interfaces=[f"Gi0/{i}" for i in range(10)],
    pim_interfaces=[f"Gi0/{i}" for i in range(10)],
)


# ---------------------------------------------------------------------------
# Scenario A – Minimal config (1 interface, no optional features)
# Measures the irreducible overhead of the generator pipeline.
# ---------------------------------------------------------------------------
class TestScenarioA_Minimal:
    def test_minimal_config_speed(self, benchmark):
        """Minimal config (1 interface, no features) – target < 20 ms"""
        result = benchmark(generate_full_config, **MINIMAL_KWARGS)
        assert isinstance(result, list)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Scenario B – Full config (3 interfaces, all features enabled)
# Original benchmark kept intact; baseline target < 100 ms.
# ---------------------------------------------------------------------------
class TestScenarioB_Full:
    def _full_config(self):
        return generate_full_config(**FULL_KWARGS)

    def test_config_generation_speed(self, benchmark):
        """Full config generation should complete in under 100 ms"""
        result = benchmark(self._full_config)
        assert isinstance(result, list)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Scenario C – Large-scale config (10 interfaces, 20 DN entries)
# Stress-tests template loops and list comprehensions.
# ---------------------------------------------------------------------------
class TestScenarioC_LargeScale:
    def test_large_config_speed(self, benchmark):
        """Large config (10 interfaces, 20 DNs) – target < 250 ms"""
        result = benchmark(generate_full_config, **LARGE_KWARGS)
        assert isinstance(result, list)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Scenario D – Validation pipeline in isolation
# Measures validate_inputs() with both valid and invalid payloads.
# ---------------------------------------------------------------------------
class TestScenarioD_Validation:
    _VALID_NETWORKS = [
        ("192.168.1.1", "255.255.255.0"),
        ("10.0.0.1",    "255.255.255.252"),
        ("172.16.0.1",  "255.255.0.0"),
    ]

    def _validate_valid(self):
        return validate_inputs(
            networks=self._VALID_NETWORKS,
            hostname="ValidRouter",
            routing_protocol="OSPF",
            router_id="1.1.1.1",
            enable_secret="Secr3tPass",
            console_password="C0nPass22",
            admin_password="Adm1nPass",
            dhcp_network="192.168.1.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.1.1",
            dhcp_dns="8.8.8.8",
        )

    def _validate_invalid_hostname(self):
        return validate_inputs(
            networks=self._VALID_NETWORKS,
            hostname="1BadHostname",
        )

    def test_validation_valid_inputs(self, benchmark):
        """validate_inputs with valid data – target < 5 ms"""
        result = benchmark(self._validate_valid)
        assert result == ""

    def test_validation_invalid_hostname(self, benchmark):
        """validate_inputs early-exit on bad hostname – target < 1 ms"""
        result = benchmark(self._validate_invalid_hostname)
        assert result.startswith("❌")


# ---------------------------------------------------------------------------
# Scenario E – Memory snapshot
# Uses memory_profiler to capture RAM delta during full config generation.
# Not a benchmark (no `benchmark` fixture); runs once and asserts < 5 MB.
# ---------------------------------------------------------------------------
class TestScenarioE_Memory:
    def test_memory_footprint_full_config(self):
        """Full config generation should use less than 5 MB additional RAM"""
        mem = memory_usage(
            (generate_full_config, [], FULL_KWARGS),
            interval=0.01,
            retval=False,
        )
        delta_mb = max(mem) - min(mem)
        # Generous threshold — the generator is pure CPU/string work
        assert delta_mb < 5.0, f"Memory delta too high: {delta_mb:.2f} MB"

    def test_memory_footprint_large_config(self):
        """Large config generation should use less than 10 MB additional RAM"""
        mem = memory_usage(
            (generate_full_config, [], LARGE_KWARGS),
            interval=0.01,
            retval=False,
        )
        delta_mb = max(mem) - min(mem)
        assert delta_mb < 10.0, f"Memory delta too high: {delta_mb:.2f} MB"
