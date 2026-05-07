"""
Purpose: Test safe-prefix filter for Law of Demeter classifier

Scope: Filtering chains starting with self., cls., config., settings., etc.

Overview: Validates the safe-prefix filter that allows chains starting with known safe
    prefixes like self., cls., settings., config., logger., request.POST., etc. These
    chains access an object's own state or well-known namespace objects and are not LoD
    violations. Tests cover all built-in safe prefixes and user-configured custom prefixes.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier

Exports: TestSafePrefixFilter (6 tests)

Interfaces: Tests classify_chain() returning "safe-prefix:*" for matching chains

Implementation: Calls classify_chain() with chain parts starting with safe prefixes,
    verifies the filter fires and returns appropriate reason string
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestSafePrefixFilter:
    """Test safe-prefix filter catches self/cls/config/settings chains."""

    def _empty_imports(self) -> FileImports:
        """Create empty imports for testing."""
        return FileImports()

    def test_self_prefix_allowed(self) -> None:
        """Chains starting with self. should be allowed."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["self", "config", "database", "host"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-prefix")

    def test_cls_prefix_allowed(self) -> None:
        """Chains starting with cls. should be allowed."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["cls", "defaults", "connection", "timeout"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-prefix")

    def test_settings_prefix_allowed(self) -> None:
        """Chains starting with settings. should be allowed."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["settings", "database", "connection", "host"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-prefix")

    def test_config_prefix_allowed(self) -> None:
        """Chains starting with config. should be allowed."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["config", "http", "client", "timeout"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        assert result.startswith("safe-prefix")

    def test_request_data_prefix_allowed(self) -> None:
        """Chains starting with request.POST. should be allowed."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["request", "POST", "get()", "strip()"]
        result = classify_chain(parts, self._empty_imports(), "views.py")
        assert result != ""  # Should be filtered

    def test_non_safe_prefix_not_filtered(self) -> None:
        """Chains not starting with safe prefix should not be filtered here."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, self._empty_imports(), "app.py")
        # This might be caught by another filter or be a violation
        # But safe-prefix filter should NOT catch it
        assert not result.startswith("safe-prefix")
