.PHONY: help install dev run stop restart logs test clean

help:		## Показать список доступных команд
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

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