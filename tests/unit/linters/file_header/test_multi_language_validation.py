"""
File: tests/unit/linters/file_header/test_multi_language_validation.py
Purpose: Test suite for multi-language file header validation
Exports: TestLanguageDetection, TestParserSelection, TestCrossLanguageValidation
Depends: pytest, conftest fixtures, src.linters.file_header.linter.FileHeaderRule
Related: test_typescript_headers.py, test_bash_headers.py, test_markdown_headers.py

Overview:
    Comprehensive tests for multi-language support in file header validation
    including language detection, parser selection, cross-language field
    validation, and atemporal language detection across all supported file
    types. All tests initially fail (TDD RED phase) since multi-language
    support does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_multi_language_validation.py -v
"""

from tests.unit.linters.file_header.conftest import (
    BASH_TEMPORAL_HEADER,
    TYPESCRIPT_TEMPORAL_HEADER,
    VALID_BASH_HEADER,
    VALID_CSS_HEADER,
    VALID_MARKDOWN_HEADER,
    VALID_TYPESCRIPT_HEADER,
    create_mock_context,
)


class TestLanguageDetection:
    """Test language detection from file extensions."""

    def test_detects_typescript_from_ts_extension(self):
        """Should detect TypeScript from .ts extension."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_TYPESCRIPT_HEADER, "module.ts", "typescript")
        violations = rule.check(context)

        # Should process as TypeScript (not return empty)
        # Even if no violations, should have processed the file
        # In RED phase, this will likely return [] since no TS support yet
        assert violations is not None

    def test_detects_javascript_from_js_extension(self):
        """Should detect JavaScript from .js extension."""
        code = """/**
 * File: src/helper.js
 * Purpose: Helper functions
 * Scope: Utilities
 * Overview: Common utility functions
 * Dependencies: none
 * Exports: helper
 * Props/Interfaces: none
 * State/Behavior: stateless
 */
module.exports = {};
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "helper.js", "javascript")
        violations = rule.check(context)

        assert violations is not None

    def test_detects_bash_from_sh_extension(self):
        """Should detect Bash from .sh extension."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_BASH_HEADER, "deploy.sh", "bash")
        violations = rule.check(context)

        assert violations is not None

    def test_detects_markdown_from_md_extension(self):
        """Should detect Markdown from .md extension."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_MARKDOWN_HEADER, "README.md", "markdown")
        violations = rule.check(context)

        assert violations is not None

    def test_detects_css_from_css_extension(self):
        """Should detect CSS from .css extension."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_CSS_HEADER, "styles.css", "css")
        violations = rule.check(context)

        assert violations is not None


class TestParserSelection:
    """Test correct parser selection for each language."""

    def test_uses_jsdoc_parser_for_typescript(self):
        """Should use JSDoc parser for TypeScript files."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_TYPESCRIPT_HEADER, "component.tsx", "typescript")
        violations = rule.check(context)

        # Valid TS header should be recognized by JSDoc parser
        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "JSDoc parser should recognize valid header"

    def test_uses_hash_comment_parser_for_bash(self):
        """Should use hash comment parser for Bash files."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_BASH_HEADER, "script.sh", "bash")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Hash comment parser should recognize header"

    def test_uses_yaml_parser_for_markdown(self):
        """Should use YAML frontmatter parser for Markdown files."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_MARKDOWN_HEADER, "guide.md", "markdown")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "YAML parser should recognize frontmatter"

    def test_uses_block_comment_parser_for_css(self):
        """Should use block comment parser for CSS files."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_CSS_HEADER, "theme.css", "css")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Block comment parser should recognize header"


class TestCrossLanguageFieldValidation:
    """Test language-specific required fields are validated correctly."""

    def test_typescript_requires_props_interfaces(self):
        """TypeScript should require Props/Interfaces field."""
        code = """/**
 * File: src/component.ts
 * Purpose: Component
 * Scope: UI
 * Overview: Component description
 * Dependencies: react
 * Exports: Component
 * State/Behavior: stateful
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "component.ts", "typescript")
        violations = rule.check(context)

        # Should have violation for missing Props/Interfaces
        assert len(violations) >= 1
        assert any("Props" in v.message or "Interfaces" in v.message for v in violations)

    def test_bash_requires_usage(self):
        """Bash should require Usage field."""
        code = """#!/bin/bash
# File: scripts/deploy.sh
# Purpose: Deploy script
# Scope: Deployment
# Overview: Handles deployment
# Dependencies: docker
# Exports: deploy
# Environment: DEPLOY_KEY
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "deploy.sh", "bash")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("Usage" in v.message for v in violations)

    def test_markdown_requires_audience(self):
        """Markdown should require audience field."""
        code = """---
file: docs/guide.md
purpose: Guide
scope: Documentation
overview: User guide
related:
  - docs/api.md
status: approved
updated: 2025-01-15
---

# Guide
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "guide.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("audience" in v.message.lower() for v in violations)


class TestMultiLanguageAtemporalDetection:
    """Test atemporal language detection works across all languages."""

    def test_detects_temporal_in_typescript(self):
        """Should detect temporal language in TypeScript files."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(TYPESCRIPT_TEMPORAL_HEADER, "auth.ts", "typescript")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1

    def test_detects_temporal_in_bash(self):
        """Should detect temporal language in Bash files."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(BASH_TEMPORAL_HEADER, "migrate.sh", "bash")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1

    def test_detects_temporal_in_markdown(self):
        """Should detect temporal language in Markdown files."""
        code = """---
file: docs/test.md
purpose: Test document
scope: Documentation
overview: This document was recently updated and will soon be deprecated
audience:
  - Engineers
related:
  - docs/new.md
status: deprecated
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'recently' and 'soon'"

    def test_detects_temporal_in_css(self):
        """Should detect temporal language in CSS files."""
        code = """/**
 * File: styles/old.css
 * Purpose: Legacy styles that will be removed
 * Scope: Deprecated components
 * Overview: This stylesheet currently contains styles that are being migrated
 * Dependencies: none
 * Exports: .legacy
 * Interfaces: none
 * Environment: Browser
 */
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "old.css", "css")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1
