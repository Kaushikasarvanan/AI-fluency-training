import ast
import operator
from config import COURSE_FEES


def get_course_fee(course_code: str) -> str:
    """Look up the fee for one course code."""
    fee = COURSE_FEES.get(course_code.strip().upper())
    return str(fee) if fee is not None else f"Unknown course code: {course_code}"


_ALLOWED = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def calculator(expression: str) -> str:
    """Safely calculate an arithmetic expression."""
    try:
        tree = ast.parse(expression, mode="eval").body
        return str(_eval(tree))
    except Exception as exc:
        return f"Calculator error: {exc}"


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](
            _eval(node.left),
            _eval(node.right),
        )

    raise ValueError("Only numbers and + - * / are allowed")

TOOL_FUNCTIONS = {
    "get_course_fee": get_course_fee,
    "calculator": calculator
}
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_course_fee",
            "description": "Get the fee for a course code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_code": {
                        "type": "string"
                    }
                },
                "required": ["course_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate a simple arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string"
                    }
                },
                "required": ["expression"],
            },
        },
    },
]