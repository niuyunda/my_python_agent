import os
from typing import Any, Dict, List

from .base import BaseLLMClient


class OpenAILLMClient(BaseLLMClient):
    """OpenAI 客户端封装（支持无 Key 的 mock 模式）。"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """初始化 OpenAI 客户端并读取环境变量配置。"""
        import openai
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL")

        if not api_key:
            self.client = None
            self.mock_mode = True
        else:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.mock_mode = False

        self.model = os.environ.get("LLM_MODEL", model)

    def chat(self, messages: List[Dict], tools_schema: List[Dict] = None) -> Any:
        """执行一次聊天请求；当开启 mock_mode 时返回模拟响应。"""
        if self.mock_mode:
            from collections import namedtuple

            Message = namedtuple("Message", ["content", "tool_calls"])
            Choice = namedtuple("Choice", ["message"])
            Response = namedtuple("Response", ["choices"])
            return Response(
                choices=[
                    Choice(
                        message=Message(
                            content="Mock response due to missing API Key.", tool_calls=None
                        )
                    )
                ]
            )

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if tools_schema and len(tools_schema) > 0:
            kwargs["tools"] = tools_schema
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message
