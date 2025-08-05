"""
Обработчики сообщений Telegram бота

Функции для обработки команд и сообщений согласно vision.md
"""

from aiogram.types import Message
from aiogram.filters import Command
from src.llm_client import send_to_llm, build_prompt
from src.config import get_public_config
from src.logging_config import log_command

# Глобальное хранилище истории диалогов в памяти
chat_conversations = {}


def save_to_history(chat_id, user_message, bot_response):
    """Сохранить сообщение в историю диалога"""
    if chat_id not in chat_conversations:
        chat_conversations[chat_id] = []
    
    # Добавляем сообщения пользователя и бота
    chat_conversations[chat_id].extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_response}
    ])
    
    # Обрезаем историю до лимита
    config = get_public_config()
    max_history = config["max_history_length"]
    if len(chat_conversations[chat_id]) > max_history:
        chat_conversations[chat_id] = chat_conversations[chat_id][-max_history:]


def get_conversation_history(chat_id):
    """Получить историю диалога для чата"""
    return chat_conversations.get(chat_id, [])


async def handle_start(message: Message):
    """Обработка команды /start"""
    chat_id = str(message.chat.id)
    username = message.from_user.username if message.from_user else None
    
    # Логируем команду
    log_command(chat_id, "/start", username)
    
    welcome = """👋 Здравствуйте! Я ИИ-ассистент для консультаций.

🔧 Мы специализируемся на:
• Разработке чат-ботов и ИИ-ассистентов
• Интеграции LLM в бизнес-процессы  
• Автоматизации задач с помощью ИИ
• Консультациях по внедрению искусственного интеллекта

❓ Задайте любой вопрос о наших услугах!

📋 Команды: /help - справка, /clear - очистить историю, /stop - завершить"""
    
    await message.answer(welcome)


async def handle_help(message: Message):
    """Обработка команды /help"""
    chat_id = str(message.chat.id)
    username = message.from_user.username if message.from_user else None
    
    # Логируем команду
    log_command(chat_id, "/help", username)
    
    help_text = """📋 Доступные команды:

/start - начать работу с ботом
/help - показать эту справку  
/clear - очистить историю диалога
/stop - завершить диалог

💬 Просто напишите вопрос о наших услугах, и я отвечу!

🔧 Примеры вопросов:
• "Как создать чат-бота для моего бизнеса?"
• "Сколько стоит интеграция ИИ в CRM?"
• "Какие задачи можно автоматизировать с помощью ИИ?"
• "Обучаете ли вы команды работе с ИИ?"
"""
    await message.answer(help_text)


async def handle_clear(message: Message):
    """Обработка команды /clear"""
    chat_id = str(message.chat.id)
    username = message.from_user.username if message.from_user else None
    
    # Логируем команду
    log_command(chat_id, "/clear", username)
    
    if chat_id in chat_conversations:
        del chat_conversations[chat_id]
        await message.answer("✅ История диалога очищена! Можете начать новый разговор.")
    else:
        await message.answer("✅ История диалога уже пуста.")


async def handle_stop(message: Message):
    """Обработка команды /stop"""
    chat_id = str(message.chat.id)
    username = message.from_user.username if message.from_user else None
    
    # Логируем команду
    log_command(chat_id, "/stop", username)
    
    # Очищаем историю при завершении
    if chat_id in chat_conversations:
        del chat_conversations[chat_id]
    
    goodbye = """👋 Спасибо за обращение!

Если у вас появятся новые вопросы о наших услугах ИИ-разработки, просто напишите /start

До свидания! 🤖"""
    
    await message.answer(goodbye)


async def handle_message(message: Message):
    """Обработка обычного сообщения пользователя с историей"""
    user_text = message.text
    chat_id = str(message.chat.id)
    
    # Проверяем что это текстовое сообщение
    if not user_text:
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return
    
    # Отправляем сообщение в LLM с учетом истории
    try:
        # Получаем историю диалога для контекста
        history = get_conversation_history(chat_id)
        
        # Отправляем в LLM с историей
        response = await send_to_llm(user_text, chat_id, history)
        
        # Сохраняем в историю
        save_to_history(chat_id, user_text, response)
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer("Извините, произошла ошибка при обработке вашего сообщения.")


# Устаревший обработчик для совместимости
async def simple_handler(message: Message):
    """Простой обработчик - перенаправляет к handle_message"""
    await handle_message(message)