"""
这是一组供 Agent 使用的“原子化”工具示例。
对于 Agent 来说，这些就像是它的手和眼睛。
"""
from src.tools_registry import tool
import os

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
