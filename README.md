# Cisco Router Wizard

Коротко: простий інструмент із GUI (Eel) для генерації конфігурацій Cisco-маршрутизаторів на основі введених даних.

## Зміст репозиторію
- `backend/` — серверна частина: генерація конфігів, валідація, утиліти.
- `web/` — фронтенд (HTML/JS) який викликає бекенд через Eel.
- `tests/` — модульні тести.
- `SPECIFICATIONS.md` — специфікації ключових функцій для тестування та рефакторингу.

## Коротка інформація про проєкт
Мета проєкту — швидко генерувати робочі конфігурації для Cisco-пристроїв (інтерфейси, маршрутизація, DHCP, telephony, SSH тощо) на основі форм у веб-інтерфейсі.

## Вимоги
- Python 3.8 або новіший
- Рекомендовано: віртуальне оточення (venv)
- Для запуску GUI: встановлений браузер (Chrome/Edge)

## Встановлення (Windows)
1. Відкрийте PowerShell або cmd і перейдіть в папку проекту.
2. (Опціонально) створіть та активуйте virtualenv:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1    # PowerShell
# або для cmd: .\.venv\Scripts\activate.bat
```

3. Встановіть залежності (якщо є `requirements.txt`):

```powershell
py -3 -m pip install -r requirements.txt
```

Примітка: якщо `py` або `python` не знайдені, встановіть Python з https://python.org або через Microsoft Store.

## Запуск застосунку
Запуск з кореня проєкту (важливо):

```powershell
py -3 -m backend.main
# або
python -m backend.main
```

Якщо запускаєте окремі файли в IDE, переконайтеся, що робоча директорія — корінь проєкту, або запускайте модулі через `-m`.

## Тести — як запускати
У репозиторії є тести в `tests/test_main.py`. Є два підходи для запуску:

- Через вбудований `unittest` (без додаткових пакетів):

```powershell
py -3 -u tests\test_main.py
```

- Через `pytest` (якщо встановлено):

```powershell
py -3 -m pip install -U pytest
py -3 -m pytest -q -s tests/test_main.py
```

Параметр `-s` у `pytest` дозволяє бачити друкований вивід з тестів (print). Ми також вмикаємо `verbosity` і вимикаємо буферизацію у тестовому файлі, щоб кінцевий вивід з конфігураціями показувався у консолі.

## Опис тестів
Файл [tests/test_main.py](tests/test_main.py) містить набори тестів для ключових сценаріїв генерації конфігурацій (короткий перелік):

- `test_basic_configuration_no_routing`: перевіряє базову генерацію з декількома інтерфейсами, адресами та `no shutdown`.
- `test_ospf_with_router_id`: перевіряє генерацію OSPF з `router-id` та правильними рядками `network`.
- `test_ospf_missing_router_id_error`: перевіряє повідомлення про помилку, коли OSPF без `router-id`.
- `test_networks_length_mismatch`: перевірка захисту від невідповідності числа інтерфейсів і мереж.
- `test_telephony_basic`: перевіряє генерацію `telephony-service`, `ephone` та `ephone-dn` блоків.
- `test_dhcp_configuration`: перевірка DHCP-пулу, шлюзу та DNS.
- `test_ssh_security_block`: перевірка генерації SSH/enable-secret/ключів RSA.

Додатково: тестова конфігурація в кінці тестів друкує згенеровані конфігурації у консоль для полегшеної перевірки.

## SPECIFICATIONS.md
Дивіться файл [SPECIFICATIONS.md](SPECIFICATIONS.md) — містить детальні специфікації для функцій: `validate_inputs`, `_mask_to_wildcard`, `generate_protocol_config`, `generate_interface_config`, `generate_full_config`.

## Додавання нових тестів / рефакторинг
- Рефакторинг логіки слід робити в `backend/` модулях; додайте модульні тести в `tests/`.
- Під час змін, переконайтеся, що `SPECIFICATIONS.md` оновлено відповідно до контрактів функцій.

## Типові проблеми та їх вирішення
- "Python was not found": використайте `py -3` або додайте `python` до PATH.
- Якщо `pytest` не встановлено, встановіть його командою `py -3 -m pip install -U pytest`.
- Якщо тести не виводять print-повідомлення під `pytest`, запускайте з `-s` або використовуйте `unittest` без буферизації.

## Корисні команди

```powershell
# Запуск бекенду
py -3 -m backend.main

# Запуск конкретного тест-файлу через unittest
py -3 -u tests\test_main.py

# Запуск тестів через pytest з виводом print
py -3 -m pytest -q -s tests/test_main.py
```

## Коректура та контриб'юція
- Відкривайте pull-request з описом змін та, за можливості, додайте/оновіть тести.

## Контакти
Якщо потрібна допомога — відкрий issue в репозиторії з описом проблеми.
