# Базовый образ — с чего начинаем (уже содержит Python нужной версии)
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей ОТДЕЛЬНО от остального кода
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry и зависимости
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Копируем весь остальной код проекта
COPY backend/ .

# Создаем директорию static в правильном месте.
RUN mkdir -p static/images

RUN chmod -R 755 static

EXPOSE 8000 

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]