"""Regression test: resolve_result_path / resolve_task_path must be deterministic.

Before the fix, list(dir.glob(...)) returned paths in filesystem iteration order
(non-deterministic across OS/FS).  After the fix, sorted() guarantees that when
multiple files match the same task_id glob the alphabetically smallest path wins.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_task_result as vtr  # noqa: E402


def test_resolve_result_path_deterministic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Multiple matching result files → always the sorted-first path is returned."""
    monkeypatch.setattr(vtr, "RESULTS_DIR", tmp_path)
    task_id = "T-9999-demo"
    (tmp_path / f"copy-{task_id}-result.json").touch()
    (tmp_path / f"alt-{task_id}-result.json").touch()
    expected = tmp_path / f"alt-{task_id}-result.json"  # "alt-" < "copy-" lexicographically
    assert vtr.resolve_result_path(task_id) == expected


def test_resolve_task_path_deterministic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Multiple matching task files → always the sorted-first path is returned."""
    monkeypatch.setattr(vtr, "TASKS_DIR", tmp_path)
    task_id = "T-9999-demo"
    (tmp_path / f"copy-{task_id}.yaml").touch()
    (tmp_path / f"alt-{task_id}.yaml").touch()
    expected = tmp_path / f"alt-{task_id}.yaml"  # "alt-" < "copy-" lexicographically
    assert vtr.resolve_task_path(task_id) == expected
