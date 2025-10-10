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

    @pytest.mark.skip(reason="100% duplicate")
    def test_can_register_rule(self):
        """Registry can register a rule."""
        from src.core.base import BaseLintContext, BaseLintRule
        from src.core.registry import RuleRegistry

        class MockRule(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.mock-rule"

            @property
            def rule_name(self) -> str:
                return "Mock Rule"

            @property
            def description(self) -> str:
                return "A mock rule for testing"

            def check(self, context: BaseLintContext) -> list:
                return []

        registry = RuleRegistry()
        rule = MockRule()
        registry.register(rule)

        # Verify it's in registry
        assert registry.get("test.mock-rule") is not None

    @pytest.mark.skip(reason="100% duplicate")
    def test_can_retrieve_registered_rule(self):
        """Registry can retrieve rule by ID."""
        from src.core.base import BaseLintContext, BaseLintRule
        from src.core.registry import RuleRegistry

        class MockRule(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.retrieve-rule"

            @property
            def rule_name(self) -> str:
                return "Retrieve Rule"

            @property
            def description(self) -> str:
                return "Test retrieval"

            def check(self, context: BaseLintContext) -> list:
                return []

        registry = RuleRegistry()
        rule = MockRule()
        registry.register(rule)

        retrieved = registry.get("test.retrieve-rule")
        assert retrieved is rule
        assert retrieved.rule_id == "test.retrieve-rule"

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

    @pytest.mark.skip(reason="100% duplicate")
    def test_can_list_all_rules(self):
        """Registry can list all registered rules."""
        from src.core.base import BaseLintContext, BaseLintRule
        from src.core.registry import RuleRegistry

        class MockRule1(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.rule-1"

            @property
            def rule_name(self) -> str:
                return "Rule 1"

            @property
            def description(self) -> str:
                return "First"

            def check(self, context: BaseLintContext) -> list:
                return []

        class MockRule2(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.rule-2"

            @property
            def rule_name(self) -> str:
                return "Rule 2"

            @property
            def description(self) -> str:
                return "Second"

            def check(self, context: BaseLintContext) -> list:
                return []

        registry = RuleRegistry()
        rule1 = MockRule1()
        rule2 = MockRule2()
        registry.register(rule1)
        registry.register(rule2)

        all_rules = registry.list_all()
        assert len(all_rules) == 2
        assert rule1 in all_rules
        assert rule2 in all_rules

    @pytest.mark.skip(reason="100% duplicate")
    def test_get_nonexistent_rule_returns_none(self):
        """Getting a nonexistent rule returns None."""
        from src.core.registry import RuleRegistry

        registry = RuleRegistry()
        result = registry.get("nonexistent.rule")

        assert result is None


class TestRuleDiscovery:
    """Test automatic rule discovery."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_discovers_rules_in_package(self, tmp_path):
        """Auto-discover rules in specified package."""
        from src.core.registry import RuleRegistry

        # Create a test package with a rule
        test_package = tmp_path / "test_rules"
        test_package.mkdir()

        # Create __init__.py
        (test_package / "__init__.py").write_text("")

        # Create a module with a rule
        rule_module = test_package / "test_rule.py"
        rule_module.write_text("""
from src.core.base import BaseLintRule, BaseLintContext

class DiscoverableRule(BaseLintRule):
    @property
    def rule_id(self) -> str:
        return "test.discoverable"

    @property
    def rule_name(self) -> str:
        return "Discoverable Rule"

    @property
    def description(self) -> str:
        return "A rule that can be discovered"

    def check(self, context: BaseLintContext) -> list:
        return []
""")

        # Add to sys.path so we can import it
        import sys

        sys.path.insert(0, str(tmp_path))

        try:
            registry = RuleRegistry()
            count = registry.discover_rules("test_rules")

            assert count == 1
            assert registry.get("test.discoverable") is not None
        finally:
            sys.path.remove(str(tmp_path))

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

    @pytest.mark.skip(reason="100% duplicate")
    def test_only_discovers_lint_rule_subclasses(self, tmp_path):
        """Discovery only finds BaseLintRule subclasses."""
        from src.core.registry import RuleRegistry

        # Create test package with mixed classes
        test_package = tmp_path / "test_mixed"
        test_package.mkdir()
        (test_package / "__init__.py").write_text("")

        # Create module with rule and non-rule classes
        mixed_module = test_package / "mixed.py"
        mixed_module.write_text('''
from src.core.base import BaseLintRule, BaseLintContext

class NotARule:
    """Regular class, not a rule."""
    pass

class ActualRule(BaseLintRule):
    @property
    def rule_id(self) -> str:
        return "test.actual"

    @property
    def rule_name(self) -> str:
        return "Actual Rule"

    @property
    def description(self) -> str:
        return "This is a real rule"

    def check(self, context: BaseLintContext) -> list:
        return []
''')

        import sys

        sys.path.insert(0, str(tmp_path))

        try:
            registry = RuleRegistry()
            count = registry.discover_rules("test_mixed")

            # Should only find ActualRule
            assert count == 1
            assert registry.get("test.actual") is not None
        finally:
            sys.path.remove(str(tmp_path))

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
