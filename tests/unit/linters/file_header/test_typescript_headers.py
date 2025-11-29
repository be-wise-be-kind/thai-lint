"""
File: tests/unit/linters/file_header/test_typescript_headers.py
Purpose: Test suite for TypeScript/JavaScript file header validation
Exports: TestTypeScriptHeaderExtraction, TestTypeScriptMandatoryFields, etc.
Depends: pytest, conftest fixtures, src.linters.file_header.linter.FileHeaderRule
Related: test_python_header_validation.py, test_multi_language_validation.py

Overview:
    Comprehensive tests for TypeScript and JavaScript file header validation
    including JSDoc comment extraction, mandatory field detection, atemporal
    language validation, and edge case handling. Tests cover .ts, .tsx, .js,
    and .jsx files with TypeScript-specific requirements. All tests initially
    fail (TDD RED phase) since TypeScript parser does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_typescript_headers.py -v
"""

from tests.unit.linters.file_header.conftest import (
    TYPESCRIPT_NO_HEADER,
    TYPESCRIPT_TEMPORAL_HEADER,
    VALID_TYPESCRIPT_HEADER,
    create_mock_context,
)


class TestTypeScriptHeaderExtraction:
    """Test extraction of JSDoc headers from TypeScript files."""

    def test_extracts_jsdoc_comment_from_ts_file(self):
        """Should extract JSDoc comment from TypeScript file."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_TYPESCRIPT_HEADER, "test.ts", "typescript")
        violations = rule.check(context)

        # Should not have "missing header" violation when valid JSDoc exists
        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Valid JSDoc header should be detected"

    def test_extracts_jsdoc_comment_from_tsx_file(self):
        """Should extract JSDoc comment from TSX (React) file."""
        code = """/**
 * File: src/components/Button.tsx
 * Purpose: Reusable button component
 * Scope: UI component library
 * Overview: Primary button component with variants for different contexts
 * Dependencies: react, styled-components
 * Exports: Button component
 * Props/Interfaces: ButtonProps interface
 * State/Behavior: Stateless presentational component
 */

import React from 'react';

export const Button: React.FC = () => <button>Click</button>;
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "Button.tsx", "typescript")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "TSX file with JSDoc should be valid"

    def test_extracts_jsdoc_comment_from_js_file(self):
        """Should extract JSDoc comment from JavaScript file."""
        code = """/**
 * File: src/utils/helper.js
 * Purpose: Helper utility functions
 * Scope: Application utilities
 * Overview: Common helper functions for data manipulation
 * Dependencies: lodash
 * Exports: helper functions
 * Props/Interfaces: none
 * State/Behavior: Stateless
 */

module.exports = { helper: () => {} };
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "helper.js", "javascript")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "JS file with JSDoc should be valid"

    def test_extracts_jsdoc_comment_from_jsx_file(self):
        """Should extract JSDoc comment from JSX file."""
        code = """/**
 * File: src/App.jsx
 * Purpose: Main application component
 * Scope: Application root
 * Overview: Root component that renders the application layout
 * Dependencies: react, react-router
 * Exports: App component
 * Props/Interfaces: none
 * State/Behavior: Manages app-level state
 */

import React from 'react';

export default function App() {
    return <div>App</div>;
}
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "App.jsx", "javascript")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "JSX file with JSDoc should be valid"

    def test_detects_missing_jsdoc_header(self):
        """Should detect when TypeScript file has no JSDoc header."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(TYPESCRIPT_NO_HEADER, "test.ts", "typescript")
        violations = rule.check(context)

        # Should have violation for missing header
        assert len(violations) >= 1, "Should detect missing JSDoc header"
        assert any(
            "missing" in v.message.lower() or "header" in v.message.lower() for v in violations
        ), "Should report missing header"

    def test_ignores_inline_comments(self):
        """Should not treat inline comments as file headers."""
        code = """// This is just a line comment, not a header
export const x = 1;
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        # Line comments are not valid JSDoc headers
        assert len(violations) >= 1, "Line comments should not be treated as headers"


