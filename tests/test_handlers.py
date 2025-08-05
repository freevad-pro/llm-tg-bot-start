"""
Тесты для обработчиков сообщений
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.handlers import (
    save_to_history, get_conversation_history, chat_conversations,
    handle_start, handle_help, handle_clear, handle_stop, handle_message
)


def test_save_to_history_new_chat():
    """Тест сохранения истории для нового чата"""
    # Очищаем глобальное состояние
    chat_conversations.clear()
    
    chat_id = "test_chat_1"
    user_message = "Привет!"
    bot_response = "Здравствуйте!"
    
    save_to_history(chat_id, user_message, bot_response)
    
    assert chat_id in chat_conversations
    assert len(chat_conversations[chat_id]) == 2
    assert chat_conversations[chat_id][0]["role"] == "user"
    assert chat_conversations[chat_id][0]["content"] == user_message
    assert chat_conversations[chat_id][1]["role"] == "assistant"
    assert chat_conversations[chat_id][1]["content"] == bot_response


def test_save_to_history_existing_chat():
    """Тест добавления к существующей истории"""
    chat_conversations.clear()
    
    chat_id = "test_chat_2"
    
    # Первое сообщение
    save_to_history(chat_id, "Первое", "Ответ1")
    # Второе сообщение
    save_to_history(chat_id, "Второе", "Ответ2")
    
    assert len(chat_conversations[chat_id]) == 4
    assert chat_conversations[chat_id][2]["content"] == "Второе"
    assert chat_conversations[chat_id][3]["content"] == "Ответ2"


@patch('src.handlers.get_public_config')
def test_save_to_history_limit(mock_config):
    """Тест ограничения длины истории"""
    chat_conversations.clear()
    mock_config.return_value = {"max_history_length": 4}
    
    chat_id = "test_chat_limit"
    
    # Добавляем больше сообщений чем лимит
    save_to_history(chat_id, "Msg1", "Resp1")  # 2 записи
    save_to_history(chat_id, "Msg2", "Resp2")  # 4 записи (лимит)
    save_to_history(chat_id, "Msg3", "Resp3")  # должно обрезать до 4
    
    assert len(chat_conversations[chat_id]) == 4
    # Проверяем что старые сообщения удалились, остались последние 4
    assert chat_conversations[chat_id][0]["content"] == "Msg2"
    assert chat_conversations[chat_id][1]["content"] == "Resp2" 
    assert chat_conversations[chat_id][2]["content"] == "Msg3"
    assert chat_conversations[chat_id][3]["content"] == "Resp3"


def test_get_conversation_history_exists():
    """Тест получения существующей истории"""
    chat_conversations.clear()
    
    chat_id = "test_history"
    test_history = [{"role": "user", "content": "test"}]
    chat_conversations[chat_id] = test_history
    
    result = get_conversation_history(chat_id)
    assert result == test_history


def test_get_conversation_history_not_exists():
    """Тест получения истории для несуществующего чата"""
    chat_conversations.clear()
    
    result = get_conversation_history("nonexistent_chat")
    assert result == []


@pytest.mark.asyncio
@patch('src.handlers.log_command')
async def test_handle_start(mock_log):
    """Тест обработчика команды /start"""
    # Создаем мок объект сообщения
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.from_user.username = "test_user"
    mock_message.answer = AsyncMock()
    
    await handle_start(mock_message)
    
    # Проверяем что команда была залогирована
    mock_log.assert_called_once_with("12345", "/start", "test_user")
    
    # Проверяем что ответ был отправлен
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "ИИ-ассистент" in args[0]
    assert "специализируемся" in args[0]


@pytest.mark.asyncio
@patch('src.handlers.log_command')
async def test_handle_help(mock_log):
    """Тест обработчика команды /help"""
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.from_user.username = "test_user"
    mock_message.answer = AsyncMock()
    
    await handle_help(mock_message)
    
    mock_log.assert_called_once_with("12345", "/help", "test_user")
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "/start" in args[0]
    assert "/clear" in args[0]
    assert "команды" in args[0]


@pytest.mark.asyncio
@patch('src.handlers.log_command')
async def test_handle_clear_with_history(mock_log):
    """Тест очистки истории когда она существует"""
    chat_conversations.clear()
    
    # Создаем историю
    chat_id = "12345"
    chat_conversations[chat_id] = [{"role": "user", "content": "test"}]
    
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.from_user.username = "test_user"
    mock_message.answer = AsyncMock()
    
    await handle_clear(mock_message)
    
    # Проверяем что история удалена
    assert chat_id not in chat_conversations
    
    mock_log.assert_called_once_with("12345", "/clear", "test_user")
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "очищена" in args[0]


@pytest.mark.asyncio
@patch('src.handlers.log_command')
async def test_handle_clear_no_history(mock_log):
    """Тест очистки истории когда её нет"""
    chat_conversations.clear()
    
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.from_user.username = "test_user"
    mock_message.answer = AsyncMock()
    
    await handle_clear(mock_message)
    
    mock_log.assert_called_once_with("12345", "/clear", "test_user")
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "уже пуста" in args[0]


@pytest.mark.asyncio
@patch('src.handlers.log_command')
async def test_handle_stop(mock_log):
    """Тест обработчика команды /stop"""
    chat_conversations.clear()
    
    # Создаем историю для удаления
    chat_id = "12345"
    chat_conversations[chat_id] = [{"role": "user", "content": "test"}]
    
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.from_user.username = "test_user"
    mock_message.answer = AsyncMock()
    
    await handle_stop(mock_message)
    
    # Проверяем что история удалена
    assert chat_id not in chat_conversations
    
    mock_log.assert_called_once_with("12345", "/stop", "test_user")
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "Спасибо" in args[0]
    assert "/start" in args[0]


@pytest.mark.asyncio
@patch('src.handlers.send_to_llm')
@patch('src.handlers.get_conversation_history')
async def test_handle_message_success(mock_get_history, mock_send_llm):
    """Тест успешной обработки сообщения"""
    chat_conversations.clear()
    
    # Настройка моков
    mock_get_history.return_value = []
    mock_send_llm.return_value = "Ответ LLM"
    
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.text = "Тестовое сообщение"
    mock_message.answer = AsyncMock()
    
    await handle_message(mock_message)
    
    # Проверки
    mock_send_llm.assert_called_once_with("Тестовое сообщение", "12345", [])
    mock_message.answer.assert_called_once_with("Ответ LLM")
    
    # Проверяем что сообщение сохранилось в историю
    assert "12345" in chat_conversations
    assert len(chat_conversations["12345"]) == 2


@pytest.mark.asyncio
async def test_handle_message_no_text():
    """Тест обработки сообщения без текста"""
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.text = None
    mock_message.answer = AsyncMock()
    
    await handle_message(mock_message)
    
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "текстовое сообщение" in args[0]


@pytest.mark.asyncio
@patch('src.handlers.send_to_llm')
@patch('src.handlers.get_conversation_history')
async def test_handle_message_llm_error(mock_get_history, mock_send_llm):
    """Тест обработки ошибки LLM"""
    chat_conversations.clear()
    
    # Настройка моков
    mock_get_history.return_value = []
    mock_send_llm.side_effect = Exception("LLM Error")
    
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.text = "Тестовое сообщение"
    mock_message.answer = AsyncMock()
    
    await handle_message(mock_message)
    
    # Проверяем что отправлено сообщение об ошибке
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "произошла ошибка" in args[0]


@pytest.mark.asyncio
async def test_handle_start_no_username():
    """Тест команды /start для пользователя без username"""
    mock_message = Mock()
    mock_message.chat.id = 12345
    mock_message.from_user = None  # Нет пользователя
    mock_message.answer = AsyncMock()
    
    with patch('src.handlers.log_command') as mock_log:
        await handle_start(mock_message)
        
        # Проверяем что username = None обрабатывается корректно
        mock_log.assert_called_once_with("12345", "/start", None)
        mock_message.answer.assert_called_once()