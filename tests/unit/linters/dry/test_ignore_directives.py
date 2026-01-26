"""
Purpose: Tests for DRY linter ignore directives and exclusion patterns

Scope: Ignore functionality including inline directives, file-level, directory-level, and pattern-based exclusions

Overview: Comprehensive test suite for ignore mechanisms covering inline ignore-block,
    ignore-next directives, file-level config exclusions, directory patterns, pattern-based
    matching, selective ignoring, multiple ignores in same file, and ignore disabled scenarios.
    Validates proper suppression and filtering of violations.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 8 test functions for ignore directive scenarios

Interfaces: Uses Linter class with config file and inline comment directives

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from src import Linter


def test_inline_ignore_next(tmp_path):
    """Test that ignore-next directive suppresses next block."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    # dry: ignore-next
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) <= 1


def test_file_level_ignore_in_config(tmp_path):
    """Test file-level ignore configured in .thailint.yaml."""
    (tmp_path / "tests").mkdir()

    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "tests" / "test_file.py"
    file2.write_text("""
def test_process():
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  ignore:
    - "tests/"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    violation_paths = [v.file_path for v in violations]
    assert not any("tests" in p for p in violation_paths)


def test_directory_level_ignore(tmp_path):
    """Test directory-level ignore patterns."""
    (tmp_path / "src").mkdir()
    (tmp_path / "vendor").mkdir()

    duplicate_code = """
    result = process()
    validated = validate(result)
    return validated
"""

    file1 = tmp_path / "src" / "module.py"
    file1.write_text(f"def func1():\n{duplicate_code}\n")

    file2 = tmp_path / "vendor" / "external.py"
    file2.write_text(f"def func2():\n{duplicate_code}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  ignore:
    - "vendor/"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    violation_paths = [v.file_path for v in violations]
    assert not any("vendor" in p for p in violation_paths)


def test_pattern_based_ignore(tmp_path):
    """Test pattern-based ignore for __init__.py files."""
    (tmp_path / "pkg1").mkdir()
    (tmp_path / "pkg2").mkdir()

    duplicate_code = """
    from .module import something
    from .other import another
    __all__ = ['something', 'another']
"""

    file1 = tmp_path / "pkg1" / "__init__.py"
    file1.write_text(duplicate_code)

    file2 = tmp_path / "pkg2" / "__init__.py"
    file2.write_text(duplicate_code)

    file3 = tmp_path / "regular.py"
    file3.write_text(duplicate_code)

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
  ignore:
    - "__init__.py"
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    violation_paths = [v.file_path for v in violations]
    assert not any("__init__.py" in p for p in violation_paths)


def test_block_ignore_start_end_suppresses_code_duplicates(tmp_path):
    """Test # thailint: ignore-start dry / ignore-end works for code duplicates.

    This tests the standard thailint ignore directive syntax that other linters support.
    """
    file1 = tmp_path / "file1.py"
    file1.write_text("""
# thailint: ignore-start dry
def process():
    for item in items:
        if item.valid:
            item.save()
# thailint: ignore-end
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    for item in items:
        if item.valid:
            item.save()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # File1's duplicate block is in ignore-start/end, so should only get violations from file2
    file1_violations = [v for v in violations if "file1.py" in v.file_path]
    assert len(file1_violations) == 0, f"Expected no violations from file1, got: {file1_violations}"


def test_block_ignore_suppresses_constants(tmp_path):
    """Test # thailint: ignore-start dry works for constant detection."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
# thailint: ignore-start dry
SAMPLE_RATE = 24000
# thailint: ignore-end
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
SAMPLE_RATE = 24000
""")

    file3 = tmp_path / "file3.py"
    file3.write_text("""
SAMPLE_RATE = 24000
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  cache_enabled: false
  detect_duplicate_constants: true
  min_constant_occurrences: 2
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # File1's constant is in ignore block, should not appear in violations
    file1_violations = [v for v in violations if "file1.py" in v.file_path]
    assert len(file1_violations) == 0, f"Expected no violations from file1, got: {file1_violations}"


def test_inline_ignore_suppresses_constant(tmp_path):
    """Test # thailint: ignore dry works for constants on the same line."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
SAMPLE_RATE = 24000  # thailint: ignore dry
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
SAMPLE_RATE = 24000
""")

    file3 = tmp_path / "file3.py"
    file3.write_text("""
SAMPLE_RATE = 24000
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  cache_enabled: false
  detect_duplicate_constants: true
  min_constant_occurrences: 2
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # File1's constant has inline ignore, should not appear in violations
    file1_violations = [v for v in violations if "file1.py" in v.file_path]
    assert len(file1_violations) == 0, f"Expected no violations from file1, got: {file1_violations}"


def test_issue_144_constants_respect_ignore_directives(tmp_path):
    """Regression test for GitHub issue #144.

    Issue: https://github.com/anthropics/thai-lint/issues/144
    Problem: DRY linter ignore patterns don't work for similar constants detection

    This test reproduces the exact scenario from the issue:
    - Constants defined in multiple files
    - One file has # thailint: ignore-start dry / ignore-end around the constant
    - The constant should not be flagged as a violation
    """
    # Simulate the user's scenario from issue #144
    audio_config = tmp_path / "audio_config.py"
    audio_config.write_text("""
# Audio configuration constants
# thailint: ignore-start dry
STT_SAMPLE_RATE = 24000
# thailint: ignore-end
""")

    speech_processor = tmp_path / "speech_processor.py"
    speech_processor.write_text("""
# Speech processing module
STT_SAMPLE_RATE = 24000
""")

    audio_handler = tmp_path / "audio_handler.py"
    audio_handler.write_text("""
# Audio handler module
STT_SAMPLE_RATE = 24000
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  cache_enabled: false
  detect_duplicate_constants: true
  min_constant_occurrences: 2
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # The audio_config.py constant is in an ignore block, should not be flagged
    audio_config_violations = [v for v in violations if "audio_config.py" in v.file_path]
    assert len(audio_config_violations) == 0, (
        f"Expected no violations from audio_config.py (constant is in ignore block), "
        f"got: {audio_config_violations}"
    )
