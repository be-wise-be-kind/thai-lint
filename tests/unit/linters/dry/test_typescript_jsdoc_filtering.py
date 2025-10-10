"""
Purpose: Test that JSDoc comments are NOT flagged as duplicate code in TypeScript

Scope: Verify DRY linter filters out JSDoc comments from duplication detection

Overview: Tests that identical JSDoc comments appearing in multiple functions/classes
    are not incorrectly flagged as duplicate code. JSDoc comments are documentation,
    not logic, and should be filtered from DRY analysis - similar to Python docstrings.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Test functions for JSDoc comment filtering

Implementation: Creates files with identical JSDoc comments in multiple locations
    and verifies they are NOT flagged as violations.
"""

from src import Linter


def test_function_jsdoc_not_flagged(tmp_path):
    """Test that identical function JSDoc comments are NOT flagged as duplicate."""
    file1 = tmp_path / "utils1.ts"
    file1.write_text("""
/**
 * This is a helper function that does something useful.
 * It has multiple lines in the JSDoc comment.
 * @param data The input data to process
 * @returns Processed result
 */
function helperOne(data: any): any {
    return processData(data);
}
""")

    file2 = tmp_path / "utils2.ts"
    file2.write_text("""
/**
 * This is a helper function that does something useful.
 * It has multiple lines in the JSDoc comment.
 * @param data The input data to process
 * @returns Processed result
 */
function helperTwo(data: any): any {
    return processOtherData(data);
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # JSDoc comments should NOT be flagged as duplicate
    assert len(violations) == 0, "JSDoc comments should not be flagged as duplicate"


def test_duplicate_code_after_jsdoc_is_still_flagged(tmp_path):
    """Test that actual duplicate code (not JSDoc) IS still flagged."""
    file1 = tmp_path / "processor1.ts"
    file1.write_text("""
/**
 * Different JSDoc for function one.
 */
function processOne(data: any): any {
    const x = validate(data);
    const y = transform(x);
    const z = save(y);
    return z;
}
""")

    file2 = tmp_path / "processor2.ts"
    file2.write_text("""
/**
 * Different JSDoc for function two.
 */
function processTwo(data: any): any {
    const x = validate(data);
    const y = transform(x);
    const z = save(y);
    return z;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # The actual code (not JSDoc) SHOULD be flagged
    assert len(violations) > 0, "Duplicate code after JSDoc should still be flagged"


def test_single_line_jsdoc_not_flagged(tmp_path):
    """Test that single-line JSDoc comments are handled correctly."""
    file1 = tmp_path / "util1.ts"
    file1.write_text("""
/** Processes data */
function process1(data: any): any {
    return transform(data);
}

/** Processes data */
function process2(data: any): any {
    return validate(data);
}
""")

    file2 = tmp_path / "util2.ts"
    file2.write_text("""
/** Processes data */
function process3(data: any): any {
    return save(data);
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 1
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Single-line JSDoc should NOT be flagged
    assert len(violations) == 0, "Single-line JSDoc should not be flagged as duplicate"
