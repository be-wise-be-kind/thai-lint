"""
Purpose: Unit tests validating JSDoc comments are excluded from TypeScript DRY detection

Scope: Testing JSDoc comment filtering to prevent false positive duplication violations

Overview: Comprehensive test suite ensuring identical JSDoc comments appearing in multiple
    TypeScript functions or classes are not incorrectly flagged as duplicate code violations.
    JSDoc comments are documentation rather than logic and should be filtered from DRY analysis
    similar to Python docstrings. Tests function JSDoc, class JSDoc, and interface JSDoc across
    multiple files to ensure consistent filtering behavior for TypeScript documentation.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: test_function_jsdoc_not_flagged, test_class_jsdoc_not_flagged,
    test_interface_jsdoc_not_flagged test functions

Interfaces: Test functions accepting tmp_path fixture for file system operations

Implementation: Creates temporary TypeScript files with identical JSDoc comments in multiple locations,
    runs DRY linter with configured min_duplicate_lines threshold, validates no violations reported
    for JSDoc comment content
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
