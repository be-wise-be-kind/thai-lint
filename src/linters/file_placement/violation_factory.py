"""
Purpose: Violation creation with helpful suggestions for file placement linter

Scope: Creates Violation objects with contextual messages and actionable suggestions

Overview: Provides violation creation functionality for the file placement linter. Generates
    descriptive error messages, creates helpful suggestions based on file type and location,
    and encapsulates all violation construction logic. Separates violation building from
    rule checking to maintain single responsibility and improve message consistency.

Dependencies: pathlib, src.core.types (Violation, Severity), src.core.violation_builder

Exports: ViolationFactory

Interfaces: create_deny_violation, create_allow_violation, create_global_deny_violation

Implementation: Uses file extension and name patterns to generate context-aware suggestions,
    extends BaseViolationBuilder for consistent violation construction
"""

from pathlib import Path

from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder


class ViolationFactory(BaseViolationBuilder):
    """Creates violations with helpful suggestions for file placement linter."""

    # Suggestion lookup by file type
    _SUGGESTIONS = {
        "test": "Move to tests/ directory",
        "component": "Move to src/components/",
        "source": "Move to src/",
        "temp": "Move to debug/logs/ or add to .gitignore",
    }
    _DEFAULT_SUGGESTION = "Review file organization and move to appropriate directory"

    def create_deny_violation(self, rel_path: Path, matched_path: str, reason: str) -> Violation:
        """Create violation for denied file.

        Args:
            rel_path: Relative path to file
            matched_path: Directory path that matched
            reason: Reason file is denied

        Returns:
            Violation with message and suggestion
        """
        message = f"File '{rel_path}' not allowed in {matched_path}: {reason}"
        suggestion = self._get_suggestion(rel_path.name)
        return self.build_from_params(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def create_allow_violation(self, rel_path: Path, matched_path: str) -> Violation:
        """Create violation for file not matching allow patterns.

        Args:
            rel_path: Relative path to file
            matched_path: Directory path that matched

        Returns:
            Violation with message and suggestion
        """
        message = f"File '{rel_path}' does not match allowed patterns for {matched_path}"
        suggestion = f"Move to {matched_path} or ensure file type is allowed"
        return self.build_from_params(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def create_global_deny_violation(self, rel_path: Path, reason: str | None) -> Violation:
        """Create violation for global deny pattern match.

        Args:
            rel_path: Relative path to file
            reason: Reason file is denied (optional)

        Returns:
            Violation with message and suggestion
        """
        message = reason or f"File '{rel_path}' matches denied pattern"
        suggestion = self._get_suggestion(rel_path.name)
        return self.build_from_params(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def create_global_allow_violation(self, rel_path: Path) -> Violation:
        """Create violation for file not matching global allow patterns.

        Args:
            rel_path: Relative path to file

        Returns:
            Violation with message and suggestion
        """
        message = f"File '{rel_path}' does not match any allowed patterns"
        suggestion = "Ensure file matches project structure patterns"
        return self.build_from_params(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def _is_temp_file(self, filename: str) -> bool:
        """Check if file is a temporary or utility file.

        Args:
            filename: File name

        Returns:
            True if file is temporary/utility file
        """
        return filename.startswith(("debug", "temp")) or filename.endswith(".log")

    def _classify_file_type(self, filename: str) -> str | None:
        """Classify file type based on filename patterns.

        Args:
            filename: File name

        Returns:
            File type classification key, or None if no pattern matches
        """
        filename_lower = filename.lower()

        # Check keyword-based patterns
        if "test" in filename_lower:
            return "test"
        if "component" in filename_lower:
            return "component"

        # Check extension-based patterns
        if filename.endswith((".ts", ".tsx", ".jsx", ".py")):
            return "source"

        # Check temp/utility patterns
        if self._is_temp_file(filename):
            return "temp"

        return None

    def _get_suggestion(self, filename: str) -> str:
        """Get suggestion for file placement based on filename patterns.

        Args:
            filename: File name

        Returns:
            Suggestion string with actionable guidance
        """
        file_type = self._classify_file_type(filename)
        if file_type is None:
            return self._DEFAULT_SUGGESTION
        return self._SUGGESTIONS.get(file_type, self._DEFAULT_SUGGESTION)
