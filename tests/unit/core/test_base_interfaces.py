"""
Purpose: Test suite for base interface abstract classes and type definitions

Scope: Validation of BaseLintRule, BaseLintContext, Violation, and Severity interfaces

Overview: Comprehensive test suite validating the core abstractions that enable the plugin
    architecture, ensuring abstract base classes enforce required interface contracts and type
    definitions provide correct behavior. Tests verify that BaseLintRule and BaseLintContext
    cannot be instantiated directly, concrete implementations must provide all required properties
    and methods, Violation dataclass includes all necessary fields for violation reporting, and
    Severity enum implements the binary error model correctly. Validates the fundamental contracts
    that all linting rules and contexts must follow, ensuring the plugin system functions correctly
    through proper interface enforcement and type system behavior.

Dependencies: pytest for testing framework, pathlib for Path types in test assertions

Exports: TestBaseLintRule, TestBaseLintContext, TestViolation, TestSeverity test classes

Interfaces: Tests abstract class instantiation errors, required method implementation,
    property accessors, dataclass serialization, enum comparison

Implementation: 15 tests covering abstract class enforcement, concrete implementation validation,
    type serialization, and enum behavior using pytest test classes and assertions
"""

from pathlib import Path

import pytest


class TestBaseLintRule:
    """Test BaseLintRule abstract base class."""

    def test_cannot_instantiate_base_rule_directly(self):
        """Base rule is abstract and cannot be instantiated."""
        from src.core.base import BaseLintRule

        with pytest.raises(TypeError):
            BaseLintRule()

    def test_rule_must_implement_rule_id(self):
        """Concrete rule must implement rule_id property."""
        from src.core.base import BaseLintRule

        # Create subclass without rule_id
        class IncompleteRule(BaseLintRule):
            @property
            def rule_name(self) -> str:
                return "Test"

            @property
            def description(self) -> str:
                return "Test"

            def check(self, context):
                return []

        with pytest.raises(TypeError):
            IncompleteRule()

    def test_rule_must_implement_check(self):
        """Concrete rule must implement check method."""
        from src.core.base import BaseLintRule

        # Create subclass without check()
        class IncompleteRule(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.rule"

            @property
            def rule_name(self) -> str:
                return "Test"

            @property
            def description(self) -> str:
                return "Test"

        with pytest.raises(TypeError):
            IncompleteRule()

    def test_concrete_rule_can_be_instantiated(self):
        """Properly implemented rule can be instantiated."""
        from src.core.base import BaseLintContext, BaseLintRule

        class ValidRule(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.valid-rule"

            @property
            def rule_name(self) -> str:
                return "Valid Rule"

            @property
            def description(self) -> str:
                return "A valid test rule"

            def check(self, context: BaseLintContext) -> list:
                return []

        # Should instantiate without error
        rule = ValidRule()
        assert rule.rule_id == "test.valid-rule"
        assert rule.rule_name == "Valid Rule"
        assert rule.description == "A valid test rule"

    def test_rule_check_returns_violations_list(self):
        """Rule check method returns list of violations."""
        from src.core.base import BaseLintContext, BaseLintRule
        from src.core.types import Violation

        class TestRule(BaseLintRule):
            @property
            def rule_id(self) -> str:
                return "test.rule"

            @property
            def rule_name(self) -> str:
                return "Test"

            @property
            def description(self) -> str:
                return "Test"

            def check(self, context: BaseLintContext) -> list[Violation]:
                return []

        rule = TestRule()

        # Create mock context
        class MockContext(BaseLintContext):
            @property
            def file_path(self) -> Path | None:
                return Path("test.py")

            @property
            def file_content(self) -> str | None:
                return "# test"

            @property
            def language(self) -> str:
                return "python"

        context = MockContext()
        violations = rule.check(context)

        assert isinstance(violations, list)


class TestBaseLintContext:
    """Test BaseLintContext."""

    def test_context_has_file_path(self):
        """Context exposes file_path property."""
        from src.core.base import BaseLintContext

        class TestContext(BaseLintContext):
            @property
            def file_path(self) -> Path | None:
                return Path("test.py")

            @property
            def file_content(self) -> str | None:
                return "content"

            @property
            def language(self) -> str:
                return "python"

        context = TestContext()
        assert context.file_path == Path("test.py")

    def test_context_has_file_content(self):
        """Context exposes file_content property."""
        from src.core.base import BaseLintContext

        class TestContext(BaseLintContext):
            @property
            def file_path(self) -> Path | None:
                return Path("test.py")

            @property
            def file_content(self) -> str | None:
                return "# test content"

            @property
            def language(self) -> str:
                return "python"

        context = TestContext()
        assert context.file_content == "# test content"

    def test_context_has_language(self):
        """Context exposes language property."""
        from src.core.base import BaseLintContext

        class TestContext(BaseLintContext):
            @property
            def file_path(self) -> Path | None:
                return Path("test.py")

            @property
            def file_content(self) -> str | None:
                return "content"

            @property
            def language(self) -> str:
                return "python"

        context = TestContext()
        assert context.language == "python"

    def test_cannot_instantiate_base_context_directly(self):
        """BaseLintContext is abstract and cannot be instantiated."""
        from src.core.base import BaseLintContext

        with pytest.raises(TypeError):
            BaseLintContext()


class TestViolation:
    """Test Violation data class."""

    def test_violation_has_required_fields(self):
        """Violation has rule_id, file_path, line, message."""
        from src.core.types import Severity, Violation

        violation = Violation(
            rule_id="test.rule",
            file_path="src/test.py",
            line=10,
            column=5,
            message="Test violation",
            severity=Severity.ERROR,
        )

        assert violation.rule_id == "test.rule"
        assert violation.file_path == "src/test.py"
        assert violation.line == 10
        assert violation.column == 5
        assert violation.message == "Test violation"
        assert violation.severity == Severity.ERROR

    def test_violation_can_be_serialized(self):
        """Violation can be converted to dict/JSON."""
        from src.core.types import Severity, Violation

        violation = Violation(
            rule_id="test.rule",
            file_path="src/test.py",
            line=10,
            column=5,
            message="Test violation",
            severity=Severity.ERROR,
            suggestion="Fix this issue",
        )

        violation_dict = violation.to_dict()

        assert isinstance(violation_dict, dict)
        assert violation_dict["rule_id"] == "test.rule"
        assert violation_dict["file_path"] == "src/test.py"
        assert violation_dict["line"] == 10
        assert violation_dict["column"] == 5
        assert violation_dict["message"] == "Test violation"
        assert violation_dict["severity"] == "error"
        assert violation_dict["suggestion"] == "Fix this issue"

    def test_violation_suggestion_optional(self):
        """Violation suggestion field is optional."""
        from src.core.types import Severity, Violation

        violation = Violation(
            rule_id="test.rule",
            file_path="src/test.py",
            line=10,
            column=5,
            message="Test violation",
            severity=Severity.ERROR,
        )

        assert violation.suggestion is None

        violation_dict = violation.to_dict()
        assert violation_dict["suggestion"] is None


class TestSeverity:
    """Test Severity enum."""

    def test_severity_has_error_level(self):
        """Severity.ERROR exists (binary model)."""
        from src.core.types import Severity

        assert hasattr(Severity, "ERROR")
        assert Severity.ERROR.value == "error"

    def test_severity_is_comparable(self):
        """Severity levels can be compared."""
        from src.core.types import Severity

        error1 = Severity.ERROR
        error2 = Severity.ERROR

        assert error1 == error2
        assert error1.value == error2.value

    def test_severity_only_has_error(self):
        """Binary severity model - only ERROR exists."""
        from src.core.types import Severity

        # Should only have ERROR, no WARNING, INFO, etc.
        severity_values = [s.value for s in Severity]
        assert len(severity_values) == 1
        assert "error" in severity_values
