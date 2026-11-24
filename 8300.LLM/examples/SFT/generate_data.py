"""答えのみと途中式付きの学習・検証データ、および共通テストデータを生成する。"""
import json
import math
import random
from pathlib import Path

SEED = 42
DATA = Path(__file__).resolve().parent / "data"
SPLITS = {"train": 1000, "validation": 100, "test": 200}
CONDITIONS = ("answer_only", "worked")
INSTRUCTION = 'Write the final line as "Answer: x = <integer>".'


def normalize(a, b, c, d):
    """共通整数因子、両辺の符号反転、左右の入れ替えを同一視する比較キーを返す。"""
    divisor = math.gcd(a, b, c, d)
    sides = (a // divisor, b // divisor), (c // divisor, d // divisor)
    negated = tuple(tuple(-value for value in side) for side in sides)
    return min(tuple(sorted(sides)), tuple(sorted(negated)))


def expression(coefficient, constant):
    """変数の係数と定数項から、方程式の片辺を表す文字列を組み立てる。"""
    if not coefficient:
        return str(constant)
    term = {1: "x", -1: "-x"}.get(coefficient, f"{coefficient}x")
    if not constant:
        return term
    sign = "+" if constant > 0 else "-"
    return f"{term} {sign} {abs(constant)}"


def generate():
    """片辺と両辺に変数がある問題を同数生成し、整数解と途中式を付ける。"""
    rng = random.Random(SEED)
    problems = {}
    coefficients = [number for number in range(-12, 13) if number]
    for both_sides in (False, True):
        count = 0
        while count < sum(SPLITS.values()) // 2:
            x = rng.randint(-20, 20)
            a = rng.choice(coefficients)
            c = rng.choice(coefficients) if both_sides else 0
            b = rng.randint(-30, 30)
            d = (a - c) * x + b
            if a == c:
                continue
            key = normalize(a, b, c, d)
            if key in problems:
                continue
            equation = f"{expression(a, b)} = {expression(c, d)}"
            question = f"Solve for x: {equation}.\n{INSTRUCTION}"
            steps = []
            if c:
                action = "Subtract" if c > 0 else "Add"
                direction = "from" if c > 0 else "to"
                steps.append(
                    f"{action} {expression(abs(c), 0)} {direction} both sides: "
                    f"{expression(a - c, b)} = {d}."
                )
            if b:
                action = "Subtract" if b > 0 else "Add"
                direction = "from" if b > 0 else "to"
                steps.append(
                    f"{action} {abs(b)} {direction} both sides: "
                    f"{expression(a - c, 0)} = {d - b}."
                )
            if a - c != 1:
                steps.append(f"Divide both sides by {a - c}: x = {x}.")
            if not steps:
                continue
            problems[key] = {
                "equation": equation,
                "form": "both_sides" if both_sides else "one_side",
                "answer": x,
                "messages": [{"role": "user", "content": question}],
                "steps": steps,
            }
            count += 1
    return list(problems.values())


def read_jsonl(path):
    """UTF-8 の JSONL ファイルを読み込み、レコードのリストを返す。"""
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source]


def write_jsonl(path, rows):
    """レコードを UTF-8 の JSONL として1行ずつ書き出す。"""
    with path.open("w", encoding="utf-8") as target:
        for row in rows:
            target.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    """問題を分割し、学習・検証の2条件と共通テストを JSONL に保存する。"""
    problems = generate()
    rng = random.Random(SEED)
    groups = {
        form: [problem for problem in problems if problem["form"] == form]
        for form in ("one_side", "both_sides")
    }
    for group in groups.values():
        rng.shuffle(group)

    DATA.mkdir(exist_ok=True)
    offset = 0
    for split, count in SPLITS.items():
        end = offset + count // 2
        rows = groups["one_side"][offset:end] + groups["both_sides"][offset:end]
        offset = end
        rng.shuffle(rows)
        if split == "test":
            write_jsonl(DATA / "test.jsonl", (
                {key: value for key, value in row.items() if key != "steps"}
                for row in rows
            ))
            continue

        for condition in CONDITIONS:
            records = []
            for row in rows:
                answer = f"Answer: x = {row['answer']}"
                lines = row["steps"] + [answer] if condition == "worked" else [answer]
                assistant = {"role": "assistant", "content": "\n".join(lines)}
                records.append({"messages": row["messages"] + [assistant]})
            write_jsonl(DATA / f"{split}_{condition}.jsonl", records)


if __name__ == "__main__":
    main()
