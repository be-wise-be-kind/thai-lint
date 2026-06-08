"""
Purpose: Unit tests for Jinja/HTML template file header validation

Scope: Testing Jinja and HTML template header parsing and validation requirements

Overview: Test suite for Jinja/HTML template file header validation including Jinja
    comment block ({# ... #}) and HTML comment block (<!-- ... -->) header extraction,
    mandatory field detection, atemporal language validation, and edge case handling.
    Tests cover .html and .jinja templates with HTML-specific mandatory fields (Purpose,
    Scope, Overview). Validates that a comment block appearing before {% extends %} or
    markup is treated as the header and that missing fields are reported with line numbers.

Dependencies: conftest fixtures (VALID_HTML_HEADER, VALID_HTML_COMMENT_HEADER,
    HTML_NO_HEADER, create_mock_context), src.linters.file_header.linter.FileHeaderRule

Exports: TestHtmlHeaderExtraction, TestHtmlMandatoryFields, TestHtmlAtemporalLanguage,
    TestHtmlEdgeCases test classes

Interfaces: test_extracts_jinja_comment_header, test_extracts_html_comment_header,
    test_detects_missing_purpose_field, and other test methods

Implementation: Uses conftest fixtures for valid and invalid HTML headers, validates
    Jinja {# #} and HTML <!-- --> comment detection
"""

from tests.unit.linters.file_header.conftest import (
    HTML_NO_HEADER,
    VALID_HTML_COMMENT_HEADER,
    VALID_HTML_HEADER,
    create_mock_context,
)


class TestHtmlHeaderExtraction:
    """Test extraction of comment block headers from Jinja/HTML templates."""

    def test_extracts_jinja_comment_header(self):
        """Should extract Jinja {# #} comment block header."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_HTML_HEADER, "orders.html", "html")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Valid Jinja comment header should be detected"

    def test_extracts_html_comment_header(self):
        """Should extract HTML <!-- --> comment block header."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_HTML_COMMENT_HEADER, "hero.html", "html")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Valid HTML comment header should be detected"

    def test_extracts_header_from_jinja_extension(self):
        """Should extract header from a .jinja file."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_HTML_HEADER, "page.jinja", "html")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, ".jinja file with header should be valid"

    def test_detects_missing_header(self):
        """Should detect when template has no header comment block."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(HTML_NO_HEADER, "orders.html", "html")
        violations = rule.check(context)

        assert len(violations) >= 1, "Should detect missing header"
        assert any(
            "missing" in v.message.lower() or "header" in v.message.lower() for v in violations
        )


class TestHtmlMandatoryFields:
    """Test mandatory field detection in Jinja/HTML headers."""

    def test_detects_missing_purpose_field(self):
        """Should detect when Purpose field is missing."""
        code = """{#
Scope: Customer Portal, order-history view.
Overview: Renders the order-history table.
#}
{% extends "newmain.html" %}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "orders.html", "html")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)

    def test_detects_missing_scope_field(self):
        """Should detect when Scope field is missing."""
        code = """{#
Purpose: Customer-portal order-history page.
Overview: Renders the order-history table.
#}
{% extends "newmain.html" %}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "orders.html", "html")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Scope" in v.message for v in violations)

    def test_detects_missing_overview_field(self):
        """Should detect when Overview field is missing."""
        code = """{#
Purpose: Customer-portal order-history page.
Scope: Customer Portal, order-history view.
#}
{% extends "newmain.html" %}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "orders.html", "html")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Overview" in v.message for v in violations)

    def test_accepts_all_mandatory_fields_present(self):
        """Should accept HTML header with all mandatory fields."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_HTML_HEADER, "orders.html", "html")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "All mandatory fields are present"


class TestHtmlAtemporalLanguage:
    """Test atemporal language detection in Jinja/HTML headers."""

    def test_detects_currently_keyword(self):
        """Should detect 'currently' temporal language."""
        code = """{#
Purpose: Customer-portal order-history page.
Scope: Customer Portal, order-history view.
Overview: Currently renders the order-history table.
#}
{% extends "newmain.html" %}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "orders.html", "html")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'currently'"

    def test_accepts_atemporal_language(self):
        """Should accept present-tense, factual descriptions."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_HTML_HEADER, "orders.html", "html")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0, "Valid header has no temporal language"


class TestHtmlEdgeCases:
    """Test edge cases in Jinja/HTML header validation."""

    def test_handles_empty_file(self):
        """Should handle empty template file gracefully."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context("", "test.html", "html")
        violations = rule.check(context)

        assert len(violations) >= 1

    def test_handles_multiline_field_values(self):
        """Should handle multi-line field values in Jinja comment."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_HTML_HEADER, "orders.html", "html")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "Multi-line fields should be parsed"
