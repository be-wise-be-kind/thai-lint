"""
File: src/linters/file_header/field_validator.py
Purpose: Validates mandatory fields in file headers
Exports: FieldValidator class
Depends: FileHeaderConfig for field requirements
Implements: Configuration-driven validation with field presence checking
Related: linter.py for validator usage, config.py for configuration

Overview:
    Validates presence and quality of mandatory header fields. Checks that all
    required fields are present, non-empty, and meet minimum content requirements.
    Supports language-specific required fields and provides detailed violation messages.

Usage:
    validator = FieldValidator(config)
    violations = validator.validate_fields(fields, "python")

Notes: Language-specific field requirements defined in config
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

    def validate_fields(  # thailint: ignore[nesting]
        self, fields: dict[str, str], language: str
    ) -> list[tuple[str, str]]:
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
            if field_name not in fields:
                violations.append((field_name, f"Missing mandatory field: {field_name}"))
            elif not fields[field_name] or len(fields[field_name].strip()) == 0:
                violations.append((field_name, f"Empty mandatory field: {field_name}"))

        return violations

    def _get_required_fields(self, language: str) -> list[str]:
        """Get required fields for language.

        Args:
            language: Programming language

        Returns:
            List of required field names for the language
        """
        if language == "python":
            return self.config.required_fields_python
        return []  # Other languages in PR5
