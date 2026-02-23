import inspect
from typing import Any, Callable, Dict


class ToolRegistry:
    """极简工具注册中心：负责工具注册、Schema 生成与执行。"""

    def __init__(self):
        """初始化工具字典与 schema 列表。"""
        self.tools: Dict[str, Callable] = {}
        self.schemas = []

    def register(self, func: Callable) -> Callable:
        """装饰器入口：将函数注册为可供 LLM 调用的工具。"""
        name = func.__name__
        self.tools[name] = func
        self.schemas.append(self._generate_schema(func))
        return func

    def _generate_schema(self, func: Callable) -> dict:
        """根据函数签名与注释生成 OpenAI Function Calling Schema。"""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"Execute {func.__name__}"

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # 简化版类型推断，教学场景足够
            param_type = "string"
            if param.annotation == int or param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"

            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}",
            }
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc.split("\n")[0],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def execute(self, tool_name: str, arguments: dict) -> Any:
        """执行指定工具并返回结果。"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        func = self.tools[tool_name]
        return func(**arguments)


# 实例化一个全局工具注册中心
registry = ToolRegistry()


def tool(func):
    """便捷装饰器：等价于 `registry.register(func)`。"""
    return registry.register(func)
