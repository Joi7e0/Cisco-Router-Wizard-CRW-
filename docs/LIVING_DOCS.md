# Жива документація (Living Documentation)

Цей документ пов’язує технічні вимоги до конфігурації Cisco IOS із реальними тестами продукту. Кожен приклад — це активний тест, який гарантує актуальність документації.

## 1. Валідація інтерфейсів
Коректність імен інтерфейсів та IP-адрес перевіряється в `tests/unit/test_validators/test_network_val.py`.

### Приклад: Валідний Hostname
- **Правило**: Починається з літери, до 63 символів.
- **Тест**: `TestHostnameValidation.test_valid_hostname`
- **Дані**: `R1`, `Branch_Office`, `Core-Switch`

---

## 2. Протоколи маршрутизації
Логіка генерації протоколів RIP, OSPF, EIGRP та BGP перевіряється в `tests/unit/test_generators/test_routing.py`.

### Приклад: OSPF з декількома Area
- **Правило**: Кожна мережа повинна мати свою Area та Wildcard Mask.
- **Тест**: `test_generate_ospf_config`
- **Очікуваний вивід**:
  ```ios
  router ospf 1
   network 192.168.1.0 0.0.0.255 area 0
  ```

---

## 3. DHCP Сервер
Конфігурація пулів та excluded-address перевіряється в `tests/unit/test_generators/test_services.py`.

### Приклад: DHCP з Option 150 (TFTP)
- **Правило**: Для IP-телефонії необхідно передати адресу TFTP-сервера в Option 150.
- **Тест**: `test_generate_dhcp_config_with_option150`
- **Дані**: `dhcp_option150="10.1.1.5"`

---

## 4. NAT (PAT та Static)
Логіка перетворення адрес перевіряється в `tests/unit/test_generators/test_advanced.py`.

### Приклад: NAT Overload (PAT)
- **Правило**: Створення access-list 1 та прив'язка до зовнішнього інтерфейсу.
- **Тест**: `test_generate_nat_pat_config`

---

## 5. Повний ланцюжок (Pipeline)
Тестування взаємодії всіх компонентів разом: `tests/integration/test_pipeline.py`.

Цей тест симулює повний ввід даних з фронтенду та перевіряє, що згенерований конфіг містить всі необхідні секції (Base, Routing, Security, NAT) у правильному порядку.
