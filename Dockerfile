FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и ставим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Для логов
ENV PYTHONUNBUFFERED=1

# Запуск main.py
CMD ["python", "app/main.py"]
