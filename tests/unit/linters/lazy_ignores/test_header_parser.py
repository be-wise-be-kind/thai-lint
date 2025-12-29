"""
Purpose: Tests for header Suppressions section parsing

Scope: Unit tests for extracting and validating Suppressions entries from file headers

Overview: Test suite for parsing the Suppressions section from Python docstring and
    TypeScript JSDoc file headers. Tests single and multiple suppression entries, rule ID
    normalization, and handling of missing or malformed sections.

Dependencies: pytest, src.linters.lazy_ignores.header_parser

Exports: Test classes for header parsing

Interfaces: pytest test discovery and execution

Implementation: Unit tests using SuppressionsParser
"""

from src.linters.lazy_ignores.header_parser import SuppressionsParser


class TestSuppressionsExtraction:
    """Tests for extracting Suppressions section from headers."""

    def test_parses_single_suppression(self) -> None:
        """Parses a single suppression entry."""
        header = '''"""
Purpose: Test file

Suppressions:
    PLR0912: Complex branching required for state machine
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert len(entries) == 1
        assert entries["plr0912"] == "Complex branching required for state machine"

    def test_parses_multiple_suppressions(self) -> None:
        """Parses multiple suppression entries."""
        header = '''"""
Purpose: Test file

Suppressions:
    PLR0912: State machine complexity
    type:ignore[arg-type]: Pydantic validation
    nosec B602: Trusted subprocess call
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert len(entries) == 3
        assert "plr0912" in entries
        assert "type:ignore[arg-type]" in entries
        assert "nosec b602" in entries

    def test_returns_empty_when_no_suppressions(self) -> None:
        """Returns empty dict when no Suppressions section."""
        header = '''"""
Purpose: Test file
Scope: Testing
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert entries == {}

    def test_handles_indented_suppressions(self) -> None:
        """Parses suppressions with various indentation levels."""
        header = '''"""
Purpose: Test file

Suppressions:
  PLR0912: Two-space indent
    PLR0915: Four-space indent
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert len(entries) == 2


class TestRuleIdNormalization:
    """Tests for rule ID normalization."""

    def test_normalizes_case(self) -> None:
        """Normalizes rule ID case for matching."""
        parser = SuppressionsParser()
        # These should all match the same rule
        assert parser.normalize_rule_id("PLR0912") == parser.normalize_rule_id("plr0912")

    def test_preserves_type_ignore_brackets(self) -> None:
        """Preserves type:ignore[code] format."""
        parser = SuppressionsParser()
        normalized = parser.normalize_rule_id("type:ignore[arg-type]")
        assert "arg-type" in normalized

    def test_normalizes_nosec_format(self) -> None:
        """Normalizes nosec B602 to consistent format."""
        parser = SuppressionsParser()
        assert parser.normalize_rule_id("nosec B602") == parser.normalize_rule_id("NOSEC b602")


class TestHeaderExtraction:
    """Tests for extracting header section from code."""

    def test_extracts_python_docstring_header(self) -> None:
        """Extracts Python triple-quoted docstring header."""
        code = '''"""
Purpose: Test
Suppressions:
    PLR0912: Reason
"""

def func():
    pass
'''
        parser = SuppressionsParser()
        header = parser.extract_header(code, language="python")
        assert "Purpose" in header
        assert "Suppressions" in header

    def test_extracts_typescript_jsdoc_header(self) -> None:
        """Extracts TypeScript JSDoc header."""
        code = """/**
 * Purpose: Test component
 *
 * Suppressions:
 *   @ts-ignore: Complex type inference
 */

export function Component() {}
"""
        parser = SuppressionsParser()
        header = parser.extract_header(code, language="typescript")
        assert "Purpose" in header
        assert "Suppressions" in header

    def test_handles_no_header(self) -> None:
        """Returns empty string when no header present."""
        code = "x = 1"
        parser = SuppressionsParser()
        header = parser.extract_header(code, language="python")
        assert header == ""


class TestThailintSuppressions:
    """Tests for thai-lint specific suppressions in header."""

    def test_parses_thailint_rule_suppression(self) -> None:
        """Parses thailint rule in Suppressions section."""
        header = '''"""
Purpose: Test file

Suppressions:
    magic-numbers: Configuration constants
    srp.violation: Framework adapter class
"""'''
        parser = SuppressionsParser()
        entries = parser.parse(header)
        assert "magic-numbers" in entries
        assert "srp.violation" in entries

    def test_validates_justification_not_empty(self) -> None:
        """Rejects empty justification strings."""
        header = '''"""
Purpose: Test file

Suppressions:
    PLR0912:
"""'''
        parser = SuppressionsParser()
        # Empty justifications should be excluded
        entries = parser.parse(header)
        assert "plr0912" not in entries
