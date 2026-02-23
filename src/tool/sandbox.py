"""供 Agent 调用的原子化工具集合（教学用途）。"""

import os

from src.tool.registry import tool


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
