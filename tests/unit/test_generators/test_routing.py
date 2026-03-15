import pytest
from backend.protocols import generate_protocol_config

class TestRipConfig:

    def test_rip_basic(self):
        result = generate_protocol_config("RIP", "", [("192.168.1.0", "255.255.255.0")])
        text = "\n".join(result)
        assert "router rip" in text
        assert "version 2" in text
        assert "network 192.168.1.0" in text
        assert "no auto-summary" in text

    def test_rip_no_auto_summary_disabled(self):
        result = generate_protocol_config("RIP", "", [("10.0.0.0", "255.0.0.0")], no_auto_summary=False)
        text = "\n".join(result)
        assert "no auto-summary" not in text

class TestOspfConfig:

    def test_ospf_basic(self):
        rc = {"processId": "10", "routerId": "1.1.1.1",
              "ospfNetworks": [{"network": "192.168.1.0", "wildcard": "0.0.0.255", "area": "0"}]}
        result = generate_protocol_config("OSPF", "1.1.1.1", [], routing_config=rc)
        text = "\n".join(result)
        assert "router ospf 10" in text
        assert "router-id 1.1.1.1" in text
        assert "network 192.168.1.0 0.0.0.255 area 0" in text

    def test_ospf_multi_area(self):
        rc = {"ospfNetworks": [
            {"network": "192.168.1.0", "wildcard": "0.0.0.255", "area": "0"},
            {"network": "10.0.0.0", "wildcard": "0.0.0.3", "area": "1"}
        ]}
        result = generate_protocol_config("OSPF", "2.2.2.2", [], routing_config=rc)
        text = "\n".join(result)
        assert "area 0" in text
        assert "area 1" in text

class TestEigrpConfig:

    def test_eigrp_basic(self):
        rc = {"asNumber": "100",
              "eigrpNetworks": [{"network": "172.16.0.0", "wildcard": "0.0.255.255"}]}
        result = generate_protocol_config("EIGRP", "", [], routing_config=rc)
        text = "\n".join(result)
        assert "router eigrp 100" in text
        assert "network 172.16.0.0 0.0.255.255" in text

    def test_eigrp_no_wildcard(self):
        rc = {"asNumber": "200",
              "eigrpNetworks": [{"network": "10.0.0.0", "wildcard": ""}]}
        result = generate_protocol_config("EIGRP", "", [], routing_config=rc)
        text = "\n".join(result)
        assert "network 10.0.0.0" in text

class TestBgpConfig:

    def test_bgp_with_neighbors_and_networks(self):
        rc = {"localAs": "65000", "routerId": "3.3.3.3",
              "bgpNeighbors": [{"ip": "10.0.0.2", "remoteAs": "65001"}],
              "bgpAdvertisedNetworks": [{"network": "192.168.1.0", "mask": "255.255.255.0"}]}
        result = generate_protocol_config("BGP", "3.3.3.3", [], routing_config=rc)
        text = "\n".join(result)
        assert "router bgp 65000" in text
        assert "bgp router-id 3.3.3.3" in text
        assert "neighbor 10.0.0.2 remote-as 65001" in text
        assert "network 192.168.1.0 mask 255.255.255.0" in text

class TestStaticConfig:

    def test_static_route_with_nexthop(self):
        rc = {"staticRoutes": [{"dest": "0.0.0.0", "mask": "0.0.0.0", "nextHop": "10.0.0.1", "interface": "", "ad": "", "metric": ""}]}
        result = generate_protocol_config("STATIC", "", [], routing_config=rc)
        text = "\n".join(result)
        assert "ip route 0.0.0.0 0.0.0.0 10.0.0.1" in text

class TestIsisConfig:

    def test_isis_basic(self):
        rc = {"areaId": "49.0001", "systemId": "0000.0000.0001", "routerType": "level-2-only"}
        result = generate_protocol_config("IS-IS", "", [], routing_config=rc)
        text = "\n".join(result)
        assert "router isis" in text
        assert "net 49.0001.0000.0000.0001.00" in text
        assert "is-type level-2-only" in text

    def test_isis_no_auto_summary(self):
        """BUG-2 regression test: IS-IS must NOT have no auto-summary"""
        rc = {"areaId": "49.0001", "systemId": "0000.0000.0001", "routerType": "level-1-2"}
        result = generate_protocol_config("IS-IS", "", [], routing_config=rc)
        text = "\n".join(result)
        assert "no auto-summary" not in text

class TestProtocolNone:

    def test_no_protocol(self):
        assert generate_protocol_config("None", "", []) == []

    def test_empty_protocol(self):
        assert generate_protocol_config("", "", []) == []
