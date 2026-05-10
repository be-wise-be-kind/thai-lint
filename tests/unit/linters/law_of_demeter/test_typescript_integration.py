"""
Purpose: Integration tests for TypeScript Law of Demeter analysis

Scope: End-to-end tests using TypeScript fixtures through LawOfDemeterRule.check()

Overview: Validates the full TypeScript linting pipeline from source code to violation output.
    Uses existing fixture samples from fixtures/typescript_samples/test_samples.py. True positive
    samples (reach-through object, method chain violation, deep property access) should produce
    violations. False positive samples (module access, fluent builder, optional chaining, string
    chain, React this, promise chain, array pipeline) should produce no violations. Tests exercise
    the complete chain: tree-sitter parsing, chain extraction, 9-filter classification, and
    violation building.

Dependencies: pytest, unittest.mock, pathlib, src.linters.law_of_demeter.linter,
    fixtures.typescript_samples.test_samples

Exports: TestTypeScriptTruePositives, TestTypeScriptFalsePositives, TestTypeScriptEdgeCases

Interfaces: Tests LawOfDemeterRule.check(context) with language="typescript"

Implementation: Creates mock BaseLintContext with language="typescript", invokes rule.check()
"""

from pathlib import Path
from unittest.mock import Mock

from src.linters.law_of_demeter.linter import LawOfDemeterRule

from .fixtures.typescript_samples.test_samples import (
    TS_ARRAY_PIPELINE,
    TS_DEEP_PROPERTY_ACCESS,
    TS_FLUENT_BUILDER,
    TS_METHOD_CHAIN_VIOLATION,
    TS_MODULE_ACCESS,
    TS_OPTIONAL_CHAIN,
    TS_PROMISE_CHAIN,
    TS_REACH_THROUGH_OBJECT,
    TS_REACT_THIS,
    TS_STRING_CHAIN,
)


def _create_ts_context(code: str, filename: str = "app.ts") -> Mock:
    """Create mock lint context for TypeScript code."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = "typescript"
    context.metadata = {}
    return context


class TestTypeScriptTruePositives:
    """Genuine LoD violations in TypeScript should be detected."""

    def test_reach_through_object(self) -> None:
        """order.customer.address.city should be flagged."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_REACH_THROUGH_OBJECT))
        assert len(violations) >= 1
        assert "law-of-demeter" in violations[0].rule_id

    def test_method_chain_violation(self) -> None:
        """service.getClient().fetchData().parse() should be flagged."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_METHOD_CHAIN_VIOLATION))
        assert len(violations) >= 1

    def test_deep_property_access(self) -> None:
        """ctx.page.header.title.text should be flagged."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_DEEP_PROPERTY_ACCESS))
        assert len(violations) >= 1


class TestTypeScriptFalsePositives:
    """Legitimate TypeScript patterns should NOT be flagged."""

    def test_module_access(self) -> None:
        """express.Router().use().get() should not be flagged (module access)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_MODULE_ACCESS))
        assert len(violations) == 0

    def test_fluent_builder(self) -> None:
        """db.select().where().orderBy().limit() should not be flagged (fluent API)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_FLUENT_BUILDER))
        assert len(violations) == 0

    def test_optional_chain(self) -> None:
        """user?.address?.city?.name should not be flagged (optional chaining)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_OPTIONAL_CHAIN))
        assert len(violations) == 0

    def test_string_chain(self) -> None:
        """text.trim().toLowerCase().replace() should not be flagged (string methods)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_STRING_CHAIN))
        assert len(violations) == 0

    def test_react_this(self) -> None:
        """this.props.config.theme.color should not be flagged (safe prefix)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_REACT_THIS))
        assert len(violations) == 0

    def test_promise_chain(self) -> None:
        """fetch().then().then() should not be flagged (fluent/promise chain)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_PROMISE_CHAIN))
        assert len(violations) == 0

    def test_array_pipeline(self) -> None:
        """items.filter().map().join() should not be flagged (collection pipeline)."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(TS_ARRAY_PIPELINE))
        assert len(violations) == 0


class TestTypeScriptEdgeCases:
    """Edge cases for TypeScript analysis."""

    def test_empty_ts_file(self) -> None:
        """Empty TypeScript file should produce no violations."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(""))
        assert violations == []

    def test_ts_file_with_no_chains(self) -> None:
        """TypeScript file without chains should produce no violations."""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context("const x = 42;"))
        assert violations == []

    def test_disabled_returns_empty(self) -> None:
        """Should return empty when disabled."""
        code = "const x = a.b.c.d;"
        rule = LawOfDemeterRule()
        context = _create_ts_context(code)
        context.metadata = {"law-of-demeter": {"enabled": False}}
        violations = rule.check(context)
        assert violations == []

    def test_test_file_not_flagged_by_default(self) -> None:
        """Violations in test files should not be flagged by default."""
        code = """
function testSomething() {
    const x = obj.deep.nested.value.extra;
}
"""
        rule = LawOfDemeterRule()
        violations = rule.check(_create_ts_context(code, "test_app.ts"))
        assert len(violations) == 0
