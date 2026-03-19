# Dockerfile для контейнеризації backend-частини (у разі переводу Eel у безголовий web-режим)
FROM python:3.10-slim

WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо вихідний код
COPY . .

# Експонуємо порт (наприклад, Eel можна запустити на 8000 порту)
EXPOSE 8000

# Змінні середовища для вимкнення автоматичного відкриття Chrome
ENV EEL_MODE=None
ENV EEL_PORT=8000

# Запуск бекенду
CMD ["python", "-m", "backend.main"]
