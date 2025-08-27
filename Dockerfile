FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY app/ .

# Чтобы вывод Python шел сразу в лог
ENV PYTHONUNBUFFERED=1

# EXPOSE нужен для Timeweb
EXPOSE 9999

# Команда запуска
CMD ["python", "app/main.py"]
