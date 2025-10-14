"""
File: tests/unit/linters/file_header/test_atemporal_language.py
Purpose: Test suite for atemporal language detection in file headers
Exports: TestDatePatternDetection, TestTemporalQualifierDetection, TestStateChangeDetection, TestFutureReferenceDetection, TestAcceptableLanguage
Depends: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule
Related: test_mandatory_fields.py, docs/ai-doc-standard.md

Overview:
    Comprehensive tests for detecting temporal language patterns that violate atemporal
    documentation requirements. Tests date detection, temporal qualifiers, state change
    language, and future references. Validates that only present-tense, factual
    descriptions are accepted. All tests initially fail (TDD RED phase) since
    FileHeaderRule does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_atemporal_language.py -v
"""

from tests.unit.linters.file_header.conftest import create_mock_context


class TestDatePatternDetection:
    """Test detection of date patterns in headers."""

    def test_detects_iso_date_format(self):
        """Should detect ISO date format (YYYY-MM-DD)."""
        code = '''"""
Purpose: Created 2025-01-15 for user authentication
Scope: Authentication module
Overview: Handles user login and session management
Dependencies: bcrypt
Exports: AuthHandler
Interfaces: login()
Implementation: Standard authentication
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("2025-01-15" in v.message or "temporal" in v.message.lower() for v in violations)

    def test_detects_month_year_format(self):
        """Should detect Month YYYY format."""
        code = '''"""
Purpose: Authentication handler
Scope: Updated January 2025 with new features
Overview: Handles user authentication
Dependencies: bcrypt
Exports: AuthHandler
Interfaces: login()
Implementation: Standard authentication
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_created_updated_metadata(self):
        """Should detect Created/Updated date metadata."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Handles user authentication
Dependencies: bcrypt
Exports: AuthHandler
Interfaces: login()
Implementation: Created: 2024-10-15
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)


class TestTemporalQualifierDetection:
    """Test detection of temporal qualifiers."""

    def test_detects_currently_qualifier(self):
        """Should detect 'currently' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Currently supports OAuth and SAML authentication methods
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: OAuth integration
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any(
            "temporal" in v.message.lower() or "currently" in v.message.lower() for v in violations
        )

    def test_detects_now_qualifier(self):
        """Should detect 'now' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Now includes support for multi-factor authentication
Dependencies: totp
Exports: AuthHandler
Interfaces: authenticate()
Implementation: MFA support
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_recently_qualifier(self):
        """Should detect 'recently' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Recently added support for biometric authentication
Dependencies: biometric_lib
Exports: AuthHandler
Interfaces: authenticate()
Implementation: Biometric support
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any(
            "temporal" in v.message.lower() or "recently" in v.message.lower() for v in violations
        )


class TestStateChangeDetection:
    """Test detection of state change language."""

    def test_detects_replaces_state_change(self):
        """Should detect state change language like 'replaces'."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: This replaces the old authentication system with a new implementation
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: OAuth integration
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_migrated_from_state_change(self):
        """Should detect 'migrated from' state change language."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Migrated from legacy authentication to modern OAuth
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: OAuth integration
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_new_old_references(self):
        """Should detect 'new' and 'old' implementation references."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: New implementation using modern security standards
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: New OAuth integration
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)


class TestFutureReferenceDetection:
    """Test detection of future reference language."""

    def test_detects_will_be_future_reference(self):
        """Should detect future reference language."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Will be extended to support biometric authentication
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: OAuth integration
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_planned_future_reference(self):
        """Should detect 'planned' future reference."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Handles OAuth authentication with planned biometric support
Dependencies: oauth2
Exports: AuthHandler
Interfaces: authenticate()
Implementation: OAuth integration
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any(
            "temporal" in v.message.lower() or "planned" in v.message.lower() for v in violations
        )


class TestAcceptableLanguage:
    """Test that present-tense factual descriptions are accepted."""

    def test_accepts_present_tense_factual(self):
        """Should accept present-tense factual descriptions."""
        code = '''"""
Purpose: Authentication handler for user login
Scope: Authentication module across the application
Overview: Handles user authentication using OAuth and SAML protocols.
    Provides secure login functionality with session management and token handling.
    Supports multi-factor authentication and password reset workflows.
Dependencies: oauth2, saml, bcrypt
Exports: AuthHandler, AuthToken, AuthError
Interfaces: authenticate(), validate_token(), refresh_session()
Implementation: Uses JWT tokens with 24-hour expiration and refresh token rotation
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Filter only temporal violations
        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0

    def test_accepts_descriptive_implementation_details(self):
        """Should accept factual implementation descriptions without temporal references."""
        code = '''"""
Purpose: Payment processing service
Scope: Payment handling and transaction management
Overview: Processes payment transactions using Stripe API integration.
    Implements retry logic with exponential backoff for transient failures.
    Handles payment method validation and charge creation.
Dependencies: stripe, redis, logging
Exports: PaymentProcessor, PaymentError
Interfaces: process_payment(), refund_payment()
Implementation: Uses Redis for deduplication and caches payment methods
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should have no temporal violations
        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0
