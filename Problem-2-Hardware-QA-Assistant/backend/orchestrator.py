
from backend.llm_client import OllamaClient
from backend.tool_registry import (
    get_tool_definitions,
    execute_registered_tool,
)
from backend.conversation import ConversationManager
from config.settings import MAX_TOOL_ROUNDS


class HardwareAssistant:

    def __init__(self):
        self.llm = OllamaClient()
        self.conversation = ConversationManager()

    def ask(self, question):

        question = question.strip()

        if not question:
            return "Please enter a question."

        self.conversation.add_user_message(question)

        try:
            for _ in range(MAX_TOOL_ROUNDS):

                message = self.llm.chat(
                    messages=self.conversation.messages,
                    tools=get_tool_definitions(),
                )

                tool_calls = message.tool_calls or []

                if not tool_calls:
                    answer = message.content or (
                        "I couldn't generate an answer."
                    )

                    self.conversation.add_assistant_message(answer)

                    return answer

                self.conversation.add_assistant_tool_call(message)

                for tool_call in tool_calls:

                    function_name = tool_call.function.name
                    arguments = tool_call.function.arguments or {}

                    # Check whether we already have recent results.
                    result = self.conversation.get_cached_result(
                        function_name
                    )

                    if result is None:

                        result = execute_registered_tool(
                            function_name,
                            arguments,
                        )

                        # Cache only successful tool executions.
                        if result.get("success") is True:
                            self.conversation.cache_result(
                                function_name,
                                result,
                            )

                    self.conversation.add_tool_result(
                        function_name,
                        result,
                    )

            return (
                "I reached the maximum number of hardware tool calls "
                "for this question. Please try a more specific question."
            )

        except Exception:
            return (
                "I couldn't complete your request. "
                "Please check that the local Ollama server is running "
                "and try again."
            )
