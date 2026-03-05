"""供 Agent 调用的原子化工具集合（教学用途）。"""

import os
import subprocess
import sys

from src.tool.registry import tool

WORKSPACE_ROOT = os.path.realpath(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)


def _normalize_output(output) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)


def _is_within_workspace(resolved_filepath: str) -> bool:
    try:
        return os.path.commonpath([resolved_filepath, WORKSPACE_ROOT]) == WORKSPACE_ROOT
    except ValueError:
        return False

@tool
def calculate(expression: str) -> str:
    """安全计算基础数学表达式并返回字符串结果。"""
    try:
        # 注意：eval 在生产中非常危险；此处仅作教学沙盒演示
        import ast
        import operator

        def eval_expr(node):
            """递归求值 AST 节点，仅允许受控算术操作。"""
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.BinOp):
                return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            if isinstance(node, ast.UnaryOp):
                return operators[type(node.op)](eval_expr(node.operand))
            raise TypeError(node)

        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        return str(eval_expr(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


@tool
def read_file(filepath: str) -> str:
    """读取指定文件内容。"""
    try:
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist."
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(filepath: str, content: str) -> str:
    """将文本内容写入指定文件。"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filepath}."
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@tool
def execute_python_file(filepath: str, timeout_seconds: int = 5) -> str:
    """执行指定的 Python 文件并返回 stdout/stderr (Execute a Python file and capture stdout/stderr)."""
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or timeout_seconds <= 0
    ):
        return "Error: timeout_seconds must be a positive number."

    try:
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist."
        if not filepath.endswith(".py"):
            return f"Error: File {filepath} is not a Python file."
        resolved_filepath = os.path.realpath(os.path.abspath(filepath))
        if not _is_within_workspace(resolved_filepath):
            return f"Error: File {filepath} is outside trusted workspace root."
        filepath = resolved_filepath

        completed = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False
        )

        stdout = _normalize_output(completed.stdout).rstrip("\n")
        stderr = _normalize_output(completed.stderr).rstrip("\n")
        return (
            f"Exit Code: {completed.returncode}\n"
            f"STDOUT:\n{stdout if stdout else '(empty)'}\n"
            f"STDERR:\n{stderr if stderr else '(empty)'}"
        )
    except subprocess.TimeoutExpired as e:
        stdout = _normalize_output(e.stdout).rstrip("\n")
        stderr = _normalize_output(e.stderr).rstrip("\n")
        return (
            f"Error: Python execution timed out after {timeout_seconds} seconds.\n"
            f"STDOUT:\n{stdout if stdout else '(empty)'}\n"
            f"STDERR:\n{stderr if stderr else '(empty)'}"
        )
    except Exception as e:
        return f"Error executing Python file: {str(e)}"
