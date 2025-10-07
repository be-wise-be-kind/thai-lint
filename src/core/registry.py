"""
Purpose: Rule registry with automatic plugin discovery and registration

Scope: Dynamic rule management and discovery across all linter plugin packages

Overview: Implements the plugin discovery system that enables the extensible architecture by
    automatically finding and registering linting rules from specified packages without requiring
    explicit registration code. The RuleRegistry maintains a collection of discovered rules indexed
    by rule_id, providing methods to register individual rules, retrieve rules by identifier, and
    list all available rules. Auto-discovery works by scanning Python packages for classes that
    inherit from BaseLintRule, filtering out abstract base classes, instantiating concrete rule
    classes, and registering them for use by the orchestrator. This enables developers to add new
    rules simply by creating a class in the appropriate package structure without modifying any
    framework code. The registry handles import errors gracefully and supports both package-level
    and module-level discovery patterns.

Dependencies: importlib for dynamic module loading, inspect for class introspection,
    pkgutil for package traversal, BaseLintRule for type checking

Exports: RuleRegistry class with register(), get(), list_all(), and discover_rules() methods

Interfaces: register(rule: BaseLintRule) -> None, get(rule_id: str) -> BaseLintRule | None,
    list_all() -> list[BaseLintRule], discover_rules(package_path: str) -> int

Implementation: Package scanning with pkgutil.iter_modules(), class introspection with inspect,
    subclass detection for BaseLintRule, abstract class filtering, graceful error handling for
    failed imports, duplicate rule_id validation
"""

import importlib
import inspect
import pkgutil
from typing import Any

from .base import BaseLintRule


class RuleRegistry:
    """Registry for linting rules with auto-discovery.

    The registry maintains a collection of registered rules and provides
    methods to register, retrieve, and discover rules dynamically.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._rules: dict[str, BaseLintRule] = {}

    def register(self, rule: BaseLintRule) -> None:
        """Register a new rule.

        Args:
            rule: The rule instance to register.

        Raises:
            ValueError: If a rule with the same ID is already registered.
        """
        rule_id = rule.rule_id

        if rule_id in self._rules:
            raise ValueError(f"Rule {rule_id} already registered")

        self._rules[rule_id] = rule

    def get(self, rule_id: str) -> BaseLintRule | None:
        """Get a rule by ID.

        Args:
            rule_id: The unique identifier of the rule.

        Returns:
            The rule instance if found, None otherwise.
        """
        return self._rules.get(rule_id)

    def list_all(self) -> list[BaseLintRule]:
        """Get all registered rules.

        Returns:
            List of all registered rule instances.
        """
        return list(self._rules.values())

    def discover_rules(self, package_path: str) -> int:
        """Discover and register rules from a package.

        This method automatically discovers all concrete BaseLintRule
        subclasses in the specified package and registers them.

        Args:
            package_path: Python package path (e.g., 'src.linters').

        Returns:
            Number of rules discovered and registered.
        """
        discovered_count = 0

        try:
            # Import the package
            package = importlib.import_module(package_path)
        except ImportError:
            # Package doesn't exist or can't be imported
            return 0

        # Check if it's a package or single module
        if not hasattr(package, "__path__"):
            # Single module - try to discover from it directly
            return self._discover_from_module(package_path)

        # Walk through all modules in the package
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package_path}.{module_name}"
            try:
                discovered_count += self._discover_from_module(full_module_name)
            except (ImportError, AttributeError):
                # Skip modules that can't be imported
                continue

        return discovered_count

    def _discover_from_module(self, module_path: str) -> int:
        """Discover rules from a specific module.

        Args:
            module_path: Full module path to search.

        Returns:
            Number of rules discovered from this module.
        """
        discovered_count = 0

        try:
            module = importlib.import_module(module_path)
        except (ImportError, AttributeError):
            return 0

        # Look for rule classes in the module
        for _name, obj in inspect.getmembers(module):
            if not self._is_rule_class(obj):
                continue

            try:
                # Instantiate the rule
                rule_instance = obj()
                self.register(rule_instance)
                discovered_count += 1
            except (TypeError, AttributeError, ValueError):
                # Skip classes that can't be instantiated
                continue

        return discovered_count

    def _is_rule_class(self, obj: Any) -> bool:
        """Check if an object is a valid rule class.

        Args:
            obj: Object to check.

        Returns:
            True if obj is a concrete BaseLintRule subclass.
        """
        return (
            inspect.isclass(obj)
            and issubclass(obj, BaseLintRule)
            and obj is not BaseLintRule  # Don't instantiate the base class
            and not inspect.isabstract(obj)  # Don't instantiate abstract classes
        )
