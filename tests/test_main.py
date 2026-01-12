# tests/test_main.py
import unittest
from unittest import mock


# Мок для eel.expose — просто повертаємо функцію без змін
def mock_expose(func):
    return func


class TestProcessText(unittest.TestCase):
    """Тести основної функції генерації конфігурації process_text"""

    @classmethod
    def setUpClass(cls):
        # Мокаємо eel.expose перед імпортом
        with mock.patch('eel.expose', mock_expose):
            from backend.main import process_text
            cls.process_text = staticmethod(process_text)
        cls._outputs = []

    @classmethod
    def tearDownClass(cls):
        if not cls._outputs:
            return
        print("\n\n=== Generated configs from tests (selected) ===")
        for name, out in cls._outputs[:8]:  # обмежуємо вивід
            print(f"\n--- {name} ---\n{out[:400]}{'...' if len(out) > 400 else ''}")
        print("\n=== End of preview ===\n")

    def call_process(self, **kwargs):
        res = self.process_text(**kwargs)
        self.__class__._outputs.append((self._testMethodName, res))
        return res

    # ─── Базові сценарії ───────────────────────────────────────────────

    def test_basic_configuration_no_routing(self):
        """Базова конфігурація без протоколу маршрутизації"""
        result = self.call_process(
            hostname="Lab-R1",
            interfaces=["GigabitEthernet0/0", "GigabitEthernet0/1"],
            networks=[
                ("192.168.10.1", "255.255.255.0"),
                ("172.16.20.1", "255.255.255.252")
            ],
            no_shutdown_interfaces=["GigabitEthernet0/0"]
        )

        self.assertIn("hostname Lab-R1", result)
        self.assertIn("ip address 192.168.10.1 255.255.255.0", result)
        self.assertIn("no shutdown", result)
        self.assertIn("end", result)
        self.assertIn("write memory", result)

    # ─── OSPF ──────────────────────────────────────────────────────────

    def test_ospf_valid_router_id(self):
        result = self.call_process(
            proto="OSPF",
            router_id="2.2.2.2",
            interfaces=["Gi0/0"],
            networks=[("10.55.55.1", "255.255.255.252")]
        )
        self.assertIn("router ospf 1", result)
        self.assertIn("router-id 2.2.2.2", result)
        self.assertIn("network 10.55.55.1 0.0.0.3 area 0", result)

    def test_ospf_missing_router_id_error(self):
        result = self.call_process(
            proto="OSPF",
            router_id="",
            interfaces=["Gi0/0"],
            networks=[("192.168.100.1", "255.255.255.0")]
        )
        self.assertTrue("❌" in result)
        self.assertIn("Для OSPF", result)

    # ─── Валідація довжин/форматів ────────────────────────────────────

    def test_networks_length_mismatch_error(self):
        result = self.call_process(
            interfaces=["Gi0/0", "Gi0/1", "Gi0/2"],
            networks=[("10.0.0.1", "255.255.255.0"), ("20.0.0.1", "255.255.255.0")]
        )
        self.assertTrue("❌" in result)
        self.assertTrue("кількість мереж" in result or "networks" in result.lower())
        self.assertTrue("не відповідає" in result or "mismatch" in result.lower())

    def test_empty_interfaces_list(self):
        result = self.call_process(
            interfaces=[],
            networks=[]
        )
        self.assertTrue("❌" in result)
        self.assertIn("інтерфейсу", result.lower())

    # ─── Telephony ─────────────────────────────────────────────────────

    def test_telephony_basic_generation(self):
        result = self.call_process(
            telephony_enabled=True,
            dn_list=[
                {"number": "2001", "user": "alice"},
                {"number": "2002", "user": "bob"}
            ],
            interfaces=["Gi0/0"],
            networks=[("192.168.77.1", "255.255.255.0")]
        )

        self.assertIn("telephony-service", result)
        self.assertIn("max-ephones 3", result)
        self.assertIn("max-dn 3", result)
        self.assertIn("ephone-dn 1", result)
        self.assertIn("number 2001", result)
        self.assertIn("ephone 1", result)
        self.assertIn("username alice", result)

    def test_telephony_disabled_no_config(self):
        result = self.call_process(
            telephony_enabled=False,
            dn_list=[{"number": "9999", "user": "test"}],
            interfaces=["Gi0/0"],
            networks=[("10.10.10.1", "255.255.255.0")]
        )
        self.assertNotIn("telephony-service", result)
        self.assertNotIn("ephone-dn", result)

    # ─── Security / SSH ────────────────────────────────────────────────

    def test_ssh_block_generation(self):
        result = self.call_process(
            enable_ssh=True,
            enable_secret="SecretPa55w0rd",
            console_password="C0ns0le123",
            vty_password="VtyP@ssw0rd",
            interfaces=["Gi0/1"],
            networks=[("192.168.200.1", "255.255.255.252")]
        )

        self.assertIn("enable secret SecretPa55w0rd", result)
        self.assertIn("crypto key generate rsa modulus 1024", result)
        self.assertIn("ip ssh version 2", result)

    # ─── DHCP ──────────────────────────────────────────────────────────

    def test_dhcp_full_pool(self):
        result = self.call_process(
            dhcp_network="192.168.88.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.88.1",
            dhcp_dns="8.8.8.8",
            interfaces=["Gi0/0"],
            networks=[("192.168.88.1", "255.255.255.0")]
        )

        self.assertIn("ip dhcp pool LAN", result)
        self.assertIn("network 192.168.88.0 255.255.255.0", result)
        self.assertIn("default-router 192.168.88.1", result)
        self.assertIn("dns-server 8.8.8.8", result)
        self.assertIn("ip dhcp excluded-address", result)

    def test_dhcp_empty_network_no_config(self):
        result = self.call_process(
            dhcp_network="",
            dhcp_mask="",
            interfaces=["Gi0/0"],
            networks=[("10.1.1.1", "255.255.255.0")]
        )
        self.assertNotIn("ip dhcp pool", result)


if __name__ == '__main__':
    unittest.main()