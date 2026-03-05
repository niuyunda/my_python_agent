import pytest
from src.tool.registry import ToolRegistry
from src.tool.registry import registry
import src.tool.sandbox  # noqa: F401  # 触发工具注册

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


def test_execute_python_file_success(tmp_path, monkeypatch):
    monkeypatch.setattr(src.tool.sandbox, "WORKSPACE_ROOT", str(tmp_path))
    script = tmp_path / "hello.py"
    write_result = registry.execute(
        "write_file",
        {
            "filepath": str(script),
            "content": (
                "import sys\n"
                "print('hello from stdout')\n"
                "print('hello from stderr', file=sys.stderr)\n"
            )
        }
    )
    assert "Successfully wrote" in write_result

    result = registry.execute(
        "execute_python_file",
        {"filepath": str(script), "timeout_seconds": 2}
    )

    assert "Exit Code: 0" in result
    assert "STDOUT:\nhello from stdout" in result
    assert "STDERR:\nhello from stderr" in result


def test_execute_python_file_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(src.tool.sandbox, "WORKSPACE_ROOT", str(tmp_path))
    script = tmp_path / "sleepy.py"
    script.write_text(
        "import time\n"
        "print('start', flush=True)\n"
        "time.sleep(2)\n"
        "print('done')\n",
        encoding="utf-8"
    )

    result = registry.execute(
        "execute_python_file",
        {"filepath": str(script), "timeout_seconds": 1}
    )

    assert "timed out after 1 seconds" in result
    assert "STDOUT:\nstart" in result


def test_execute_python_file_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(src.tool.sandbox, "WORKSPACE_ROOT", str(tmp_path))
    missing = tmp_path / "missing.py"

    result = registry.execute(
        "execute_python_file",
        {"filepath": str(missing), "timeout_seconds": 2}
    )

    assert "does not exist" in result


def test_execute_python_file_non_py_file(tmp_path, monkeypatch):
    monkeypatch.setattr(src.tool.sandbox, "WORKSPACE_ROOT", str(tmp_path))
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("not python", encoding="utf-8")

    result = registry.execute(
        "execute_python_file",
        {"filepath": str(txt_file), "timeout_seconds": 2}
    )

    assert "is not a Python file" in result


def test_execute_python_file_invalid_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(src.tool.sandbox, "WORKSPACE_ROOT", str(tmp_path))
    script = tmp_path / "valid.py"
    script.write_text("print('ok')\n", encoding="utf-8")

    result = registry.execute(
        "execute_python_file",
        {"filepath": str(script), "timeout_seconds": 0}
    )

    assert "timeout_seconds must be a positive number" in result
