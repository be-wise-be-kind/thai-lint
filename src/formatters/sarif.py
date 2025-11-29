"""
Purpose: SARIF v2.1.0 formatter for converting Violation objects to SARIF JSON documents

Scope: SARIF document generation, tool metadata, result conversion, location mapping

Overview: Implements SarifFormatter class that converts thai-lint Violation objects to SARIF
    (Static Analysis Results Interchange Format) v2.1.0 compliant JSON documents. Produces
    output compatible with GitHub Code Scanning, Azure DevOps, VS Code SARIF Viewer, and
    other industry-standard static analysis tools. Handles proper field mapping including
    1-indexed column conversion, rule metadata deduplication, and tool versioning.

Dependencies: src (for __version__), src.core.types (Violation, Severity)

Exports: SarifFormatter class with format() method

Interfaces: SarifFormatter.format(violations: list[Violation]) -> dict

Implementation: Converts Violation objects to SARIF structure with proper indexing and metadata
"""

from typing import Any

from src import __version__
from src.core.types import Violation


class SarifFormatter:
    """Formats Violation objects as SARIF v2.1.0 JSON documents.

    SARIF (Static Analysis Results Interchange Format) is the OASIS standard
    for static analysis tool output, enabling integration with GitHub Code
    Scanning, Azure DevOps, and other CI/CD platforms.

    Attributes:
        tool_name: Name of the tool in SARIF output (default: "thai-lint")
        tool_version: Version string for the tool (default: package version)
        information_uri: URL for tool documentation
    """

    SARIF_VERSION = "2.1.0"
    SARIF_SCHEMA = (
        "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
        "main/sarif-2.1/schema/sarif-schema-2.1.0.json"
    )
    DEFAULT_INFORMATION_URI = "https://github.com/be-wise-be-kind/thai-lint"

    def __init__(
        self,
        tool_name: str = "thai-lint",
        tool_version: str | None = None,
        information_uri: str | None = None,
    ) -> None:
        """Initialize SarifFormatter with tool metadata.

        Args:
            tool_name: Name of the tool (default: "thai-lint")
            tool_version: Version string (default: package __version__)
            information_uri: URL for tool documentation
        """
        self.tool_name = tool_name
        self.tool_version = tool_version or __version__
        self.information_uri = information_uri or self.DEFAULT_INFORMATION_URI

    def format(self, violations: list[Violation]) -> dict[str, Any]:
        """Convert violations to SARIF v2.1.0 document.

        Args:
            violations: List of Violation objects to format

        Returns:
            SARIF v2.1.0 compliant dictionary ready for JSON serialization
        """
        return {
            "version": self.SARIF_VERSION,
            "$schema": self.SARIF_SCHEMA,
            "runs": [self._create_run(violations)],
        }

    def _create_run(self, violations: list[Violation]) -> dict[str, Any]:
        """Create a SARIF run object containing tool and results.

        Args:
            violations: List of violations for this run

        Returns:
            SARIF run object with tool and results
        """
        return {
            "tool": self._create_tool(violations),
            "results": [self._create_result(v) for v in violations],
        }

    def _create_tool(self, violations: list[Violation]) -> dict[str, Any]:
        """Create SARIF tool object with driver metadata.

        Args:
            violations: List of violations to extract rule metadata from

        Returns:
            SARIF tool object with driver
        """
        return {
            "driver": {
                "name": self.tool_name,
                "version": self.tool_version,
                "informationUri": self.information_uri,
                "rules": self._create_rules(violations),
            }
        }

    def _create_rules(self, violations: list[Violation]) -> list[dict[str, Any]]:
        """Create deduplicated SARIF rules array from violations.

        Args:
            violations: List of violations to extract unique rules from

        Returns:
            List of SARIF rule objects with unique IDs
        """
        seen_rule_ids: set[str] = set()
        rules: list[dict[str, Any]] = []

        for violation in violations:
            if violation.rule_id not in seen_rule_ids:
                seen_rule_ids.add(violation.rule_id)
                rules.append(self._create_rule(violation))

        return rules

    def _create_rule(self, violation: Violation) -> dict[str, Any]:
        """Create SARIF rule object from violation.

        Args:
            violation: Violation to extract rule metadata from

        Returns:
            SARIF rule object with id and shortDescription
        """
        # Extract rule category from rule_id (e.g., "nesting" from "nesting.excessive-depth")
        parts = violation.rule_id.split(".")
        category = parts[0] if parts else violation.rule_id

        descriptions: dict[str, str] = {
            "file-placement": "File placement violation",
            "nesting": "Nesting depth violation",
            "srp": "Single Responsibility Principle violation",
            "dry": "Don't Repeat Yourself violation",
            "magic-number": "Magic number violation",
            "magic-numbers": "Magic number violation",
            "file-header": "File header violation",
            "print-statements": "Print statement violation",
        }

        description = descriptions.get(category, f"Rule: {violation.rule_id}")

        return {
            "id": violation.rule_id,
            "shortDescription": {
                "text": description,
            },
        }

    def _create_result(self, violation: Violation) -> dict[str, Any]:
        """Create SARIF result object from violation.

        Args:
            violation: Violation to convert to SARIF result

        Returns:
            SARIF result object with ruleId, level, message, locations
        """
        # thai-lint uses binary severity (ERROR only), map all to "error" level
        return {
            "ruleId": violation.rule_id,
            "level": "error",
            "message": {
                "text": violation.message,
            },
            "locations": [self._create_location(violation)],
        }

    def _create_location(self, violation: Violation) -> dict[str, Any]:
        """Create SARIF location object from violation.

        Args:
            violation: Violation with location information

        Returns:
            SARIF location object with physicalLocation
        """
        return {
            "physicalLocation": {
                "artifactLocation": {
                    "uri": violation.file_path,
                },
                "region": {
                    "startLine": violation.line,
                    # SARIF uses 1-indexed columns, Violation uses 0-indexed
                    "startColumn": violation.column + 1,
                },
            }
        }
