import copy
from typing import List, Dict, Any

class AgentMemory:
    """管理对话上下文 (Context Window)"""
    def __init__(self, system_prompt: str):
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        
    def add_user_message(self, text: str):
        self.messages.append({"role": "user", "content": text})
        
    def add_assistant_message(self, text: str = None, tool_calls: list = None):
        msg = {"role": "assistant"}
        if text:
            msg["content"] = text
        if tool_calls:
            msg["tool_calls"] = tool_calls
            if not text:
               msg["content"] = None #  openai 要求如果只有tool_calls，content必须是空或者 None 
        self.messages.append(msg)
        
    def add_tool_response(self, tool_call_id: str, tool_name: str, content: str):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": str(content)
        })
        
    def get_messages(self):
        return copy.deepcopy(self.messages)
