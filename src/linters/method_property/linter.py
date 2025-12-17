"""
Purpose: Main method-should-be-property linter rule implementation

Scope: Method-should-be-property detection for Python files

Overview: Implements method-should-be-property linter rule following MultiLanguageLintRule
    interface. Orchestrates configuration loading, Python AST analysis for property candidates,
    and violation building through focused helper classes. Detects methods that should be
    converted to @property decorators following Pythonic conventions. Supports configurable
    max_body_statements threshold, ignore patterns for excluding files, and inline ignore
    directives (thailint: ignore, noqa) for suppressing specific violations. Handles test file
    detection and non-Python languages gracefully.

Dependencies: BaseLintContext and MultiLanguageLintRule from core, ast module, pathlib,
    analyzer classes, config classes

Exports: MethodPropertyRule class implementing MultiLanguageLintRule interface

Interfaces: check(context) -> list[Violation] for rule validation, standard rule properties
    (rule_id, rule_name, description)

Implementation: Composition pattern with helper classes (analyzer, violation builder),
    AST-based analysis for Python with comprehensive exclusion rules
"""

import ast
from pathlib import Path

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.types import Violation

from .config import MethodPropertyConfig
from .python_analyzer import PropertyCandidate, PythonMethodAnalyzer
from .violation_builder import ViolationBuilder


