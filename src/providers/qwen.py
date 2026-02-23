import os
from typing import Any, Dict, List

from .base import BaseLLMClient


class QwenLLMClient(BaseLLMClient):
    """Qwen（DashScope OpenAI 兼容）客户端封装。"""

    def __init__(self, model: str = "qwen-plus"):
        """初始化 Qwen 客户端并读取环境变量配置。"""
        import openai
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.environ.get("QWEN_API_KEY")
        base_url = os.environ.get(
            "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        if not api_key:
            self.client = None
            self.mock_mode = True
        else:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.mock_mode = False

        self.model = os.environ.get("LLM_MODEL", model)

    def chat(self, messages: List[Dict], tools_schema: List[Dict] = None) -> Any:
        """执行一次聊天请求；当无 QWEN_API_KEY 时返回 mock 响应。"""
        if self.mock_mode:
            from collections import namedtuple

            Message = namedtuple("Message", ["content", "tool_calls"])
            return Message(content="Mock response due to missing QWEN_API_KEY.", tool_calls=None)

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
