import copy
from typing import Any, Dict, List


class AgentMemory:
    """管理 Agent 的对话上下文（Context Window）。"""

    def __init__(self, system_prompt: str):
        """初始化记忆窗并写入 system prompt。"""
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_user_message(self, text: str):
        """追加一条用户消息。"""
        self.messages.append({"role": "user", "content": text})

    def add_assistant_message(self, text: str = None, tool_calls: list = None):
        """追加一条助手消息，支持普通文本或 tool_calls。"""
        msg = {"role": "assistant"}
        if text:
            msg["content"] = text
        if tool_calls:
            msg["tool_calls"] = tool_calls
            if not text:
                # OpenAI 要求如果仅返回 tool_calls，content 需为 None 或空字符串
                msg["content"] = None
        self.messages.append(msg)

    def add_tool_response(self, tool_call_id: str, tool_name: str, content: str):
        """追加一条 tool 执行结果消息。"""
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": str(content),
            }
        )

    def get_messages(self) -> List[Dict[str, Any]]:
        """返回当前消息列表的深拷贝，避免外部篡改内部状态。"""
        return copy.deepcopy(self.messages)
