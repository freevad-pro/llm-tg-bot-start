"""
Главный файл Telegram бота для консультации через LLM
"""

import asyncio
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from dotenv import load_dotenv
from src.handlers import simple_handler, handle_start, handle_help, handle_clear, handle_stop, handle_message
from src.config import get_public_config
from src.logging_config import setup_logging, log_bot_start, log_bot_stop


async def main():
    """Основная функция запуска бота"""
    start_time = time.time()
    
    print("LLM Telegram Bot v1.0.0")
    print("Инициализация...")
    
    # Настройка логирования
    logger = setup_logging()
    log_bot_start("1.0.0")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем секретные данные из .env
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Валидация секретных переменных
    if not telegram_token:
        print("Ошибка: TELEGRAM_BOT_TOKEN не найден в .env файле")
        print("Проверьте файл .env и добавьте токен от @BotFather")
        return
        
    if not openrouter_api_key:
        print("Предупреждение: OPENROUTER_API_KEY не найден в .env файле")
        print("Это понадобится для интеграции с LLM на Этапе 4")
    
    # Получаем публичную конфигурацию
    config = get_public_config()
    
    print(f"Конфигурация загружена:")
    print(f"- Модель LLM: {config['model_name']}")
    print(f"- Максимум истории: {config['max_history_length']} сообщений")
    
    # Создаем бота и диспетчер
    bot = Bot(token=telegram_token)
    dp = Dispatcher()
    
    # Регистрируем обработчики команд
    dp.message.register(handle_start, Command("start"))
    dp.message.register(handle_help, Command("help"))
    dp.message.register(handle_clear, Command("clear"))
    dp.message.register(handle_stop, Command("stop"))
    
    # Регистрируем обработчик обычных сообщений (должен быть последним)
    dp.message.register(handle_message)
    
    print("Бот запущен и готов к работе!")
    logger.info("Бот запущен и готов к работе!")
    
    try:
        # Запускаем polling
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        # Логируем остановку
        uptime = time.time() - start_time
        log_bot_stop(uptime_seconds=int(uptime))
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())