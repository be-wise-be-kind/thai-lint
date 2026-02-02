"""
Purpose: Unit tests for BlockingAsyncConfig dataclass

Scope: Validates default values, from_dict loading, and pattern toggle behavior

Overview: Tests the BlockingAsyncConfig dataclass for correct default values, loading from
    dictionary with various inputs (empty, partial, full), and verifying that pattern toggles
    (detect_fs_in_async, detect_sleep_in_async, detect_net_in_async) are correctly handled.
    Follows the clone_abuse test_config pattern for consistency.

Dependencies: src.linters.blocking_async.config

Exports: TestBlockingAsyncConfigDefaults, TestBlockingAsyncConfigFromDict,
    TestBlockingAsyncConfigPatternToggles

Interfaces: Standard pytest test classes

Implementation: Direct dataclass instantiation and from_dict factory method testing
"""

from src.linters.blocking_async.config import BlockingAsyncConfig


class TestBlockingAsyncConfigDefaults:
    """Tests for default configuration values."""

    def test_enabled_by_default(self) -> None:
        """Should be enabled by default."""
        config = BlockingAsyncConfig()
        assert config.enabled is True

    def test_allow_in_tests_by_default(self) -> None:
        """Should allow blocking calls in tests by default."""
        config = BlockingAsyncConfig()
        assert config.allow_in_tests is True

    def test_detect_fs_in_async_by_default(self) -> None:
        """Should detect fs in async by default."""
        config = BlockingAsyncConfig()
        assert config.detect_fs_in_async is True

    def test_detect_sleep_in_async_by_default(self) -> None:
        """Should detect sleep in async by default."""
        config = BlockingAsyncConfig()
        assert config.detect_sleep_in_async is True

    def test_detect_net_in_async_by_default(self) -> None:
        """Should detect net in async by default."""
        config = BlockingAsyncConfig()
        assert config.detect_net_in_async is True

    def test_default_ignore_patterns(self) -> None:
        """Should have examples/ and benches/ in ignore by default."""
        config = BlockingAsyncConfig()
        assert "examples/" in config.ignore
        assert "benches/" in config.ignore


class TestBlockingAsyncConfigFromDict:
    """Tests for from_dict factory method."""

    def test_from_empty_dict(self) -> None:
        """Should use defaults for empty dict."""
        config = BlockingAsyncConfig.from_dict({})
        assert config.enabled is True
        assert config.allow_in_tests is True
        assert config.detect_fs_in_async is True
        assert config.detect_sleep_in_async is True
        assert config.detect_net_in_async is True

    def test_from_dict_disabled(self) -> None:
        """Should respect enabled=false."""
        config = BlockingAsyncConfig.from_dict({"enabled": False})
        assert config.enabled is False

    def test_from_dict_disallow_tests(self) -> None:
        """Should flag test code when configured."""
        config = BlockingAsyncConfig.from_dict({"allow_in_tests": False})
        assert config.allow_in_tests is False

    def test_from_dict_custom_ignore(self) -> None:
        """Should use custom ignore patterns."""
        config = BlockingAsyncConfig.from_dict({"ignore": ["tests/", "scripts/"]})
        assert config.ignore == ["tests/", "scripts/"]

    def test_from_dict_full_config(self) -> None:
        """Should load all fields from complete config."""
        config = BlockingAsyncConfig.from_dict(
            {
                "enabled": True,
                "allow_in_tests": False,
                "detect_fs_in_async": True,
                "detect_sleep_in_async": False,
                "detect_net_in_async": False,
                "ignore": ["vendor/"],
            }
        )
        assert config.enabled is True
        assert config.allow_in_tests is False
        assert config.detect_fs_in_async is True
        assert config.detect_sleep_in_async is False
        assert config.detect_net_in_async is False
        assert config.ignore == ["vendor/"]

    def test_from_dict_ignores_language_param(self) -> None:
        """Should accept language parameter without error."""
        config = BlockingAsyncConfig.from_dict({}, language="rust")
        assert config.enabled is True

    def test_from_dict_partial_config(self) -> None:
        """Should use defaults for missing fields in partial config."""
        config = BlockingAsyncConfig.from_dict({"detect_sleep_in_async": False})
        assert config.enabled is True
        assert config.allow_in_tests is True
        assert config.detect_fs_in_async is True
        assert config.detect_sleep_in_async is False
        assert config.detect_net_in_async is True


class TestBlockingAsyncConfigPatternToggles:
    """Tests for individual pattern toggle behavior."""

    def test_disable_fs_detection(self) -> None:
        """Should disable fs-in-async without affecting other patterns."""
        config = BlockingAsyncConfig(detect_fs_in_async=False)
        assert config.detect_fs_in_async is False
        assert config.detect_sleep_in_async is True
        assert config.detect_net_in_async is True

    def test_disable_sleep_detection(self) -> None:
        """Should disable sleep-in-async without affecting other patterns."""
        config = BlockingAsyncConfig(detect_sleep_in_async=False)
        assert config.detect_fs_in_async is True
        assert config.detect_sleep_in_async is False
        assert config.detect_net_in_async is True

    def test_disable_net_detection(self) -> None:
        """Should disable net-in-async without affecting other patterns."""
        config = BlockingAsyncConfig(detect_net_in_async=False)
        assert config.detect_fs_in_async is True
        assert config.detect_sleep_in_async is True
        assert config.detect_net_in_async is False

    def test_disable_all_patterns(self) -> None:
        """Should disable all patterns simultaneously."""
        config = BlockingAsyncConfig(
            detect_fs_in_async=False,
            detect_sleep_in_async=False,
            detect_net_in_async=False,
        )
        assert config.detect_fs_in_async is False
        assert config.detect_sleep_in_async is False
        assert config.detect_net_in_async is False
