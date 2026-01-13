import pytest
from backend.validate import (
    validate_general,
    validate_ip,
    validate_mask,
    validate_router_id,
    validate_password,
    validate_inputs
)

# Константи для параметрів функції validate_inputs
VALIDATE_INPUTS_PARAMS = [
    'ip_lan', 'mask_lan', 
    'ip_wan', 'mask_wan', 
    'ip_loopback', 'mask_loopback',
    'routing_protocol', 'router_id',
    'enable_secret', 'console_password', 'vty_password',
    'dhcp_pool_name', 'dhcp_network', 'dhcp_mask', 'dhcp_excluded'
]

def create_validate_inputs_args(**kwargs):
    default_args = {param: '' for param in VALIDATE_INPUTS_PARAMS}
    default_args.update(kwargs)
    return default_args

# 1. Тести для validate_general
class TestValidateGeneral:
    """Тести для загальної валідації"""
    
    @pytest.mark.parametrize("value, expected", [
        ("192.168.1.1", ""),  # Валідне: цифри та крапки
        ("255.255.255.0", ""),  # Валідне: маска
        ("192.168.1.0/24", ""),  # Валідне: з / для CIDR
        ("", ""),  # Порожнє: дозволено (але не для IP/масок)
        ("10.0.0.0/24", ""),  # Валідне CIDR
    ])
    #Тестування валідних значень
    def test_valid_strings(self, value, expected):
        assert validate_general(value) == expected
    
    @pytest.mark.parametrize("value, expected", [
        (123, "❌ Error: Value must be a string."),  # Не str
        ("192.168.1.1 ", "❌ Error: '192.168.1.1 ' містить пробіли."),  # З пробілом
        ("192.168.1.1a", "❌ Error: '192.168.1.1a' містить недопустимі символи (дозволено: 0-9, ., /)."),  # Недозволений символ
        ("192.168.1.1-", "❌ Error: '192.168.1.1-' містить недопустимі символи (дозволено: 0-9, ., /)."),  # Інший недозволений символ
    ])
    #Тестування невалідних значень
    def test_invalid_strings(self, value, expected):
        assert validate_general(value) == expected
    
    @pytest.mark.parametrize("value", [
        None,       # None значення
        [],         # список
        {},         # словник
        (),         # кортеж
        123.45,     # float
        True,       # bool
        ["test"],   # список з рядком
    ])
    #Тестування не рядкових типів
    def test_non_string_types(self, value):
        result = validate_general(value)
        assert "must be a string" in result or "рядок" in result.lower()

# 2. Тести для validate_ip
class TestValidateIP:
    
    @pytest.mark.parametrize("ip, expected", [
        ("192.168.1.1", ""),  # Валідне приватне IP
        ("10.0.0.1", ""),  # Валідне приватне
        ("172.16.0.1", ""),  # Валідне приватне
        ("8.8.8.8", ""),  # Валідне публічне
        ("1.1.1.1", ""),  # Валідне публічне
        ("0.0.0.0", ""),  # Валідне, але не для router_id
        ("255.255.255.255", ""),  # Broadcast
        ("169.254.0.1", ""),  # Link-local (але дозволено)
        ("010.010.010.010", ""),  # З ведучими нулями
        ("0.0.0.0", ""),  # Мінімальне значення
        ("255.255.255.255", ""),  # Максимальне значення
    ])
    #Тестування валідних IP
    def test_valid_ips(self, ip, expected):
        assert validate_ip(ip) == expected
    
    @pytest.mark.parametrize("ip, expected", [
        ("127.0.0.1", "❌ Error: IP '127.0.0.1' є зарезервованим (multicast, loopback тощо)."),  # Loopback
        ("127.1.1.1", "❌ Error: IP '127.1.1.1' є зарезервованим (multicast, loopback тощо)."),  # Весь блок 127
        ("224.0.0.1", "❌ Error: IP '224.0.0.1' є зарезервованим (multicast, loopback тощо)."),  # Multicast
        ("224.1.1.1", "❌ Error: IP '224.1.1.1' є зарезервованим (multicast, loopback тощо)."),  # Весь блок 224-239
        ("239.255.255.255", "❌ Error: IP '239.255.255.255' є зарезервованим (multicast, loopback тощо)."),  # Кінець multicast
        ("240.0.0.0", "❌ Error: IP '240.0.0.0' є зарезервованим (multicast, loopback тощо)."),  # Reserved
        ("255.255.255.254", "❌ Error: IP '255.255.255.254' є зарезервованим (multicast, loopback тощо)."),  # Broadcast-1
    ])
    #Тестування зарезервованих IP
    def test_reserved_ips(self, ip, expected):
        assert validate_ip(ip) == expected
    
    @pytest.mark.parametrize("ip, expected", [
        ("300.0.0.1", "❌ Error: Неправильний формат IP-адреси '300.0.0.1'."),  # Не валідне (>255)
        ("192.168.1", "❌ Error: Неправильний формат IP-адреси '192.168.1'."),  # Неповне
        ("192.168.1.1.1", "❌ Error: Неправильний формат IP-адреси '192.168.1.1.1'."),  # Занадто багато октетів
        ("abc", "❌ Error: Неправильний формат IP-адреси 'abc'."),  # Не цифри
        ("192.168.a.1", "❌ Error: Неправильний формат IP-адреси '192.168.a.1'."),  # Буква в октеті
        ("-1.0.0.1", "❌ Error: Неправильний формат IP-адреси '-1.0.0.1'."),  # Від'ємне число
        (" 192.168.1.1", "❌ Error: Неправильний формат IP-адреси ' 192.168.1.1'."),  # З пробілом на початку
        ("192.168.1.1 ", "❌ Error: Неправильний формат IP-адреси '192.168.1.1 '."),  # З пробілом в кінці
    ])
    #Тестування невалідних IP
    def test_invalid_formats(self, ip, expected):
        assert validate_ip(ip) == expected
    #Тестування не рядкових типів
    def test_non_string_ip(self):
        result = validate_ip(123)
        assert "формат" in result or "format" in result.lower()

