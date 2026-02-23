from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMClient(ABC):
    """
    所有 LLM 客户端的抽象基类。
    规范了标准接口，实现 Agent 和具体大模型供应商的解耦。
    """
    
    @abstractmethod
    def chat(self, messages: List[Dict], tools_schema: List[Dict] = None) -> Any:
        """
        核心聊天方法，子类必须实现此方法。
        
        Args:
            messages: OpenAI 格式的对话历史记录 (e.g., [{"role": "user", "content": "hello"}])
            tools_schema: 用于 Function Calling 的工具描述列表
            
        Returns:
            模型返回的统一响应对象 (目前兼容 OpenAI Message 对象格式，需包含 content 和可选的 tool_calls)
        """
        pass
