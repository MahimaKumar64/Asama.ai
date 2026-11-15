
import time

from backend.prompts import SYSTEM_PROMPT


class ConversationManager:

    def __init__(self, cache_ttl=60):
        self.cache_ttl = cache_ttl

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        self.tool_cache = {}

    def add_user_message(self, question):
        self.messages.append({
            "role": "user",
            "content": question,
        })

    def add_assistant_tool_call(self, message):
        self.messages.append(
            message.model_dump(exclude_none=True)
        )

    def add_tool_result(self, tool_name, result):
        import json

        self.messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": json.dumps(result),
        })

    def add_assistant_message(self, answer):
        self.messages.append({
            "role": "assistant",
            "content": answer,
        })

    def get_cached_result(self, tool_name):
        cached = self.tool_cache.get(tool_name)

        if cached is None:
            return None

        result, timestamp = cached

        if time.monotonic() - timestamp > self.cache_ttl:
            del self.tool_cache[tool_name]
            return None

        return result

    def cache_result(self, tool_name, result):
        self.tool_cache[tool_name] = (
            result,
            time.monotonic(),
        )
