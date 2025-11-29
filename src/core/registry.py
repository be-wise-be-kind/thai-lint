"""
Purpose: Rule registry with automatic plugin discovery and registration

Scope: Dynamic rule management and discovery across all linter plugin packages

Overview: Implements rule registry that maintains a collection of registered linting rules indexed
    by rule_id. Provides methods to register individual rules, retrieve rules by identifier, list
    all available rules, and discover rules from packages using the RuleDiscovery helper. Enables
    the extensible plugin architecture by allowing dynamic rule registration without framework
    modifications. Validates rule uniqueness and handles registration errors gracefully.

Dependencies: BaseLintRule, RuleDiscovery

Exports: RuleRegistry class with register(), get(), list_all(), and discover_rules() methods

Interfaces: register(rule: BaseLintRule) -> None, get(rule_id: str) -> BaseLintRule | None,
    list_all() -> list[BaseLintRule], discover_rules(package_path: str) -> int

Implementation: Dictionary-based registry with RuleDiscovery delegation, duplicate validation
"""

from .base import BaseLintRule
from .rule_discovery import RuleDiscovery


class RuleRegistry:
    """Registry for linting rules with auto-discovery.

    The registry maintains a collection of registered rules and provides
    methods to register, retrieve, and discover rules dynamically.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._rules: dict[str, BaseLintRule] = {}
        self._discovery = RuleDiscovery()

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
        discovered_rules = self._discovery.discover_from_package(package_path)
        return sum(1 for rule in discovered_rules if self._try_register(rule))

    def _try_register(self, rule: BaseLintRule) -> bool:
        """Try to register a rule, return True if successful."""
        try:
            self.register(rule)
            return True
        except ValueError:
            # Rule already registered, skip
            return False
