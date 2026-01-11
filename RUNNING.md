Запуск (швидко)

Вимоги
- Python 3.8+
- Windows (PowerShell або cmd)
- Браузер Chrome/Edge для GUI (опційно)

Коротко — з кореня проєкту:

1) Створити та активувати віртуальне середовище

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1    # PowerShell
# або для cmd:
# .\.venv\Scripts\activate.bat
```

2) Встановити залежності

```powershell
pip install -r requirements.txt
# якщо потрібно pytest для тестів:
pip install pytest
```

3) Запустити програму

```powershell
py -3 -m backend.main
# або
python -m backend.main
```

4) Запустити тести

```powershell
# Усі тести
py -3 -m pytest -q
# Конкретний файл
py -3 -m pytest tests/test_main.py -q
# або через unittest
py -3 -m unittest tests.test_main -v
```

Зауваження
- Обов'язково запускати з кореня проєкту, щоб відносні імпорти працювали.
- Якщо "Python was not found" — використайте `py -3` або додайте `python` до PATH.
- Для GUI Eel відкриває браузер; якщо не відкривається, вкажіть `mode` у `backend/main.py`.
