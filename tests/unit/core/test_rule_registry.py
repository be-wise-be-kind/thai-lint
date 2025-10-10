"""
Purpose: Test suite for rule registry and automatic plugin discovery system

Scope: Validation of RuleRegistry registration, retrieval, and auto-discovery functionality

Overview: Validates the dynamic rule discovery and registration system that enables the plugin
    architecture, ensuring rules can be registered, retrieved, and discovered automatically from
    packages without manual registration code. Tests cover rule registration with duplicate ID
    detection, rule retrieval by identifier, listing all registered rules, and automatic discovery
    from Python packages. Verifies that auto-discovery correctly identifies BaseLintRule subclasses,
    filters out abstract base classes, skips non-rule classes, and handles import errors gracefully.
    Ensures the registry enables the extensible plugin system where new rules can be added simply
    by creating classes in the appropriate package structure.

Dependencies: pytest for testing framework, pathlib for temporary directory creation,
    tmp_path fixture for isolated test environments

Exports: TestRuleRegistry, TestRuleDiscovery test classes

Interfaces: Tests register(), get(), list_all(), discover_rules() methods, validates rule
    filtering logic and error handling paths

Implementation: 9 tests using pytest fixtures for temporary packages, dynamic module creation
    for discovery testing, mock rule classes for registration validation, sys.path manipulation
    for package imports
"""

import pytest


class TestRuleRegistry:
    """Test RuleRegistry functionality."""

    def test_duplicate_rule_id_raises_error(self):
        """Registering duplicate rule ID raises error."""
        from src.core.base import BaseLintContext, BaseLintRule
        from src.core.registry import RuleRegistry

        class MockRule1(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.duplicate"

            @property
            def rule_name(self) -> str:
                return "Rule 1"

            @property
            def description(self) -> str:
                return "First rule"

            def check(self, context: BaseLintContext) -> list:
                return []

        class MockRule2(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.duplicate"

            @property
            def rule_name(self) -> str:
                return "Rule 2"

            @property
            def description(self) -> str:
                return "Second rule"

            def check(self, context: BaseLintContext) -> list:
                return []

        registry = RuleRegistry()
        registry.register(MockRule1())

        # Registering duplicate should raise error
        with pytest.raises(ValueError, match="already registered"):
            registry.register(MockRule2())


class TestRuleDiscovery:
    """Test automatic rule discovery."""

    def test_skips_abstract_base_classes(self):
        """Discovery skips ABC classes."""
        from src.core.registry import RuleRegistry

        registry = RuleRegistry()

        # Try to discover from src.core.base (which has BaseLintRule)
        count = registry.discover_rules("src.core.base")

        # Should not discover BaseLintRule itself
        assert registry.get("base.lint.rule") is None
        # Count should be 0 since BaseLintRule is abstract
        assert count == 0

    def test_discovery_handles_import_errors_gracefully(self, tmp_path):
        """Discovery handles modules with import errors."""
        from src.core.registry import RuleRegistry

        # Create package with broken module
        test_package = tmp_path / "test_broken"
        test_package.mkdir()
        (test_package / "__init__.py").write_text("")

        broken_module = test_package / "broken.py"
        broken_module.write_text("import nonexistent_module")

        import sys

        sys.path.insert(0, str(tmp_path))

        try:
            registry = RuleRegistry()
            # Should not crash, just skip the broken module
            count = registry.discover_rules("test_broken")
            assert count == 0
        finally:
            sys.path.remove(str(tmp_path))
