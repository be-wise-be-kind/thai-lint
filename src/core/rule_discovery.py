"""
Purpose: Automatic rule discovery for plugin-based linter architecture

Scope: Discovers and validates linting rules from Python packages

Overview: Provides automatic rule discovery functionality for the linter framework. Scans Python
    packages for classes inheriting from BaseLintRule, filters out abstract base classes, validates
    rule classes, and attempts instantiation. Handles import errors gracefully to support partial
    package installations. Enables plugin architecture by discovering rules without explicit registration.

Dependencies: importlib, inspect, pkgutil, BaseLintRule

Exports: RuleDiscovery

Interfaces: discover_from_package(package_path) -> list[BaseLintRule]

Implementation: Package traversal with pkgutil, class introspection with inspect, error handling
"""

import importlib
import inspect
import pkgutil
from typing import Any

from .base import BaseLintRule


class RuleDiscovery:
    """Discovers linting rules from Python packages."""

    def discover_from_package(self, package_path: str) -> list[BaseLintRule]:
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
            return self._discover_from_module(package_path)

        return self._discover_from_package_modules(package_path, package)

    def _discover_from_package_modules(self, package_path: str, package: Any) -> list[BaseLintRule]:
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
            module_rules = self._try_discover_from_module(full_module_name)
            rules.extend(module_rules)
        return rules

    def _try_discover_from_module(self, module_name: str) -> list[BaseLintRule]:
        """Try to discover rules from a module, return empty list on error.

        Args:
            module_name: Full module name

        Returns:
            List of discovered rules (empty on error)
        """
        try:
            return self._discover_from_module(module_name)
        except (ImportError, AttributeError):
            return []

    def _discover_from_module(self, module_path: str) -> list[BaseLintRule]:
        """Discover rules from a specific module.

        Args:
            module_path: Full module path to search

        Returns:
            List of discovered rule instances
        """
        try:
            module = importlib.import_module(module_path)
        except (ImportError, AttributeError):
            return []

        rules = []
        for _name, obj in inspect.getmembers(module):
            if not self._is_rule_class(obj):
                continue
            rule_instance = self._try_instantiate_rule(obj)
            if rule_instance:
                rules.append(rule_instance)
        return rules

    def _try_instantiate_rule(self, rule_class: type[BaseLintRule]) -> BaseLintRule | None:
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

    def _is_rule_class(self, obj: Any) -> bool:
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
