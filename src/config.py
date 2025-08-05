"""
Конфигурация приложения

Публичные настройки приложения согласно vision.md
Секретные данные (токены) читаются отдельно из .env
"""

# Настройки LLM
MODEL_NAME = "openai/gpt-4o-mini"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Настройки истории диалогов
MAX_HISTORY_LENGTH = 20

# Системные настройки
SYSTEM_PROMPT_FILE = "src/system_prompt.md"

# Настройки логирования
LOG_TO_FILE = True          # Логировать в файл
LOG_TO_CONSOLE = True       # Логировать в консоль
LOG_FILE_PATH = "logs/llm_bot.log"
LOG_LEVEL = "INFO"
LOG_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5        # Количество файлов ротации


def get_public_config():
    """Получить публичные настройки приложения"""
    return {
        "model_name": MODEL_NAME,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "max_history_length": MAX_HISTORY_LENGTH,
        "system_prompt_file": SYSTEM_PROMPT_FILE,
        # Настройки логирования
        "log_to_file": LOG_TO_FILE,
        "log_to_console": LOG_TO_CONSOLE,
        "log_file_path": LOG_FILE_PATH,
        "log_level": LOG_LEVEL,
        "log_max_file_size": LOG_MAX_FILE_SIZE,
        "log_backup_count": LOG_BACKUP_COUNT
    }