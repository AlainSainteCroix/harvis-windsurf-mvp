#!/usr/bin/env python3
"""
validate_task_result.py — Validate a Harvis result packet (schema + cross-task checks).

Usage:
    # Schema validation only:
    python scripts/validate_task_result.py --file .harvis/results/T-0001-example-result.json

    # Schema + full cross-task validation:
    python scripts/validate_task_result.py --task T-0001-example

    # Direct task file path (utile pour les tests):
    python scripts/validate_task_result.py --task-file path/to/task.yaml --file path/to/result.json

Exit codes:
    0  — valid
    1  — validation errors
    2  — system error (missing file, missing schema, import error)

Dependencies: jsonschema, pyyaml
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: 'pyyaml' required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import ValidationError, validate
except ImportError:
    print("ERROR: 'jsonschema' required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULT_SCHEMA_PATH = REPO_ROOT / ".harvis" / "contracts" / "result-packet.schema.json"
TASK_SCHEMA_PATH = REPO_ROOT / ".harvis" / "contracts" / "task-packet.schema.json"
RESULTS_DIR = REPO_ROOT / ".harvis" / "results"
TASKS_DIR = REPO_ROOT / ".harvis" / "tasks"


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_result_path(task_id: str) -> Path:
    candidate = RESULTS_DIR / f"{task_id}-result.json"
    if not candidate.exists():
        matches = list(RESULTS_DIR.glob(f"*{task_id}*result*.json"))
        if matches:
            return matches[0]
    return candidate


def resolve_task_path(task_id: str) -> Path:
    candidate = TASKS_DIR / f"{task_id}.yaml"
    if not candidate.exists():
        matches = list(TASKS_DIR.glob(f"*{task_id}*.yaml"))
        if matches:
            return matches[0]
    return candidate


# ── Check 0 : Task packet schema ─────────────────────────────────────────────

def check_task_packet_schema(task: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        validate(instance=task, schema=schema)
    except ValidationError as e:
        errors.append(f"[task_schema] {e.message} (path: {list(e.absolute_path)})")
    return errors


# ── Check 1 : Result packet JSON Schema ───────────────────────────────────────

def check_schema(result: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        validate(instance=result, schema=schema)
    except ValidationError as e:
        errors.append(f"[result_schema] {e.message} (path: {list(e.absolute_path)})")
    return errors


# ── Check 2 : task_id coherence ───────────────────────────────────────────────

def check_task_id(task: dict[str, Any], result: dict[str, Any]) -> list[str]:
    t_id: str = task.get("task_id", "")
    r_id: str = result.get("task_id", "")
    if t_id != r_id:
        return [f"[task_id] mismatch — task='{t_id}' vs result='{r_id}'"]
    return []


# ── Check 3 : scope (allowed_paths / forbidden_paths) ─────────────────────────

def _path_matches(filepath: str, pattern: str) -> bool:
    """True if filepath matches pattern (exact, glob, or directory prefix)."""
    if fnmatch.fnmatch(filepath, pattern):
        return True
    norm = pattern.rstrip("/")
    if filepath == norm or filepath.startswith(norm + "/"):
        return True
    return False


def check_scope(task: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scope: dict[str, Any] = task.get("scope", {})
    allowed: list[str] = scope.get("allowed_paths", [])
    forbidden: list[str] = scope.get("forbidden_paths", [])
    changed: list[str] = result.get("changed_files", [])

    if not allowed:
        return []

    for filepath in changed:
        if not any(_path_matches(filepath, p) for p in allowed):
            errors.append(
                f"[scope] '{filepath}' is not in allowed_paths {allowed}"
            )
        for fp in forbidden:
            if _path_matches(filepath, fp):
                errors.append(
                    f"[scope] '{filepath}' matches forbidden_paths pattern '{fp}'"
                )
    return errors


# ── Check 4 : required_outputs presence ──────────────────────────────────────
# required_outputs = the field must be PRESENT (non-null) in the result packet.
# Whether the field must be non-empty is status-dependent and handled by
# check_checks_present(), check_status_coherence(), check_changed_files_coherence().

def check_required_outputs(task: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required: list[str] = task.get("required_outputs", [])
    for field in required:
        if result.get(field) is None:
            errors.append(f"[required_outputs] '{field}' is missing from result packet")
    return errors


# ── Check 5 : checks mandatory for completed statuses ────────────────────────

def check_checks_present(result: dict[str, Any]) -> list[str]:
    status: str = result.get("status", "")
    checks: list[Any] = result.get("checks", [])
    if status in ("completed", "completed_with_risks") and not checks:
        return [
            f"[checks] status='{status}' requires at least one check — 'checks' is empty"
        ]
    return []


# ── Check 6a : status / blockers / risks coherence ───────────────────────────

def check_status_coherence(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status: str = result.get("status", "")
    blockers: list[Any] = result.get("blockers", [])
    risks: list[Any] = result.get("risks", [])

    rules: dict[str, tuple[bool, str]] = {
        "blocked":              (bool(blockers),          "at least one blocker required"),
        "failed":               (bool(blockers or risks), "at least one risk or blocker required"),
        "completed":            (not blockers,            "no blockers allowed (use 'blocked' or 'completed_with_risks')"),
        "completed_with_risks": (bool(risks),             "at least one risk required"),
        "out_of_scope":         (bool(blockers or risks), "at least one blocker or risk required as explanation"),
    }

    if status in rules:
        ok, msg = rules[status]
        if not ok:
            errors.append(f"[status_coherence] status='{status}': {msg}")
    return errors


# ── Check 6b : changed_files / status coherence ──────────────────────────────

def check_changed_files_coherence(result: dict[str, Any]) -> list[str]:
    status: str = result.get("status", "")
    changed: list[Any] = result.get("changed_files", [])
    if status in ("completed", "completed_with_risks") and not changed:
        return [
            f"[changed_files] status='{status}' but 'changed_files' is empty"
            " — a completing execution must declare what it changed"
        ]
    return []


# ── Runner ────────────────────────────────────────────────────────────────────

def run_all_checks(
    result: dict[str, Any],
    schema: dict[str, Any],
    task: dict[str, Any] | None,
) -> list[str]:
    errors = check_schema(result, schema)
    if task is not None:
        errors += check_task_id(task, result)
        errors += check_scope(task, result)
        errors += check_required_outputs(task, result)
    errors += check_checks_present(result)
    errors += check_status_coherence(result)
    errors += check_changed_files_coherence(result)
    return errors


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Harvis result packet (schema + cross-task checks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s --task T-0001-example          # schema + cross-task\n"
            "  %(prog)s --file path/to/result.json     # schema only\n"
            "  %(prog)s --task T-0001-example --file path/to/result.json  # both"
        ),
    )
    parser.add_argument(
        "--task", metavar="TASK_ID",
        help="Task ID (e.g. T-0001-example) — loads task packet, enables cross-checks",
    )
    parser.add_argument(
        "--file", metavar="PATH",
        help="Direct path to result JSON (uses task result file if --task given without --file)",
    )
    parser.add_argument(
        "--task-file", metavar="PATH",
        help="Direct path to task YAML file (overrides --task lookup; requires --file)",
    )
    args = parser.parse_args()

    if args.task_file and not args.file:
        print("ERROR: --task-file requires --file", file=sys.stderr)
        return 1

    if not args.task and not args.file and not args.task_file:
        parser.print_help()
        return 1

    if not RESULT_SCHEMA_PATH.exists():
        print(f"ERROR: Result schema not found: {RESULT_SCHEMA_PATH}", file=sys.stderr)
        return 2

    result_path: Path
    if args.file:
        result_path = Path(args.file).resolve()
    elif args.task:
        result_path = resolve_result_path(args.task)
    else:
        print("ERROR: provide --task or --file", file=sys.stderr)
        return 1

    if not result_path.exists():
        print(f"ERROR: Result file not found: {result_path}", file=sys.stderr)
        return 2

    result: dict[str, Any] = load_json(result_path)
    schema: dict[str, Any] = load_json(RESULT_SCHEMA_PATH)

    task: dict[str, Any] | None = None
    task_display_path: Path | None = None

    if args.task_file:
        p = Path(args.task_file).resolve()
        if not p.exists():
            print(f"ERROR: Task file not found: {p}", file=sys.stderr)
            return 2
        task = load_yaml(p)
        task_display_path = p
    elif args.task:
        p = resolve_task_path(args.task)
        if p.exists():
            task = load_yaml(p)
            task_display_path = p
        else:
            print(
                f"WARNING: Task file not found at {p} — skipping cross-checks",
                file=sys.stderr,
            )

    if task:
        if not TASK_SCHEMA_PATH.exists():
            print(f"ERROR: Task schema not found: {TASK_SCHEMA_PATH}", file=sys.stderr)
            return 2
        task_schema: dict[str, Any] = load_json(TASK_SCHEMA_PATH)
        task_errors = check_task_packet_schema(task, task_schema)
        if task_errors:
            if task_display_path:
                try:
                    print(f"Task packet : {task_display_path.relative_to(REPO_ROOT)}")
                except ValueError:
                    print(f"Task packet : {task_display_path}")
            print(f"\n[FAIL] Task packet is invalid ({len(task_errors)} error(s)):")
            for err in task_errors:
                print(f"  x {err}")
            return 1

    mode = "task-schema + result-schema + cross-task" if task else "result-schema only"
    print(f"Validating [{mode}]: {result_path.relative_to(REPO_ROOT)}")
    if task and task_display_path:
        try:
            print(f"Task packet : {task_display_path.relative_to(REPO_ROOT)}")
        except ValueError:
            print(f"Task packet : {task_display_path}")

    errors = run_all_checks(result, schema, task)

    if errors:
        print(f"\n[FAIL] {len(errors)} error(s):")
        for err in errors:
            print(f"  x {err}")
        return 1

    print(
        f"[OK] valid — task_id={result.get('task_id')}, status={result.get('status')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
