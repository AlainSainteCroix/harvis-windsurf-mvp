#!/usr/bin/env python3
"""
new_task.py — Scaffold a new Harvis task packet YAML.

Generates a conformant task packet in .harvis/tasks/ from minimal CLI arguments.
The generated file is validated against task-packet.schema.json before writing.

Usage:
    python scripts/new_task.py \\
        --task-id T-0003-my-task \\
        --title "My task title" \\
        --objective "What the task should accomplish."

    # Preview without writing:
    python scripts/new_task.py --task-id T-0003-my-task --title "X" --objective "Y" --dry-run

    # Custom scope:
    python scripts/new_task.py --task-id T-0003-my-task --title "X" --objective "Y" \\
        --allowed-path "scripts/**" --allowed-path "README.md"

Exit codes:
    0  task packet written (or --dry-run printed)
    1  validation or usage error
    2  system error (missing schema, import error)

Dependencies: jsonschema, pyyaml
"""

from __future__ import annotations

import argparse
import json
import re
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
TASKS_DIR = REPO_ROOT / ".harvis" / "tasks"
TASK_SCHEMA_PATH = REPO_ROOT / ".harvis" / "contracts" / "task-packet.schema.json"

TASK_ID_PATTERN = re.compile(r"^T-\d{4}-[a-z0-9-]+$")

DEFAULT_FORBIDDEN_PATHS: list[str] = [
    ".harvis/contracts/",
    ".windsurf/",
    "AGENTS.md",
    "pyproject.toml",
    "tests/",
]
DEFAULT_REQUIRED_OUTPUTS: list[str] = ["changed_files", "checks", "next_step"]


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    branch: str = args.branch_name or f"harvis/{args.task_id}"
    allowed: list[str] = args.allowed_path or ["scripts/**"]
    forbidden: list[str] = args.forbidden_path or DEFAULT_FORBIDDEN_PATHS

    packet: dict[str, Any] = {
        "task_id": args.task_id,
        "title": args.title,
        "objective": args.objective,
        "repo_root": str(REPO_ROOT),
        "branch_name": branch,
        "executor": args.executor,
        "model_tier": "high_capability",
        "scope": {
            "allowed_paths": allowed,
            "forbidden_paths": forbidden,
        },
        "acceptance_criteria": [
            "Le livrable est produit, fonctionnel et conforme à l'objectif déclaré.",
        ],
        "required_outputs": DEFAULT_REQUIRED_OUTPUTS,
        "execution_policy": {
            "max_attempts": 2,
            "escalate_if": [
                "ambiguïté sur le scope ou les critères d'acceptation",
            ],
        },
    }
    return packet


def validate_packet(packet: dict[str, Any]) -> list[str]:
    if not TASK_SCHEMA_PATH.exists():
        return [f"Schema not found: {TASK_SCHEMA_PATH}"]
    schema: dict[str, Any] = json.loads(TASK_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        validate(instance=packet, schema=schema)
    except ValidationError as e:
        return [f"{e.message} (path: {list(e.absolute_path)})"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new Harvis task packet YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s --task-id T-0003-my-task --title 'Do X' --objective 'Accomplish X.'\n"
            "  %(prog)s --task-id T-0003-my-task --title 'Do X' --objective 'Y' --dry-run\n"
            "  %(prog)s --task-id T-0003-my-task --title 'Do X' --objective 'Y' \\\n"
            "      --allowed-path 'scripts/**' --allowed-path 'README.md'\n\n"
            "note: --task-id must match pattern T-NNNN-slug (e.g. T-0003-my-task)"
        ),
    )
    parser.add_argument(
        "--task-id", required=True, metavar="ID",
        help="Task ID — must match T-NNNN-slug (e.g. T-0003-my-task)",
    )
    parser.add_argument(
        "--title", required=True,
        help="Short title of the task",
    )
    parser.add_argument(
        "--objective", required=True,
        help="Task objective (one or more sentences describing what must be done)",
    )
    parser.add_argument(
        "--branch-name", metavar="BRANCH",
        help="Git branch (default: harvis/<task_id>)",
    )
    parser.add_argument(
        "--allowed-path", metavar="PATTERN", action="append",
        help="Allowed path/glob pattern (repeatable; default: scripts/**)",
    )
    parser.add_argument(
        "--forbidden-path", metavar="PATTERN", action="append",
        help="Forbidden path/glob pattern (repeatable; overrides defaults)",
    )
    parser.add_argument(
        "--executor", default="cascade",
        help="Executor name (default: cascade)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing task file",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print generated YAML without writing",
    )
    args = parser.parse_args()

    if not TASK_ID_PATTERN.match(args.task_id):
        print(
            f"ERROR: --task-id '{args.task_id}' is invalid.\n"
            "       Expected format: T-NNNN-slug (e.g. T-0003-my-task)",
            file=sys.stderr,
        )
        return 1

    packet = build_packet(args)

    errors = validate_packet(packet)
    if errors:
        print("[FAIL] Generated packet is invalid:", file=sys.stderr)
        for err in errors:
            print(f"  x {err}", file=sys.stderr)
        return 1

    yaml_out = yaml.dump(
        packet,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )

    if args.dry_run:
        print(f"# [dry-run] Would write: .harvis/tasks/{args.task_id}.yaml\n")
        print(yaml_out)
        return 0

    output_path = TASKS_DIR / f"{args.task_id}.yaml"
    if output_path.exists() and not args.force:
        print(
            f"ERROR: {output_path.relative_to(REPO_ROOT)} already exists.\n"
            "       Use --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml_out, encoding="utf-8")
    print(f"[OK] .harvis/tasks/{args.task_id}.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
