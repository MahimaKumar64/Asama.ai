
from ollama import Client

from config.settings import OLLAMA_HOST, OLLAMA_MODEL


class OllamaClient:

    def __init__(self):
        self.client = Client(host=OLLAMA_HOST)
        self.model = OLLAMA_MODEL

    def chat(self, messages, tools=None):

        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options={
                "temperature": 0
            }
        )

        return response.message
