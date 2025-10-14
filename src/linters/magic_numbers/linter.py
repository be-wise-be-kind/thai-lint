"""
Purpose: Main magic numbers linter rule implementation

Scope: MagicNumberRule class implementing BaseLintRule interface

Overview: Implements magic numbers linter rule following BaseLintRule interface. Orchestrates
    configuration loading, Python AST analysis, context detection, and violation building through
    focused helper classes. Detects numeric literals that should be extracted to named constants.
    Supports configurable allowed_numbers set and max_small_integer threshold. Handles ignore
    directives for suppressing specific violations. Main rule class acts as coordinator for magic
    number checking workflow across Python code files. Method count (17) exceeds SRP limit (8)
    because refactoring for A-grade complexity requires extracting helper methods. Class maintains
    single responsibility of magic number detection - all methods support this core purpose.

Dependencies: BaseLintRule, BaseLintContext, PythonMagicNumberAnalyzer, ContextAnalyzer,
    ViolationBuilder, MagicNumberConfig, IgnoreDirectiveParser

Exports: MagicNumberRule class

Interfaces: MagicNumberRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Composition pattern with helper classes, AST-based analysis with configurable
    allowed numbers and context detection
"""

import ast
from pathlib import Path

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import MagicNumberConfig
from .context_analyzer import ContextAnalyzer
from .python_analyzer import PythonMagicNumberAnalyzer
from .typescript_analyzer import TypeScriptMagicNumberAnalyzer
from .violation_builder import ViolationBuilder


