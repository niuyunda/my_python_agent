import pytest
from unittest.mock import MagicMock
from src.agent import Agent
import src.sandbox_tools  # 必须引入以触发 @tool 注册

class MockToolCall:
    def __init__(self, name, arguments):
        self.id = "call_mock_id_123"
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments

class MockResponseMsg:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

def test_agent_run_loop_with_tool_call(monkeypatch):
    """验证 Agent 的 Thought -> Action 循环是否能被正确驱动"""
    agent = Agent()
    
    # 模拟一个两步的完美 LLM 响应流
    # Loop 1: LLM 决定调用 `calculate` 工具
    # Loop 2: LLM 拿到工具结果后，给出最终文本
    mock_responses = [
        MockResponseMsg(None, [MockToolCall("calculate", '{"expression": "10 * 5"}')]),
        MockResponseMsg("计算结果是 50 啦！", None)
    ]
    
    def mock_chat(*args, **kwargs):
        if not mock_responses:
             return MockResponseMsg("Agent stopped early", None)
        return mock_responses.pop(0)
        
    # 打桩替换掉真实的 LLM 网络请求
    monkeypatch.setattr(agent.llm, "chat", mock_chat)
    
    # 触发测试
    final_answer = agent.run("10 * 5 等于多少？")
    
    # 验证最终结果
    assert "50" in final_answer
    
    # 验证记忆窗是否捕获了所有的步骤 (system -> user -> assistant(tool_call) -> tool(result) -> assistant_final)
    messages = agent.memory.get_messages()
    assert len(messages) == 5
    assert messages[2]["role"] == "assistant"
    assert "tool_calls" in messages[2]
    assert messages[3]["role"] == "tool"
    assert messages[3]["name"] == "calculate"
    assert messages[3]["content"] == "50"
    assert messages[4]["role"] == "assistant"
    assert messages[4]["content"] == "计算结果是 50 啦！"
