# 极简 AI Agent 引擎演示项目

本项目已经从“传统的企业级 MVC 架构（Controller/Service/Repository）”脱胎换骨，重构为**基于第一性原理的纯粹 AI Agent 核心引擎**。这参考了目前硅谷流行的 `pi-mono` 等极简、高内聚 Agent 框架的设计哲学。

在 AI 时代，冗长的业务串联代码变成了耗材，真正长青的资产是：**“对 LLM 意图的驱动循环（Agent Loop）”** 与 **“绝对纯粹的原子化工具箱（Tools Registry）”**。

## 核心架构大跃进

原有的业务层代码被全部剔除，现在的世界极其清爽：

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
如果不配置 `OPENAI_API_KEY`，Agent 将会在 Mock（打桩）模式下运行，用于安全测试。
如果你想见证奇迹的发生，请配置你的 API Key 然后运行核心引擎：
```bash
export OPENAI_API_KEY="sk-xxxx"
python3 src/main.py
```

### 3. 如何增加它的能力？
你不需要去修改那些冗杂的 Service 层。你要做的，仅仅是在 `src/sandbox_tools.py` 中写一个最质朴的 Python 原子函数，然后加上 `@tool` 装饰器。
**它立刻就能听懂并调用！**

## 运行自动化测试护栏

正如在《第五部分：防腐化工程》中所述，AI 时代代码是最廉价的，**但“测试（Gatekeeper）”是最昂贵且不可或缺的**。

我们配套了 AgentLoop 和 ToolRegistry 解析层面的拦截测试，确保任何对底层引擎的扰动都会被拦下：
```bash
python3 -m pytest tests/unit/
```

---
*“在算力泛滥的时代，软件不再是一台复杂的预先装配好的汽车，而是一套严丝合缝的履带和一堆高质量的齿轮原件，等待智能意志自行拼装。—— 这就是 AI 时代的软件工程核心思想。”*
