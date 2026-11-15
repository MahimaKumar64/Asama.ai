
from unittest.mock import MagicMock, patch

from backend.llm_client import OllamaClient


@patch("backend.llm_client.Client")
def test_ollama_client_initialization(mock_client):

    assistant = OllamaClient()

    assert assistant.client is not None
    assert assistant.model == "qwen2.5:3b"


@patch("backend.llm_client.Client")
def test_chat_calls_ollama(mock_client_class):

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    expected_message = MagicMock()
    mock_client.chat.return_value.message = expected_message

    assistant = OllamaClient()

    result = assistant.chat(
        messages=[
            {"role": "user", "content": "What CPU do I have?"}
        ],
        tools=[]
    )

    assert result == expected_message
    mock_client.chat.assert_called_once()
