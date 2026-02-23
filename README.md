# 极简 Python Agent（Tool Calling ReAct Loop）

这是一个教学向的最小可运行 Agent 项目：
- 用 **ReAct 循环**（Thought → Action → Observation）驱动推理与工具调用
- 用 **装饰器 + 反射** 自动把 Python 函数注册为 LLM 可调用工具
- 保持高内聚、低复杂度，便于学习与二次扩展

---

## 当前代码结构（以仓库为准）

```text
src/
├─ agent/core.py         # Agent 主循环（ReAct）
├─ memory/buffer.py      # 对话记忆窗
├─ providers/openai.py   # OpenAI 客户端封装（支持 mock 模式）
├─ providers/anthropic.py# Anthropic 客户端封装（兼容工具调用）
├─ providers/qwen.py     # Qwen(DashScope) 客户端封装
├─ providers/__init__.py # provider 工厂（按 LLM_PROVIDER 选择）
├─ tool/registry.py      # @tool 注册器 + schema 生成 + 执行
├─ tool/sandbox.py       # 示例工具（calculate/read_file/write_file）
└─ main.py               # 终端入口

tests/unit/
├─ test_agent.py         # Agent 循环行为测试
└─ test_tools.py         # Tool Registry 测试
```

---

## 运行环境

- Python: `>=3.14`（见 `pyproject.toml`）
- 包管理：`uv`

> 如果你想兼容更常见环境（如 3.11/3.12），可把 `requires-python` 下调后重新测试。

---

## 快速开始

### 1) 安装依赖

```bash
uv sync
```

### 2) 配置环境变量

可复制示例：

```bash
cp .env.example .env
```

常用变量：
- `LLM_PROVIDER`：`openai` / `anthropic` / `qwen`
- `LLM_MODEL`：可选，覆盖各 provider 默认模型
- OpenAI: `OPENAI_API_KEY`、`OPENAI_BASE_URL`（可选）
- Anthropic: `ANTHROPIC_API_KEY`
- Qwen: `QWEN_API_KEY`、`QWEN_BASE_URL`（可选，默认 DashScope 兼容地址）

### 3) 启动 Agent

```bash
uv run src/main.py
```

---

## 测试

```bash
uv run --with pytest python -m pytest -q
```

当前测试覆盖：
- Agent 的工具调用闭环是否正常
- Tool schema 生成是否符合 function calling 预期
- Tool 执行路径是否正常

---

## 如何扩展 Agent 能力

在 `src/tool/sandbox.py`（或你自己的工具模块）里新增函数并加 `@tool`：

```python
from src.tool.registry import tool

@tool
def weather(city: str) -> str:
    """获取城市天气。"""
    return f"{city}: sunny"
```

只要模块被 import，工具就会自动注册进 `registry`，Agent 下一轮推理就可调用它。

---

## 已知限制（教学版刻意简化）

- `ToolRegistry` 的类型推断较简化（主要是 string/number/boolean）
- `calculate` 仅做了基础 AST 安全处理，不适合作为生产计算沙盒
- `read_file/write_file` 没有做更严格的路径白名单控制
- Agent `max_loops=5`，用于防止无限调用

---

## 设计目标

这个仓库不是“全功能框架”，而是一个方便你快速理解 Agent 基本原理的 **最小内核**。先跑通闭环，再按业务逐层增强。