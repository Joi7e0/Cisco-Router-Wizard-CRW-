import pytest
from backend.generate import generate_security_config

class TestSecurityConfig:

    def test_enable_secret(self):
        result = generate_security_config(False, "MySecret1", "", "", "", "")
        text = "\n".join(result)
        assert "service password-encryption" in text
        assert "enable algorithm-type scrypt secret MySecret1" in text

    def test_console_password(self):
        result = generate_security_config(False, "", "ConPass1", "", "", "")
        text = "\n".join(result)
        assert "line console 0" in text
        assert "password ConPass1" in text
        assert "login" in text

    def test_ssh_enabled(self):
        result = generate_security_config(True, "", "", "admin", "AdminPass1", "lab.local")
        text = "\n".join(result)
        assert "ip domain-name lab.local" in text
        assert "username admin" in text
        assert "crypto key generate rsa modulus 2048" in text
        assert "ip ssh version 2" in text
        assert "line vty 0 4" in text
        assert "transport input ssh" in text
        assert "login local" in text

    def test_ssh_disabled(self):
        result = generate_security_config(False, "", "", "", "", "")
        text = "\n".join(result)
        assert "line vty" not in text
        assert "crypto key" not in text

    def test_ssh_missing_fields_disables_ssh(self):
        # SSH enabled but missing username → SSH should not generate
        result = generate_security_config(True, "", "", "", "", "lab.local")
        text = "\n".join(result)
        assert "line vty" not in text

    def test_vty_has_exit(self):
        """BUG-1 regression test: VTY block must end with exit"""
        result = generate_security_config(True, "", "", "admin", "Pass1234", "lab.local")
        text = "\n".join(result)
        # Find vty block and check exit exists after login local
        assert "login local" in text
        idx_login = text.index("login local")
        after_login = text[idx_login:]
        assert "exit" in after_login
