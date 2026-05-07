"""
Purpose: Test fluent-chain filter for Law of Demeter classifier

Scope: Filtering ORM queries, builder patterns, and collection pipelines

Overview: Validates the fluent-chain filter that allows chains consisting entirely of
    collection pipeline methods (filter, map, select, where, order_by, limit) or builder
    methods (set, with_, add, configure, build). These are fluent APIs where each call
    returns the same or similar type, not Law of Demeter violations.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestFluentChainFilter (5 tests)

Interfaces: Tests classify_chain() returning "fluent-chain" for pipeline chains

Implementation: Calls classify_chain() with ORM/builder chain parts,
    verifies fluent-chain filter fires
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestFluentChainFilter:
    """Test fluent-chain filter for ORM/builder/pipeline patterns."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_orm_query_chain(self) -> None:
        """db.query().filter().order_by().limit() should be fluent-chain."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["db", "filter()", "order_by()", "limit()"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result == "fluent-chain"

    def test_builder_pattern(self) -> None:
        """builder.set().set().build() should be fluent-chain."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["builder", "set()", "set()", "build()"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result == "fluent-chain"

    def test_django_queryset(self) -> None:
        """Post.objects.filter().exclude().order_by() should be fluent-chain."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["Post", "filter()", "exclude()", "order_by()"]
        result = classify_chain(parts, self._empty_imports(), "views.py")
        assert result == "fluent-chain"

    def test_pandas_pipeline(self) -> None:
        """df.filter().groupby().sum() should be fluent-chain."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["df", "filter()", "groupby()", "sorted()"]
        result = classify_chain(parts, self._empty_imports(), "analysis.py")
        assert result == "fluent-chain"

    def test_mixed_non_fluent_not_filtered(self) -> None:
        """Chain with non-fluent methods should not be caught."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result != "fluent-chain"
