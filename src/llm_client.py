"""
Работа с LLM через OpenRouter

Функции взаимодействия с LLM согласно vision.md
"""

import os
import time
from openai import OpenAI
from src.config import get_public_config
from src.logging_config import log_llm_request, log_llm_response, log_llm_error


def get_llm_client():
    """Создать клиент для OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY не найден в .env файле")
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )


def load_system_prompt():
    """Загрузка системного промпта из файла"""
    config = get_public_config()
    try:
        with open(config["system_prompt_file"], "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Вы - дружелюбный ИИ-ассистент. Отвечайте вежливо и профессионально на русском языке."


async def send_to_llm(user_message, chat_id="unknown", history=None):
    """Отправка запроса в OpenRouter с учетом истории диалога"""
    start_time = time.time()
    
    try:
        config = get_public_config()
        client = get_llm_client()
        
        # Логируем запрос
        log_llm_request(chat_id, len(user_message), config["model_name"])
        
        # Строим сообщения для LLM с историей
        messages = build_prompt(chat_id, user_message, history)
        
        # Отправляем запрос
        response = client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"]
        )
        
        response_content = response.choices[0].message.content
        response_time = time.time() - start_time
        
        # Логируем ответ
        log_llm_response(chat_id, response_time, len(response_content))
        
        return response_content
        
    except Exception as e:
        # Логируем ошибку
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            error_type = "timeout"
            user_message = "Извините, сервис временно недоступен. Попробуйте еще раз."
        elif "rate limit" in error_msg.lower():
            error_type = "rate_limit"
            user_message = "Слишком много запросов. Подождите немного и повторите."
        elif "api" in error_msg.lower():
            error_type = "api_error"
            user_message = "Произошла техническая ошибка. Обратитесь к администратору."
        else:
            error_type = "unknown"
            user_message = "Не удалось получить ответ. Попробуйте переформулировать вопрос."
        
        log_llm_error(chat_id, error_type, error_msg)
        return user_message


def build_prompt(chat_id, user_message, history=None):
    """Формирование промпта с контекстом и системным сообщением"""
    messages = [{"role": "system", "content": load_system_prompt()}]
    
    # Добавляем историю диалога если есть
    if history:
        messages.extend(history)
    
    # Добавляем текущее сообщение пользователя
    messages.append({"role": "user", "content": user_message})
    
    return messages