class MagicNumberRule(MultiLanguageLintRule):  # thailint: ignore[srp]
    """Detects magic numbers that should be replaced with named constants."""

    def __init__(self) -> None:
        """Initialize the magic numbers rule."""
        self._ignore_parser = IgnoreDirectiveParser()
        self._violation_builder = ViolationBuilder(self.rule_id)
        self._context_analyzer = ContextAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "magic-numbers.numeric-literal"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Magic Numbers"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Numeric literals should be replaced with named constants for better maintainability"

    def _load_config(self, context: BaseLintContext) -> MagicNumberConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            MagicNumberConfig instance
        """
        # Try test-style config first
        test_config = self._try_load_test_config(context)
        if test_config is not None:
            return test_config

        # Try production config
        prod_config = self._try_load_production_config(context)
        if prod_config is not None:
            return prod_config

        # Use defaults
        return MagicNumberConfig()

    def _try_load_test_config(self, context: BaseLintContext) -> MagicNumberConfig | None:
        """Try to load test-style configuration."""
        if not hasattr(context, "config"):
            return None
        config_attr = context.config
        if config_attr is None or not isinstance(config_attr, dict):
            return None
        return MagicNumberConfig.from_dict(config_attr, context.language)

    def _try_load_production_config(self, context: BaseLintContext) -> MagicNumberConfig | None:
        """Try to load production configuration."""
        if not hasattr(context, "metadata") or not isinstance(context.metadata, dict):
            return None

        # Try both hyphenated and underscored keys for backward compatibility
        # The config parser normalizes keys when loading from YAML, but
        # direct metadata injection (tests) may use either format
        metadata = context.metadata

        # Try underscore version first (normalized format)
        if "magic_numbers" in metadata:
            return load_linter_config(context, "magic_numbers", MagicNumberConfig)

        # Fallback to hyphenated version (for direct test injection)
        if "magic-numbers" in metadata:
            return load_linter_config(context, "magic-numbers", MagicNumberConfig)

        # No config found, return None to use defaults
        return None

    def _is_file_ignored(self, context: BaseLintContext, config: MagicNumberConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: Magic numbers configuration

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

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file path matches a glob pattern.

        Args:
            file_path: Path to check
            pattern: Glob pattern (e.g., "test/**", "**/test_*.py", "specific/file.py")

        Returns:
            True if path matches pattern
        """
        # Try glob pattern matching first (handles **, *, etc.)
        if file_path.match(pattern):
            return True

        # Also check if pattern is a substring (for partial path matching)
        if pattern in str(file_path):
            return True

        return False

    def _check_python(self, context: BaseLintContext, config: MagicNumberConfig) -> list[Violation]:
        """Check Python code for magic number violations.

        Args:
            context: Lint context with Python file information
            config: Magic numbers configuration

        Returns:
            List of violations found in Python code
        """
        if self._is_file_ignored(context, config):
            return []

        tree = self._parse_python_code(context.file_content)
        if tree is None:
            return []

        numeric_literals = self._find_numeric_literals(tree)
        return self._collect_violations(numeric_literals, context, config)

    def _parse_python_code(self, code: str | None) -> ast.AST | None:
        """Parse Python code into AST."""
        try:
            return ast.parse(code or "")
        except SyntaxError:
            return None

    def _find_numeric_literals(self, tree: ast.AST) -> list:
        """Find all numeric literals in AST."""
        analyzer = PythonMagicNumberAnalyzer()
        return analyzer.find_numeric_literals(tree)

    def _collect_violations(
        self, numeric_literals: list, context: BaseLintContext, config: MagicNumberConfig
    ) -> list[Violation]:
        """Collect violations from numeric literals."""
        violations = []
        for literal_info in numeric_literals:
            violation = self._try_create_violation(literal_info, context, config)
            if violation is not None:
                violations.append(violation)
        return violations

    def _try_create_violation(
        self, literal_info: tuple, context: BaseLintContext, config: MagicNumberConfig
    ) -> Violation | None:
        """Try to create a violation for a numeric literal.

        Args:
            literal_info: Tuple of (node, parent, value, line_number)
            context: Lint context
            config: Configuration
        """
        node, parent, value, line_number = literal_info
        if not self._should_flag_number(value, (node, parent), config, context):
            return None

        violation = self._violation_builder.create_violation(
            node, value, line_number, context.file_path
        )
        if self._should_ignore(violation, context):
            return None

        return violation

    def _should_flag_number(
        self,
        value: int | float,
        node_info: tuple[ast.Constant, ast.AST | None],
        config: MagicNumberConfig,
        context: BaseLintContext,
    ) -> bool:
        """Determine if a number should be flagged as a magic number.

        Args:
            value: The numeric value
            node_info: Tuple of (node, parent) AST nodes
            config: Configuration
            context: Lint context

        Returns:
            True if the number should be flagged
        """
        if value in config.allowed_numbers:
            return False

        node, parent = node_info
        config_dict = {
            "max_small_integer": config.max_small_integer,
            "allowed_numbers": config.allowed_numbers,
        }

        if self._context_analyzer.is_acceptable_context(
            node, parent, context.file_path, config_dict
        ):
            return False

        return True

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored based on inline directives.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be ignored
        """
        # Check using standard ignore parser
        if self._ignore_parser.should_ignore_violation(violation, context.file_content or ""):
            return True

        # Workaround for generic ignore directives
        return self._check_generic_ignore(violation, context)

    def _check_generic_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check for generic ignore directives (workaround for parser limitation).

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if line has generic ignore directive
        """
        line_text = self._get_violation_line(violation, context)
        if line_text is None:
            return False

        return self._has_generic_ignore_directive(line_text)

    def _get_violation_line(self, violation: Violation, context: BaseLintContext) -> str | None:
        """Get the line text for a violation."""
        if not context.file_content:
            return None

        lines = context.file_content.splitlines()
        if violation.line <= 0 or violation.line > len(lines):
            return None

        return lines[violation.line - 1].lower()

    def _has_generic_ignore_directive(self, line_text: str) -> bool:
        """Check if line has generic ignore directive."""
        if self._has_generic_thailint_ignore(line_text):
            return True
        return self._has_noqa_directive(line_text)

    def _has_generic_thailint_ignore(self, line_text: str) -> bool:
        """Check for generic thailint: ignore (no brackets)."""
        if "# thailint: ignore" not in line_text:
            return False
        after_ignore = line_text.split("# thailint: ignore")[1].split("#")[0]
        return "[" not in after_ignore

    def _has_noqa_directive(self, line_text: str) -> bool:
        """Check for noqa-style comments."""
        return "# noqa" in line_text

    def _check_typescript(
        self, context: BaseLintContext, config: MagicNumberConfig
    ) -> list[Violation]:
        """Check TypeScript/JavaScript code for magic number violations.

        Args:
            context: Lint context with TypeScript/JavaScript file information
            config: Magic numbers configuration

        Returns:
            List of violations found in TypeScript/JavaScript code
        """
        if self._is_file_ignored(context, config):
            return []

        analyzer = TypeScriptMagicNumberAnalyzer()
        root_node = analyzer.parse_typescript(context.file_content or "")
        if root_node is None:
            return []

        numeric_literals = analyzer.find_numeric_literals(root_node)
        return self._collect_typescript_violations(numeric_literals, context, config, analyzer)

    def _collect_typescript_violations(
        self,
        numeric_literals: list,
        context: BaseLintContext,
        config: MagicNumberConfig,
        analyzer: TypeScriptMagicNumberAnalyzer,
    ) -> list[Violation]:
        """Collect violations from TypeScript numeric literals.

        Args:
            numeric_literals: List of (node, value, line_number) tuples
            context: Lint context
            config: Configuration
            analyzer: TypeScript analyzer instance

        Returns:
            List of violations
        """
        violations = []
        for node, value, line_number in numeric_literals:
            violation = self._try_create_typescript_violation(
                node, value, line_number, context, config, analyzer
            )
            if violation is not None:
                violations.append(violation)
        return violations

    def _try_create_typescript_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        node: object,
        value: float | int,
        line_number: int,
        context: BaseLintContext,
        config: MagicNumberConfig,
        analyzer: TypeScriptMagicNumberAnalyzer,
    ) -> Violation | None:
        """Try to create a violation for a TypeScript numeric literal.

        Args:
            node: Tree-sitter node
            value: Numeric value
            line_number: Line number of literal
            context: Lint context
            config: Configuration
            analyzer: TypeScript analyzer

        Returns:
            Violation or None if should not flag
        """
        if not self._should_flag_typescript_number(node, value, context, config, analyzer):
            return None

        violation = self._violation_builder.create_typescript_violation(
            value, line_number, context.file_path
        )
        if self._should_ignore_typescript(violation, context):
            return None

        return violation

    def _should_flag_typescript_number(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        node: object,
        value: float | int,
        context: BaseLintContext,
        config: MagicNumberConfig,
        analyzer: TypeScriptMagicNumberAnalyzer,
    ) -> bool:
        """Determine if a TypeScript number should be flagged.

        Args:
            node: Tree-sitter node
            value: Numeric value
            context: Lint context
            config: Configuration
            analyzer: TypeScript analyzer

        Returns:
            True if should flag as magic number
        """
        # Early return for allowed contexts
        if self._is_typescript_allowed_context(value, context, config):
            return False

        # Check TypeScript-specific contexts
        return not self._is_typescript_special_context(node, analyzer, context)

    def _is_typescript_allowed_context(
        self, value: float | int, context: BaseLintContext, config: MagicNumberConfig
    ) -> bool:
        """Check if number is in allowed context."""
        return value in config.allowed_numbers or self._is_test_file(context.file_path)

    def _is_typescript_special_context(
        self, node: object, analyzer: TypeScriptMagicNumberAnalyzer, context: BaseLintContext
    ) -> bool:
        """Check if in TypeScript-specific special context."""
        # Calls require type: ignore because node is typed as object but analyzer expects Node
        in_enum = analyzer.is_enum_context(node)  # type: ignore[arg-type]
        in_const_def = analyzer.is_constant_definition(node, context.file_content or "")  # type: ignore[arg-type]
        return in_enum or in_const_def

    def _is_test_file(self, file_path: object) -> bool:
        """Check if file is a test file.

        Args:
            file_path: Path to check

        Returns:
            True if test file
        """
        path_str = str(file_path)
        return any(
            pattern in path_str
            for pattern in [".test.", ".spec.", "test_", "_test.", "/tests/", "/test/"]
        )

    def _should_ignore_typescript(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if TypeScript violation should be ignored.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if should ignore
        """
        # Check standard ignore directives
        if self._ignore_parser.should_ignore_violation(violation, context.file_content or ""):
            return True

        # Check TypeScript-style comments
        return self._check_typescript_ignore(violation, context)

    def _check_typescript_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check for TypeScript-style ignore directives.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if line has ignore directive
        """
        line_text = self._get_violation_line(violation, context)
        if line_text is None:
            return False

        # Check for // thailint: ignore or // noqa
        return self._has_typescript_ignore_directive(line_text)

    def _has_typescript_ignore_directive(self, line_text: str) -> bool:
        """Check if line has TypeScript-style ignore directive.

        Args:
            line_text: Line text to check

        Returns:
            True if has ignore directive
        """
        # Check for // thailint: ignore[magic-numbers]
        if "// thailint: ignore[magic-numbers]" in line_text:
            return True

        # Check for // thailint: ignore (generic)
        if "// thailint: ignore" in line_text:
            after_ignore = line_text.split("// thailint: ignore")[1].split("//")[0]
            if "[" not in after_ignore:
                return True

        # Check for // noqa
        if "// noqa" in line_text:
            return True

        return False
