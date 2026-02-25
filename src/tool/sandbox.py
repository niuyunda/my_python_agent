"""
这是一组供 Agent 使用的“原子化”工具示例。
对于 Agent 来说，这些就像是它的手和眼睛。
"""
from src.tool.registry import tool
import os
import subprocess
import sys


def _normalize_output(output) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return str(output)

@tool
def calculate(expression: str) -> str:
    """计算数学表达式的值 (Evaluate a mathematical expression)."""
    try:
        # 注意：eval在生产中非常危险，此处仅为演示沙盒Agent能力
        import ast
        import operator
        
        def eval_expr(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return operators[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(node)

        operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
        
        return str(eval_expr(ast.parse(expression, mode='eval').body))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

@tool
def read_file(filepath: str) -> str:
    """读取指定文件的内容 (Read contents of a file)."""
    try:
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist."
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_file(filepath: str, content: str) -> str:
    """将文本内容写入到指定文件中 (Write text content to a file)."""
    try:
        # 为了演示安全，我们这里最好加一点防守逻辑，比如检查路径
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filepath}."
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@tool
def execute_python_file(filepath: str, timeout_seconds: int = 5) -> str:
    """执行指定的 Python 文件并返回 stdout/stderr (Execute a Python file and capture stdout/stderr)."""
    try:
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist."
        if not filepath.endswith(".py"):
            return f"Error: File {filepath} is not a Python file."

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
