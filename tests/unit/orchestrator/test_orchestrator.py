"""
Purpose: Test suite for main orchestrator engine

Scope: Validation of file linting, directory traversal, and ignore pattern integration

Overview: Validates the main orchestration engine that coordinates rule
    execution across files and directories, ensuring proper integration with
    the ignore system, rule registry, and configuration loader. Tests verify
    single file linting returns violations correctly, directory linting
    traverses recursively and non-recursively, ignore patterns from
    .thailintignore are respected, and the orchestrator integrates properly
    with all framework components (registry, config, ignore parser). Ensures
    the orchestrator provides the main entry point for linting operations
    while delegating to appropriate subsystems.

Dependencies: pytest for testing framework, pathlib for file operations,
    tmp_path fixture

Exports: TestOrchestrator test class

Interfaces: Tests Orchestrator.lint_file(), lint_directory() methods,
    validates ignore pattern integration and rule execution coordination

Implementation: 6 tests using pytest tmp_path for isolated file/directory
    creation, ignore file creation for integration testing, recursive and
    non-recursive directory testing
"""


class TestOrchestrator:
    """Test main Orchestrator class."""

    def test_respects_ignore_patterns(self, tmp_path):
        """Orchestrator respects .thailintignore patterns."""
        (tmp_path / ".thailintignore").write_text("*.pyc\n__pycache__/\n")
        (tmp_path / "test.pyc").write_text("compiled")
        (tmp_path / "test.py").write_text("# python")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_directory(tmp_path)

        # Should not lint .pyc file
        assert all("test.pyc" not in v.file_path for v in violations)

    def test_lint_multiple_files_ignores_ignored_files(self, tmp_path):
        """Should respect .thailintignore when linting multiple files."""
        # Create .thailintignore
        (tmp_path / ".thailintignore").write_text("test2.py\n")

        # Create test files
        file1 = tmp_path / "test1.py"
        file1.write_text("# test file 1\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("# test file 2 - should be ignored\n")

        from src.orchestrator import Orchestrator

        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_files([file1, file2])

        # Should not include violations from test2.py
        assert isinstance(violations, list)
        # Violations should not reference ignored file
        for v in violations:
            assert "test2.py" not in str(v.file_path)

    def test_collect_files_fast_prunes_configured_ignore_directories(self, tmp_path, monkeypatch):
        """Directory walk must prune configured ignore: dirs, not just filter them after.

        Regression test for issue #240: previously _collect_files_fast only pruned a
        hardcoded directory list during os.walk() and relied on a later per-file
        is_ignored() check to filter out configured ignore: patterns - meaning a large
        ignored directory was still fully enumerated on every run. This asserts the
        walk itself never descends into the ignored directory, by counting os.walk()
        calls against it directly.
        """
        (tmp_path / ".thailintignore").write_text("**/ignored_cache/**\n")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# kept\n")
        ignored_dir = tmp_path / "ignored_cache" / "sub"
        ignored_dir.mkdir(parents=True)
        (ignored_dir / "file.bin").write_text("x")

        import os

        from src.linter_config.ignore import IgnoreDirectiveParser
        from src.orchestrator.core import _collect_files_fast

        visited_roots = []
        real_walk = os.walk

        def spying_walk(top, *args, **kwargs):
            for root, dirs, files in real_walk(top, *args, **kwargs):
                visited_roots.append(root)
                yield root, dirs, files

        monkeypatch.setattr(os, "walk", spying_walk)

        ignore_parser = IgnoreDirectiveParser(tmp_path)
        collected = _collect_files_fast(tmp_path, ignore_parser)

        assert all("ignored_cache" not in str(p) for p in collected)
        assert not any("ignored_cache" in root for root in visited_roots)
