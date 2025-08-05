FROM python:3.11-slim

# Установка uv для управления зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей (только production)
RUN uv sync --frozen --no-dev

# Копирование исходного кода приложения (без тестов)
COPY main.py ./
COPY src/ ./src/

# Создание директории для логов
RUN mkdir -p logs

# Запуск приложения
CMD ["uv", "run", "python", "main.py"]