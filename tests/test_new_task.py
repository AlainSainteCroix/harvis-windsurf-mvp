"""Regression tests for scripts/new_task.py — CLI behaviour."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "new_task.py"
TASKS_DIR = REPO_ROOT / ".harvis" / "tasks"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


# ── Invalid task IDs ───────────────────────────────────────────────────────────

def test_invalid_task_id_exits_1() -> None:
    """Malformed --task-id → exit 1, error on stderr."""
    result = run("--task-id", "BADID", "--title", "T", "--objective", "O")
    assert result.returncode == 1
    assert "invalid" in result.stderr.lower()


def test_invalid_task_id_no_uppercase_slug_exits_1() -> None:
    """Slug with uppercase letters → exit 1 (pattern ^T-\\d{4}-[a-z0-9-]+$)."""
    result = run("--task-id", "T-0099-BadSlug", "--title", "T", "--objective", "O")
    assert result.returncode == 1
    assert "invalid" in result.stderr.lower()


def test_invalid_task_id_does_not_create_file() -> None:
    """exit 1 on bad ID must not leave any artefact in .harvis/tasks/."""
    bad_id = "NOT-A-VALID-ID"
    target = TASKS_DIR / f"{bad_id}.yaml"
    run("--task-id", bad_id, "--title", "T", "--objective", "O")
    assert not target.exists(), f"Unexpected file created: {target}"


# ── Dry-run mode ───────────────────────────────────────────────────────────────

def test_dry_run_exits_0() -> None:
    """--dry-run with valid args → exit 0."""
    result = run(
        "--task-id", "T-9999-dry-run-test",
        "--title", "Dry run title",
        "--objective", "Verify dry-run behaviour.",
        "--dry-run",
    )
    assert result.returncode == 0


def test_dry_run_prints_target_path() -> None:
    """--dry-run stdout must contain the would-be target path."""
    result = run(
        "--task-id", "T-9999-dry-run-test",
        "--title", "Dry run title",
        "--objective", "Verify dry-run behaviour.",
        "--dry-run",
    )
    assert "# [dry-run] Would write: .harvis/tasks/T-9999-dry-run-test.yaml" in result.stdout


def test_dry_run_does_not_write_file() -> None:
    """--dry-run must not create any file in .harvis/tasks/."""
    task_id = "T-9999-dry-run-test"
    target = TASKS_DIR / f"{task_id}.yaml"
    target.unlink(missing_ok=True)  # ensure clean state
    run(
        "--task-id", task_id,
        "--title", "Dry run title",
        "--objective", "Verify dry-run behaviour.",
        "--dry-run",
    )
    assert not target.exists(), f"dry-run must not write: {target}"