# 3. Тести для validate_mask
class TestValidateMask:
    
    @pytest.mark.parametrize("mask, expected", [
        ("255.255.255.0", ""),  # Валідне
        ("255.255.255.252", ""),  # Валідне
        ("255.255.255.128", ""),  # Валідне
        ("255.255.0.0", ""),  # Валідне
        ("255.0.0.0", ""),  # Валідне
        ("0.0.0.0", ""),  # Мінімальна маска
        ("255.255.255.255", ""),  # Максимальна маска
        ("32", ""),  # CIDR без / (ip_network дозволяє)
        ("0", ""),  # CIDR 0
        ("24", ""),  # CIDR 24
        ("30", ""),  # CIDR 30
    ])
    #Тестування валідних масок
    def test_valid_masks(self, mask, expected):
        assert validate_mask(mask) == expected
    
    @pytest.mark.parametrize("mask, expected", [
        ("/24", "❌ Error: Неправильний формат маски '/24'."),  # З / - не валідне
        ("255.255.255.256", "❌ Error: Неправильний формат маски '255.255.255.256'."),  # Не валідне (>255)
        ("255.255.256.0", "❌ Error: Неправильний формат маски '255.255.256.0'."),  # Не валідне
        ("255.255.255.1", "❌ Error: Неправильний формат маски '255.255.255.1'."),  # Невалідна маска (непряма)
        ("abc", "❌ Error: Неправильний формат маски 'abc'."),  # Не цифри
        ("255.255.255", "❌ Error: Неправильний формат маски '255.255.255'."),  # Неповна
        ("255.255.255.0.0", "❌ Error: Неправильний формат маски '255.255.255.0.0'."),  # Занадто багато октетів
        ("33", "❌ Error: Неправильний формат маски '33'."),  # CIDR > 32
        ("-1", "❌ Error: Неправильний формат маски '-1'."),  # Від'ємний CIDR
    ])
    #Тестування невалідних масок
    def test_invalid_masks(self, mask, expected):
        assert validate_mask(mask) == expected
    #Тестування не рядкових типів
    def test_non_string_mask(self):
        result = validate_mask(123)
        assert "формат" in result or "format" in result.lower()

