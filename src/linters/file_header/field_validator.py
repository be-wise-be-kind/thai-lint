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
        required_fields = self._get_required_fields(language)
        return [
            error
            for field_name in required_fields
            if (error := self._check_field(fields, field_name))
        ]

    def validate_tags(self, fields: dict[str, str]) -> list[str]:
        """Validate the optional Tags field against the allowed vocabulary.

        Args:
            fields: Dictionary of parsed header fields

        Returns:
            List of tag values that are not in the configured allowed_tags vocabulary.
            Empty when no Tags field is present or no vocabulary is configured.
        """
        if not self.config.allowed_tags:
            return []

        tags = self._parse_tag_list(fields.get("Tags", ""))
        return [tag for tag in tags if tag not in self.config.allowed_tags]

    def _parse_tag_list(self, raw_value: str) -> list[str]:
        """Split a comma-separated Tags value into stripped, non-empty tags."""
        return [tag.strip() for tag in raw_value.split(",") if tag.strip()]

    def _check_field(self, fields: dict[str, str], field_name: str) -> tuple[str, str] | None:
        """Check a single field for presence and content."""
        if field_name not in fields:
            return (field_name, f"Missing mandatory field: {field_name}")

        if not fields[field_name] or not fields[field_name].strip():
            return (field_name, f"Empty mandatory field: {field_name}")

        return None

    def _get_required_fields(self, language: str) -> list[str]:
        """Get required fields for language (javascript reuses the typescript set)."""
        normalized = "typescript" if language == "javascript" else language
        return self.config.required_fields_for(normalized)
