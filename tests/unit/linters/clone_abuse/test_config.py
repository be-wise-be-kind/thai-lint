"""
Purpose: Unit tests for CloneAbuseConfig dataclass

Scope: Validates default values, from_dict loading, and pattern toggle behavior

Overview: Tests the CloneAbuseConfig dataclass for correct default values, loading from
    dictionary with various inputs (empty, partial, full), and verifying that pattern toggles
    (detect_clone_in_loop, detect_clone_chain, detect_unnecessary_clone) are correctly
    handled. Follows the unwrap_abuse test_config pattern for consistency.

Dependencies: src.linters.clone_abuse.config

Exports: TestCloneAbuseConfigDefaults, TestCloneAbuseConfigFromDict, TestCloneAbuseConfigPatternToggles

Interfaces: Standard pytest test classes

Implementation: Direct dataclass instantiation and from_dict factory method testing
"""

from src.linters.clone_abuse.config import CloneAbuseConfig


class TestCloneAbuseConfigDefaults:
    """Tests for default configuration values."""

    def test_enabled_by_default(self) -> None:
        """Should be enabled by default."""
        config = CloneAbuseConfig()
        assert config.enabled is True

    def test_allow_in_tests_by_default(self) -> None:
        """Should allow clone in tests by default."""
        config = CloneAbuseConfig()
        assert config.allow_in_tests is True

    def test_detect_clone_in_loop_by_default(self) -> None:
        """Should detect clone in loop by default."""
        config = CloneAbuseConfig()
        assert config.detect_clone_in_loop is True

    def test_detect_clone_chain_by_default(self) -> None:
        """Should detect clone chain by default."""
        config = CloneAbuseConfig()
        assert config.detect_clone_chain is True

    def test_detect_unnecessary_clone_by_default(self) -> None:
        """Should detect unnecessary clone by default."""
        config = CloneAbuseConfig()
        assert config.detect_unnecessary_clone is True

    def test_default_ignore_patterns(self) -> None:
        """Should have examples/ and benches/ in ignore by default."""
        config = CloneAbuseConfig()
        assert "examples/" in config.ignore
        assert "benches/" in config.ignore


class TestCloneAbuseConfigFromDict:
    """Tests for from_dict factory method."""

    def test_from_empty_dict(self) -> None:
        """Should use defaults for empty dict."""
        config = CloneAbuseConfig.from_dict({})
        assert config.enabled is True
        assert config.allow_in_tests is True
        assert config.detect_clone_in_loop is True
        assert config.detect_clone_chain is True
        assert config.detect_unnecessary_clone is True

    def test_from_dict_disabled(self) -> None:
        """Should respect enabled=false."""
        config = CloneAbuseConfig.from_dict({"enabled": False})
        assert config.enabled is False

    def test_from_dict_disallow_tests(self) -> None:
        """Should flag test code when configured."""
        config = CloneAbuseConfig.from_dict({"allow_in_tests": False})
        assert config.allow_in_tests is False

    def test_from_dict_custom_ignore(self) -> None:
        """Should use custom ignore patterns."""
        config = CloneAbuseConfig.from_dict({"ignore": ["tests/", "scripts/"]})
        assert config.ignore == ["tests/", "scripts/"]

    def test_from_dict_full_config(self) -> None:
        """Should load all fields from complete config."""
        config = CloneAbuseConfig.from_dict(
            {
                "enabled": True,
                "allow_in_tests": False,
                "detect_clone_in_loop": True,
                "detect_clone_chain": False,
                "detect_unnecessary_clone": False,
                "ignore": ["vendor/"],
            }
        )
        assert config.enabled is True
        assert config.allow_in_tests is False
        assert config.detect_clone_in_loop is True
        assert config.detect_clone_chain is False
        assert config.detect_unnecessary_clone is False
        assert config.ignore == ["vendor/"]

    def test_from_dict_ignores_language_param(self) -> None:
        """Should accept language parameter without error."""
        config = CloneAbuseConfig.from_dict({}, language="rust")
        assert config.enabled is True

    def test_from_dict_partial_config(self) -> None:
        """Should use defaults for missing fields in partial config."""
        config = CloneAbuseConfig.from_dict({"detect_clone_chain": False})
        assert config.enabled is True
        assert config.allow_in_tests is True
        assert config.detect_clone_in_loop is True
        assert config.detect_clone_chain is False
        assert config.detect_unnecessary_clone is True


class TestCloneAbuseConfigPatternToggles:
    """Tests for individual pattern toggle behavior."""

    def test_disable_clone_in_loop(self) -> None:
        """Should disable clone-in-loop without affecting other patterns."""
        config = CloneAbuseConfig(detect_clone_in_loop=False)
        assert config.detect_clone_in_loop is False
        assert config.detect_clone_chain is True
        assert config.detect_unnecessary_clone is True

    def test_disable_clone_chain(self) -> None:
        """Should disable clone-chain without affecting other patterns."""
        config = CloneAbuseConfig(detect_clone_chain=False)
        assert config.detect_clone_in_loop is True
        assert config.detect_clone_chain is False
        assert config.detect_unnecessary_clone is True

    def test_disable_unnecessary_clone(self) -> None:
        """Should disable unnecessary-clone without affecting other patterns."""
        config = CloneAbuseConfig(detect_unnecessary_clone=False)
        assert config.detect_clone_in_loop is True
        assert config.detect_clone_chain is True
        assert config.detect_unnecessary_clone is False

    def test_disable_all_patterns(self) -> None:
        """Should disable all patterns simultaneously."""
        config = CloneAbuseConfig(
            detect_clone_in_loop=False,
            detect_clone_chain=False,
            detect_unnecessary_clone=False,
        )
        assert config.detect_clone_in_loop is False
        assert config.detect_clone_chain is False
        assert config.detect_unnecessary_clone is False
