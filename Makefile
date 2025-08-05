.PHONY: help install dev run stop restart logs test clean build run-docker stop-docker logs-docker clean-docker

help:		## Показать список доступных команд
	@echo "Доступные команды:"
	@echo "  install      - Установить зависимости"
	@echo "  dev          - Запустить бота локально (интерактивно)"
	@echo "  run          - Запустить бота в фоне"
	@echo "  stop         - Остановить бота"
	@echo "  restart      - Перезапустить бота"
	@echo "  logs         - Показать логи бота"
	@echo "  test         - Запустить тесты"
	@echo "  clean        - Очистить кеш uv"
	@echo "  build        - Собрать Docker образ"
	@echo "  run-docker   - Запустить бота в Docker контейнере"
	@echo "  stop-docker  - Остановить Docker контейнер"
	@echo "  logs-docker  - Показать логи из Docker контейнера"
	@echo "  clean-docker - Очистить Docker образы и контейнеры"

install:	## Установить зависимости
	uv sync

dev:		## Запустить бота локально (интерактивно)
	uv run python main.py

run:		## Запустить бота в фоне
	@echo "Запуск LLM Telegram Bot..."
	@uv run python main.py &
	@echo "Бот запущен в фоне"

stop:		## Остановить бота
	@echo "Остановка LLM Telegram Bot..."
	@taskkill /F /IM python.exe 2>nul || echo "Процесс не найден"
	@echo "Бот остановлен"

restart:	## Перезапустить бота
	@$(MAKE) stop
	@sleep 2
	@$(MAKE) run

logs:		## Показать логи бота
	@echo "Показ логов LLM Telegram Bot:"
	@if exist logs\\llm_bot.log (type logs\\llm_bot.log) else (echo "Логи не найдены. Запустите бота для создания логов.")

test:		## Запустить тесты
	uv run pytest

clean:		## Очистить кеш uv
	uv clean

build:		## Собрать Docker образ
	@echo "Сборка Docker образа LLM Telegram Bot..."
	docker-compose build
	@echo "Docker образ собран"

run-docker:	## Запустить бота в Docker контейнере
	@echo "Запуск LLM Telegram Bot в Docker..."
	docker-compose up -d
	@echo "Бот запущен в Docker (контейнер: llm-telegram-bot)"

stop-docker:	## Остановить Docker контейнер
	@echo "Остановка Docker контейнера..."
	docker-compose down
	@echo "Docker контейнер остановлен"

logs-docker:	## Показать логи из Docker контейнера
	@echo "Логи LLM Telegram Bot из Docker:"
	docker-compose logs -f

clean-docker:	## Очистить Docker образы и контейнеры
	@echo "Очистка Docker..."
	docker-compose down --rmi all --volumes --remove-orphans || true
	docker system prune -f
	@echo "Docker очищен"