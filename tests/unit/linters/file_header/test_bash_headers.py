"""
Purpose: Unit tests for Bash shell script file header validation

Scope: Testing Bash-specific header parsing and validation requirements

Overview: Comprehensive test suite for Bash shell script file header validation including
    hash comment header extraction after shebang, mandatory field detection, shebang line
    handling, atemporal language validation, and edge case handling. Tests cover .sh and .bash
    files with Bash-specific mandatory fields including Usage and Environment. Validates proper
    header detection with and without shebang lines.

Dependencies: pytest, conftest fixtures (VALID_BASH_HEADER, BASH_NO_HEADER, etc.),
    src.linters.file_header.linter.FileHeaderRule

Exports: TestBashHeaderExtraction, TestBashMandatoryFields, TestBashShebangHandling,
    TestBashAtemporalLanguage, TestBashEdgeCases test classes

Interfaces: test_extracts_comment_header_after_shebang, test_detects_missing_purpose_field,
    test_handles_bin_bash_shebang, test_detects_date_in_header, and other test methods

Implementation: Uses conftest fixtures for valid and invalid Bash headers, mock contexts
    for isolated testing, validates Bash-specific field requirements
"""

from tests.unit.linters.file_header.conftest import (
    BASH_NO_HEADER,
    BASH_TEMPORAL_HEADER,
    VALID_BASH_HEADER,
    create_mock_context,
)


class TestBashHeaderExtraction:
    """Test extraction of comment headers from Bash files."""

    def test_extracts_comment_header_after_shebang(self):
        """Should extract comment header after shebang line."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_BASH_HEADER, "deploy.sh", "bash")
        violations = rule.check(context)

        # Should not have "missing header" violation when valid header exists
        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Valid comment header should be detected"

    def test_extracts_header_without_shebang(self):
        """Should extract header from script without shebang."""
        code = """# File: scripts/helper.sh
# Purpose: Helper functions
# Scope: Utility functions
# Overview: Provides common shell helper functions
# Dependencies: coreutils
# Exports: log_info, log_error
# Usage: source helper.sh
# Environment: BASH_VERSION

log_info() {
    echo "[INFO] $1"
}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "helper.sh", "bash")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Header without shebang should be valid"

    def test_detects_missing_header(self):
        """Should detect when Bash file has no header."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(BASH_NO_HEADER, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1, "Should detect missing header"
        assert any(
            "missing" in v.message.lower() or "header" in v.message.lower() for v in violations
        )

    def test_extracts_header_from_bash_extension(self):
        """Should handle .bash file extension."""
        code = """#!/usr/bin/env bash
# File: scripts/setup.bash
# Purpose: Setup script
# Scope: Environment setup
# Overview: Configures development environment
# Dependencies: apt-get, curl
# Exports: setup_env
# Usage: ./setup.bash
# Environment: HOME, PATH

setup_env() {
    echo "Setting up..."
}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "setup.bash", "bash")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0


class TestBashMandatoryFields:
    """Test mandatory field detection in Bash headers."""

    def test_detects_missing_purpose_field(self):
        """Should detect when Purpose field is missing."""
        code = """#!/bin/bash
# File: scripts/test.sh
# Scope: Testing
# Overview: Test script
# Dependencies: none
# Exports: none
# Usage: ./test.sh
# Environment: none
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)

    def test_detects_missing_scope_field(self):
        """Should detect when Scope field is missing."""
        code = """#!/bin/bash
# File: scripts/test.sh
# Purpose: Test script
# Overview: Test script description
# Dependencies: none
# Exports: none
# Usage: ./test.sh
# Environment: none
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Scope" in v.message for v in violations)

    def test_detects_missing_overview_field(self):
        """Should detect when Overview field is missing."""
        code = """#!/bin/bash
# File: scripts/test.sh
# Purpose: Test script
# Scope: Testing
# Dependencies: none
# Exports: none
# Usage: ./test.sh
# Environment: none
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Overview" in v.message for v in violations)

    def test_detects_missing_usage_field(self):
        """Should detect when Usage field is missing (Bash-specific)."""
        code = """#!/bin/bash
# File: scripts/test.sh
# Purpose: Test script
# Scope: Testing
# Overview: Test script description
# Dependencies: none
# Exports: none
# Environment: none
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Usage" in v.message for v in violations)

    def test_detects_missing_environment_field(self):
        """Should detect when Environment field is missing (Bash-specific)."""
        code = """#!/bin/bash
# File: scripts/test.sh
# Purpose: Test script
# Scope: Testing
# Overview: Test script description
# Dependencies: none
# Exports: none
# Usage: ./test.sh
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Environment" in v.message for v in violations)

    def test_accepts_all_mandatory_fields_present(self):
        """Should accept Bash header with all mandatory fields."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_BASH_HEADER, "deploy.sh", "bash")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "All mandatory fields are present"


class TestBashShebangHandling:
    """Test shebang line handling in Bash files."""

    def test_handles_bin_bash_shebang(self):
        """Should handle #!/bin/bash shebang."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_BASH_HEADER, "test.sh", "bash")
        violations = rule.check(context)

        # Shebang should not interfere with header detection
        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0

    def test_handles_env_bash_shebang(self):
        """Should handle #!/usr/bin/env bash shebang."""
        code = """#!/usr/bin/env bash
# File: scripts/test.sh
# Purpose: Test script
# Scope: Testing
# Overview: Test script description
# Dependencies: none
# Exports: none
# Usage: ./test.sh
# Environment: PATH

echo "test"
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0

    def test_handles_bin_sh_shebang(self):
        """Should handle #!/bin/sh shebang for POSIX scripts."""
        code = """#!/bin/sh
# File: scripts/posix.sh
# Purpose: POSIX-compatible script
# Scope: Cross-platform
# Overview: Script that works with POSIX sh
# Dependencies: coreutils
# Exports: run_command
# Usage: ./posix.sh
# Environment: SHELL

run_command() {
    "$@"
}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "posix.sh", "bash")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0


class TestBashAtemporalLanguage:
    """Test atemporal language detection in Bash headers."""

    def test_detects_date_in_header(self):
        """Should detect date references in header."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(BASH_TEMPORAL_HEADER, "migrate.sh", "bash")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect date '2025-01-15'"

    def test_detects_replaces_keyword(self):
        """Should detect 'replaces' state change language."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(BASH_TEMPORAL_HEADER, "migrate.sh", "bash")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'replaces'"

    def test_detects_soon_keyword(self):
        """Should detect 'soon' temporal qualifier."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(BASH_TEMPORAL_HEADER, "migrate.sh", "bash")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'soon'"

    def test_accepts_atemporal_language(self):
        """Should accept present-tense, factual descriptions."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_BASH_HEADER, "deploy.sh", "bash")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0, "Valid header has no temporal language"


class TestBashEdgeCases:
    """Test edge cases in Bash header validation."""

    def test_handles_empty_file(self):
        """Should handle empty Bash file gracefully."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context("", "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1

    def test_handles_only_shebang(self):
        """Should detect missing header when file has only shebang."""
        code = "#!/bin/bash\n"
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1, "Shebang alone is not a valid header"
