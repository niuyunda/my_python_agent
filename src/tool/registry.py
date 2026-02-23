import inspect
from typing import Callable, Any, Dict

class ToolRegistry:
    """
    极简工具箱 (参考 pi-mono `CallableTool`)
    把一个普通的 Python 函数转化为大模型可以通过 JSON 调用的工具。
    核心利用 Python 的 TypeHint 和 Docstring 来自动生成 Schema。
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas = []

    def register(self, func: Callable) -> Callable:
        """装饰器：将函数注册为 Tool"""
        name = func.__name__
        self.tools[name] = func
        self.schemas.append(self._generate_schema(func))
        return func

    def _generate_schema(self, func: Callable) -> dict:
        """解析函数签名，生成 OpenAI 兼容的 Function Calling Schema"""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"Execute {func.__name__}"
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
                
            # 简化版：这里我们将所有参数都视作 string 或 number，实际中可以做更复杂的类型推断
            param_type = "string" 
            if param.annotation == int or param.annotation == float:
                 param_type = "number"
            elif param.annotation == bool:
                 param_type = "boolean"
                 
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}" # 在真实环境下这里可以进一步解析 docstring 里的 Args:
            }
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc.split('\n')[0], # 取简短描述
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def execute(self, tool_name: str, arguments: dict) -> Any:
        """真正的执行动作 (Action)"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        func = self.tools[tool_name]
        return func(**arguments)

# 实例化一个全局的沙盒工具箱
registry = ToolRegistry()

# 提供一个便捷装饰器
def tool(func):
    return registry.register(func)
