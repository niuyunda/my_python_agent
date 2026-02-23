import pytest
from src.tool.registry import ToolRegistry

def test_tool_registry_schema_generation():
    registry = ToolRegistry()
    
    @registry.register
    def mock_weather_tool(location: str, unit: str = "celsius") -> str:
        """Get the current weather for a location."""
        return f"Weather in {location} is 20 {unit}"

    # 1. 验证函数是否成功注册
    assert "mock_weather_tool" in registry.tools
    
    # 2. 验证 Schema 生成是否符合 OpenAI Function Calling 规范
    schema = registry.schemas[0]
    assert schema["type"] == "function"
    
    function_def = schema["function"]
    assert function_def["name"] == "mock_weather_tool"
    assert function_def["description"] == "Get the current weather for a location."
    
    props = function_def["parameters"]["properties"]
    assert "location" in props
    assert props["location"]["type"] == "string"
    assert "unit" in props
    
    # 3. 验证 required 字段 (unit有默认值，不应在 required 中)
    required = function_def["parameters"]["required"]
    assert "location" in required
    assert "unit" not in required

def test_tool_execution():
    registry = ToolRegistry()
    
    @registry.register
    def add(a: int, b: int) -> int:
        return a + b
        
    result = registry.execute("add", {"a": 5, "b": 10})
    assert result == 15
