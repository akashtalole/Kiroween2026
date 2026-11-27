#!/usr/bin/env python3
"""Proof strength: mutate a module with small, realistic bugs and count how many the tests catch.

Usage: mutate.py <module.py> <tests path> [--max N] [--json]
A mutant is 'killed' when the test command fails. Score = killed / total. Survivors are blind spots worth a new property.
"""
from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

CMP_SWAP = {ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
            ast.In: ast.NotIn, ast.NotIn: ast.In}


def mutation_points(tree: ast.AST) -> list[tuple[int, str]]:
    pts = []
    for idx, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and type(node.ops[0]) in CMP_SWAP:
            pts.append((idx, f"line {node.lineno}: flip comparison {type(node.ops[0]).__name__}"))
        elif isinstance(node, ast.BoolOp):
            pts.append((idx, f"line {node.lineno}: swap {'and' if isinstance(node.op, ast.And) else 'or'}"))
        elif isinstance(node, ast.Constant) and type(node.value) is int:
            pts.append((idx, f"line {node.lineno}: constant {node.value} -> {node.value + 1}"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("max", "min"):
            pts.append((idx, f"line {node.lineno}: {node.func.id} -> {'min' if node.func.id == 'max' else 'max'}"))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            pts.append((idx, f"line {node.lineno}: drop 'not'"))
        elif isinstance(node, ast.List) and len(node.elts) > 1 and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
            for k in range(len(node.elts)):
                pts.append((idx * 1000 + k, f"line {node.lineno}: drop list item {node.elts[k].value!r}"))
    return pts


def apply(tree: ast.AST, point: int) -> ast.AST:
    t = copy.deepcopy(tree)
    idx, item = (point // 1000, point % 1000) if point >= 1000 else (point, None)
    for i, node in enumerate(ast.walk(t)):
        if i != idx:
            continue
        if item is not None and isinstance(node, ast.List):
            del node.elts[item]
        elif isinstance(node, ast.Compare):
            node.ops[0] = CMP_SWAP[type(node.ops[0])]()
        elif isinstance(node, ast.BoolOp):
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        elif isinstance(node, ast.Constant):
            node.value = node.value + 1
        elif isinstance(node, ast.Call):
            node.func.id = "min" if node.func.id == "max" else "max"
        elif isinstance(node, ast.UnaryOp):
            # replace `not x` by `x` via a no-op unary plus on a bool-coerced operand
            node.op = ast.UAdd()
            node.operand = ast.Call(func=ast.Name("bool", ast.Load()), args=[node.operand], keywords=[])
        break
    return ast.fix_missing_locations(t)


def run(module: pathlib.Path, tests: pathlib.Path, max_mutants: int | None) -> dict:
    src = module.read_text(encoding="utf-8")
    tree = ast.parse(src)
    pts = mutation_points(tree)[: max_mutants or None]
    killed, survivors = 0, []
    with tempfile.TemporaryDirectory() as tmp:
        shadow = pathlib.Path(tmp) / module.name
        # copy the tests beside the mutant: pytest puts a test file's own folder first on sys.path,
        # so tests left in place would import the original module and every mutant would "survive"
        test_files = [tests] if tests.is_file() else sorted(tests.glob("test_*.py"))
        for tf in test_files:
            shutil.copy(tf, pathlib.Path(tmp) / tf.name)
        tests = pathlib.Path(tmp)
        for point, desc in pts:
            shadow.write_text(ast.unparse(apply(tree, point)), encoding="utf-8")
            env = {**os.environ, "PYTHONPATH": tmp + os.pathsep + os.environ.get("PYTHONPATH", ""),
                   "PYTHONDONTWRITEBYTECODE": "1"}
            p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", str(tests)],
                               capture_output=True, text=True, env=env, cwd=tmp, stdin=subprocess.DEVNULL)
            if p.returncode != 0:
                killed += 1
            else:
                survivors.append(desc)
    total = len(pts)
    return {"module": str(module), "mutants": total, "killed": killed,
            "score": round(killed / total, 3) if total else None, "survivors": survivors}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module"); ap.add_argument("tests")
    ap.add_argument("--max", type=int); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = run(pathlib.Path(a.module).resolve(), pathlib.Path(a.tests).resolve(), a.max)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"Proof strength for {a.module}: {r['killed']}/{r['mutants']} mutants killed ({r['score']})")
        for s in r["survivors"]:
            print(f"  survived: {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