# 4. Тести для validate_router_id
class TestValidateRouterID:

    @pytest.mark.parametrize("router_id, routing_protocol, expected", [
        ("1.1.1.1", "OSPF", ""),  # Валідне для OSPF
        ("192.168.1.1", "OSPF", ""),  # Валідне для OSPF
        ("10.0.0.1", "OSPF", ""),  # Валідне для OSPF
        ("1.1.1.1", "RIP", ""),  # Опціональне для інших, валідне
        ("192.168.1.1", "RIP", ""),  # Опціональне, валідне
        ("", "RIP", ""),  # Опціональне, порожнє ОК
        ("", "EIGRP", ""),  # Опціональне, порожнє ОК
        ("", "Static", ""),  # Опціональне, порожнє ОК
        ("", "", ""),  # Порожній протокол, порожній ID
    ])
    #Тестування валідних Router ID
    def test_valid_router_ids(self, router_id, routing_protocol, expected):
        assert validate_router_id(router_id, routing_protocol) == expected
    
    @pytest.mark.parametrize("router_id, routing_protocol, expected", [
        ("", "OSPF", "❌ Error: Для OSPF потрібно вказати Router ID."),  # Порожнє для OSPF
        ("0.0.0.0", "OSPF", "❌ Error: Router ID не може бути 0.0.0.0."),  # 0.0.0.0 для OSPF
        ("0.0.0.0", "RIP", "❌ Error: Router ID не може бути 0.0.0.0."),  # 0.0.0.0 для RIP
        ("0.0.0.0", "EIGRP", "❌ Error: Router ID не може бути 0.0.0.0."),  # 0.0.0.0 для EIGRP
        ("invalid", "OSPF", "❌ Error: Неправильний формат IP-адреси 'invalid'."),  # Не валідне IP для OSPF
        ("invalid", "RIP", "❌ Error: Неправильний формат IP-адреси 'invalid'."),  # Якщо вказано - перевіряє
        ("127.0.0.1", "OSPF", "❌ Error: IP '127.0.0.1' є зарезервованим (multicast, loopback тощо)."),  # Loopback для OSPF
        ("224.0.0.1", "RIP", "❌ Error: IP '224.0.0.1' є зарезервованим (multicast, loopback тощо)."),  # Multicast для RIP
        ("255.255.255.255", "OSPF", "❌ Error: Router ID не може бути 255.255.255.255."),  # Broadcast для OSPF
    ])
    #Тестування невалідних Router ID
    def test_invalid_router_ids(self, router_id, routing_protocol, expected):
        assert validate_router_id(router_id, routing_protocol) == expected
    
    @pytest.mark.parametrize("router_id, routing_protocol", [
        (123, "OSPF"),  # Не str для router_id
        ("1.1.1.1", 123),  # Не str для protocol
        (None, "OSPF"),  # None для router_id
        ("1.1.1.1", None),  # None для protocol
    ])
    #Тестування не рядкових типів
    def test_non_string_types(self, router_id, routing_protocol):
        result = validate_router_id(router_id, routing_protocol)
        # Може повертати різні помилки в залежності від реалізації
        assert "Error" in result

# 5. Тести для validate_password
class TestValidatePassword:
    
    @pytest.mark.parametrize("password, field_name, expected", [
        ("Passw0rd", "Enable secret", ""),  # Валідне: 8 символів, літера+цифра
        ("Abcdefg1", "Console password", ""),  # Валідне
        ("Test1234", "VTY password", ""),  # Валідне
        ("A" * 7 + "1", "Enable secret", ""),  # 7 літер + 1 цифра = 8 символів
        ("A" * 31 + "1", "Enable secret", ""),  # 32 символи (граничне значення)
        ("P@ssw0rd", "Console password", ""),  # З спецсимволом (якщо дозволено)
        ("MyP@ss123", "VTY password", ""),  # З спецсимволом
    ])
    #Тестування валідних паролів
    def test_valid_passwords(self, password, field_name, expected):
        assert validate_password(password, field_name) == expected
    
    @pytest.mark.parametrize("password, field_name, expected", [
        ("", "VTY password", "❌ Error: VTY password не може бути порожнім."),  # Порожнє
        ("", "Enable secret", "❌ Error: Enable secret не може бути порожнім."),  # Порожнє
        ("", "Console password", "❌ Error: Console password не може бути порожнім."),  # Порожнє
        ("short1", "Enable secret", "❌ Error: Enable secret повинен бути 8-32 символи."),  # Коротке (7 символів)
        ("a" * 33, "Console password", "❌ Error: Console password повинен бути 8-32 символи."),  # Довге (33 символи)
        ("12345678", "VTY password", "❌ Error: VTY password повинен містити мінімум 1 цифру та 1 літеру."),  # Без літер
        ("abcdefgh", "Enable secret", "❌ Error: Enable secret повинен містити мінімум 1 цифру та 1 літеру."),  # Без цифр
        ("ABCDEFGH", "Console password", "❌ Error: Console password повинен містити мінімум 1 цифру та 1 літеру."),  # Тільки великі літери, без цифр
        ("a1", "VTY password", "❌ Error: VTY password повинен бути 8-32 символи."),  # Занадто коротке
        ("A" * 40, "Enable secret", "❌ Error: Enable secret повинен бути 8-32 символи."),  # Занадто довге
    ])
    #Тестування невалідних паролів
    def test_invalid_passwords(self, password, field_name, expected):
        assert validate_password(password, field_name) == expected
    
    @pytest.mark.parametrize("password, field_name", [
        (123, "Enable secret"),  # Не str
        (None, "Console password"),  # None
        (["pass"], "VTY password"),  # Список
        ({"pass": "word"}, "Enable secret"),  # Словник
    ])
    #Тестування не рядкових типів
    def test_non_string_passwords(self, password, field_name):
        result = validate_password(password, field_name)
        # Пароль зазвичай має бути рядком
        assert "Error" in result or "повинен" in result

