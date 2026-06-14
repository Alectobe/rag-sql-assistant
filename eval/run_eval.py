"""Evaluation harness: execution accuracy of generated vs reference SQL.

Run from project root:  python eval/run_eval.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from app import execute  # noqa: E402
from app.pipeline import ask  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent / "cases.yaml"


def _run_reference(sql: str):
    res = execute.run(sql)
    # Order-insensitive comparison of the result set.
    return sorted(tuple(str(c) for c in row) for row in res.rows)


def main() -> int:
    cases = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
    passed = errors = 0

    for case in cases:
        cid, question = case["id"], case["question"]
        try:
            expected = _run_reference(case["reference_sql"])
        except Exception as exc:  # noqa: BLE001
            print(f"[SKIP] {cid}: reference SQL failed: {exc}")
            continue

        result = ask(question)
        if result.error:
            errors += 1
            print(f"[FAIL] {cid}: pipeline error: {result.error}")
            continue

        actual = sorted(tuple(str(c) for c in row) for row in result.rows)
        if actual == expected:
            passed += 1
            print(f"[PASS] {cid}")
        else:
            print(f"[FAIL] {cid}: result mismatch")
            print(f"       generated SQL: {result.sql}")

    total = len(cases)
    print(f"\nExecution accuracy: {passed}/{total} passed, {errors} pipeline errors")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
