# Cisco Router Wizard

Коротко: небольшое приложение с GUI (Eel) для генерации конфигураций Cisco‑маршрутизаторов.

**Содержание:**
- `backend/` — серверная часть (генерация конфигураций, валидация).
- `web/` — фронтенд (HTML/JS интерфейс, вызывающий функции через Eel).

## Требования
- Python 3.8 или новее
- Git (опционально)
- Установленные браузеры (Chrome/Edge) для запуска Eel

## Установка (Windows)
1. Откройте PowerShell или cmd
2. Клонируйте репозиторий (если нужно):

```powershell
git clone <repository-url>
cd cisco-router-wizard
```

3. Создайте и активируйте виртуальное окружение:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# или для cmd: .\.venv\Scripts\activate.bat
```

4. Установите зависимости:

```powershell
pip install -r requirements.txt
```

## Запуск
Запускайте приложение из корня проекта (важно — текущая рабочая директория должна быть корнем проекта):

```powershell
py -3 -m backend.main
# или, если python в PATH:
python -m backend.main
```

Если вы запускаете `backend/main.py` напрямую в IDE, убедитесь, что рабочая директория — корень проекта, либо запускайте модуль как `-m backend.main`.

## Типичные проблемы и решения
- "Python was not found": используйте Windows launcher `py -3` или добавьте `python` в PATH.
- Ошибки импорта после перемещения файлов: запускайте как модуль из корня (`python -m backend.main`) или используйте относительные импорты.
- Eel не открывает браузер: убедитесь, что установлен поддерживаемый браузер или передайте `mode` с нужным браузером в коде.

## Структура проекта
- backend/ — Python модули (`main.py`, `generate.py`, `validate.py`, `protocols.py`)
- web/ — `home.html`, `index.html`, `main.js`, стили
- requirements.txt — зависимости

Если нужно, могу добавить инструкцию на английском или подготовить скрипт для запуска (`run.ps1`).
