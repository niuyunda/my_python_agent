# 极简 AI Agent 引擎演示项目

本项目为**基于第一性原理的纯粹 AI Agent 核心引擎**。这参考了目前硅谷流行的 `pi-mono` 等极简、高内聚 Agent 框架的设计哲学。

## 核心架构

1. **`src/llm_client.py`**:
   极简的 LLM 通信基座。在这里，与模型（如 OpenAI API）的交互被抽象为最基础的聊天收发，并维护了一个原生的 Memory（上下文窗口）。
2. **`src/tools_registry.py`**:
   极其强大的魔法部件。“把常规函数变成大模型的肢体”。我们设计了一个 `@tool` 装饰器，它能利用 Python 的反射机制（Inspector）自动解析类型注解和文档说明，将其零成本转换为符合 LLM Function Calling 规范的 JSON Schema 契约。
3. **`src/agent.py`**:
   **引擎的心脏 (The ReAct Loop)**。它不关心任何具体业务，只负责无限循环驱动经典的 `Thought -> Action -> Observation` 模式。
4. **`src/sandbox_tools.py`**:
   我们提供给这头猛兽的“原子积木”和沙盒。例如 `read_file`, `write_file`, `calculate`。

## 如何运行你的 Agent

这是一个可以直接在终端交互的纯粹数字生命体。

### 1. 安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境并唤醒 Agent
如果不配置 `OPENAI_API_KEY`，Agent 将会在 Mock 模式下运行，用于安全测试。
如果你想见证奇迹的发生，请配置你的 API Key 然后运行核心引擎：
```bash
export OPENAI_API_KEY="sk-xxxx"
python3 src/main.py
```

### 3. 如何增加它的能力？
你不需要去修改那些冗杂的 Service 层。你要做的，仅仅是在 `src/sandbox_tools.py` 中写一个最质朴的 Python 原子函数，然后加上 `@tool` 装饰器。
**它立刻就能听懂并调用！**


我们配套了 AgentLoop 和 ToolRegistry 解析层面的拦截测试，确保任何对底层引擎的扰动都会被拦下：
```bash
python3 -m pytest tests/unit/
```
