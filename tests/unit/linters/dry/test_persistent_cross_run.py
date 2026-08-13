"""
Purpose: Acceptance tests for the persistent, cross-run DRY duplicate index

Scope: End-to-end behavior through Orchestrator/DRYRule with storage_mode: persistent

Overview: Exercises the BDD scenarios from the project plan
    (.roadmap/planning/dry-persistent-cache/PLAN.md) at the full-stack level: a fresh
    Orchestrator per "run" (simulating separate CLI invocations) sharing the same project_root,
    and therefore the same on-disk .thailint-cache/dry.db. Covers cross-run matching against a
    file not passed to the current run, the #35 regression (fixing a duplicate makes the
    violation disappear on the next run, not just the current one), transparent rescanning of an
    externally-edited matched file, and purging of a deleted matched file.

Dependencies: pytest, pathlib.Path, src.orchestrator.core.Orchestrator

Exports: Test classes for each BDD scenario

Interfaces: Exercises Orchestrator(project_root, config).lint_files(paths)

Implementation: Each "run" constructs a brand-new Orchestrator against the same tmp_path project
    root, so no in-memory state survives between runs - only what's in the on-disk persistent
    store does
"""

from pathlib import Path

from src.orchestrator.core import Orchestrator

_DUPLICATE_BODY = "\n".join(f"    value_{i} = compute({i})" for i in range(6))


def _persistent_config() -> dict:
    return {
        "dry": {
            "enabled": True,
            "min_duplicate_lines": 3,
            "storage_mode": "persistent",
            "detect_duplicate_constants": False,
        }
    }


def _dry_violations(violations: list) -> list:
    return [v for v in violations if v.rule_id.startswith("dry.")]


def _run(tmp_path: Path, files: list[Path]) -> list:
    """Simulate one CLI invocation: a fresh Orchestrator, same project_root/cache file."""
    orchestrator = Orchestrator(project_root=tmp_path, config=_persistent_config())
    return _dry_violations(orchestrator.lint_files(files))


class TestCachePathResolvesToTrueProjectRoot:
    """The persistent cache must land at project_root, not a scanned file's own directory.

    Regression test: DRYRule._get_project_root previously read
    context.metadata["project_root"], but the orchestrator sets "_project_root" (see
    Orchestrator.lint_file) - the lookup always missed, silently falling back to
    Path(file_path).parent. Invisible when files sit directly in project_root (as in every
    other test in this module), but wrong as soon as a file is nested in a subdirectory:
    the cache would land inside that subdirectory instead of at the true project root.
    """

    def test_cache_file_lands_at_project_root_not_nested_file_directory(
        self, tmp_path: Path
    ) -> None:
        """A file nested in a subdirectory must not relocate the persistent cache there."""
        nested_dir = tmp_path / "sub" / "deep"
        nested_dir.mkdir(parents=True)
        nested_file = nested_dir / "file_a.py"
        nested_file.write_text(f"def handler():\n{_DUPLICATE_BODY}\n")

        _run(tmp_path, [nested_file])

        assert (tmp_path / ".thailint-cache" / "dry.db").exists()
        assert not (nested_dir / ".thailint-cache").exists()


class TestCrossRunMatchAgainstUnscannedFile:
    """A changed file duplicates an unchanged, previously-indexed file not passed this run."""

    def test_second_run_finds_duplicate_against_file_not_in_this_runs_list(
        self, tmp_path: Path
    ) -> None:
        """A run passing only file_a must still find its match against indexed file_b."""
        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        file_a.write_text(content)
        file_b.write_text(content)

        first_run = _run(tmp_path, [file_a, file_b])
        assert len(first_run) == 4, "sanity check: first run must index both files"

        second_run = _run(tmp_path, [file_a])
        # Both sides of the match are reported, exactly as a full-tree scan would -
        # file_b wasn't in this invocation's file list, but it's still a legitimate,
        # unchanged part of the persisted duplicate group.
        assert len(second_run) == 4
        assert all("file_b.py" in v.message or "file_a.py" in v.message for v in second_run)


