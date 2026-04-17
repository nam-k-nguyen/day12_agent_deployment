import json
import re
import requests
import dotenv
import os
from openai import OpenAI

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
open_router_key = os.getenv("OPEN_ROUTER_API")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set!")

client = OpenAI(api_key=openai_api_key)

SYSTEM_PROMPT = """
You are a helpful assistant for a banking application. Be concise and accurate.
"""

class LLM:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.messages = [{"role": "system", "content": system_prompt}]

    def call_llm_openai(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=self.messages, max_tokens=200
        )
        message = response.choices[0].message
        return message.content

    def call_llm_openrouter(self, user_input: str) -> str:
        try:
            self.messages.append({"role": "user", "content": user_input})
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {open_router_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(
                    {
                        "model": "z-ai/glm-4.5-air:free",
                        "messages": self.messages,
                        "max_tokens": 200,
                    }
                ),
            ).json()
            message = response["choices"][0]["message"]
            return message["content"]
        except Exception as e:
            print(e)
            return "Error"

    def call_llm(self, user_input: str) -> str:
        return self.call_llm_openai(user_input)
