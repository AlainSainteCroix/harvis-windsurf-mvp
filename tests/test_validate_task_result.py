"""Tests for scripts/validate_task_result.py — comportement CLI."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate_task_result.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
EXAMPLE_RESULT = REPO_ROOT / ".harvis" / "results" / "T-0001-example-result.json"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


# ── Cas valides ───────────────────────────────────────────────────────────────

def test_nominal_task_result_passes() -> None:
    """Le couple exemple task/result passe en mode --task (exit 0)."""
    result = run("--task", "T-0001-example")
    assert result.returncode == 0
    assert "[OK]" in result.stdout


def test_schema_only_valid_result_passes() -> None:
    """--file seul sur result valide → exit 0 (schéma uniquement)."""
    result = run("--file", str(EXAMPLE_RESULT))
    assert result.returncode == 0
    assert "[OK]" in result.stdout


# ── Cas invalides ─────────────────────────────────────────────────────────────

def test_missing_checks_fails() -> None:
    """status=completed avec checks vide → exit 1."""
    result = run(
        "--task", "T-0001-example",
        "--file", str(FIXTURES / "invalid-result-missing-checks.json"),
    )
    assert result.returncode == 1
    assert "[FAIL]" in result.stdout
    assert "checks" in result.stdout


def test_out_of_scope_fails() -> None:
    """changed_files contient un fichier interdit → exit 1."""
    result = run(
        "--task", "T-0001-example",
        "--file", str(FIXTURES / "invalid-result-out-of-scope.json"),
    )
    assert result.returncode == 1
    assert "[FAIL]" in result.stdout
    assert "scope" in result.stdout


def test_file_outside_repo_does_not_crash(tmp_path: Path) -> None:
    """--file pointing outside repo root must not raise ValueError (regression)."""
    outside = tmp_path / "some-result.json"
    outside.write_text(
        (REPO_ROOT / ".harvis" / "results" / "T-0001-example-result.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    result = run("--file", str(outside))
    assert result.returncode == 0, result.stderr
    assert "[OK]" in result.stdout
    assert "ValueError" not in result.stderr


def test_invalid_task_packet_fails_fast() -> None:
    """Task packet sans scope → fail-fast avant cross-checks (exit 1)."""
    result = run(
        "--task-file", str(FIXTURES / "invalid-task-missing-scope.yaml"),
        "--file", str(EXAMPLE_RESULT),
    )
    assert result.returncode == 1
    assert "[FAIL]" in result.stdout
    assert "Task packet is invalid" in result.stdout
