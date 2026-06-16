"""Evaluation harness: execution accuracy of generated vs reference SQL.

Execution accuracy = the result set of the generated SQL equals the result set
of the reference SQL (order-insensitive). On top of accuracy the harness reports
latency, retry rate and parse errors, broken down by difficulty.

A case whose reference SQL returns nothing (empty or a single scalar 0) is marked
[INVALID] and excluded from the accuracy denominator: it would otherwise pass
vacuously ("empty == empty") and hide real failures.

Run from project root:  python eval/run_eval.py
"""
from __future__ import annotations

import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from app import execute  # noqa: E402
from app.pipeline import ask  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent / "cases.yaml"
_ZERO_SCALARS = {"0", "0.0", "None", ""}


def _norm_cell(value) -> str:
    """Normalize a cell for comparison. A DateTime at midnight equals the Date,
    so toStartOfDay(d) and d compare equal ('2026-06-15 00:00:00' -> '2026-06-15')."""
    s = str(value)
    if s.endswith(" 00:00:00"):
        s = s[:-9]
    return s


def _result_set(rows: list[list]) -> list[tuple[str, ...]]:
    """Order-insensitive, type-insensitive view of a result for comparison."""
    return sorted(tuple(_norm_cell(c) for c in row) for row in rows)


def _is_vacuous(result_set: list[tuple[str, ...]]) -> bool:
    """True if the reference produced nothing to actually compare against."""
    if not result_set:
        return True
    return len(result_set) == 1 and len(result_set[0]) == 1 and result_set[0][0] in _ZERO_SCALARS


def _is_parse_error(error: str | None) -> bool:
    return bool(error) and ("parse" in error.lower() or "json" in error.lower())


def main() -> int:
    cases = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))

    passed = failed = invalid = errors = parse_errors = retried = 0
    by_difficulty: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # diff -> [passed, valid_total]
    latencies: list[float] = []

    for case in cases:
        cid = case["id"]
        question = case["question"]
        difficulty = case.get("difficulty", "?")

        try:
            expected = _result_set(execute.run(case["reference_sql"]).rows)
        except Exception as exc:  # noqa: BLE001
            invalid += 1
            print(f"[INVALID] {cid}: reference SQL failed: {exc}")
            continue

        if _is_vacuous(expected):
            invalid += 1
            print(f"[INVALID] {cid}: reference returned empty/zero — fix the case or the seed")
            continue

        start = time.perf_counter()
        result = ask(question)
        latencies.append(time.perf_counter() - start)

        by_difficulty[difficulty][1] += 1
        if result.attempts > 1:
            retried += 1

        if result.error:
            failed += 1
            if _is_parse_error(result.error):
                parse_errors += 1
            print(f"[FAIL] {cid} ({difficulty}): pipeline error: {result.error}")
            continue

        actual = _result_set(result.rows)
        if actual == expected:
            passed += 1
            by_difficulty[difficulty][0] += 1
            print(f"[PASS] {cid} ({difficulty})")
        else:
            failed += 1
            print(f"[FAIL] {cid} ({difficulty}): result mismatch")
            print(f"       generated: {result.sql}")
            print(f"       reference: {' '.join(case['reference_sql'].split())}")
            print(f"       expected[:3]: {expected[:3]}")
            print(f"       actual[:3]:   {actual[:3]}")

    _print_summary(
        cases=cases,
        passed=passed,
        failed=failed,
        invalid=invalid,
        parse_errors=parse_errors,
        retried=retried,
        by_difficulty=by_difficulty,
        latencies=latencies,
    )
    return 0 if (failed == 0 and invalid == 0 and passed > 0) else 1


def _print_summary(*, cases, passed, failed, invalid, parse_errors, retried, by_difficulty, latencies) -> None:
    valid = passed + failed
    print("\n" + "=" * 56)
    acc = f"{passed}/{valid}" if valid else "0/0"
    pct = f" ({100 * passed / valid:.0f}%)" if valid else ""
    print(f"Execution accuracy: {acc}{pct}   [invalid cases excluded: {invalid}]")

    if by_difficulty:
        print("\nBy difficulty:")
        for diff in ("easy", "medium", "hard", "?"):
            if diff in by_difficulty:
                p, total = by_difficulty[diff]
                pct = f" ({100 * p / total:.0f}%)" if total else ""
                print(f"  {diff:<8} {p}/{total}{pct}")

    if latencies:
        print(
            f"\nLatency: avg {statistics.mean(latencies):.1f}s · "
            f"median {statistics.median(latencies):.1f}s · max {max(latencies):.1f}s"
        )
    print(f"Self-correction: {retried}/{valid} cases needed a retry" if valid else "")
    print(f"Parse errors: {parse_errors}")


if __name__ == "__main__":
    raise SystemExit(main())
