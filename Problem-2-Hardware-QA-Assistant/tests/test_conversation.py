
from unittest.mock import MagicMock

from backend.conversation import ConversationManager


def test_conversation_starts_with_system_prompt():
    conversation = ConversationManager()

    assert conversation.messages[0]["role"] == "system"


def test_add_user_message():
    conversation = ConversationManager()

    conversation.add_user_message("What CPU do I have?")

    assert conversation.messages[-1]["role"] == "user"
    assert conversation.messages[-1]["content"] == "What CPU do I have?"


def test_cache_stores_and_returns_result():
    conversation = ConversationManager()

    result = {
        "success": True,
        "result": {"model": "AMD Ryzen"}
    }

    conversation.cache_result("get_cpu_info", result)

    assert conversation.get_cached_result("get_cpu_info") == result


def test_cache_returns_none_for_missing_tool():
    conversation = ConversationManager()

    assert conversation.get_cached_result("get_cpu_info") is None


def test_expired_cache_is_removed():
    conversation = ConversationManager(cache_ttl=0)

    result = {"success": True}

    conversation.cache_result("get_cpu_info", result)

    assert conversation.get_cached_result("get_cpu_info") is None


def test_tool_result_is_added_to_history():
    conversation = ConversationManager()

    result = {"success": True}

    conversation.add_tool_result("get_cpu_info", result)

    assert conversation.messages[-1]["role"] == "tool"
    assert conversation.messages[-1]["tool_name"] == "get_cpu_info"


def test_assistant_message_is_added_to_history():
    conversation = ConversationManager()

    conversation.add_assistant_message("Your CPU is AMD Ryzen.")

    assert conversation.messages[-1]["role"] == "assistant"
    assert "AMD Ryzen" in conversation.messages[-1]["content"]