class TestFixThenRescanRegression:
    """The #35 regression: fixing a duplicate makes the violation disappear on the next run."""

    def test_violation_disappears_after_fix_on_a_later_run(self, tmp_path: Path) -> None:
        """Fixing a duplicate and rescanning must not leave a stale violation behind."""
        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        file_a.write_text(content)
        file_b.write_text(content)

        first_run = _run(tmp_path, [file_a, file_b])
        assert len(first_run) == 4, "sanity check: first run must index both files"

        # file_a is fixed to remove the duplicate, then rescanned by itself.
        file_a.write_text("def handler():\n    return 'no duplicate anymore'\n")
        second_run = _run(tmp_path, [file_a])
        assert second_run == []

        # A later run touching file_a again must not resurrect the old block either.
        third_run = _run(tmp_path, [file_a])
        assert third_run == []


class TestStaleMatchedFileIsRescanned:
    """A matched file's on-disk content changed since indexing; it's rescanned, not trusted."""

    def test_matched_file_edited_externally_is_rescanned_before_matching(
        self, tmp_path: Path
    ) -> None:
        """A matched file's stale indexed content must not produce a phantom violation."""
        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        file_a.write_text(content)
        file_b.write_text(content)

        first_run = _run(tmp_path, [file_a, file_b])
        assert len(first_run) == 4, "sanity check: first run must index both files"

        # file_b is edited outside of any lint run (no invocation ever rescans it
        # directly) to remove the duplicate.
        file_b.write_text("def handler():\n    return 'no duplicate anymore'\n")

        second_run = _run(tmp_path, [file_a])
        assert second_run == [], (
            "file_b's stale indexed content must not produce a phantom match "
            f"against file_a: {second_run}"
        )


class TestReportScopedToInvocation:
    """A duplicate group neither side of which is in this run's file list must not be
    reported - regression test for the issue #238 report: persistent mode's report
    included the entire indexed violation backlog on every invocation, not just matches
    touching the current invocation, defeating the point of a diff-scoped run.
    """

    def test_unrelated_duplicate_group_is_not_reported_for_a_diff_scoped_run(
        self, tmp_path: Path
    ) -> None:
        """A pre-existing duplicate between two files outside this run must be silent."""
        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content_ab = f"def handler():\n{_DUPLICATE_BODY}\n"
        file_a.write_text(content_ab)
        file_b.write_text(content_ab)

        unrelated_body = "\n".join(f"    other_{i} = fetch({i})" for i in range(6))
        file_c = tmp_path / "file_c.py"
        file_d = tmp_path / "file_d.py"
        content_cd = f"def handler():\n{unrelated_body}\n"
        file_c.write_text(content_cd)
        file_d.write_text(content_cd)

        first_run = _run(tmp_path, [file_a, file_b, file_c, file_d])
        assert len(first_run) == 8, "sanity check: first run must index both duplicate groups"

        # Diff-scoped run touches only file_a. The file_a/file_b group must still be
        # reported (file_a is in scope), but the entirely-untouched file_c/file_d group
        # must not be - neither side of it was part of this invocation.
        second_run = _run(tmp_path, [file_a])

        assert all("file_c.py" not in v.message for v in second_run)
        assert all("file_d.py" not in v.message for v in second_run)
        assert all(v.file_path not in (str(file_c), str(file_d)) for v in second_run)
        assert len(second_run) == 4
        assert all("file_b.py" in v.message or "file_a.py" in v.message for v in second_run)


class TestDeletedMatchedFileIsPurged:
    """A matched file deleted from disk since indexing must not produce phantom violations."""

    def test_deleted_matched_file_produces_no_violation(self, tmp_path: Path) -> None:
        """A matched file deleted from disk must be purged, not produce a phantom violation."""
        file_a = tmp_path / "file_a.py"
        file_b = tmp_path / "file_b.py"
        content = f"def handler():\n{_DUPLICATE_BODY}\n"
        file_a.write_text(content)
        file_b.write_text(content)

        first_run = _run(tmp_path, [file_a, file_b])
        assert len(first_run) == 4, "sanity check: first run must index both files"

        file_b.unlink()

        second_run = _run(tmp_path, [file_a])
        assert second_run == []
