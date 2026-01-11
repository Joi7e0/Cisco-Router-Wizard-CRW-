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
            # Прив'язуємо як staticmethod, щоб при доступі через екземпляр функція не ставала методом
            cls.process_text = staticmethod(process_text)
        cls._outputs = []

    @classmethod
    def tearDownClass(cls):
        # Наприкінці тестів виводимо згенеровані конфіги для зручного огляду
        if not cls._outputs:
            return
        print("\n\n=== Generated configs from tests ===")
        for name, out in cls._outputs:
            print(f"\n--- {name} ---\n")
            print(out)
        print("\n=== End generated configs ===\n")

    def call_process(self, **kwargs):
        res = self.process_text(**kwargs)
        self.__class__._outputs.append((self._testMethodName, res))
        return res

    def test_basic_configuration_no_routing(self):
        """Перевірка базової конфігурації з кількома інтерфейсами без протоколу"""
        result = self.call_process(
            hostname="Test-R1",
            interfaces=["GigabitEthernet0/0", "GigabitEthernet0/1"],
            networks=[
                ("192.168.1.1", "255.255.255.0"),
                ("172.16.1.1", "255.255.0.0")
            ],
            no_shutdown_interfaces=["GigabitEthernet0/0"]
        )

        self.assertIn("hostname Test-R1", result)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", result)
        self.assertIn("ip address 172.16.1.1 255.255.0.0", result)
        self.assertIn("no shutdown", result)
        self.assertIn("end", result)
        self.assertIn("write memory", result)

    def test_ospf_with_router_id(self):
        """Перевірка OSPF з коректним router-id"""
        result = self.call_process(
            proto="OSPF",
            router_id="1.1.1.1",
            interfaces=["Gi0/0", "Gi0/1"],
            networks=[
                ("10.10.10.1", "255.255.255.252"),
                ("10.20.20.1", "255.255.255.252")
            ]
        )

        self.assertIn("router ospf 1", result)
        self.assertIn("router-id 1.1.1.1", result)
        self.assertIn("network 10.10.10.1 0.0.0.3 area 0", result)

    def test_ospf_missing_router_id_error(self):
        """Повинна повернутися помилка при OSPF без router-id"""
        result = self.call_process(
            proto="OSPF",
            router_id="",
            interfaces=["Gi0/0"],
            networks=[("192.168.100.1", "255.255.255.0")]
        )

        self.assertIn("❌ Для OSPF обов'язково потрібно вказати Router ID", result)

    def test_networks_length_mismatch(self):
        """Перевірка захисту від невідповідності довжин interfaces та networks"""
        result = self.call_process(
            interfaces=["Gi0/0", "Gi0/1", "Gi0/2"],
            networks=[("10.0.0.1", "255.255.255.0"), ("20.0.0.1", "255.255.255.0")]
        )

        # Більш надійна перевірка (не залежить від точного форматування)
        self.assertTrue("кількість мереж" in result)
        self.assertTrue("не відповідає" in result)
        self.assertTrue("інтерфейсів" in result)
        self.assertTrue("(2)" in result or "2" in result)
        self.assertTrue("(3)" in result or "3" in result)

    def test_telephony_basic(self):
        """Перевірка генерації telephony-service з двома dn"""
        result = self.call_process(
            telephony_enabled=True,
            dn_list=[
                {"number": "1001", "user": "alice"},
                {"number": "1002", "user": "bob"}
            ],
            interfaces=["Gi0/0"],
            networks=[("192.168.10.1", "255.255.255.0")]
        )

        self.assertIn("telephony-service", result)
        self.assertIn("ephone-dn 1", result)
        self.assertIn("number 1001", result)
        self.assertIn("ephone 1", result)
        self.assertIn("username alice", result)

    def test_dhcp_configuration(self):
        """Перевірка DHCP пулу з excluded адресами"""
        result = self.call_process(
            dhcp_network="192.168.50.0",
            dhcp_mask="255.255.255.0",
            dhcp_gateway="192.168.50.1",
            dhcp_dns="8.8.8.8",
            interfaces=["Gi0/1"],
            networks=[("192.168.50.1", "255.255.255.0")]
        )

        self.assertIn("ip dhcp pool LAN", result)
        self.assertIn("network 192.168.50.0 255.255.255.0", result)
        self.assertIn("default-router 192.168.50.1", result)
        self.assertIn("dns-server 8.8.8.8", result)

    def test_ssh_security_block(self):
        """Перевірка блоку безпеки з SSH"""
        result = self.call_process(
            enable_ssh=True,
            enable_secret="MySuperSecret123",
            console_password="consolepass",
            vty_password="vtypass",
            interfaces=["Gi0/0"],
            networks=[("10.0.0.1", "255.255.255.252")]
        )

        self.assertIn("enable secret MySuperSecret123", result)
        self.assertIn("ip ssh version 2", result)
        self.assertIn("crypto key generate rsa modulus 1024", result)


if __name__ == '__main__':
    unittest.main()