# 6. Тести для validate_inputs (комплексна)
class TestValidateInputs:
    
    def test_valid_complete_inputs(self):
        """Тестування повного набору валідних даних"""
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            routing_protocol='RIP',
            router_id='',
            enable_secret='EnablePass1',
            console_password='ConsolePass1',
            vty_password='VtyPass123',
            dhcp_pool_name='LAN_POOL',
            dhcp_network='192.168.1.0',
            dhcp_mask='255.255.255.0',
            dhcp_excluded='192.168.1.1 192.168.1.10'
        )
        result = validate_inputs(**args)
        assert result == ""

    #Тестування мінімального набору валідних даних
    def test_valid_minimal_inputs(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0'
        )
        result = validate_inputs(**args)
        assert result == ""
    
    #Тестування OSPF з валідним Router ID
    def test_ospf_with_router_id(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            routing_protocol='OSPF',
            router_id='1.1.1.1'
        )
        result = validate_inputs(**args)
        assert result == ""
    
    #Тестування відсутніх обов'язкових полів
    def test_missing_required_fields(self):
        args = create_validate_inputs_args(
            ip_lan='',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0'
        )
        result = validate_inputs(**args)
        assert "заповніть усі поля IP та маски" in result
    
    #Тестування невалідного формату IP
    def test_invalid_ip_format(self):
        args = create_validate_inputs_args(
            ip_lan='invalid',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0'
        )
        result = validate_inputs(**args)
        assert "формат IP-адреси" in result
    
    #Тестування відсутнього Router ID для OSPF
    def test_ospf_without_router_id(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            routing_protocol='OSPF',
            router_id=''
        )
        result = validate_inputs(**args)
        assert "Для OSPF потрібно вказати Router ID" in result
    
    #Тестування невалідного Router ID для OSPF
    def test_invalid_router_id_for_ospf(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            routing_protocol='OSPF',
            router_id='0.0.0.0'
        )
        result = validate_inputs(**args)
        assert "Router ID не може бути 0.0.0.0" in result
    
    #Тестування короткого пароля
    def test_short_password(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            enable_secret='short1'
        )
        result = validate_inputs(**args)
        assert "повинен бути 8-32 символи" in result
    
    #Тестування пароля без цифр
    def test_password_without_digit(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            console_password='NoDigitsHere'
        )
        result = validate_inputs(**args)
        assert "мінімум 1 цифру та 1 літеру" in result
    
    #Тестування невалідної DHCP мережі
    def test_dhcp_invalid_network(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0',
            dhcp_network='invalid',
            dhcp_mask='255.255.255.0'
        )
        result = validate_inputs(**args)
        assert "формат IP-адреси" in result

    #Тестування пробілів в IP
    def test_spaces_in_ip(self):
        args = create_validate_inputs_args(
            ip_lan='192.168.1.1 ',
            mask_lan='255.255.255.0',
            ip_wan='10.0.0.1',
            mask_wan='255.255.255.252',
            ip_loopback='172.16.0.1',
            mask_loopback='255.255.0.0'
        )
        result = validate_inputs(**args)
        assert "містить пробіли" in result

# 7. Інтеграційні тести
def test_validation_sequence():

    # Спочатку загальна валідація
    result = validate_general("192.168.1.1 ")
    assert "пробіли" in result
    
    # Якщо загальна пройшла, тоді специфічна IP валідація
    result = validate_ip("192.168.1.1")
    assert result == ""
    
    # Перевірка правильного порядку обробки помилок
    result = validate_general("invalid")
    result_ip = validate_ip("invalid")
    assert "символи" in result or "формат" in result_ip

# Додаткові тести для граничних випадків
def test_edge_case_ip_with_leading_zeros():
    # IP з ведучими нулями має бути валідним
    assert validate_ip("010.010.010.010") == ""
    assert validate_ip("001.002.003.004") == ""

# Додаткові тести для граничних випадків паролів
def test_edge_case_password_length_boundaries():
    # Межові значення довжини
    assert validate_password("A" * 7 + "1", "Test") != ""  # 7 символів + 1 цифра = 8, але може бути недостатньо літер або цифр
    assert validate_password("A" * 31 + "1", "Test") == ""  # 32 символи (граничне значення)
    assert validate_password("A" * 32 + "1", "Test") != ""  # 33 символи (занадто багато)

# 8. Тести продуктивності (додатково)
def test_validation_performance(benchmark):

    # Виконати 100 валідацій через benchmark
    def validate_multiple():
        for _ in range(100):
            validate_ip("192.168.1.1")
            validate_mask("255.255.255.0")
            validate_password("Test1234", "Password")
    
    benchmark(validate_multiple)
    # Benchmark автоматично обчислить час виконання
    
if __name__ == "__main__":
    # Запуск тестів з командного рядка
    pytest.main([__file__, "-v"])