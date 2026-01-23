"""
Purpose: Coordinate LBYL pattern detection and violation generation

Scope: Orchestrates multiple pattern detectors and converts results to violations

Overview: Provides PythonLBYLAnalyzer class that coordinates all LBYL pattern detectors
    and converts detected patterns into Violation objects. Handles AST parsing with
    graceful syntax error handling, runs enabled detectors based on configuration toggles,
    and aggregates violations from all detectors. Serves as the main analysis engine
    called by LBYLRule.

Dependencies: ast module, LBYLConfig, pattern detectors, violation_builder functions

Exports: PythonLBYLAnalyzer

Interfaces: analyze(code: str, file_path: str, config: LBYLConfig) -> list[Violation]

Implementation: Detector coordination with config-driven pattern selection
"""

import ast

from src.core.types import Violation

from .config import LBYLConfig
from .pattern_detectors.dict_key_detector import DictKeyDetector, DictKeyPattern
from .pattern_detectors.file_exists_detector import FileExistsDetector, FileExistsPattern
from .pattern_detectors.hasattr_detector import HasattrDetector, HasattrPattern
from .pattern_detectors.isinstance_detector import IsinstanceDetector, IsinstancePattern
from .pattern_detectors.len_check_detector import LenCheckDetector, LenCheckPattern
from .violation_builder import (
    build_dict_key_violation,
    build_file_exists_violation,
    build_hasattr_violation,
    build_isinstance_violation,
    build_len_check_violation,
)


def _parse_python_code(code: str) -> ast.Module | None:
    """Parse Python code into AST, returning None if empty or invalid."""
    if not code or not code.strip():
        return None
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def _convert_dict_key_pattern(pattern: DictKeyPattern, file_path: str) -> Violation:
    """Convert DictKeyPattern to Violation."""
    return build_dict_key_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        dict_name=pattern.dict_name,
        key_expression=pattern.key_expression,
    )


def _convert_hasattr_pattern(pattern: HasattrPattern, file_path: str) -> Violation:
    """Convert HasattrPattern to Violation."""
    return build_hasattr_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        object_name=pattern.object_name,
        attribute_name=pattern.attribute_name,
    )


def _convert_isinstance_pattern(pattern: IsinstancePattern, file_path: str) -> Violation:
    """Convert IsinstancePattern to Violation."""
    return build_isinstance_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        object_name=pattern.object_name,
        type_name=pattern.type_name,
    )


def _convert_file_exists_pattern(pattern: FileExistsPattern, file_path: str) -> Violation:
    """Convert FileExistsPattern to Violation."""
    return build_file_exists_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        path_expression=pattern.file_path_expression,
        check_type=pattern.check_type,
    )


def _convert_len_check_pattern(pattern: LenCheckPattern, file_path: str) -> Violation:
    """Convert LenCheckPattern to Violation."""
    return build_len_check_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        collection_name=pattern.collection_name,
        index_expression=pattern.index_expression,
    )


class PythonLBYLAnalyzer:
    """Coordinates LBYL pattern detection for Python code."""

    def __init__(self) -> None:
        """Initialize the analyzer with pattern detectors."""
        self._dict_key_detector = DictKeyDetector()
        self._file_exists_detector = FileExistsDetector()
        self._hasattr_detector = HasattrDetector()
        self._isinstance_detector = IsinstanceDetector()
        self._len_check_detector = LenCheckDetector()

    def analyze(self, code: str, file_path: str, config: LBYLConfig) -> list[Violation]:
        """Analyze Python code for LBYL patterns."""
        tree = _parse_python_code(code)
        if tree is None:
            return []
        return self._run_enabled_detectors(tree, file_path, config)

    def _run_enabled_detectors(
        self, tree: ast.Module, file_path: str, config: LBYLConfig
    ) -> list[Violation]:
        """Run all enabled pattern detectors and collect violations."""
        detectors = [
            (config.detect_dict_key, self._run_dict_key),
            (config.detect_file_exists, self._run_file_exists),
            (config.detect_hasattr, self._run_hasattr),
            (config.detect_isinstance, self._run_isinstance),
            (config.detect_len_check, self._run_len_check),
        ]
        violations: list[Violation] = []
        for enabled, runner in detectors:
            if enabled:
                violations.extend(runner(tree, file_path))
        return violations

    def _run_dict_key(self, tree: ast.Module, file_path: str) -> list[Violation]:
        """Run dict key detector and convert patterns to violations."""
        return [
            _convert_dict_key_pattern(p, file_path)
            for p in self._dict_key_detector.find_patterns(tree)
            if isinstance(p, DictKeyPattern)
        ]

    def _run_file_exists(self, tree: ast.Module, file_path: str) -> list[Violation]:
        """Run file exists detector and convert patterns to violations."""
        return [
            _convert_file_exists_pattern(p, file_path)
            for p in self._file_exists_detector.find_patterns(tree)
            if isinstance(p, FileExistsPattern)
        ]

    def _run_hasattr(self, tree: ast.Module, file_path: str) -> list[Violation]:
        """Run hasattr detector and convert patterns to violations."""
        return [
            _convert_hasattr_pattern(p, file_path)
            for p in self._hasattr_detector.find_patterns(tree)
            if isinstance(p, HasattrPattern)
        ]

    def _run_isinstance(self, tree: ast.Module, file_path: str) -> list[Violation]:
        """Run isinstance detector and convert patterns to violations."""
        return [
            _convert_isinstance_pattern(p, file_path)
            for p in self._isinstance_detector.find_patterns(tree)
            if isinstance(p, IsinstancePattern)
        ]

    def _run_len_check(self, tree: ast.Module, file_path: str) -> list[Violation]:
        """Run len check detector and convert patterns to violations."""
        return [
            _convert_len_check_pattern(p, file_path)
            for p in self._len_check_detector.find_patterns(tree)
            if isinstance(p, LenCheckPattern)
        ]
