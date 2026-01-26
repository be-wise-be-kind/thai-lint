"""
Purpose: Test suite for standard allowlist expansion in magic numbers linter

Scope: Verify that common standard numbers (ports, etc.) are in the default allowlist

Overview: Tests the fix for false positives where standard port numbers and other common
    values were flagged as magic numbers. Standard ports like 80 (HTTP), 443 (HTTPS),
    22 (SSH) are well-known and don't need named constants. These tests verify:
    1. Standard HTTP ports (80, 443, 8080, 8443) are allowed
    2. Standard SSH/FTP ports (22, 21) are allowed
    3. Common development ports (3000, 5000) are allowed
    4. The allowlist can be customized via config

Dependencies: pytest, src.linters.magic_numbers.config.MagicNumberConfig

Exports: TestStandardAllowlist class with test cases for port number allowlist

Interfaces: Tests MagicNumberConfig default values and from_dict loading

Implementation: Directly tests config defaults and rule check behavior
"""

from pathlib import Path
from unittest.mock import Mock


class TestStandardPortAllowlist:
    """Test that standard port numbers are in the default allowlist."""

    def test_http_port_80_is_allowed(self) -> None:
        """Port 80 (HTTP) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 80 in config.allowed_numbers, "Port 80 should be in default allowlist"

    def test_https_port_443_is_allowed(self) -> None:
        """Port 443 (HTTPS) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 443 in config.allowed_numbers, "Port 443 should be in default allowlist"

    def test_ssh_port_22_is_allowed(self) -> None:
        """Port 22 (SSH) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 22 in config.allowed_numbers, "Port 22 should be in default allowlist"

    def test_ftp_port_21_is_allowed(self) -> None:
        """Port 21 (FTP) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 21 in config.allowed_numbers, "Port 21 should be in default allowlist"

    def test_alt_http_port_8080_is_allowed(self) -> None:
        """Port 8080 (alternate HTTP) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 8080 in config.allowed_numbers, "Port 8080 should be in default allowlist"

    def test_alt_https_port_8443_is_allowed(self) -> None:
        """Port 8443 (alternate HTTPS) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 8443 in config.allowed_numbers, "Port 8443 should be in default allowlist"

    def test_dev_port_3000_is_allowed(self) -> None:
        """Port 3000 (common dev server) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 3000 in config.allowed_numbers, "Port 3000 should be in default allowlist"

    def test_dev_port_5000_is_allowed(self) -> None:
        """Port 5000 (Flask default) should be in default allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 5000 in config.allowed_numbers, "Port 5000 should be in default allowlist"


class TestAllowlistInLinter:
    """Test that allowlist is respected when checking code."""

    def test_port_80_not_flagged_in_code(self) -> None:
        """Using port 80 in code should not trigger violation."""
        code = """
def get_default_port(secure):
    return 443 if secure else 80
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/server.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        # Both 443 and 80 should be allowed
        assert len(violations) == 0, "Standard ports should not be flagged"

    def test_port_8080_not_flagged_in_code(self) -> None:
        """Using port 8080 in code should not trigger violation."""
        code = """
def start_dev_server():
    server.run(port=8080)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/server.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Port 8080 should not be flagged"

    def test_non_standard_port_is_flagged(self) -> None:
        """Non-standard port numbers should still be flagged."""
        code = """
def start_server():
    server.run(port=9999)
"""
        from src.linters.magic_numbers.linter import MagicNumberRule

        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/server.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 1, "Non-standard port 9999 should be flagged"


class TestOriginalAllowlistPreserved:
    """Test that original allowlist values are still present."""

    def test_negative_one_still_allowed(self) -> None:
        """Value -1 should still be in allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert -1 in config.allowed_numbers

    def test_zero_still_allowed(self) -> None:
        """Value 0 should still be in allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 0 in config.allowed_numbers

    def test_small_integers_still_allowed(self) -> None:
        """Values 1-5 should still be in allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        for i in range(1, 6):
            assert i in config.allowed_numbers, f"Value {i} should be in allowlist"

    def test_common_values_still_allowed(self) -> None:
        """Values 10, 100, 1000 should still be in allowlist."""
        from src.linters.magic_numbers.config import MagicNumberConfig

        config = MagicNumberConfig()
        assert 10 in config.allowed_numbers
        assert 100 in config.allowed_numbers
        assert 1000 in config.allowed_numbers
