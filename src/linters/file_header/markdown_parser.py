"""
Purpose: Markdown YAML frontmatter extraction and parsing

Scope: Markdown file header parsing from YAML frontmatter

Overview: Extracts YAML frontmatter from Markdown files. Frontmatter must be at the
    start of the file, enclosed in --- markers. Parses YAML content to extract
    field values using PyYAML when available, falling back to regex parsing if not.
    Handles both simple key-value pairs and complex YAML structures including lists.
    Flattens nested structures into string representations for field validation.

Dependencies: re module for frontmatter pattern matching, yaml module (optional) for parsing, logging module

Exports: MarkdownHeaderParser class

Interfaces: extract_header(code) -> str | None for frontmatter extraction,
    parse_fields(header) -> dict[str, str] for field parsing

Implementation: YAML frontmatter extraction with PyYAML parsing and regex fallback for robustness
"""

import logging
import re

logger = logging.getLogger(__name__)


class MarkdownHeaderParser:  # thailint: ignore[srp]
    """Extracts and parses Markdown file headers from YAML frontmatter.

    Method count (10) exceeds SRP guideline (8) because proper A-grade complexity
    refactoring requires extracting small focused helper methods. Class maintains
    single responsibility of YAML frontmatter parsing - all methods support this
    core purpose through either PyYAML or simple regex parsing fallback.
    """

    # Pattern to match YAML frontmatter at start of file
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

    def extract_header(self, code: str) -> str | None:
        """Extract YAML frontmatter from Markdown file."""
        if not code or not code.strip():
            return None

        match = self.FRONTMATTER_PATTERN.match(code)
        return match.group(1).strip() if match else None

    def parse_fields(self, header: str) -> dict[str, str]:
        """Parse YAML frontmatter into field dictionary."""
        yaml_result = self._try_yaml_parse(header)
        if yaml_result is not None:
            return yaml_result

        return self._parse_simple_yaml(header)

    def _try_yaml_parse(self, header: str) -> dict[str, str] | None:
        """Try to parse with PyYAML, returning None if unavailable or failed."""
        try:
            import yaml

            data = yaml.safe_load(header)
            if isinstance(data, dict):
                return self._flatten_yaml_dict(data)
        except ImportError:
            logger.debug("PyYAML not available, using simple parser")
        except Exception:  # noqa: BLE001
            logger.debug("YAML parsing failed, falling back to simple parser")
        return None

    def _flatten_yaml_dict(self, data: dict) -> dict[str, str]:
        """Convert YAML dict to string values."""
        result: dict[str, str] = {}
        for key, value in data.items():
            result[str(key)] = self._convert_value(value)
        return result

    def _convert_value(self, value: object) -> str:
        """Convert a single YAML value to string."""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        if value is not None:
            return str(value)
        return ""

    def _parse_simple_yaml(  # thailint: ignore[nesting,dry]
        self, header: str
    ) -> dict[str, str]:
        """Simple regex-based YAML parsing fallback."""
        fields: dict[str, str] = {}
        current_field: str | None = None
        current_value: list[str] = []

        for line in header.split("\n"):
            if self._is_field_start(line):
                self._save_field(fields, current_field, current_value)
                current_field, current_value = self._start_field(line)
            elif current_field and line.strip():
                current_value.append(self._process_continuation(line))

        self._save_field(fields, current_field, current_value)
        return fields

    def _is_field_start(self, line: str) -> bool:
        """Check if line starts a new field (not indented, has colon)."""
        return not line.startswith(" ") and ":" in line

    def _start_field(self, line: str) -> tuple[str, list[str]]:
        """Parse field start and return field name and initial value."""
        parts = line.split(":", 1)
        field_name = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else ""
        return field_name, [value] if value else []

    def _process_continuation(self, line: str) -> str:
        """Process a continuation line (list item or multiline value)."""
        stripped = line.strip()
        return stripped[2:] if stripped.startswith("- ") else stripped

    def _save_field(
        self, fields: dict[str, str], field_name: str | None, values: list[str]
    ) -> None:
        """Save field to dictionary if field name exists."""
        if field_name:
            fields[field_name] = "\n".join(values).strip()
