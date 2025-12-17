"""
Purpose: Builds Violation objects for method-should-be-property detection

Scope: Violation creation for methods that should be @property decorators

Overview: Provides ViolationBuilder class that creates Violation objects for method-property
    detections. Generates descriptive messages indicating which methods should be converted to
    @property decorators, with special handling for get_* prefix methods (Java-style) that
    suggests removing the prefix. Constructs complete Violation instances with rule_id,
    file_path, line number, column, message, and suggestions for Pythonic refactoring.

Dependencies: pathlib.Path for file paths, src.core.types.Violation for violation structure

Exports: ViolationBuilder class

Interfaces: create_violation(method_name, line, column, file_path, is_get_prefix, class_name)

Implementation: Builder pattern with message templates suggesting @property decorator conversion
"""

from pathlib import Path

from src.core.types import Violation


class ViolationBuilder:
    """Builds violations for method-should-be-property detections."""

    def __init__(self, rule_id: str) -> None:
        """Initialize the violation builder.

        Args:
            rule_id: The rule ID to use in violations
        """
        self.rule_id = rule_id

    def create_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        method_name: str,
        line: int,
        column: int,
        file_path: Path | None,
        is_get_prefix: bool = False,
        class_name: str | None = None,
    ) -> Violation:
        """Create a violation for a method that should be a property.

        Args:
            method_name: Name of the method
            line: Line number where the violation occurs
            column: Column number where the violation occurs
            file_path: Path to the file
            is_get_prefix: Whether method has get_ prefix
            class_name: Optional class name for context

        Returns:
            Violation object with details about the method
        """
        message = self._build_message(method_name, is_get_prefix, class_name)
        suggestion = self._build_suggestion(method_name, is_get_prefix)

        return Violation(
            rule_id=self.rule_id,
            file_path=str(file_path) if file_path else "",
            line=line,
            column=column,
            message=message,
            suggestion=suggestion,
        )

    def _build_message(
        self,
        method_name: str,
        is_get_prefix: bool,
        class_name: str | None,
    ) -> str:
        """Build the violation message.

        Args:
            method_name: Name of the method
            is_get_prefix: Whether method has get_ prefix
            class_name: Optional class name

        Returns:
            Human-readable message describing the violation
        """
        if is_get_prefix:
            property_name = method_name[4:]  # Remove 'get_' prefix
            if class_name:
                return (
                    f"Method '{method_name}' in class '{class_name}' should be "
                    f"a @property named '{property_name}'"
                )
            return f"Method '{method_name}' should be a @property named '{property_name}'"

        if class_name:
            return f"Method '{method_name}' in class '{class_name}' should be a @property"
        return f"Method '{method_name}' should be a @property"

    def _build_suggestion(self, method_name: str, is_get_prefix: bool) -> str:
        """Build the suggestion for fixing the violation.

        Args:
            method_name: Name of the method
            is_get_prefix: Whether method has get_ prefix

        Returns:
            Actionable suggestion for fixing
        """
        if is_get_prefix:
            property_name = method_name[4:]  # Remove 'get_' prefix
            return (
                f"Add @property decorator and rename to '{property_name}' "
                f"for Pythonic attribute access"
            )
        return "Add @property decorator for Pythonic attribute access"