class MethodPropertyRule(MultiLanguageLintRule):  # thailint: ignore[srp,dry]
    """Detects methods that should be @property decorators."""

    def __init__(self) -> None:
        """Initialize the method property rule."""
        self._violation_builder = ViolationBuilder(self.rule_id)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "method-property.should-be-property"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "method should be property"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Methods should be converted to @property decorators for Pythonic attribute access"

    def _load_config(self, context: BaseLintContext) -> MethodPropertyConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            MethodPropertyConfig instance
        """
        test_config = self._try_load_test_config(context)
        if test_config is not None:
            return test_config

        return MethodPropertyConfig()

    # dry: ignore-block
    def _try_load_test_config(self, context: BaseLintContext) -> MethodPropertyConfig | None:
        """Try to load test-style configuration.

        Args:
            context: Lint context

        Returns:
            Config if found, None otherwise
        """
        if not hasattr(context, "config"):
            return None
        config_attr = context.config
        if config_attr is None or not isinstance(config_attr, dict):
            return None

        # Check for method-property specific config
        linter_config = config_attr.get("method-property", config_attr)
        return MethodPropertyConfig.from_dict(linter_config)

    # dry: ignore-block
    def _is_file_ignored(self, context: BaseLintContext, config: MethodPropertyConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: Configuration

        Returns:
            True if file should be ignored
        """
        if not config.ignore:
            return False

        if not context.file_path:
            return False

        file_path = Path(context.file_path)
        for pattern in config.ignore:
            if self._matches_pattern(file_path, pattern):
                return True
        return False

    # dry: ignore-block
    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file path matches a glob pattern.

        Args:
            file_path: Path to check
            pattern: Glob pattern

        Returns:
            True if path matches pattern
        """
        if file_path.match(pattern):
            return True
        if pattern in str(file_path):
            return True
        return False

    # dry: ignore-block
    def _is_test_file(self, file_path: object) -> bool:
        """Check if file is a test file.

        Args:
            file_path: Path to check

        Returns:
            True if test file
        """
        path_str = str(file_path)
        file_name = Path(path_str).name

        # Check test_*.py pattern
        if file_name.startswith("test_") and file_name.endswith(".py"):
            return True

        # Check *_test.py pattern
        if file_name.endswith("_test.py"):
            return True

        return False

    def _check_python(
        self, context: BaseLintContext, config: MethodPropertyConfig
    ) -> list[Violation]:
        """Check Python code for method property violations.

        Args:
            context: Lint context with Python file information
            config: Method property configuration

        Returns:
            List of violations found in Python code
        """
        if self._is_file_ignored(context, config):
            return []

        if self._is_test_file(context.file_path):
            return []

        tree = self._parse_python_code(context.file_content)
        if tree is None:
            return []

        analyzer = PythonMethodAnalyzer(
            max_body_statements=config.max_body_statements,
            exclude_prefixes=config.exclude_prefixes,
            exclude_names=config.exclude_names,
        )
        candidates = analyzer.find_property_candidates(tree)
        candidates = self._filter_ignored_methods(candidates, config)
        return self._collect_violations(candidates, context)

    def _filter_ignored_methods(
        self,
        candidates: list[PropertyCandidate],
        config: MethodPropertyConfig,
    ) -> list[PropertyCandidate]:
        """Filter out candidates with ignored method names.

        Args:
            candidates: List of property candidates
            config: Configuration with ignore_methods list

        Returns:
            Filtered list of candidates
        """
        if not config.ignore_methods:
            return candidates
        return [c for c in candidates if c.method_name not in config.ignore_methods]

    # dry: ignore-block
    def _parse_python_code(self, code: str | None) -> ast.AST | None:
        """Parse Python code into AST.

        Args:
            code: Python source code

        Returns:
            AST or None if parse fails
        """
        try:
            return ast.parse(code or "")
        except SyntaxError:
            return None

    def _collect_violations(
        self,
        candidates: list[PropertyCandidate],
        context: BaseLintContext,
    ) -> list[Violation]:
        """Collect violations from property candidates.

        Args:
            candidates: List of property candidates
            context: Lint context

        Returns:
            List of violations
        """
        violations = []
        for candidate in candidates:
            violation = self._create_violation(candidate, context)
            if not self._should_ignore(violation, candidate, context):
                violations.append(violation)
        return violations

    def _create_violation(
        self,
        candidate: PropertyCandidate,
        context: BaseLintContext,
    ) -> Violation:
        """Create a violation for a property candidate.

        Args:
            candidate: The property candidate
            context: Lint context

        Returns:
            Violation object
        """
        return self._violation_builder.create_violation(
            method_name=candidate.method_name,
            line=candidate.line,
            column=candidate.column,
            file_path=context.file_path,
            is_get_prefix=candidate.is_get_prefix,
            class_name=candidate.class_name,
        )

    def _should_ignore(
        self,
        violation: Violation,
        candidate: PropertyCandidate,
        context: BaseLintContext,
    ) -> bool:
        """Check if violation should be ignored based on directives.

        Args:
            violation: Violation to check
            candidate: The property candidate
            context: Lint context

        Returns:
            True if violation should be ignored
        """
        if self._has_inline_ignore(violation, context):
            return True
        if self._has_docstring_ignore(candidate, context):
            return True
        return False

    # dry: ignore-block
    def _has_inline_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check for inline ignore directive on method line.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if line has ignore directive
        """
        line_text = self._get_line_text(violation.line, context)
        if line_text is None:
            return False

        line_lower = line_text.lower()

        # Check for thailint: ignore[method-property]
        if "thailint:" in line_lower and "ignore" in line_lower:
            return True

        # Check for noqa
        if "# noqa" in line_lower:
            return True

        return False

    def _has_docstring_ignore(
        self,
        candidate: PropertyCandidate,
        context: BaseLintContext,
    ) -> bool:
        """Check for ignore directive in method docstring.

        Args:
            candidate: Property candidate
            context: Lint context

        Returns:
            True if docstring has ignore directive
        """
        tree = self._parse_python_code(context.file_content)
        if tree is None:
            return False

        docstring = self._find_method_docstring(tree, candidate)
        if docstring is None:
            return False

        docstring_lower = docstring.lower()
        return "thailint: ignore" in docstring_lower

    def _find_method_docstring(
        self,
        tree: ast.AST,
        candidate: PropertyCandidate,
    ) -> str | None:
        """Find the docstring for a method.

        Args:
            tree: AST tree
            candidate: Property candidate

        Returns:
            Docstring text or None
        """
        target_class = self._find_class_node(tree, candidate.class_name)
        if target_class is None:
            return None
        return self._find_method_in_class(target_class, candidate.method_name)

    def _find_class_node(self, tree: ast.AST, class_name: str) -> ast.ClassDef | None:
        """Find a class node by name in the AST.

        Args:
            tree: AST tree
            class_name: Name of the class to find

        Returns:
            ClassDef node or None
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        return None

    def _find_method_in_class(self, class_node: ast.ClassDef, method_name: str) -> str | None:
        """Find method docstring within a class.

        Args:
            class_node: Class node to search
            method_name: Method name to find

        Returns:
            Docstring or None
        """
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                return ast.get_docstring(item)
        return None

    def _get_line_text(self, line: int, context: BaseLintContext) -> str | None:
        """Get the text of a specific line.

        Args:
            line: Line number (1-indexed)
            context: Lint context

        Returns:
            Line text or None
        """
        if not context.file_content:
            return None

        lines = context.file_content.splitlines()
        if line <= 0 or line > len(lines):
            return None

        return lines[line - 1]

    def _check_typescript(
        self, context: BaseLintContext, config: MethodPropertyConfig
    ) -> list[Violation]:
        """Check TypeScript code for violations.

        Args:
            context: Lint context
            config: Configuration

        Returns:
            Empty list (not implemented for TypeScript)
        """
        return []
