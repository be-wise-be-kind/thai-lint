"""
File: tests/unit/linters/file_header/test_markdown_headers.py
Purpose: Test suite for Markdown file header (YAML frontmatter) validation
Exports: TestMarkdownFrontmatterExtraction, TestMarkdownMandatoryFields, etc.
Depends: pytest, conftest fixtures, src.linters.file_header.linter.FileHeaderRule
Related: test_python_header_validation.py, test_multi_language_validation.py

Overview:
    Comprehensive tests for Markdown file header validation using YAML frontmatter
    format. Includes frontmatter extraction, mandatory field detection, YAML parsing,
    atemporal language validation, and edge case handling. Tests cover .md files with
    Markdown-specific requirements. All tests initially fail (TDD RED phase) since
    Markdown parser does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_markdown_headers.py -v
"""

from tests.unit.linters.file_header.conftest import (
    MARKDOWN_NO_FRONTMATTER,
    VALID_MARKDOWN_HEADER,
    create_mock_context,
)


class TestMarkdownFrontmatterExtraction:
    """Test extraction of YAML frontmatter from Markdown files."""

    def test_extracts_yaml_frontmatter(self):
        """Should extract YAML frontmatter between --- markers."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_MARKDOWN_HEADER, "architecture.md", "markdown")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Valid frontmatter should be detected"

    def test_detects_missing_frontmatter(self):
        """Should detect when Markdown file has no frontmatter."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(MARKDOWN_NO_FRONTMATTER, "readme.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1, "Should detect missing frontmatter"
        assert any(
            "missing" in v.message.lower() or "frontmatter" in v.message.lower() for v in violations
        )

    def test_extracts_frontmatter_with_list_values(self):
        """Should handle frontmatter with YAML list values."""
        code = """---
file: docs/guide.md
purpose: User guide
scope: Documentation
overview: Comprehensive user documentation
audience:
  - Users
  - Administrators
dependencies:
  - markdown
related:
  - docs/api.md
status: approved
updated: 2025-01-15
---

# User Guide
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "guide.md", "markdown")
        violations = rule.check(context)

        missing_header = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_header) == 0, "Frontmatter with lists should be valid"

    def test_handles_frontmatter_at_file_start_only(self):
        """Should only recognize frontmatter at the start of file."""
        code = """# Title First

---
file: docs/wrong.md
purpose: This is not frontmatter
---

Content here.
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "wrong.md", "markdown")
        violations = rule.check(context)

        # YAML not at start should not be recognized as frontmatter
        assert len(violations) >= 1, "Frontmatter must be at file start"


class TestMarkdownMandatoryFields:
    """Test mandatory field detection in Markdown frontmatter."""

    def test_detects_missing_purpose_field(self):
        """Should detect when purpose field is missing."""
        code = """---
file: docs/test.md
scope: Documentation
overview: Test document description
audience:
  - Engineers
related:
  - docs/other.md
status: draft
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("purpose" in v.message.lower() for v in violations)

    def test_detects_missing_scope_field(self):
        """Should detect when scope field is missing."""
        code = """---
file: docs/test.md
purpose: Test document
overview: Test document description
audience:
  - Engineers
related:
  - docs/other.md
status: draft
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("scope" in v.message.lower() for v in violations)

    def test_detects_missing_overview_field(self):
        """Should detect when overview field is missing."""
        code = """---
file: docs/test.md
purpose: Test document
scope: Documentation
audience:
  - Engineers
related:
  - docs/other.md
status: draft
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("overview" in v.message.lower() for v in violations)

    def test_detects_missing_audience_field(self):
        """Should detect when audience field is missing (Markdown-specific)."""
        code = """---
file: docs/test.md
purpose: Test document
scope: Documentation
overview: Test document description
related:
  - docs/other.md
status: draft
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("audience" in v.message.lower() for v in violations)

    def test_detects_missing_status_field(self):
        """Should detect when status field is missing (Markdown-specific)."""
        code = """---
file: docs/test.md
purpose: Test document
scope: Documentation
overview: Test document description
audience:
  - Engineers
related:
  - docs/other.md
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1
        assert any("status" in v.message.lower() for v in violations)

    def test_accepts_all_mandatory_fields_present(self):
        """Should accept Markdown frontmatter with all mandatory fields."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_MARKDOWN_HEADER, "architecture.md", "markdown")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "All mandatory fields are present"


class TestMarkdownYamlParsing:
    """Test YAML parsing in Markdown frontmatter."""

    def test_handles_invalid_yaml(self):
        """Should handle invalid YAML gracefully."""
        code = """---
file: docs/test.md
purpose: This has invalid YAML
  indentation: wrong
overview: broken
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        # Should report parsing error or missing fields
        assert len(violations) >= 1

    def test_handles_empty_frontmatter(self):
        """Should handle empty frontmatter block."""
        code = """---
---

# Empty Frontmatter
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1, "Empty frontmatter should have violations"

    def test_handles_multiline_string_values(self):
        """Should handle YAML multiline string values."""
        code = """---
file: docs/test.md
purpose: Test document
scope: Documentation
overview: |
  This is a multiline overview
  that spans several lines
  with proper YAML syntax
audience:
  - Engineers
related:
  - docs/other.md
status: approved
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        field_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(field_violations) == 0, "Multiline YAML should be parsed"


class TestMarkdownAtemporalLanguage:
    """Test atemporal language detection in Markdown frontmatter."""

    def test_detects_currently_in_overview(self):
        """Should detect 'currently' in overview field."""
        code = """---
file: docs/test.md
purpose: Test document
scope: Documentation
overview: This document currently describes the API
audience:
  - Engineers
related:
  - docs/other.md
status: approved
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'currently'"

    def test_detects_will_be_in_purpose(self):
        """Should detect 'will be' future reference in purpose."""
        code = """---
file: docs/test.md
purpose: This will be the main documentation
scope: Documentation
overview: Comprehensive documentation guide
audience:
  - Engineers
related:
  - docs/other.md
status: draft
updated: 2025-01-15
---

# Test
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) >= 1, "Should detect 'will be'"

    def test_accepts_atemporal_content(self):
        """Should accept present-tense, factual descriptions."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(VALID_MARKDOWN_HEADER, "architecture.md", "markdown")
        violations = rule.check(context)

        # Note: The valid header has 'updated: 2025-01-15' which is metadata, not prose
        # The atemporal check should focus on prose fields like overview, purpose
        temporal_violations = [
            v
            for v in violations
            if "temporal" in v.message.lower() and "updated" not in v.message.lower()
        ]
        # Prose fields in valid header should have no temporal language
        assert len(temporal_violations) == 0


class TestMarkdownEdgeCases:
    """Test edge cases in Markdown header validation."""

    def test_handles_empty_file(self):
        """Should handle empty Markdown file gracefully."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context("", "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1

    def test_handles_unclosed_frontmatter(self):
        """Should handle frontmatter without closing ---."""
        code = """---
file: docs/test.md
purpose: Unclosed frontmatter

# This might be interpreted as content
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        # Unclosed frontmatter should be flagged
        assert len(violations) >= 1

    def test_handles_only_title(self):
        """Should detect missing frontmatter when file has only a title."""
        code = """# Document Title

Some content without frontmatter.
"""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.md", "markdown")
        violations = rule.check(context)

        assert len(violations) >= 1, "Missing frontmatter should be detected"
