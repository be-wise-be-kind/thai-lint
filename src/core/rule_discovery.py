"""
Purpose: Automatic rule discovery for plugin-based linter architecture

Scope: Discovers and validates linting rules from Python packages

Overview: Provides automatic rule discovery functionality for the linter framework. Scans Python
    packages for classes inheriting from BaseLintRule, filters out abstract base classes, validates
    rule classes, and attempts instantiation. Handles import errors gracefully to support partial
    package installations. Enables plugin architecture by discovering rules without explicit registration.

Dependencies: importlib, inspect, pkgutil, BaseLintRule

Exports: discover_from_package function, RuleDiscovery class (compat)

Interfaces: discover_from_package(package_path) -> list[BaseLintRule]

Implementation: Package traversal with pkgutil, class introspection with inspect, error handling
"""

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Any

from .base import BaseLintRule


def discover_from_package(package_path: str) -> list[BaseLintRule]:
    """Discover rules from a package and its modules.

    Args:
        package_path: Python package path (e.g., 'src.linters')

    Returns:
        List of discovered rule instances
    """
    try:
        package = importlib.import_module(package_path)
    except ImportError:
        return []

    if not hasattr(package, "__path__"):
        return _discover_from_module(package_path)

    return _discover_from_package_modules(package_path, package)


def _discover_from_package_modules(package_path: str, package: Any) -> list[BaseLintRule]:
    """Discover rules from all modules in a package.

    Args:
        package_path: Package path
        package: Imported package object

    Returns:
        List of discovered rules
    """
    rules = []
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package_path}.{module_name}"
        module_rules = _try_discover_from_module(full_module_name)
        rules.extend(module_rules)
    return rules


def _try_discover_from_module(module_name: str) -> list[BaseLintRule]:
    """Try to discover rules from a module, return empty list on error.

    Args:
        module_name: Full module name

    Returns:
        List of discovered rules (empty on error)
    """
    try:
        return _discover_from_module(module_name)
    except (ImportError, AttributeError):
        return []


def _discover_from_module(module_path: str) -> list[BaseLintRule]:
    """Discover rules from a specific module.

    Args:
        module_path: Full module path to search

    Returns:
        List of discovered rule instances
    """
    module = _try_import_module(module_path)
    if module is None:
        return []
    return _extract_rules_from_module(module)


def _try_import_module(module_path: str) -> ModuleType | None:
    """Try to import a module, returning None on failure.

    Args:
        module_path: Full module path to import

    Returns:
        Module object or None if import fails
    """
    try:
        return importlib.import_module(module_path)
    except (ImportError, AttributeError):
        return None


def _extract_rules_from_module(module: ModuleType) -> list[BaseLintRule]:
    """Extract rule instances from a module.

    Args:
        module: Imported module to scan

    Returns:
        List of discovered rule instances
    """
    rule_classes = [obj for _name, obj in inspect.getmembers(module) if _is_rule_class(obj)]
    return _instantiate_rules(rule_classes)


def _instantiate_rules(rule_classes: list[type[BaseLintRule]]) -> list[BaseLintRule]:
    """Instantiate a list of rule classes.

    Args:
        rule_classes: List of rule classes to instantiate

    Returns:
        List of successfully instantiated rules
    """
    instances = (_try_instantiate_rule(cls) for cls in rule_classes)
    return [inst for inst in instances if inst is not None]


def _try_instantiate_rule(rule_class: type[BaseLintRule]) -> BaseLintRule | None:
    """Try to instantiate a rule class.

    Args:
        rule_class: Rule class to instantiate

    Returns:
        Rule instance or None on error
    """
    try:
        return rule_class()
    except (TypeError, AttributeError):
        return None


def _is_rule_class(obj: Any) -> bool:
    """Check if an object is a valid rule class.

    Args:
        obj: Object to check

    Returns:
        True if obj is a concrete BaseLintRule subclass
    """
    return (
        inspect.isclass(obj)
        and issubclass(obj, BaseLintRule)
        and obj is not BaseLintRule
        and not inspect.isabstract(obj)
    )


# Legacy class wrapper for backward compatibility
class RuleDiscovery:
    """Discovers linting rules from Python packages.

    Note: This class is a thin wrapper around module-level functions
    for backward compatibility.
    """

    def __init__(self) -> None:
        """Initialize the discovery service."""
        pass  # No state needed

    def discover_from_package(self, package_path: str) -> list[BaseLintRule]:
        """Discover rules from a package and its modules.

        Args:
            package_path: Python package path (e.g., 'src.linters')

        Returns:
            List of discovered rule instances
        """
        return discover_from_package(package_path)
