"""
File: src/linters/file_header/linter.py
Purpose: Main file header linter rule implementation
Exports: FileHeaderRule class
Depends: BaseLintRule, PythonHeaderParser, FieldValidator, AtemporalDetector, ViolationBuilder
Implements: Composition pattern with helper classes, AST-based Python parsing
Related: config.py for configuration, python_parser.py for extraction

Overview:
    Orchestrates file header validation for Python files using focused helper classes.
    Coordinates docstring extraction, field validation, atemporal language detection, and
    violation building. Supports configuration from .thailint.yaml and ignore directives.
    Validates headers against mandatory field requirements and atemporal language standards.

Usage:
    rule = FileHeaderRule()
    violations = rule.check(context)

Notes: Follows composition pattern from magic_numbers linter for maintainability
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .atemporal_detector import AtemporalDetector
from .config import FileHeaderConfig
from .field_validator import FieldValidator
from .python_parser import PythonHeaderParser
from .violation_builder import ViolationBuilder


class FileHeaderRule(BaseLintRule):  # thailint: ignore[srp]
    """Validates file headers for mandatory fields and atemporal language.

    Method count (17) exceeds SRP guideline (8) because proper A-grade complexity
    refactoring requires extracting helper methods. Class maintains single responsibility
    of file header validation - all methods support this core purpose through composition
    pattern with focused helper classes (parser, validator, detector, builder).
    """

    def __init__(self) -> None:
        """Initialize the file header rule."""
        self._violation_builder = ViolationBuilder(self.rule_id)
        self._ignore_parser = IgnoreDirectiveParser()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule.

        Returns:
            Rule identifier string
        """
        return "file-header.validation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule.

        Returns:
            Rule name string
        """
        return "File Header Validation"

    @property
    def description(self) -> str:
        """Description of what this rule checks.

        Returns:
            Rule description string
        """
        return "Validates file headers for mandatory fields and atemporal language"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file header for violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found in file header
        """
        # Only Python for now (PR3), multi-language in PR5
        if context.language != "python":
            return []

        # Check for file-level ignore directives first
        if self._has_file_ignore(context):
            return []

        # Load configuration
        config = self._load_config(context)

        # Check if file should be ignored by pattern
        if self._should_ignore_file(context, config):
            return []

        # Extract and validate header
        return self._check_python_header(context, config)

    def _has_file_ignore(self, context: BaseLintContext) -> bool:
        """Check if file has file-level ignore directive.

        Args:
            context: Lint context

        Returns:
            True if file has ignore-file directive
        """
        file_content = context.file_content or ""

        if self._has_standard_ignore(file_content):
            return True

        return self._has_custom_ignore_syntax(file_content)

    def _has_standard_ignore(self, file_content: str) -> bool:  # thailint: ignore[nesting]
        """Check standard ignore parser for file-level ignores."""
        # Check first 10 lines for standard ignore directives
        first_lines = file_content.splitlines()[:10]
        for line in first_lines:
            if self._ignore_parser._has_ignore_directive_marker(line):  # pylint: disable=protected-access
                if self._ignore_parser._check_specific_rule_ignore(line, self.rule_id):  # pylint: disable=protected-access
                    return True
                if self._ignore_parser._check_general_ignore(line):  # pylint: disable=protected-access
                    return True
        return False

    def _has_custom_ignore_syntax(self, file_content: str) -> bool:
        """Check custom file-level ignore syntax."""
        first_lines = file_content.splitlines()[:10]
        return any(self._is_ignore_line(line) for line in first_lines)

    def _is_ignore_line(self, line: str) -> bool:
        """Check if line contains ignore directive."""
        line_lower = line.lower()
        return "# thailint-ignore-file:" in line_lower or "# thailint-ignore" in line_lower

    def _load_config(self, context: BaseLintContext) -> FileHeaderConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            FileHeaderConfig with loaded or default values
        """
        # Try production config first
        if hasattr(context, "metadata") and isinstance(context.metadata, dict):
            if "file_header" in context.metadata:
                return load_linter_config(context, "file_header", FileHeaderConfig)  # type: ignore[type-var]

        # Use defaults
        return FileHeaderConfig()

    def _should_ignore_file(self, context: BaseLintContext, config: FileHeaderConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: File header configuration

        Returns:
            True if file should be ignored
        """
        if not context.file_path:
            return False

        file_path = Path(context.file_path)
        return any(self._matches_ignore_pattern(file_path, p) for p in config.ignore)

    def _matches_ignore_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file path matches a single ignore pattern."""
        if file_path.match(pattern):
            return True

        if self._matches_directory_pattern(file_path, pattern):
            return True

        if self._matches_file_pattern(file_path, pattern):
            return True

        return pattern in str(file_path)

    def _matches_directory_pattern(self, file_path: Path, pattern: str) -> bool:
        """Match directory patterns like **/migrations/**."""
        if pattern.startswith("**/") and pattern.endswith("/**"):
            dir_name = pattern[3:-3]
            return dir_name in file_path.parts
        return False

    def _matches_file_pattern(self, file_path: Path, pattern: str) -> bool:
        """Match file patterns like **/__init__.py."""
        if pattern.startswith("**/"):
            filename_pattern = pattern[3:]
            path_str = str(file_path)
            return file_path.name == filename_pattern or path_str.endswith(filename_pattern)
        return False

    def _check_python_header(
        self, context: BaseLintContext, config: FileHeaderConfig
    ) -> list[Violation]:
        """Check Python file header.

        Args:
            context: Lint context
            config: Configuration

        Returns:
            List of violations filtered through ignore directives
        """
        parser = PythonHeaderParser()
        header = parser.extract_header(context.file_content or "")

        if not header:
            return self._build_missing_header_violations(context)

        fields = parser.parse_fields(header)
        violations = self._validate_header_fields(fields, context, config)
        violations.extend(self._check_atemporal_violations(header, context, config))

        return self._filter_ignored_violations(violations, context)

    def _build_missing_header_violations(self, context: BaseLintContext) -> list[Violation]:
        """Build violations for missing header."""
        return [
            self._violation_builder.build_missing_field(
                "docstring", str(context.file_path or ""), 1
            )
        ]

    def _validate_header_fields(
        self, fields: dict[str, str], context: BaseLintContext, config: FileHeaderConfig
    ) -> list[Violation]:
        """Validate mandatory header fields."""
        violations = []
        field_validator = FieldValidator(config)
        field_violations = field_validator.validate_fields(fields, context.language)

        for field_name, _error_message in field_violations:
            violations.append(
                self._violation_builder.build_missing_field(
                    field_name, str(context.file_path or ""), 1
                )
            )
        return violations

    def _check_atemporal_violations(
        self, header: str, context: BaseLintContext, config: FileHeaderConfig
    ) -> list[Violation]:
        """Check for atemporal language violations."""
        if not config.enforce_atemporal:
            return []

        violations = []
        atemporal_detector = AtemporalDetector()
        atemporal_violations = atemporal_detector.detect_violations(header)

        for pattern, description, line_num in atemporal_violations:
            violations.append(
                self._violation_builder.build_atemporal_violation(
                    pattern, description, str(context.file_path or ""), line_num
                )
            )
        return violations

    def _filter_ignored_violations(
        self, violations: list[Violation], context: BaseLintContext
    ) -> list[Violation]:
        """Filter out violations that should be ignored.

        Args:
            violations: List of violations to filter
            context: Lint context with file content

        Returns:
            Filtered list of violations
        """
        file_content = context.file_content or ""
        lines = file_content.splitlines()

        filtered = []
        for v in violations:
            # Check standard ignore directives
            if self._ignore_parser.should_ignore_violation(v, file_content):
                continue

            # Check custom line-level ignore syntax: # thailint-ignore-line:
            if self._has_line_level_ignore(lines, v):
                continue

            filtered.append(v)

        return filtered

    def _has_line_level_ignore(self, lines: list[str], violation: Violation) -> bool:
        """Check for thailint-ignore-line directive.

        Args:
            lines: File content split into lines
            violation: Violation to check

        Returns:
            True if line has ignore directive
        """
        if violation.line <= 0 or violation.line > len(lines):
            return False

        line_content = lines[violation.line - 1]  # Convert to 0-indexed
        return "# thailint-ignore-line:" in line_content.lower()
