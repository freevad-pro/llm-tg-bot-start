"""
Конфигурация логирования для LLM Telegram Bot

Двойное логирование согласно vision.md: файл + консоль одновременно
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from src.config import get_public_config


def setup_logging():
    """Настройка двойного логирования (файл + консоль)"""
    config = get_public_config()
    
    # Создаем главный logger для бота
    logger = logging.getLogger("llm_bot")
    logger.setLevel(getattr(logging, config["log_level"]))
    
    # Очищаем существующие handlers (для перезапуска)
    logger.handlers.clear()
    
    # Создаем директорию для логов если её нет
    log_dir = os.path.dirname(config["log_file_path"])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Единый формат для всех handlers
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler для файла с ротацией (если включен)
    if config["log_to_file"]:
        file_handler = RotatingFileHandler(
            config["log_file_path"], 
            maxBytes=config["log_max_file_size"],
            backupCount=config["log_backup_count"],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Handler для консоли (если включен)
    if config["log_to_console"]:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger():
    """Получить logger для использования в других модулях"""
    return logging.getLogger("llm_bot")


# Функции для структурированного логирования согласно vision.md
def log_bot_start(version="1.0.0"):
    """Логирование запуска бота"""
    logger = get_logger()
    logger.info(f"BOT_START | version={version} | config_loaded=success")


def log_bot_stop(uptime_seconds=None, total_requests=None):
    """Логирование остановки бота"""
    logger = get_logger()
    uptime = f"{uptime_seconds}s" if uptime_seconds else "unknown"
    requests = total_requests if total_requests else "unknown"
    logger.info(f"BOT_STOP | uptime={uptime} | total_requests={requests}")


def log_llm_request(chat_id, message_length, model):
    """Логирование LLM запроса"""
    logger = get_logger()
    logger.info(f"LLM_REQUEST | chat_id={chat_id} | model={model} | message_length={message_length}")


def log_llm_response(chat_id, response_time, response_length):
    """Логирование LLM ответа"""
    logger = get_logger()
    logger.info(f"LLM_RESPONSE | chat_id={chat_id} | response_time={response_time:.2f}s | response_length={response_length}")


def log_llm_error(chat_id, error_type, error_message):
    """Логирование ошибки LLM"""
    logger = get_logger()
    logger.error(f"LLM_ERROR | chat_id={chat_id} | error={error_type} | message=\"{error_message}\"")


def log_command(chat_id, command, username=None):
    """Логирование выполнения команды"""
    logger = get_logger()
    user_info = f"user={username}" if username else "user=unknown"
    logger.info(f"COMMAND | chat_id={chat_id} | {user_info} | command={command}")