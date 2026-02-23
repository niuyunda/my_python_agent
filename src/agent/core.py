import json
from src.providers.base import BaseLLMClient
from src.memory.buffer import AgentMemory
from src.tool.registry import registry

class Agent:
    """
    Agent 核心引擎：
    负责驱动 Thought(思考) -> Action(调用工具) -> Observation(获取结果) 的循环。
    """
    def __init__(self, llm_client: BaseLLMClient, system_prompt: str = "You are a helpful AI assistant."):
        """初始化 Agent，注入 LLM 客户端与系统提示词。"""
        self.memory = AgentMemory(system_prompt)
        self.llm = llm_client
        self.max_loops = 5 # 防止陷入无限工具调用死循环

    def run(self, user_input: str) -> str:
        """主运行循环 (Event Loop)"""
        self.memory.add_user_message(user_input)
        
        loop_count = 0
        while loop_count < self.max_loops:
            loop_count += 1
            
            # 1. 发送给大模型进行思考 (Thought)
            print(f"[Agent] 思考中... (Loop {loop_count})")
            response_msg = self.llm.chat(
                messages=self.memory.get_messages(),
                tools_schema=registry.schemas
            )
            
            # 处理响应格式并加入记忆
            if getattr(response_msg, 'tool_calls', None):
                self.memory.add_assistant_message(tool_calls=response_msg.tool_calls)
            else:
                 self.memory.add_assistant_message(text=response_msg.content)

            # 2. 判断是否需要行动 (Action)
            if not getattr(response_msg, 'tool_calls', None):
                # 没有工具调用，模型给出了最终的文本回答，结束循环
                return response_msg.content

            # 3. 执行工具调用！(Execution & Observation)
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"[Agent] 决定执行工具 -> {func_name}({arguments})")
                
                try:
                    # 原生 Python 级别的方法调用
                    result = registry.execute(func_name, arguments)
                    print(f"         └─> Observation: {str(result)[:50]}...")
                except Exception as e:
                    result = f"Error executing tool {func_name}: {str(e)}"
                    print(f"         └─> Observation Error: {result}")
                
                # 将观察结果喂回给模型记忆中
                self.memory.add_tool_response(
                    tool_call_id=tool_call.id,
                    tool_name=func_name,
                    content=result
                )
            
            # 循环继续，LLM 会基于新的 Observation 再次评估
        
        return "Agent stopped: Reached maximum loop iteration limit."
