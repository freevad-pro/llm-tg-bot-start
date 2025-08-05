"""
Тесты для модуля конфигурации
"""

import pytest
from src.config import get_public_config


def test_get_public_config():
    """Тест получения публичной конфигурации"""
    config = get_public_config()
    
    # Проверяем наличие всех обязательных ключей
    required_keys = [
        "model_name", "temperature", "max_tokens", "max_history_length",
        "system_prompt_file", "log_to_file", "log_to_console", 
        "log_file_path", "log_level", "log_max_file_size", "log_backup_count"
    ]
    
    for key in required_keys:
        assert key in config, f"Отсутствует обязательный ключ: {key}"
    
    # Проверяем типы данных
    assert isinstance(config["model_name"], str)
    assert isinstance(config["temperature"], (int, float))
    assert isinstance(config["max_tokens"], int)
    assert isinstance(config["max_history_length"], int)
    assert isinstance(config["system_prompt_file"], str)
    assert isinstance(config["log_to_file"], bool)
    assert isinstance(config["log_to_console"], bool)
    assert isinstance(config["log_file_path"], str)
    assert isinstance(config["log_level"], str)
    assert isinstance(config["log_max_file_size"], int)
    assert isinstance(config["log_backup_count"], int)
    
    # Проверяем разумные значения
    assert 0.0 <= config["temperature"] <= 2.0, "Температура должна быть от 0 до 2"
    assert config["max_tokens"] > 0, "max_tokens должен быть положительным"
    assert config["max_history_length"] > 0, "max_history_length должен быть положительным"
    assert config["log_max_file_size"] > 0, "log_max_file_size должен быть положительным"
    assert config["log_backup_count"] > 0, "log_backup_count должен быть положительным"


def test_config_constants():
    """Тест проверки констант конфигурации"""
    from src.config import MODEL_NAME, TEMPERATURE, MAX_TOKENS, MAX_HISTORY_LENGTH
    
    # Проверяем что константы имеют правильные типы
    assert isinstance(MODEL_NAME, str)
    assert isinstance(TEMPERATURE, (int, float))
    assert isinstance(MAX_TOKENS, int)
    assert isinstance(MAX_HISTORY_LENGTH, int)
    
    # Проверяем что константы не пустые
    assert MODEL_NAME.strip() != ""
    assert MAX_TOKENS > 0
    assert MAX_HISTORY_LENGTH > 0