FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Чтобы вывод Python шел сразу в лог
ENV PYTHONUNBUFFERED=1

# EXPOSE нужен для Timeweb
EXPOSE 8080

# Команда запуска
CMD ["python", "main.py"]
