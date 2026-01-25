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

Implementation: Detector coordination with config-driven pattern selection using
    generic detector runner for code reuse
"""

import ast
from collections.abc import Callable
from typing import Any, TypeVar

from src.core.types import Violation

from .config import LBYLConfig
from .pattern_detectors.base import BaseLBYLDetector, LBYLPattern
from .pattern_detectors.dict_key_detector import DictKeyDetector, DictKeyPattern
from .pattern_detectors.division_check_detector import (
    DivisionCheckDetector,
    DivisionCheckPattern,
)
from .pattern_detectors.file_exists_detector import FileExistsDetector, FileExistsPattern
from .pattern_detectors.hasattr_detector import HasattrDetector, HasattrPattern
from .pattern_detectors.isinstance_detector import IsinstanceDetector, IsinstancePattern
from .pattern_detectors.len_check_detector import LenCheckDetector, LenCheckPattern
from .pattern_detectors.none_check_detector import NoneCheckDetector, NoneCheckPattern
from .pattern_detectors.string_validator_detector import (
    StringValidatorDetector,
    StringValidatorPattern,
)
from .violation_builder import (
    build_dict_key_violation,
    build_division_check_violation,
    build_file_exists_violation,
    build_hasattr_violation,
    build_isinstance_violation,
    build_len_check_violation,
    build_none_check_violation,
    build_string_validator_violation,
)

PatternT = TypeVar("PatternT", bound=LBYLPattern)


def _parse_python_code(code: str) -> ast.Module | None:
    """Parse Python code into AST, returning None if empty or invalid."""
    if not code or not code.strip():
        return None
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def _run_detector(
    detector: BaseLBYLDetector[PatternT],
    tree: ast.Module,
    file_path: str,
    converter: Callable[[PatternT, str], Violation],
    pattern_type: type[PatternT],
) -> list[Violation]:
    """Run a detector and convert patterns to violations."""
    return [
        converter(p, file_path) for p in detector.find_patterns(tree) if isinstance(p, pattern_type)
    ]


def _build_dict_key(pattern: DictKeyPattern, file_path: str) -> Violation:
    """Convert DictKeyPattern to Violation."""
    return build_dict_key_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        dict_name=pattern.dict_name,
        key_expression=pattern.key_expression,
    )


def _build_division_check(pattern: DivisionCheckPattern, file_path: str) -> Violation:
    """Convert DivisionCheckPattern to Violation."""
    return build_division_check_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        divisor_name=pattern.divisor_name,
        operation=pattern.operation,
    )


def _build_file_exists(pattern: FileExistsPattern, file_path: str) -> Violation:
    """Convert FileExistsPattern to Violation."""
    return build_file_exists_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        path_expression=pattern.file_path_expression,
        check_type=pattern.check_type,
    )


def _build_hasattr(pattern: HasattrPattern, file_path: str) -> Violation:
    """Convert HasattrPattern to Violation."""
    return build_hasattr_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        object_name=pattern.object_name,
        attribute_name=pattern.attribute_name,
    )


def _build_isinstance(pattern: IsinstancePattern, file_path: str) -> Violation:
    """Convert IsinstancePattern to Violation."""
    return build_isinstance_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        object_name=pattern.object_name,
        type_name=pattern.type_name,
    )


def _build_len_check(pattern: LenCheckPattern, file_path: str) -> Violation:
    """Convert LenCheckPattern to Violation."""
    return build_len_check_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        collection_name=pattern.collection_name,
        index_expression=pattern.index_expression,
    )


def _build_none_check(pattern: NoneCheckPattern, file_path: str) -> Violation:
    """Convert NoneCheckPattern to Violation."""
    return build_none_check_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        variable_name=pattern.variable_name,
    )


def _build_string_validator(pattern: StringValidatorPattern, file_path: str) -> Violation:
    """Convert StringValidatorPattern to Violation."""
    return build_string_validator_violation(
        file_path=file_path,
        line=pattern.line_number,
        column=pattern.column,
        string_name=pattern.string_name,
        validator_method=pattern.validator_method,
        conversion_func=pattern.conversion_func,
    )


class PythonLBYLAnalyzer:
    """Coordinates LBYL pattern detection for Python code."""

    def __init__(self) -> None:
        """Initialize the analyzer with pattern detectors."""
        # Each tuple: (detector, converter, pattern_type)
        self._detector_configs: list[
            tuple[BaseLBYLDetector[Any], Callable[..., Violation], type]
        ] = [
            (DictKeyDetector(), _build_dict_key, DictKeyPattern),
            (DivisionCheckDetector(), _build_division_check, DivisionCheckPattern),
            (FileExistsDetector(), _build_file_exists, FileExistsPattern),
            (HasattrDetector(), _build_hasattr, HasattrPattern),
            (IsinstanceDetector(), _build_isinstance, IsinstancePattern),
            (LenCheckDetector(), _build_len_check, LenCheckPattern),
            (NoneCheckDetector(), _build_none_check, NoneCheckPattern),
            (StringValidatorDetector(), _build_string_validator, StringValidatorPattern),
        ]

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
        # Map detector types to their config flags
        enabled_flags = {
            DictKeyDetector: config.detect_dict_key,
            DivisionCheckDetector: config.detect_division_check,
            FileExistsDetector: config.detect_file_exists,
            HasattrDetector: config.detect_hasattr,
            IsinstanceDetector: config.detect_isinstance,
            LenCheckDetector: config.detect_len_check,
            NoneCheckDetector: config.detect_none_check,
            StringValidatorDetector: config.detect_string_validation,
        }

        violations: list[Violation] = []
        for detector, converter, pattern_type in self._detector_configs:
            if enabled_flags.get(type(detector), False):
                violations.extend(_run_detector(detector, tree, file_path, converter, pattern_type))
        return violations
