# Генерація документації — Cisco Router Wizard

> **Інструмент**: `pdoc3` — lightweight Python doc generator  
> **Формат**: HTML (Google-style docstrings)  
> **Вихідна директорія**: `docs/html/`

---

## Вимоги

```powershell
# pdoc3 вже є у requirements.txt. Встановити окремо:
py -m pip install pdoc3
```

---

## Генерація документації

Виконайте команду з **кореня проєкту** (`d:\...\Cisco-Router-Wizard-CRW-`):

```powershell
py -m pdoc --html backend --output-dir docs/html --force
```

### Параметри команди

| Параметр | Значення | Опис |
|----------|---------|------|
| `--html` | _(прапор)_ | Генерувати HTML (не Markdown) |
| `backend` | модуль | Пакет для документування |
| `--output-dir docs/html` | шлях | Куди зберегти файли |
| `--force` | _(прапор)_ | Перезаписати існуючі файли |

### Очікуваний вивід

```
docs/html/backend/index.html
docs/html/backend/generate.html
docs/html/backend/validate.html
docs/html/backend/protocols.html
docs/html/backend/main.html
```

---

## Перегляд документації

Відкрийте в браузері:

```powershell
# Windows — відкрити Entry point у браузері
Start-Process docs/html/backend/index.html
```

Або відкрийте файл вручну: `docs/html/backend/index.html`

---

## Створення ZIP-архіву

```powershell
Compress-Archive -Path docs/html -DestinationPath docs/cisco_router_wizard_docs.zip -Force
```

Готовий архів: `docs/cisco_router_wizard_docs.zip`

---

## Структура документації

```
docs/html/backend/
├── index.html       ← Огляд пакету backend
├── generate.html    ← Усі генератори конфігурацій
├── validate.html    ← Усі валідатори
├── protocols.html   ← Протоколи маршрутизації
├── main.html        ← Точка входу (Eel)
└── config/
    ├── index.html
    └── defaults.html
```

---

## Стандарт документування

Проєкт використовує **Google-style docstrings**. Кожна публічна функція повинна мати:

```python
def my_function(param: str) -> str:
    """Короткий опис (одним реченням).

    Розширений опис за потреби.

    Args:
        param (str): Опис параметра.

    Returns:
        str: Що повертає функція.

    Examples:
        >>> my_function("hello")
        'HELLO'
    """
```

### Що документувати обов'язково

- Всі публічні функції у `backend/validate.py`, `backend/generate.py`, `backend/protocols.py`
- Нові протоколи маршрутизації — ключі `routing_config` у docstring `generate_protocol_config`
- Нові валідатори — повертаємий формат (`""` або `"❌ Error:"`)

### Що НЕ потрібно документувати

- Приватні функції (ім'я починається з `_`) — якщо логіка очевидна
- `conftest.py` fixtures з очевидними назвами
- Однорядкові lambdas та list comprehensions

---

## Швидке оновлення після змін

```powershell
# 1. Внесіть зміни в backend/*.py з docstrings
# 2. Перегенеруйте документацію:
py -m pdoc --html backend --output-dir docs/html --force

# 3. Оновіть архів:
Compress-Archive -Path docs/html -DestinationPath docs/cisco_router_wizard_docs.zip -Force
```

---

## Альтернативні інструменти

| Інструмент | Команда | Коли використати |
|------------|---------|-----------------|
| **pdoc3** _(поточний)_ | `py -m pdoc --html backend --output-dir docs/html --force` | Швидка генерація без конфігурації |
| **Sphinx** | `sphinx-apidoc -o docs/sphinx backend/` | Детальна документація з Makefile |
| **mkdocs** | `mkdocs serve` | Live-preview у браузері |
