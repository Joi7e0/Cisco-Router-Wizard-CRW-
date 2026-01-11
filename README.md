# Cisco Router Wizard

Невеликий додаток із GUI (Eel) для генерації конфігурацій маршрутизаторів Cisco.

**Зміст:**
- `backend/` — серверна частина (генерація конфігурацій, валідація).
- `web/` — фронтенд (HTML/JS інтерфейс, що викликає функції через Eel).

## Вимоги
- Python 3.8 або новіший
- Git (необов'язково)
- Встановлені браузери (Chrome/Edge) для запуску Eel

## Встановлення (Windows)
1. Відкрийте PowerShell або cmd
2. Склонуйте репозиторій (за потреби):

```powershell
git clone <repository-url>
cd cisco-router-wizard
```

3. Створіть та активуйте віртуальне середовище:

```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1   # PowerShell
# або для cmd: .\\.venv\\Scripts\\activate.bat
```

4. Встановіть залежності:

```powershell
pip install -r requirements.txt
```

## Запуск
Запускайте застосунок із кореня проєкту (важливо — поточна робоча директорія має бути коренем проєкту):

```powershell
py -3 -m backend.main
# або, якщо python в PATH:
python -m backend.main
```

Якщо ви запускаєте `backend/main.py` безпосередньо в IDE, переконайтеся, що робоча директорія — корінь проєкту, або запускайте модуль як `-m backend.main`.

## Типові проблеми та рішення
- "Python was not found": використайте Windows launcher `py -3` або додайте `python` до PATH.
- Помилки імпорту після переміщення файлів: запускайте як модуль із кореня (`python -m backend.main`) або використовуйте відносні імпорти.
- Eel не відкриває браузер: переконайтеся, що встановлено підтримуваний браузер, або передайте `mode` з потрібним браузером у коді.

## Структура проєкту
- backend/ — Python модулі (`main.py`, `generate.py`, `validate.py`, `protocols.py`)
- web/ — `home.html`, `index.html`, `main.js`, стилі
- requirements.txt — залежності

Якщо потрібно, можу додати інструкцію англійською або підготувати скрипт для запуску (`run.ps1`).
