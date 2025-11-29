"""
Purpose: SARIF formatter package for thai-lint output

Scope: SARIF v2.1.0 formatter implementation and package exports

Overview: Formatters package providing SARIF (Static Analysis Results Interchange Format) v2.1.0
    output generation from thai-lint Violation objects. Enables integration with GitHub Code
    Scanning, Azure DevOps, VS Code SARIF Viewer, and other industry-standard CI/CD platforms.
    Provides the SarifFormatter class for converting violations to SARIF JSON documents.

Dependencies: sarif module for SarifFormatter class

Exports: SarifFormatter class from sarif.py module

Interfaces: from src.formatters.sarif import SarifFormatter

Implementation: Package initialization with SarifFormatter export
"""

from src.formatters.sarif import SarifFormatter

__all__ = ["SarifFormatter"]
