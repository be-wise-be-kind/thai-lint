"""
Purpose: Regression test for DRY ignore patterns skipping full file analysis (issue #232)

Scope: DRYRule._process_file gating of FileAnalyzer.analyze for ignored paths

Overview: Guards against the bug reported in issue #232, where `dry.ignore` patterns in
    .thailint.yaml only filtered which violations were reported after a file was fully
    analyzed, rather than skipping analysis of the file altogether. A file matching
    `ignore_patterns` still paid the full block-extraction and filtering cost of a normal
    scan. Verifies that DRYRule consults `config.ignore_patterns` before calling
    FileAnalyzer.analyze, so an ignored file's content is never passed to analysis, while a
    non-ignored file in the same run still is. Also guards against ignore-pattern matching
    using Python substring containment instead of gitignore-style glob matching, which
    wrongly ignores a directory whose name merely contains the pattern as a substring
    (e.g. pattern "vendor/" matching "not_vendor/"). File-pattern tests use a "**/" prefix
    per docs/configuration.md's documented convention, since file paths reaching the
    linter are absolute and a bare filename pattern only matches a single-segment path.

Dependencies: pytest, unittest.mock, pathlib.Path, src.Linter, src.linters.dry.file_analyzer

Exports: test_ignored_file_is_not_analyzed, test_non_ignored_file_is_still_analyzed,
    test_similarly_named_directory_is_not_incorrectly_ignored

Interfaces: Exercises the public Linter.lint(path, rules) entry point

Implementation: Wraps FileAnalyzer.analyze with a recording wrapper and asserts which file
    paths it was invoked with, rather than asserting on reported violations (which already
    passed before the fix, since filtering happened after analysis).
"""

from unittest.mock import patch

from src import Linter
from src.linters.dry.file_analyzer import FileAnalyzer


def test_ignored_file_is_not_analyzed(tmp_path):
    """A file matching dry.ignore must never reach FileAnalyzer.analyze."""
    ignored = tmp_path / "vendor_ignored.py"
    ignored.write_text("x = 1\ny = 2\nz = 3\n" * 5)

    kept = tmp_path / "kept.py"
    kept.write_text("a = 1\nb = 2\nc = 3\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text(
        "dry:\n"
        "  enabled: true\n"
        "  min_duplicate_lines: 3\n"
        "  cache_enabled: false\n"
        "  ignore:\n"
        "    - '**/vendor_ignored.py'\n"
    )

    analyzed_paths: list[str] = []
    original_analyze = FileAnalyzer.analyze

    def recording(self, file_path, content, language, cfg):
        analyzed_paths.append(str(file_path))
        return original_analyze(self, file_path, content, language, cfg)

    with patch.object(FileAnalyzer, "analyze", recording):
        linter = Linter(config_file=config, project_root=tmp_path)
        linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert not any("vendor_ignored.py" in p for p in analyzed_paths), (
        f"ignored file was analyzed anyway: {analyzed_paths}"
    )


def test_non_ignored_file_is_still_analyzed(tmp_path):
    """A file not matching dry.ignore must still reach FileAnalyzer.analyze."""
    ignored = tmp_path / "vendor_ignored.py"
    ignored.write_text("x = 1\ny = 2\nz = 3\n" * 5)

    kept = tmp_path / "kept.py"
    kept.write_text("a = 1\nb = 2\nc = 3\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text(
        "dry:\n"
        "  enabled: true\n"
        "  min_duplicate_lines: 3\n"
        "  cache_enabled: false\n"
        "  ignore:\n"
        "    - '**/vendor_ignored.py'\n"
    )

    analyzed_paths: list[str] = []
    original_analyze = FileAnalyzer.analyze

    def recording(self, file_path, content, language, cfg):
        analyzed_paths.append(str(file_path))
        return original_analyze(self, file_path, content, language, cfg)

    with patch.object(FileAnalyzer, "analyze", recording):
        linter = Linter(config_file=config, project_root=tmp_path)
        linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert any("kept.py" in p for p in analyzed_paths), (
        f"non-ignored file was never analyzed: {analyzed_paths}"
    )


def test_similarly_named_directory_is_not_incorrectly_ignored(tmp_path):
    """A dir pattern must not match an unrelated dir containing it as a substring."""
    (tmp_path / "not_vendor").mkdir()
    similarly_named = tmp_path / "not_vendor" / "mod.py"
    similarly_named.write_text("x = 1\ny = 2\nz = 3\n" * 5)

    config = tmp_path / ".thailint.yaml"
    config.write_text(
        "dry:\n"
        "  enabled: true\n"
        "  min_duplicate_lines: 3\n"
        "  cache_enabled: false\n"
        "  ignore:\n"
        "    - vendor/\n"
    )

    analyzed_paths: list[str] = []
    original_analyze = FileAnalyzer.analyze

    def recording(self, file_path, content, language, cfg):
        analyzed_paths.append(str(file_path))
        return original_analyze(self, file_path, content, language, cfg)

    with patch.object(FileAnalyzer, "analyze", recording):
        linter = Linter(config_file=config, project_root=tmp_path)
        linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert any("not_vendor" in p for p in analyzed_paths), (
        f"file in a similarly-named directory was wrongly ignored: {analyzed_paths}"
    )
