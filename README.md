# Cisco Router Wizard

Простий інструмент із GUI (Eel) для генерації конфігурацій Cisco-маршрутизаторів на основі введених даних.

## Зміст репозиторію

```
backend/           # Бекенд: генерація конфігів, валідація
  templates/       # Jinja2-шаблони для кожної секції конфігу
web/               # Фронтенд (HTML/JS), з'єднаний з бекендом через Eel
tests/
  unit/
    test_validators/   # Тести валідаторів
    test_generators/   # Тести генераторів конфігурацій
  integration/         # End-to-end тести
  performance/         # Benchmark тести
SPECIFICATIONS.md  # Специфікації ключових функцій
README.md
```

## Вимоги

- Python 3.8+
- Рекомендовано: virtualenv (venv)
- Для GUI: браузер Chrome або Edge

## Встановлення (Windows)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
```

## Запуск застосунку

```powershell
py -3 -m backend.main
```

## Запуск тестів

```powershell
# Усі тести
py -m pytest tests/ -v

# Тільки валідатори
py -m pytest tests/unit/test_validators/ -v

# Тільки генератори
py -m pytest tests/unit/test_generators/ -v

# З benchmark
py -m pytest tests/performance/ -v
```

---

## 📖 Стандарти документування

### Мова та формат: Google-style docstrings

У проєкті використовується **Google-style docstrings** — стандарт документування для Python, підтримуваний Sphinx, pdoc3 та VSCode IntelliSense.

#### Структура docstring

```python
def my_function(param1: str, param2: int = 0) -> str:
    #Короткий опис того, що робить функція (одним реченням).

    Розширений опис, якщо потрібен. Може займати декілька рядків.
    Описує поведінку, важливі особливості, граничні випадки.

    Args:
        param1 (str): Опис першого параметра.
        param2 (int, optional): Опис другого. Defaults to ``0``.

    Returns:
        str: Що повертає функція та в якому форматі.

    Raises:
        ValueError: Коли і чому виникає виняток.

    Examples:
        >>> my_function("hello")
        'HELLO'
        >>> my_function("world", 1)
        'WORLD!'
    #
```

#### Правила для цього проєкту

| Правило | Деталі |
|---------|--------|
| **Обов'язкові секції** | `Args`, `Returns` для всіх публічних функцій |
| **Опціональні секції** | `Raises`, `Examples`, `Note` — додавати за потреби |
| **Мова** | Опис функції — українська; назви параметрів, типи, IOS-команди — англійська |
| **Типізація** | Використовувати type hints у сигнатурі (`param: str -> str`) |
| **Приклади** | Обов'язкові для складних функцій (валідатори, генератори) |
| **Інлайн-коментарі** | `#` для пояснення нетривіальної логіки всередині функцій |

#### Що документувати

✅ **Обов'язково**:
- Всі публічні функції в `backend/` (`validate.py`, `generate.py`, `protocols.py`)
- Тест-класи — docstring з описом що тестується
- Складна логіка (конвертація масок, шаблонний рендеринг)

⚠️ **За потреби**:
- Допоміжні приватні функції (`_mask_to_wildcard`) — якщо логіка нетривіальна
- Jinja2-шаблони — коментар вгорі файлу з описом змінних контексту

❌ **Не потрібно**:
- Геттери/сеттери з очевидною поведінкою
- `conftest.py` fixtures з самоочевидними назвами

---

### 🔧 Інструменти для автоматичної генерації документації

| Інструмент | Опис | Команда |
|------------|------|---------|
| **[Sphinx](https://www.sphinx-doc.org/)** | Стандарт Python-документації; генерує HTML, PDF. Підтримує Google-style через `napoleon` extension | `sphinx-apidoc -o docs/ backend/` |
| **[pdoc3](https://pdoc3.github.io/pdoc/)** | Простіший аналог Sphinx; генерує HTML прямо з docstrings без конфігурації | `pdoc3 --html backend/ -o docs/` |
| **[mkdocs + mkdocstrings](https://mkdocstrings.github.io/)** | Документація у Markdown + автовставка docstrings; гарний UI | `mkdocs serve` |
| **VSCode IntelliSense** | Показує docstrings у hover-підказках автоматично | (вбудований) |

**Рекомендація для проєкту**: `pdoc3` — мінімальна конфігурація, швидкий старт:
```powershell
py -m pip install pdoc3
py -m pdoc3 --html backend/ -o docs/
```

---

## Правила для нових контриб'юторів

### Додаючи нову функцію

1. **Напишіть docstring** за Google-style перед кодом.
2. **Вкажіть типи** у сигнатурі функції.
3. **Додайте приклад** у секцію `Examples:`.
4. **Напишіть тест** у відповідний файл у `tests/`.

### Додаючи новий протокол маршрутизації

1. Додайте Jinja2-шаблон у `backend/templates/routing/<назва>.j2`.
2. Додайте обробку в `generate_protocol_config()` у `protocols.py`.
3. Задокументуйте нові ключі `routing_config` у docstring функції.
4. Напишіть тест-клас у `tests/unit/test_generators/test_routing.py`.

### Додаючи новий валідатор

1. Реалізуйте в `backend/validate.py`.
2. Функція повинна повертати `""` (OK) або `"❌ Error: ..."` (помилка).
3. Додайте тест у `tests/unit/test_validators/`.
4. Додайте виклик у `validate_inputs()`, якщо потрібно.

---

## Типові проблеми

- `"Python was not found"` → використайте `py -3` або додайте Python до PATH.
- Тести не знаходять `backend` → запускайте pytest з кореня проєкту.
- `pytest` не встановлено → `py -3 -m pip install pytest pytest-benchmark`.

## Контакти

Відкривайте issue в репозиторії з описом проблеми або pull request.
