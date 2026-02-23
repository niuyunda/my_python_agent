import pytest

from src.providers import (
    AnthropicLLMClient,
    OpenAILLMClient,
    QwenLLMClient,
    create_llm_client,
)


def test_create_llm_client_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    client = create_llm_client()

    assert isinstance(client, OpenAILLMClient)
    assert client.mock_mode is True


def test_create_llm_client_anthropic(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    client = create_llm_client()

    assert isinstance(client, AnthropicLLMClient)
    assert client.mock_mode is True


def test_create_llm_client_qwen(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "qwen")
    monkeypatch.delenv("QWEN_API_KEY", raising=False)

    client = create_llm_client()

    assert isinstance(client, QwenLLMClient)
    assert client.mock_mode is True


def test_create_llm_client_invalid_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "not-supported")

    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        create_llm_client()


def test_anthropic_tools_schema_conversion():
    tools_schema = [
        {
            "type": "function",
            "function": {
                "name": "weather",
                "description": "get weather",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }
    ]

    tools = AnthropicLLMClient._to_anthropic_tools(tools_schema)

    assert len(tools) == 1
    assert tools[0]["name"] == "weather"
    assert tools[0]["description"] == "get weather"
    assert tools[0]["input_schema"]["required"] == ["city"]


def test_anthropic_message_conversion_with_tool_calls():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "2+2?"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {"name": "calculate", "arguments": '{"expression":"2+2"}'},
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "name": "calculate",
            "content": "4",
        },
    ]

    system_prompt, anth_messages = AnthropicLLMClient._convert_messages(messages)

    assert system_prompt == "You are helpful."
    assert anth_messages[0] == {"role": "user", "content": "2+2?"}
    assert anth_messages[1]["role"] == "assistant"
    assert anth_messages[1]["content"][0]["type"] == "tool_use"
    assert anth_messages[1]["content"][0]["name"] == "calculate"
    assert anth_messages[2]["role"] == "user"
    assert anth_messages[2]["content"][0]["type"] == "tool_result"
    assert anth_messages[2]["content"][0]["tool_use_id"] == "call_1"
