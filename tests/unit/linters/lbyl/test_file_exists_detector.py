"""
Purpose: Tests for file exists LBYL pattern detection

Scope: Unit tests for detecting 'if os.path.exists(f): open(f)' patterns

Overview: Test suite for file exists LBYL pattern detection. Tests detection of basic
    patterns using os.path.exists and pathlib.Path.exists before file operations.
    Verifies handling of import aliases, no false positives for directory checks or
    different file paths, and EAFP suggestion generation using try/except FileNotFoundError.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for file exists detection

Interfaces: pytest test discovery and execution

Implementation: Tests for FileExistsDetector and LBYLViolationBuilder
"""

import ast

from src.linters.lbyl.pattern_detectors.file_exists_detector import (
    FileExistsDetector,
    FileExistsPattern,
)
from src.linters.lbyl.violation_builder import build_file_exists_violation


class TestFileExistsDetectorBasic:
    """Tests for basic file exists LBYL detection."""

    def test_detects_os_path_exists_before_open(self) -> None:
        """Detect: if os.path.exists(f): open(f) pattern."""
        code = """
import os.path
if os.path.exists(filename):
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], FileExistsPattern)
        assert patterns[0].file_path_expression == "filename"
        assert patterns[0].check_type == "os.path.exists"

    def test_detects_pathlib_exists_before_open(self) -> None:
        """Detect: if Path(f).exists(): open(f) pattern."""
        code = """
from pathlib import Path
if Path(filename).exists():
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], FileExistsPattern)
        assert patterns[0].file_path_expression == "filename"
        assert patterns[0].check_type == "Path.exists"

    def test_detects_path_variable_exists_before_operation(self) -> None:
        """Detect: p = Path(f); if p.exists(): p.read_text() pattern."""
        code = """
from pathlib import Path
p = Path(filename)
if p.exists():
    content = p.read_text()
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].file_path_expression == "p"
        assert patterns[0].check_type == "Path.exists"

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
import os.path
# Comment line

if os.path.exists(filename):
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 5

    def test_detects_with_else_branch(self) -> None:
        """Detect pattern with else branch."""
        code = """
import os.path
if os.path.exists(filename):
    f = open(filename)
else:
    raise FileNotFoundError(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestFileExistsDetectorImportAliases:
    """Tests for handling import aliases."""

    def test_handles_from_os_path_import_exists(self) -> None:
        """Detect with: from os.path import exists; if exists(f): open(f)."""
        code = """
from os.path import exists
if exists(filename):
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].check_type == "exists"

    def test_handles_import_os_path_as_alias(self) -> None:
        """Detect with: import os.path as osp; if osp.exists(f): open(f)."""
        code = """
import os.path as osp
if osp.exists(filename):
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_import_os_module(self) -> None:
        """Detect with: import os; if os.path.exists(f): open(f)."""
        code = """
import os
if os.path.exists(filename):
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestFileExistsDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_file(self) -> None:
        """No detection when exists and open use different files."""
        code = """
import os.path
if os.path.exists(file1):
    f = open(file2)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_no_flag_for_directory_check_isdir(self) -> None:
        """Don't flag: if os.path.isdir(d): os.listdir(d)."""
        code = """
import os.path
if os.path.isdir(dirname):
    files = os.listdir(dirname)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_exists_without_file_operation(self) -> None:
        """Don't flag exists when body doesn't operate on the file."""
        code = """
import os.path
if os.path.exists(filename):
    print("File found")
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_inverted_exists_check(self) -> None:
        """Don't flag: if not os.path.exists(f): create_file(f)."""
        code = """
import os.path
if not os.path.exists(filename):
    create_file(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0


class TestFileExistsDetectorEdgeCases:
    """Edge case tests for file exists detection."""

    def test_handles_nested_path_expression(self) -> None:
        """Detect when path is attribute: if self.path.exists(): open(self.path)."""
        code = """
if self.filepath.exists():
    f = open(self.filepath)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_pathlib_read_text(self) -> None:
        """Detect: if p.exists(): p.read_text()."""
        code = """
from pathlib import Path
p = Path("config.txt")
if p.exists():
    content = p.read_text()
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_pathlib_write_text(self) -> None:
        """Detect write operations as file operations."""
        code = """
from pathlib import Path
p = Path("output.txt")
if p.exists():
    p.write_text("data")
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        # Write after exists check is also LBYL
        assert len(patterns) == 1


class TestFileExistsDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_includes_try_except_filenotfounderror(self) -> None:
        """Suggestion should mention try/except FileNotFoundError."""
        code = """
import os.path
if os.path.exists(filename):
    f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, FileExistsPattern)
        violation = build_file_exists_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            path_expression=pattern.file_path_expression,
            check_type=pattern.check_type,
        )
        assert "try" in violation.suggestion.lower()
        assert "FileNotFoundError" in violation.suggestion

    def test_suggestion_uses_actual_file_path(self) -> None:
        """Suggestion uses the actual file path variable name."""
        code = """
import os.path
if os.path.exists(my_config_file):
    f = open(my_config_file)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, FileExistsPattern)
        violation = build_file_exists_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            path_expression=pattern.file_path_expression,
            check_type=pattern.check_type,
        )
        assert "my_config_file" in violation.suggestion


class TestMultipleFileExistsPatterns:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_file_exists_patterns(self) -> None:
        """Detects multiple file exists LBYL patterns."""
        code = """
import os.path
if os.path.exists(file1):
    f1 = open(file1)

if os.path.exists(file2):
    f2 = open(file2)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
import os.path
if condition:
    if os.path.exists(filename):
        f = open(filename)
"""
        tree = ast.parse(code)
        detector = FileExistsDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
