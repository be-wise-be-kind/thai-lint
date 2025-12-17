"""
Purpose: Package exports for method-should-be-property linter

Scope: Method property linter public API

Overview: Exports the MethodPropertyRule class and MethodPropertyConfig dataclass for use by
    the orchestrator and external consumers. Provides a convenience lint() function for
    standalone usage of the linter.

Dependencies: MethodPropertyRule from linter module, MethodPropertyConfig from config module

Exports: MethodPropertyRule, MethodPropertyConfig, lint function

Interfaces: lint(file_path, content, config) -> list[Violation] convenience function

Implementation: Simple re-exports from submodules with optional convenience wrapper
"""

from .config import MethodPropertyConfig
from .linter import MethodPropertyRule

__all__ = ["MethodPropertyRule", "MethodPropertyConfig", "lint"]


def lint(
    file_path: str,
    content: str,
    config: dict | None = None,
) -> list:
    """Lint a file for method-should-be-property violations.

    Args:
        file_path: Path to the file being linted
        content: Content of the file
        config: Optional configuration dictionary

    Returns:
        List of Violation objects
    """
    from unittest.mock import Mock

    rule = MethodPropertyRule()
    context = Mock()
    context.file_path = file_path
    context.file_content = content
    context.language = "python"
    context.config = config

    return rule.check(context)
