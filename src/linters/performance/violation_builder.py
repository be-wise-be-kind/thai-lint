"""
Purpose: Violation creation for performance linter rules

Scope: Builds Violation objects for string-concat-loop and regex-in-loop rules

Overview: Provides violation building functionality for the performance linter. Creates
    violations for string concatenation in loops with contextual error messages,
    variable names, and actionable refactoring suggestions (use join(), list comprehension).
    Handles syntax errors gracefully. Isolates violation construction from analysis logic.

Dependencies: BaseLintContext, Violation, Severity, PerformanceConfig, src.core.violation_builder

Exports: PerformanceViolationBuilder

Interfaces: create_string_concat_violation, create_syntax_error_violation

Implementation: Formats messages with variable names, provides targeted refactoring suggestions,
    extends BaseViolationBuilder for consistent violation construction

Suppressions:
    - too-many-arguments,too-many-positional-arguments: Violation builder methods inherently
      require multiple parameters (variable_name, line, column, loop_type, context)
"""

from src.core.base import BaseLintContext
from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder


class PerformanceViolationBuilder(BaseViolationBuilder):
    """Builds violations for performance issues."""

    def __init__(self, rule_id: str):
        """Initialize violation builder.

        Args:
            rule_id: Rule identifier for violations
        """
        self.rule_id = rule_id

    def create_syntax_error_violation(
        self, error: SyntaxError, context: BaseLintContext
    ) -> Violation:
        """Create violation for syntax error.

        Args:
            error: SyntaxError exception
            context: Lint context

        Returns:
            Syntax error violation
        """
        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=error.lineno or 0,
            column=error.offset or 0,
            message=f"Syntax error: {error.msg}",
            severity=Severity.ERROR,
            suggestion="Fix syntax errors before checking for performance issues",
        )

    def create_string_concat_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        variable_name: str,
        line_number: int,
        column: int,
        loop_type: str,
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for string concatenation in loop.

        Args:
            variable_name: Name of the variable being concatenated
            line_number: Line number of the violation
            column: Column number of the violation
            loop_type: Type of loop ('for' or 'while')
            context: Lint context

        Returns:
            String concat in loop violation
        """
        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=line_number,
            column=column,
            message=(
                f"String concatenation in {loop_type} loop: '{variable_name} +=' "
                f"creates O(n²) complexity"
            ),
            severity=Severity.ERROR,
            suggestion=self._generate_suggestion(variable_name),
        )

    def _generate_suggestion(self, variable_name: str) -> str:
        """Generate refactoring suggestion for string concatenation.

        Args:
            variable_name: Variable being concatenated

        Returns:
            Suggestion string with refactoring advice
        """
        return (
            f"Use ''.join() with a list comprehension or generator instead of "
            f"repeatedly concatenating to '{variable_name}'. "
            f"Example: {variable_name} = ''.join(items) or "
            f"{variable_name} = ''.join(str(x) for x in items)"
        )

    def create_regex_in_loop_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        method_name: str,
        line_number: int,
        column: int,
        loop_type: str,
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for regex function call in loop.

        Args:
            method_name: Name of the regex method (e.g., 're.match', 'search')
            line_number: Line number of the violation
            column: Column number of the violation
            loop_type: Type of loop ('for' or 'while')
            context: Lint context

        Returns:
            Regex in loop violation
        """
        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=line_number,
            column=column,
            message=(
                f"Regex compilation in {loop_type} loop: '{method_name}()' "
                f"recompiles pattern on each iteration"
            ),
            severity=Severity.ERROR,
            suggestion=self._generate_regex_suggestion(method_name),
        )

    def _generate_regex_suggestion(self, method_name: str) -> str:
        """Generate refactoring suggestion for regex in loop.

        Args:
            method_name: Regex method being called

        Returns:
            Suggestion string with refactoring advice
        """
        # Extract just the method name if prefixed with 're.'
        base_method = method_name.split(".")[-1]
        return (
            f"Compile the pattern once outside the loop using re.compile(), "
            f"then use pattern.{base_method}() inside the loop. "
            f"Example: pattern = re.compile(r'...'); pattern.{base_method}(text)"
        )
