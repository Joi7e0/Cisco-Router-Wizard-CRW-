import pytest
import sys
import os

# Додаємо шлях до backend, щоб pytest міг його знайти
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.validate import validate_password, validate_general, validate_hostname

class TestPasswordValidation:
    """Тестування валідації паролів (Enable Secret, Console, Admin SSH)"""

    @pytest.mark.parametrize("password, field_name", [
        ("Passw0rd", "Enable secret"),        # Класичний валідний пароль
        ("C1scoR0uter!", "Console password"), # Зі спецсимволами
        ("Admin12345", "Admin password"),     # Для SSH доступу
        ("A" * 7 + "1", "Enable secret"),     # Рівно 8 символів (мінімум)
        ("A" * 31 + "1", "Console password"), # Рівно 32 символи (максимум)
    ])
    def test_valid_passwords(self, password, field_name):
        """Перевірка правильних паролів, які мають проходити валідацію."""
        assert validate_password(password, field_name) == ""

    @pytest.mark.parametrize("password, field_name", [
        ("", "Enable secret"),
        ("", "Admin password"),
    ])
    def test_empty_passwords(self, password, field_name):
        """Перевірка, що пароль не може бути порожнім."""
        result = validate_password(password, field_name)
        assert "❌ Error" in result
        assert "не може бути порожнім" in result.lower()

    @pytest.mark.parametrize("password, field_name", [
        ("short1", "Enable secret"),          # 6 символів
        ("a" * 32 + "1", "Admin password"),   # 33 символи (перевищення ліміту)
    ])
    def test_password_length_boundaries(self, password, field_name):
        """Перевірка обмежень довжини пароля (від 8 до 32 символів)."""
        result = validate_password(password, field_name)
        assert "❌ Error" in result
        assert "8-32 символи" in result

    @pytest.mark.parametrize("password, field_name, expected_error", [
        ("NoDigitsHere", "Console password", "мінімум 1 цифру та 1 літеру"),
        ("123456789", "Enable secret", "мінімум 1 цифру та 1 літеру"),
    ])
    def test_password_complexity(self, password, field_name, expected_error):
        """Перевірка наявності хоча б однієї літери та однієї цифри."""
        result = validate_password(password, field_name)
        assert "❌ Error" in result
        assert expected_error in result

    @pytest.mark.parametrize("password, field_name", [
        (12345678, "Enable secret"), 
        (None, "Admin password")
    ])
    def test_non_string_passwords(self, password, field_name):
        """Перевірка обробки нерядкових типів даних (захист від крашу)."""
        result = validate_password(password, field_name)
        assert "Error" in result

class TestHostnameValidation:
    """
    Тестування валідації Hostname. 
    Оскільки специфічної функції немає, використовуємо validate_general.
    """

    @pytest.mark.parametrize("hostname", [
        "R1", 
        "Branch-Router", 
        "Core_Switch_01"
    ])
    def test_valid_hostname(self, hostname):
        assert validate_hostname(hostname) == ""

    @pytest.mark.parametrize("hostname", [
        "Router 1",      # Містить пробіл
        "R1@Branch",     # Містить недопустимі символи (якщо ваша функція їх блокує)
    ])
    def test_invalid_hostname(self, hostname):
        result = validate_hostname(hostname)
        assert "❌ Error" in result