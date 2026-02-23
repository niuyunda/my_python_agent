import os
from typing import List, Dict, Any
from .base import BaseLLMClient

class OpenAILLMClient(BaseLLMClient):
    """极简的 OpenAI 客户端封装"""
    def __init__(self, model: str = "gpt-3.5-turbo"):
        import openai
        from dotenv import load_dotenv
        
        # 尝试从当前目录加载 .env 文件
        load_dotenv()
        
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL") # 支持自定义代理或 OpenRouter 接口
        
        if not api_key:
            # Fallback 伪造返回以通过本地免网络测试
            self.client = None
            self.mock_mode = True
        else:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.mock_mode = False
            
        self.model = os.environ.get("LLM_MODEL", model) # 支持通过环境变量动态覆盖模型名字
        
    def chat(self, messages: List[Dict], tools_schema: List[Dict] = None) -> Any:
        if self.mock_mode:
             # 为了在没有 API Key 的情况下跑通测试，我们返回一个 Mock 的 response
             from collections import namedtuple
             Message = namedtuple('Message', ['content', 'tool_calls'])
             Choice = namedtuple('Choice', ['message'])
             Response = namedtuple('Response', ['choices'])
             return Response(choices=[Choice(message=Message(content="Mock response due to missing API Key.", tool_calls=None))])

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        if tools_schema and len(tools_schema) > 0:
            kwargs["tools"] = tools_schema
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message
