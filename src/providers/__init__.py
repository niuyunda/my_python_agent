import os

from .anthropic import AnthropicLLMClient
from .base import BaseLLMClient
from .openai import OpenAILLMClient
from .qwen import QwenLLMClient


def create_llm_client() -> BaseLLMClient:
    """根据 `LLM_PROVIDER` 创建对应的 LLM 客户端实例。"""
    provider = os.environ.get("LLM_PROVIDER", "openai").strip().lower()

    if provider == "openai":
        return OpenAILLMClient()
    if provider == "anthropic":
        return AnthropicLLMClient()
    if provider == "qwen":
        return QwenLLMClient()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}. Supported providers: openai, anthropic, qwen"
    )


__all__ = [
    "BaseLLMClient",
    "OpenAILLMClient",
    "AnthropicLLMClient",
    "QwenLLMClient",
    "create_llm_client",
]
