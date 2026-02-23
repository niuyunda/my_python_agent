import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base import BaseLLMClient


@dataclass
class _ToolFunction:
    """OpenAI 风格 tool.function 的最小兼容结构。"""

    name: str
    arguments: str


@dataclass
class _ToolCall:
    """OpenAI 风格 tool_call 的最小兼容结构。"""

    id: str
    function: _ToolFunction


@dataclass
class _ResponseMessage:
    """统一返回给 Agent 的消息结构。"""

    content: Optional[str]
    tool_calls: Optional[List[_ToolCall]]


class AnthropicLLMClient(BaseLLMClient):
    """Anthropic 客户端封装，向上兼容 OpenAI 风格响应。"""

    def __init__(self, model: str = "claude-3-5-sonnet-latest"):
        """初始化 Anthropic 客户端并加载环境变量配置。"""
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            self.client = None
            self.mock_mode = True
        else:
            import anthropic

            self.client = anthropic.Anthropic(api_key=api_key)
            self.mock_mode = False

        self.model = os.environ.get("LLM_MODEL", model)

    @staticmethod
    def _to_anthropic_tools(tools_schema: Optional[List[Dict]]) -> List[Dict]:
        """将 OpenAI tools schema 转换为 Anthropic tools 格式。"""
        if not tools_schema:
            return []

        tools = []
        for t in tools_schema:
            func = t.get("function", {})
            tools.append(
                {
                    "name": func.get("name", "tool"),
                    "description": func.get("description", ""),
                    "input_schema": func.get(
                        "parameters", {"type": "object", "properties": {}}
                    ),
                }
            )
        return tools

    @staticmethod
    def _convert_messages(messages: List[Dict]) -> tuple[str, List[Dict]]:
        """将 OpenAI 风格消息列表转换为 Anthropic messages。"""
        system_parts: List[str] = []
        anth_messages: List[Dict] = []

        for msg in messages:
            role = msg.get("role")
            if role == "system":
                system_parts.append(msg.get("content", ""))
                continue

            if role == "user":
                anth_messages.append({"role": "user", "content": msg.get("content", "")})
                continue

            if role == "assistant":
                if msg.get("tool_calls"):
                    blocks = []
                    text = msg.get("content")
                    if text:
                        blocks.append({"type": "text", "text": text})
                    for tc in msg.get("tool_calls", []):
                        args = tc.get("function", {}).get("arguments", "{}")
                        try:
                            input_obj = json.loads(args)
                        except json.JSONDecodeError:
                            input_obj = {"raw_arguments": args}
                        blocks.append(
                            {
                                "type": "tool_use",
                                "id": tc.get("id", "tool_use_unknown"),
                                "name": tc.get("function", {}).get("name", "unknown_tool"),
                                "input": input_obj,
                            }
                        )
                    anth_messages.append({"role": "assistant", "content": blocks})
                else:
                    anth_messages.append(
                        {"role": "assistant", "content": msg.get("content", "")}
                    )
                continue

            if role == "tool":
                anth_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.get("tool_call_id", "tool_use_unknown"),
                                "content": str(msg.get("content", "")),
                            }
                        ],
                    }
                )

        system_prompt = "\n".join([p for p in system_parts if p]).strip()
        return system_prompt, anth_messages

    def chat(self, messages: List[Dict], tools_schema: List[Dict] = None) -> Any:
        """执行一次 Anthropic 请求并转换为统一响应结构。"""
        if self.mock_mode:
            return _ResponseMessage(
                content="Mock response due to missing ANTHROPIC_API_KEY.", tool_calls=None
            )

        system_prompt, anth_messages = self._convert_messages(messages)
        tools = self._to_anthropic_tools(tools_schema)

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": anth_messages,
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)

        text_parts: List[str] = []
        tool_calls: List[_ToolCall] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(
                    _ToolCall(
                        id=block.id,
                        function=_ToolFunction(
                            name=block.name,
                            arguments=json.dumps(block.input, ensure_ascii=False),
                        ),
                    )
                )

        content = "\n".join([p for p in text_parts if p]).strip() or None
        return _ResponseMessage(content=content, tool_calls=tool_calls or None)
