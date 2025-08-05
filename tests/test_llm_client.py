"""
Тесты для LLM клиента
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from src.llm_client import load_system_prompt, build_prompt, get_llm_client, send_to_llm


def test_load_system_prompt_success():
    """Тест успешной загрузки системного промпта из файла"""
    test_prompt = "Тестовый системный промпт для ИИ-ассистента"
    
    with patch("builtins.open", mock_open(read_data=test_prompt)):
        result = load_system_prompt()
        assert result == test_prompt


def test_load_system_prompt_file_not_found():
    """Тест загрузки промпта при отсутствии файла"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_system_prompt()
        # Проверяем что возвращается fallback промпт
        assert "дружелюбный ИИ-ассистент" in result
        assert "русском языке" in result


def test_build_prompt_without_history():
    """Тест построения промпта без истории"""
    test_message = "Привет, как дела?"
    
    with patch('src.llm_client.load_system_prompt', return_value="Системный промпт"):
        result = build_prompt("test_chat", test_message)
        
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[0]["content"] == "Системный промпт"
        assert result[1]["role"] == "user"
        assert result[1]["content"] == test_message


def test_build_prompt_with_history():
    """Тест построения промпта с историей"""
    test_message = "Как дела?"
    history = [
        {"role": "user", "content": "Привет!"},
        {"role": "assistant", "content": "Здравствуйте!"}
    ]
    
    with patch('src.llm_client.load_system_prompt', return_value="Системный промпт"):
        result = build_prompt("test_chat", test_message, history)
        
        assert len(result) == 4  # система + 2 история + новое сообщение
        assert result[0]["role"] == "system"
        assert result[1] == history[0]
        assert result[2] == history[1]
        assert result[3]["role"] == "user"
        assert result[3]["content"] == test_message


@patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'})
@patch('src.llm_client.OpenAI')
def test_get_llm_client_success(mock_openai):
    """Тест успешного создания LLM клиента"""
    result = get_llm_client()
    
    mock_openai.assert_called_once_with(
        base_url="https://openrouter.ai/api/v1",
        api_key="test_key"
    )


@patch.dict('os.environ', {}, clear=True)
def test_get_llm_client_no_api_key():
    """Тест создания клиента без API ключа"""
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY не найден"):
        get_llm_client()


@pytest.mark.asyncio
@patch('src.llm_client.get_llm_client')
@patch('src.llm_client.build_prompt')
@patch('src.llm_client.get_public_config')
@patch('src.llm_client.log_llm_request')
@patch('src.llm_client.log_llm_response')
async def test_send_to_llm_success(mock_log_response, mock_log_request, mock_config, mock_build_prompt, mock_get_client):
    """Тест успешной отправки в LLM"""
    # Настройка моков
    mock_config.return_value = {
        "model_name": "test-model",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    mock_build_prompt.return_value = [{"role": "user", "content": "test"}]
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Тестовый ответ"
    
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Выполнение теста
    result = await send_to_llm("Тестовое сообщение", "test_chat")
    
    # Проверки
    assert result == "Тестовый ответ"
    mock_log_request.assert_called_once()
    mock_log_response.assert_called_once()


@pytest.mark.asyncio
@patch('src.llm_client.get_llm_client')
@patch('src.llm_client.build_prompt')
@patch('src.llm_client.get_public_config')
@patch('src.llm_client.log_llm_request')
@patch('src.llm_client.log_llm_error')
async def test_send_to_llm_timeout_error(mock_log_error, mock_log_request, mock_config, mock_build_prompt, mock_get_client):
    """Тест обработки timeout ошибки"""
    # Настройка моков
    mock_config.return_value = {"model_name": "test-model"}
    mock_build_prompt.return_value = []
    mock_get_client.side_effect = Exception("timeout error")
    
    # Выполнение теста
    result = await send_to_llm("test", "test_chat")
    
    # Проверки
    assert "временно недоступен" in result
    mock_log_error.assert_called_once()


@pytest.mark.asyncio
@patch('src.llm_client.get_llm_client')
@patch('src.llm_client.build_prompt')
@patch('src.llm_client.get_public_config')
@patch('src.llm_client.log_llm_request')
@patch('src.llm_client.log_llm_error')
async def test_send_to_llm_rate_limit_error(mock_log_error, mock_log_request, mock_config, mock_build_prompt, mock_get_client):
    """Тест обработки rate limit ошибки"""
    # Настройка моков
    mock_config.return_value = {"model_name": "test-model"}
    mock_build_prompt.return_value = []
    mock_get_client.side_effect = Exception("rate limit exceeded")
    
    # Выполнение теста
    result = await send_to_llm("test", "test_chat")
    
    # Проверки
    assert "Слишком много запросов" in result
    mock_log_error.assert_called_once()