class TestTypeScriptMandatoryFields:
    """Test mandatory field detection in TypeScript headers."""

    def test_detects_missing_purpose_field(self):
        """Should detect when Purpose field is missing from TypeScript header."""
        code = """/**
 * File: src/test.ts
 * Scope: Testing
 * Overview: Test module
 * Dependencies: none
 * Exports: none
 * Props/Interfaces: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Purpose" in v.message for v in violations)

    def test_detects_missing_scope_field(self):
        """Should detect when Scope field is missing from TypeScript header."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Overview: Test module description
 * Dependencies: none
 * Exports: none
 * Props/Interfaces: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Scope" in v.message for v in violations)

    def test_detects_missing_overview_field(self):
        """Should detect when Overview field is missing from TypeScript header."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Scope: Testing
 * Dependencies: none
 * Exports: none
 * Props/Interfaces: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Overview" in v.message for v in violations)

    def test_detects_missing_dependencies_field(self):
        """Should detect when Dependencies field is missing."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Scope: Testing
 * Overview: Test module description
 * Exports: none
 * Props/Interfaces: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Dependencies" in v.message for v in violations)

    def test_detects_missing_exports_field(self):
        """Should detect when Exports field is missing."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Scope: Testing
 * Overview: Test module description
 * Dependencies: none
 * Props/Interfaces: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Exports" in v.message for v in violations)

    def test_detects_missing_props_interfaces_field(self):
        """Should detect when Props/Interfaces field is missing."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Scope: Testing
 * Overview: Test module description
 * Dependencies: none
 * Exports: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Props" in v.message or "Interfaces" in v.message for v in violations)

    def test_detects_missing_state_behavior_field(self):
        """Should detect when State/Behavior field is missing."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Scope: Testing
 * Overview: Test module description
 * Dependencies: none
 * Exports: none
 * Props/Interfaces: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("State" in v.message or "Behavior" in v.message for v in violations)

    def test_accepts_all_mandatory_fields_present(self):
        """Should accept TypeScript header with all mandatory fields."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_TYPESCRIPT_HEADER, "test.ts", "typescript")
        violations = rule.check(context)

        # Filter only mandatory field violations
        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "All mandatory fields are present"


class TestTypeScriptAtemporalLanguage:
    """Test atemporal language detection in TypeScript headers."""

    def test_detects_currently_keyword(self):
        """Should detect 'currently' temporal language."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(TYPESCRIPT_TEMPORAL_HEADER, "test.ts", "typescript")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'currently'"

    def test_detects_will_be_keyword(self):
        """Should detect 'will be' future reference."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(TYPESCRIPT_TEMPORAL_HEADER, "test.ts", "typescript")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'will be'"

    def test_detects_now_keyword(self):
        """Should detect 'now' temporal qualifier."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module
 * Scope: Testing
 * Overview: Now supports multiple authentication methods
 * Dependencies: none
 * Exports: none
 * Props/Interfaces: none
 * State/Behavior: none
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'now'"

    def test_accepts_atemporal_language(self):
        """Should accept present-tense, factual descriptions."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_TYPESCRIPT_HEADER, "test.ts", "typescript")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0, "Valid header has no temporal language"


class TestTypeScriptEdgeCases:
    """Test edge cases in TypeScript header validation."""

    def test_handles_empty_file(self):
        """Should handle empty TypeScript file gracefully."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context("", "test.ts", "typescript")
        violations = rule.check(context)

        # Should report missing header, not crash
        assert len(violations) >= 1

    def test_handles_only_whitespace(self):
        """Should handle file with only whitespace."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context("   \n\n   \n", "test.ts", "typescript")
        violations = rule.check(context)

        assert len(violations) >= 1

    def test_handles_malformed_jsdoc(self):
        """Should handle malformed JSDoc comment gracefully."""
        code = """/**
 * This is not properly formatted
 * Missing all required fields
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        # Should have violations for missing fields
        assert len(violations) >= 1

    def test_handles_multiline_field_values(self):
        """Should handle multi-line field values in JSDoc."""
        code = """/**
 * File: src/test.ts
 * Purpose: Test module with long description
 * Scope: Testing scope that spans
 *     multiple lines with proper indentation
 * Overview: Comprehensive overview that provides detailed
 *     information about the module functionality across
 *     several lines of text
 * Dependencies: lodash, react, typescript
 * Exports: Component, hook, utility
 * Props/Interfaces: TestProps, TestConfig
 * State/Behavior: Manages component state
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        # Should successfully parse multi-line values
        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "Multi-line fields should be parsed"

    def test_distinguishes_jsdoc_from_block_comment(self):
        """Should distinguish JSDoc (/**) from regular block comment (/*)."""
        code = """/*
 * This is a regular block comment, not JSDoc
 * Purpose: This should NOT be treated as a header
 */

export const x = 1;
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.ts", "typescript")
        violations = rule.check(context)

        # Regular block comments are not JSDoc headers
        assert len(violations) >= 1, "Block comment should not be treated as JSDoc"
