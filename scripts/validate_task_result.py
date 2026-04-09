#!/usr/bin/env python3
"""
validate_task_result.py — Validate a Harvis result packet against its JSON Schema.

Usage:
    python scripts/validate_task_result.py --task T-0001-example
    python scripts/validate_task_result.py --file .harvis/results/my-result.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import ValidationError, validate
except ImportError:
    print(
        "ERROR: 'jsonschema' package required. Install with: pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / ".harvis" / "contracts" / "result-packet.schema.json"
RESULTS_DIR = REPO_ROOT / ".harvis" / "results"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_schema(result: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        validate(instance=result, schema=schema)
    except ValidationError as e:
        errors.append(f"Schema violation: {e.message} (path: {list(e.absolute_path)})")
    return errors


def validate_logic(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    task_id: str = result.get("task_id", "")
    if not task_id.startswith("T-"):
        errors.append(f"task_id '{task_id}' does not match expected pattern T-NNNN-*")

    status: str = result.get("status", "")
    if status == "failure" and "error" not in result:
        errors.append("status is 'failure' but 'error' field is missing")

    if status == "success" and result.get("error"):
        errors.append("status is 'success' but 'error' field is present — inconsistent")

    trace: list[dict[str, Any]] = result.get("trace", [])
    for i, entry in enumerate(trace):
        if not isinstance(entry.get("step"), int):
            errors.append(f"trace[{i}].step is not an integer")
        if not entry.get("message"):
            errors.append(f"trace[{i}].message is empty")

    return errors


def resolve_result_path(task_id: str | None, file_path: str | None) -> Path:
    if file_path:
        return Path(file_path).resolve()
    if task_id:
        candidate = RESULTS_DIR / f"{task_id}-result.json"
        if not candidate.exists():
            matches = list(RESULTS_DIR.glob(f"*{task_id}*result*.json"))
            if matches:
                return matches[0]
        return candidate
    raise ValueError("Either --task or --file must be provided")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Harvis result packet")
    parser.add_argument("--task", metavar="TASK_ID", help="Task ID (e.g. T-0001-example)")
    parser.add_argument("--file", metavar="PATH", help="Direct path to result JSON file")
    args = parser.parse_args()

    if not args.task and not args.file:
        parser.print_help()
        return 1

    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema not found at {SCHEMA_PATH}", file=sys.stderr)
        return 2

    try:
        result_path = resolve_result_path(args.task, args.file)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not result_path.exists():
        print(f"ERROR: Result file not found: {result_path}", file=sys.stderr)
        return 2

    print(f"Validating: {result_path}")
    schema = load_json(SCHEMA_PATH)
    result = load_json(result_path)

    schema_errors = validate_schema(result, schema)
    logic_errors = validate_logic(result)
    all_errors = schema_errors + logic_errors

    if all_errors:
        print(f"\n[FAIL] {len(all_errors)} error(s) found:")
        for err in all_errors:
            print(f"  x {err}")
        return 1

    print(
        f"[OK] Result packet is valid"
        f" (task_id={result.get('task_id')}, status={result.get('status')})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
