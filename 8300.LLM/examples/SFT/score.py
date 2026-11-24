"""生成回答の最終行を採点し、途中式の等式変形が同値か確認する。"""
import ast
import operator
import re
from fractions import Fraction

FINAL = re.compile(r"Answer: x = ([+-]?[0-9]+)")
EQUATION = re.compile(
    r"([0-9x+*/().\-][0-9x+*/().\- \t]*)\s*=\s*"
    r"([0-9x+*/().\-][0-9x+*/().\- \t]*)"
)


def linear(node):
    """対応する構文木から変数の係数と定数項を分数で求める。"""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return Fraction(0), Fraction(str(node.value))
    if isinstance(node, ast.Name) and node.id == "x":
        return Fraction(1), Fraction(0)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        a, b = linear(node.operand)
        return (-a, -b) if isinstance(node.op, ast.USub) else (a, b)
    if isinstance(node, ast.BinOp):
        a, b = linear(node.left)
        c, d = linear(node.right)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            combine = operator.add if isinstance(node.op, ast.Add) else operator.sub
            return combine(a, c), combine(b, d)
        if isinstance(node.op, ast.Mult) and (not a or not c):
            return a * d + c * b, b * d
        if isinstance(node.op, ast.Div) and not c and d:
            return a / d, b / d
    raise ValueError("Unsupported expression")


def solution(left, right):
    """唯一の解を分数で、恒等式と矛盾式をそれぞれ all と none で返す。"""
    def parse(side):
        """暗黙の乗算を補って片辺を解析し、変数の係数と定数項を返す。"""
        side = re.sub(r"(?<=[0-9)])\s*(?=[x(])", "*", side.strip())
        return linear(ast.parse(side, mode="eval").body)

    a, b = parse(left)
    c, d = parse(right)
    if a == c:
        return "all" if b == d else "none"
    return (d - b) / (a - c)


def score(response, problem):
    """最終回答の正誤・抽出可否と、各途中式の同値性を判定する。"""
    lines = response.strip().splitlines()
    answer_match = FINAL.fullmatch(lines[-1].strip()) if lines else None
    answer = int(answer_match[1]) if answer_match else None
    answer_status = "unparseable"
    if answer is not None:
        answer_status = "correct" if answer == problem["answer"] else "incorrect"

    previous = solution(*problem["equation"].split("="))
    steps = []
    for line in lines[:-1] if answer_match else lines:
        for part in re.split(r"(?:⇒|→|\\implies|\\Rightarrow)", line):
            part = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", part)
            part = part.replace("−", "-").replace("×", "*").replace("÷", "/")
            match = EQUATION.search(part) if part.count("=") == 1 else None
            if "=" not in part:
                continue
            if match is None:
                steps.append("unparseable")
                previous = None
                continue
            try:
                current = solution(*(side.rstrip(" .") for side in match.groups()))
            except (SyntaxError, ValueError, ArithmeticError):
                steps.append("unparseable")
                previous = None
                continue
            steps.append(
                "unparseable" if previous is None else
                "equivalent" if current == previous else "not_equivalent"
            )
            previous = current
    reasoning = "no_steps"
    if steps:
        reasoning = (
            "not_equivalent" if "not_equivalent" in steps else
            "unparseable" if "unparseable" in steps else "equivalent"
        )
    return {"answer": answer_status, "reasoning": reasoning, "steps": steps}
