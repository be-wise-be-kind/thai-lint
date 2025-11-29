"""
Purpose: Unit tests for CSS file header validation

Scope: Testing CSS and SCSS file header parsing and validation requirements

Overview: Comprehensive test suite for CSS file header validation including block comment
    header extraction, mandatory field detection, atemporal language validation, and edge
    case handling. Tests cover .css and .scss files with CSS-specific mandatory fields
    including Environment. Validates JSDoc-style comment detection and differentiates from
    regular block comments. Tests @charset directive handling and multi-line field values.

Dependencies: pytest, conftest fixtures (VALID_CSS_HEADER, CSS_NO_HEADER),
    src.linters.file_header.linter.FileHeaderRule

Exports: TestCssHeaderExtraction, TestCssMandatoryFields, TestCssAtemporalLanguage,
    TestCssEdgeCases test classes

Interfaces: test_extracts_block_comment_header, test_detects_missing_purpose_field,
    test_detects_currently_keyword, test_handles_css_with_charset, and other test methods

Implementation: Uses conftest fixtures for valid and invalid CSS headers, validates
    JSDoc-style comment requirement, tests CSS-specific features
"""

from tests.unit.linters.file_header.conftest import (
    CSS_NO_HEADER,
    VALID_CSS_HEADER,
    create_mock_context,
)


class TestCssHeaderExtraction:
    """Test extraction of block comment headers from CSS files."""

    def test_extracts_block_comment_header(self):
        """Should extract block comment header from CSS file."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_CSS_HEADER, "components.css", "css")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Valid block comment header should be detected"

    def test_extracts_header_from_scss_file(self):
        """Should extract header from SCSS file."""
        code = """/**
 * File: styles/variables.scss
 * Purpose: SCSS variables and mixins
 * Scope: Global style variables
 * Overview: Defines CSS custom properties, SCSS variables, and mixins
 *     used throughout the application styling system.
 * Dependencies: none
 * Exports: $primary-color, $spacing, @mixin button-style
 * Interfaces: CSS custom properties --color-*, --spacing-*
 * Environment: Sass preprocessor, CSS Grid support
 */

$primary-color: #007bff;
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "variables.scss", "css")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "SCSS file with header should be valid"

    def test_detects_missing_header(self):
        """Should detect when CSS file has no header."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(CSS_NO_HEADER, "styles.css", "css")
        violations = rule.check(context)

        assert len(violations) >= 1, "Should detect missing header"
        assert any(
            "missing" in v.message.lower() or "header" in v.message.lower() for v in violations
        )

    def test_distinguishes_jsdoc_style_from_regular_block(self):
        """Should require JSDoc-style comment (/**) not regular block (/*)."""
        code = """/*
 * This is a regular block comment
 * Purpose: Not JSDoc style
 */

.button {
    color: blue;
}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "styles.css", "css")
        violations = rule.check(context)

        # Regular block comments should not count as valid headers
        assert len(violations) >= 1, "Regular block comment is not JSDoc-style"


class TestCssMandatoryFields:
    """Test mandatory field detection in CSS headers."""

    def test_detects_missing_purpose_field(self):
        """Should detect when Purpose field is missing."""
        code = """/**
 * File: styles/test.css
 * Scope: Component styles
 * Overview: Test stylesheet
 * Dependencies: reset.css
 * Exports: .test-class
 * Interfaces: none
 * Environment: Browser
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.css", "css")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)

    def test_detects_missing_scope_field(self):
        """Should detect when Scope field is missing."""
        code = """/**
 * File: styles/test.css
 * Purpose: Test styles
 * Overview: Test stylesheet
 * Dependencies: reset.css
 * Exports: .test-class
 * Interfaces: none
 * Environment: Browser
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.css", "css")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Scope" in v.message for v in violations)

    def test_detects_missing_overview_field(self):
        """Should detect when Overview field is missing."""
        code = """/**
 * File: styles/test.css
 * Purpose: Test styles
 * Scope: Component styles
 * Dependencies: reset.css
 * Exports: .test-class
 * Interfaces: none
 * Environment: Browser
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.css", "css")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Overview" in v.message for v in violations)

    def test_detects_missing_environment_field(self):
        """Should detect when Environment field is missing (CSS-specific)."""
        code = """/**
 * File: styles/test.css
 * Purpose: Test styles
 * Scope: Component styles
 * Overview: Test stylesheet description
 * Dependencies: reset.css
 * Exports: .test-class
 * Interfaces: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.css", "css")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Environment" in v.message for v in violations)

    def test_accepts_all_mandatory_fields_present(self):
        """Should accept CSS header with all mandatory fields."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_CSS_HEADER, "components.css", "css")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "All mandatory fields are present"


class TestCssAtemporalLanguage:
    """Test atemporal language detection in CSS headers."""

    def test_detects_currently_keyword(self):
        """Should detect 'currently' temporal language."""
        code = """/**
 * File: styles/test.css
 * Purpose: Test styles
 * Scope: Component styles
 * Overview: Currently implements the button styling
 * Dependencies: reset.css
 * Exports: .btn
 * Interfaces: none
 * Environment: Browser
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.css", "css")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'currently'"

    def test_accepts_atemporal_language(self):
        """Should accept present-tense, factual descriptions."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_CSS_HEADER, "components.css", "css")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0, "Valid header has no temporal language"


class TestCssEdgeCases:
    """Test edge cases in CSS header validation."""

    def test_handles_empty_file(self):
        """Should handle empty CSS file gracefully."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context("", "test.css", "css")
        violations = rule.check(context)

        assert len(violations) >= 1

    def test_handles_multiline_field_values(self):
        """Should handle multi-line field values in CSS comment."""
        code = """/**
 * File: styles/layout.css
 * Purpose: Layout styles for main application
 * Scope: Application-wide layout styles
 * Overview: Comprehensive layout system including grid definitions,
 *     flexbox utilities, and responsive breakpoints. Implements
 *     a 12-column grid system with automatic gutter spacing.
 * Dependencies: variables.css, reset.css
 * Exports: .container, .row, .col-*, .grid
 * Interfaces: CSS Grid areas, Flexbox containers
 * Environment: Modern browsers with CSS Grid support
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "layout.css", "css")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "Multi-line fields should be parsed"

    def test_handles_css_with_charset(self):
        """Should handle CSS file starting with @charset."""
        code = """@charset "UTF-8";
/**
 * File: styles/international.css
 * Purpose: Internationalization styles
 * Scope: Multi-language support
 * Overview: Styles for RTL and LTR language support
 * Dependencies: base.css
 * Exports: .rtl, .ltr classes
 * Interfaces: Direction-aware layout classes
 * Environment: Browser with unicode support
 */

.rtl {
    direction: rtl;
}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "international.css", "css")
        violations = rule.check(context)

        # @charset before header should be acceptable
        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "@charset should not prevent header detection"
