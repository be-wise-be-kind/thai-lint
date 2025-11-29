"""
Purpose: Validates mandatory fields in file headers

Scope: File header field validation for all supported languages

Overview: Validates presence and quality of mandatory header fields. Checks that all
    required fields are present, non-empty, and meet minimum content requirements.
    Supports language-specific required fields and provides detailed violation messages
    for missing or empty fields. Uses configuration-driven validation to support
    different field requirements per language type.

Dependencies: FileHeaderConfig for language-specific field requirements

Exports: FieldValidator class

Interfaces: validate_fields(fields, language) -> list[tuple[str, str]] returns field violations

Implementation: Configuration-driven validation with field presence and emptiness checking
"""

from .config import FileHeaderConfig


class FieldValidator:
    """Validates mandatory fields in headers."""

    def __init__(self, config: FileHeaderConfig):
        """Initialize validator with configuration.

        Args:
            config: File header configuration with required fields
        """
        self.config = config

    def validate_fields(self, fields: dict[str, str], language: str) -> list[tuple[str, str]]:
        """Validate all required fields are present.

        Args:
            fields: Dictionary of parsed header fields
            language: File language (python, typescript, etc.)

        Returns:
            List of (field_name, error_message) tuples for missing/invalid fields
        """
        violations = []
        required_fields = self._get_required_fields(language)

        for field_name in required_fields:
            error = self._check_field(fields, field_name)
            if error:
                violations.append(error)

        return violations

    def _check_field(self, fields: dict[str, str], field_name: str) -> tuple[str, str] | None:
        """Check a single field for presence and content."""
        if field_name not in fields:
            return (field_name, f"Missing mandatory field: {field_name}")

        if not fields[field_name] or not fields[field_name].strip():
            return (field_name, f"Empty mandatory field: {field_name}")

        return None

    def _get_required_fields(self, language: str) -> list[str]:
        """Get required fields for language using dictionary lookup."""
        language_fields = {
            "python": self.config.required_fields_python,
            "typescript": self.config.required_fields_typescript,
            "javascript": self.config.required_fields_typescript,
            "bash": self.config.required_fields_bash,
            "markdown": self.config.required_fields_markdown,
            "css": self.config.required_fields_css,
        }
        return language_fields.get(language, [])
