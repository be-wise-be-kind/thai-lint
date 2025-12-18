"""
Purpose: Main file header linter rule implementation

Scope: File header validation for Python, TypeScript, JavaScript, Bash, Markdown, and CSS files

Overview: Orchestrates file header validation for multiple languages using focused helper classes.
    Coordinates header extraction, field validation, atemporal language detection, and
    violation building. Supports configuration from .thailint.yaml and ignore directives
    including file-level and line-level ignore markers. Validates headers against mandatory
    field requirements and atemporal language standards. Handles language-specific parsing
    and special Markdown prose field extraction for atemporal checking.

Dependencies: BaseLintRule and BaseLintContext from core, language-specific parsers,
    FieldValidator, AtemporalDetector, ViolationBuilder

Exports: FileHeaderRule class implementing BaseLintRule interface

Interfaces: check(context) -> list[Violation] for rule validation, standard rule properties
    (rule_id, rule_name, description)

Implementation: Composition pattern with helper classes for parsing, validation,
    and violation building
"""

from pathlib import Path
from typing import Protocol

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .atemporal_detector import AtemporalDetector
from .bash_parser import BashHeaderParser
from .config import FileHeaderConfig
from .css_parser import CssHeaderParser
from .field_validator import FieldValidator
from .markdown_parser import MarkdownHeaderParser
from .python_parser import PythonHeaderParser
from .typescript_parser import TypeScriptHeaderParser
from .violation_builder import ViolationBuilder


class HeaderParser(Protocol):
    """Protocol for header parsers."""

    def extract_header(self, code: str) -> str | None:
        """Extract header from source code."""

    def parse_fields(self, header: str) -> dict[str, str]:
        """Parse fields from header."""


class FileHeaderRule(BaseLintRule):  # thailint: ignore[srp]
    """Validates file headers for mandatory fields and atemporal language.

    Method count (17) exceeds SRP guideline (8) because proper A-grade complexity
    refactoring requires extracting helper methods. Class maintains single responsibility
    of file header validation - all methods support this core purpose through composition
    pattern with focused helper classes (parser, validator, detector, builder).
    """

    # Parser instances for each language
    _parsers: dict[str, HeaderParser] = {
        "python": PythonHeaderParser(),
        "typescript": TypeScriptHeaderParser(),
        "javascript": TypeScriptHeaderParser(),
        "bash": BashHeaderParser(),
        "markdown": MarkdownHeaderParser(),
        "css": CssHeaderParser(),
    }

    def __init__(self) -> None:
        """Initialize the file header rule."""
        self._violation_builder = ViolationBuilder(self.rule_id)
        self._ignore_parser = IgnoreDirectiveParser()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "file-header.validation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "File Header Validation"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Validates file headers for mandatory fields and atemporal language"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file header for violations."""
        if self._has_file_ignore(context):
            return []

        config = self._load_config(context)

        if self._should_ignore_file(context, config):
            return []

        return self._check_language_header(context, config)

    def _check_language_header(
        self, context: BaseLintContext, config: FileHeaderConfig
    ) -> list[Violation]:
        """Dispatch to language-specific header checking."""
        parser = self._parsers.get(context.language)
        if not parser:
            return []

        # Markdown has special atemporal handling
        if context.language == "markdown":
            return self._check_markdown_header(parser, context, config)

        return self._check_header_with_parser(parser, context, config)

    def _check_header_with_parser(
        self, parser: HeaderParser, context: BaseLintContext, config: FileHeaderConfig
    ) -> list[Violation]:
        """Check header using the given parser."""
        header = parser.extract_header(context.file_content or "")

        if not header:
            return self._build_missing_header_violations(context)

        fields = parser.parse_fields(header)
        violations = self._validate_header_fields(fields, context, config)
        violations.extend(self._check_atemporal_violations(header, context, config))

        return self._filter_ignored_violations(violations, context)

    def _check_markdown_header(
        self, parser: HeaderParser, context: BaseLintContext, config: FileHeaderConfig
    ) -> list[Violation]:
        """Check Markdown file header with special prose-only atemporal checking."""
        header = parser.extract_header(context.file_content or "")

        if not header:
            return self._build_missing_header_violations(context)

        fields = parser.parse_fields(header)
        violations = self._validate_header_fields(fields, context, config)

        # For Markdown, only check atemporal language in prose fields
        prose_content = self._extract_markdown_prose_fields(fields)
        violations.extend(self._check_atemporal_violations(prose_content, context, config))

        return self._filter_ignored_violations(violations, context)

    def _has_file_ignore(self, context: BaseLintContext) -> bool:
        """Check if file has file-level ignore directive."""
        file_content = context.file_content or ""

        if self._has_standard_ignore(file_content):
            return True

        return self._has_custom_ignore_syntax(file_content)

    def _has_standard_ignore(self, file_content: str) -> bool:  # thailint: ignore[nesting]
        """Check standard ignore parser for file-level ignores."""
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
        """Load configuration from context."""
        if hasattr(context, "metadata") and isinstance(context.metadata, dict):
            if "file_header" in context.metadata:
                return load_linter_config(context, "file_header", FileHeaderConfig)  # type: ignore[type-var]

        return FileHeaderConfig()

    def _should_ignore_file(self, context: BaseLintContext, config: FileHeaderConfig) -> bool:
        """Check if file matches ignore patterns."""
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
        """Filter out violations that should be ignored."""
        file_content = context.file_content or ""
        lines = file_content.splitlines()

        non_ignored = (
            v
            for v in violations
            if not self._ignore_parser.should_ignore_violation(v, file_content)
            and not self._has_line_level_ignore(lines, v)
        )
        return list(non_ignored)

    def _has_line_level_ignore(self, lines: list[str], violation: Violation) -> bool:
        """Check for thailint-ignore-line directive."""
        if violation.line <= 0 or violation.line > len(lines):
            return False

        line_content = lines[violation.line - 1]
        return "# thailint-ignore-line:" in line_content.lower()

    def _extract_markdown_prose_fields(self, fields: dict[str, str]) -> str:
        """Extract prose fields from Markdown frontmatter for atemporal checking."""
        prose_fields = ["purpose", "scope", "overview"]
        prose_parts = []

        for field_name in prose_fields:
            if field_name in fields:
                prose_parts.append(f"{field_name}: {fields[field_name]}")

        return "\n".join(prose_parts)
