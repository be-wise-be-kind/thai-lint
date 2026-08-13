"""
Purpose: Regression test for parallel linting losing cross-file rule state

Scope: Orchestrator.lint_files_parallel interaction with rules that override finalize()

Overview: Guards against a correctness bug found while researching persistent DRY caching:
    lint_files_parallel dispatches each file to a worker process via _lint_file_worker, and each
    worker constructs its own fresh Orchestrator/DRYRule with an isolated in-memory store. Workers
    always return [] for DRY (violations are deferred to finalize()). Back in the main process,
    finalize() runs on a DRYRule instance that never had check() called on it (all processing
    happened in throwaway worker processes), so its storage is never initialized and finalize()
    short-circuits to []. Net effect: thai-lint dry --parallel silently reports zero duplicate-code
    violations regardless of input. Verifies parallel execution finds the same cross-file duplicate
    a sequential run finds, on a real DRYRule instance (not a mock), forcing enough files that the
    parallel code path actually engages instead of falling back to sequential. Also covers
    StringlyTypedRule, the only other rule in the codebase with a meaningful finalize(), which has
    the exact same shape of bug.

Dependencies: pytest, pathlib.Path, src.orchestrator.core.Orchestrator

Exports: TestParallelCrossFileState, TestParallelCrossFileStateStringlyTyped test classes

Interfaces: Exercises the public Orchestrator.lint_files_parallel(paths, max_workers) entry point

Implementation: Builds 4-file fixtures (two files sharing cross-file state, two unique filler
    files, satisfying lint_files_parallel's `len(file_paths) >= max_workers * 2` parallel-path
    threshold) and asserts the cross-file violations are found, matching a sequential run
"""

from pathlib import Path

from src.orchestrator.core import Orchestrator

DUPLICATE_BLOCK = "\n".join(f"    value_{i} = compute({i})" for i in range(6))


def _write_fixture(tmp_path: Path) -> list[Path]:
    """Write a 4-file fixture: file_a/file_b share a duplicate block, c/d are unique filler."""
    file_a = tmp_path / "file_a.py"
    file_a.write_text(f"def handler_a():\n{DUPLICATE_BLOCK}\n")

    file_b = tmp_path / "file_b.py"
    file_b.write_text(f"def handler_b():\n{DUPLICATE_BLOCK}\n")

    file_c = tmp_path / "file_c.py"
    file_c.write_text("def unique_c():\n    return 'nothing shared here'\n")

    file_d = tmp_path / "file_d.py"
    file_d.write_text("def unique_d():\n    return 'nor here either'\n")

    return [file_a, file_b, file_c, file_d]


def _dry_config() -> dict:
    return {"dry": {"enabled": True, "min_duplicate_lines": 3, "storage_mode": "memory"}}


class TestParallelCrossFileState:
    """Rules with cross-file state (finalize()) must work correctly under --parallel."""

    def test_parallel_run_finds_same_duplicate_as_sequential(self, tmp_path: Path) -> None:
        """A cross-file duplicate found sequentially must also be found in parallel mode."""
        files = _write_fixture(tmp_path)
        config = _dry_config()

        sequential = Orchestrator(project_root=tmp_path, config=config)
        sequential_violations = sequential.lint_files(files)
        dry_sequential = [v for v in sequential_violations if v.rule_id.startswith("dry.")]

        parallel = Orchestrator(project_root=tmp_path, config=config)
        parallel_violations = parallel.lint_files_parallel(files, max_workers=2)
        dry_parallel = [v for v in parallel_violations if v.rule_id.startswith("dry.")]

        assert dry_sequential, "sanity check: sequential mode must find the duplicate"
        assert len(dry_parallel) == len(dry_sequential), (
            f"parallel mode found {len(dry_parallel)} dry violations, "
            f"sequential found {len(dry_sequential)}: {dry_parallel} vs {dry_sequential}"
        )


def _write_stringly_typed_fixture(tmp_path: Path) -> list[Path]:
    """Write a 4-file fixture: file_a/file_b share a membership-check pattern, c/d are filler."""
    file_a = tmp_path / "module_a.py"
    file_a.write_text(
        "def check_env_a(env: str) -> bool:\n"
        '    if env in ("staging", "production"):\n'
        "        return True\n"
        "    return False\n"
    )

    file_b = tmp_path / "module_b.py"
    file_b.write_text(
        "def check_env_b(env: str) -> None:\n"
        '    if env not in ("staging", "production"):\n'
        '        raise ValueError("Invalid env")\n'
    )

    file_c = tmp_path / "module_c.py"
    file_c.write_text("def unique_c() -> str:\n    return 'nothing shared here'\n")

    file_d = tmp_path / "module_d.py"
    file_d.write_text("def unique_d() -> str:\n    return 'nor here either'\n")

    return [file_a, file_b, file_c, file_d]


def _stringly_typed_config() -> dict:
    return {"stringly_typed": {"enabled": True, "min_occurrences": 2, "require_cross_file": True}}


class TestParallelCrossFileStateStringlyTyped:
    """StringlyTypedRule has the same finalize()-based cross-file-state shape as DRY."""

    def test_parallel_run_finds_same_pattern_as_sequential(self, tmp_path: Path) -> None:
        """A cross-file pattern found sequentially must also be found in parallel mode."""
        files = _write_stringly_typed_fixture(tmp_path)
        config = _stringly_typed_config()

        sequential = Orchestrator(project_root=tmp_path, config=config)
        sequential_violations = sequential.lint_files(files)
        st_sequential = [
            v for v in sequential_violations if v.rule_id.startswith("stringly-typed.")
        ]

        parallel = Orchestrator(project_root=tmp_path, config=config)
        parallel_violations = parallel.lint_files_parallel(files, max_workers=2)
        st_parallel = [v for v in parallel_violations if v.rule_id.startswith("stringly-typed.")]

        assert st_sequential, "sanity check: sequential mode must find the pattern"
        assert len(st_parallel) == len(st_sequential), (
            f"parallel mode found {len(st_parallel)} stringly-typed violations, "
            f"sequential found {len(st_sequential)}: {st_parallel} vs {st_sequential}"
        )
