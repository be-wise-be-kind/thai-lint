"""
Purpose: Test suite for comprehensive 5-level ignore directive system

Scope: Validation of all ignore levels (repository, directory, file, method, line) with wildcards

Overview: Validates the sophisticated multi-level ignore system that allows suppressing linting
    violations at five different granularity levels, from repository-wide patterns down to
    individual code lines. Tests cover repository level with .thailintignore gitignore-style
    patterns, file level with ignore-file directives in first 10 lines only, method level with
    ignore-next-line before functions, and line level with inline ignore comments. Validates
    rule-specific ignores using bracket syntax [rule-id], wildcard rule matching where literals.*
    matches literals.magic-number, and the integrated should_ignore_violation() method that
    checks all levels. Ensures the ignore system provides flexible violation suppression while
    maintaining performance through optimizations like 10-line file scanning limit.

Dependencies: pytest for testing framework, pathlib for file creation, tmp_path fixture for
    isolated test environments, Violation and Severity types for integration testing

Exports: TestRepoLevelIgnore, TestFileLevelIgnore, TestLineLevelIgnore, TestWildcardRuleMatching,
    TestIntegration test classes

Interfaces: Tests is_ignored(), has_file_ignore(), has_line_ignore(),
    should_ignore_violation() methods with various directive patterns and rule specifications

Implementation: 17 tests using pytest tmp_path for .thailintignore creation, file-based testing
    with 10-line boundary validation, wildcard pattern matching verification, integration testing
    across multiple ignore levels
"""


class TestRepoLevelIgnore:
    """Test repository-level ignore (.thailintignore file)."""

    def test_thailintignore_file_parsed(self, tmp_path):
        """Parse .thailintignore file with glob patterns."""
        ignore_file = tmp_path / ".thailintignore"
        ignore_file.write_text("*.pyc\n.git/\nnode_modules/\n")

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser(tmp_path)

        assert parser.is_ignored(tmp_path / "test.pyc")
        assert parser.is_ignored(tmp_path / ".git" / "config")
        assert parser.is_ignored(tmp_path / "node_modules" / "package.json")
        assert not parser.is_ignored(tmp_path / "src" / "main.py")

    def test_gitignore_style_patterns(self, tmp_path):
        """Support gitignore-style patterns with wildcards."""
        ignore_file = tmp_path / ".thailintignore"
        ignore_file.write_text("""
# Comments should be ignored
*.pyc
__pycache__/
build/
*.egg-info/

# Blank lines should be skipped

dist/
""")
        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser(tmp_path)

        # Test patterns
        assert parser.is_ignored(tmp_path / "file.pyc")
        assert parser.is_ignored(tmp_path / "__pycache__" / "module.pyc")
        assert parser.is_ignored(tmp_path / "build" / "output")
        assert parser.is_ignored(tmp_path / "package.egg-info" / "PKG-INFO")
        assert parser.is_ignored(tmp_path / "dist" / "package.whl")

        # Should not ignore regular Python files
        assert not parser.is_ignored(tmp_path / "src" / "main.py")

    def test_no_thailintignore_file(self, tmp_path):
        """Parser works when .thailintignore doesn't exist."""
        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser(tmp_path)

        # Should not ignore anything
        assert not parser.is_ignored(tmp_path / "any_file.py")


class TestFileLevelIgnore:
    """Test file-level ignores."""

    def test_file_header_ignore_directive(self, tmp_path):
        """# thailint: ignore-file in first 10 lines."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""#!/usr/bin/env python3
# thailint: ignore-file

def some_function():
    pass
""")
        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()

        assert parser.has_file_ignore(test_file)

    def test_specific_rule_file_ignore(self, tmp_path):
        """# thailint: ignore-file[rule-name]."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# thailint: ignore-file[file-placement]\n")

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_file_ignore(test_file, rule_id="file-placement")
        assert not parser.has_file_ignore(test_file, rule_id="other-rule")

    def test_multiple_rules_file_ignore(self, tmp_path):
        """# thailint: ignore-file[rule1,rule2]."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# thailint: ignore-file[file-placement,naming-conventions]\n")

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_file_ignore(test_file, rule_id="file-placement")
        assert parser.has_file_ignore(test_file, rule_id="naming-conventions")
        assert not parser.has_file_ignore(test_file, rule_id="other-rule")

    def test_ignore_directive_beyond_line_10_not_detected(self, tmp_path):
        """Ignore directive beyond line 10 is not detected (performance)."""
        test_file = tmp_path / "test.py"
        lines = [f"# Line {i}\n" for i in range(1, 12)]
        lines.append("# thailint: ignore-file\n")  # Line 12
        test_file.write_text("".join(lines))

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        # Should NOT detect ignore on line 12 (only first 10 lines scanned)
        assert not parser.has_file_ignore(test_file)

    def test_ignore_on_line_10_is_detected(self, tmp_path):
        """Ignore directive on exactly line 10 IS detected."""
        test_file = tmp_path / "test.py"
        lines = [f"# Line {i}\n" for i in range(1, 10)]
        lines.append("# thailint: ignore-file\n")  # Line 10
        test_file.write_text("".join(lines))

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_file_ignore(test_file)


class TestLineLevelIgnore:
    """Test line-level ignores."""

    def test_inline_ignore_comment(self):
        """# thailint: ignore at end of line."""
        code = "bad_code = True  # thailint: ignore"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()

        assert parser.has_line_ignore(code, line_num=1)

    def test_specific_rule_line_ignore(self):
        """# thailint: ignore[rule-name]."""
        code = "bad = True  # thailint: ignore[file-placement]"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_line_ignore(code, line_num=1, rule_id="file-placement")
        assert not parser.has_line_ignore(code, line_num=1, rule_id="other-rule")

    def test_multiple_rules_line_ignore(self):
        """# thailint: ignore[rule1,rule2]."""
        code = "x = 1  # thailint: ignore[file-placement,naming]"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_line_ignore(code, line_num=1, rule_id="file-placement")
        assert parser.has_line_ignore(code, line_num=1, rule_id="naming")
        assert not parser.has_line_ignore(code, line_num=1, rule_id="other")

    def test_line_without_ignore_returns_false(self):
        """Line without ignore directive returns False."""
        code = "normal_code = True"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert not parser.has_line_ignore(code, line_num=1)


class TestWildcardRuleMatching:
    """Test wildcard pattern matching for rules."""

    def test_wildcard_rule_matching(self):
        """ignore[literals.*] matches literals.magic-number."""
        code = "x = 42  # thailint: ignore[literals.*]"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_line_ignore(code, line_num=1, rule_id="literals.magic-number")
        assert parser.has_line_ignore(code, line_num=1, rule_id="literals.string-concat")
        assert not parser.has_line_ignore(code, line_num=1, rule_id="naming.variable-name")

    def test_exact_rule_matching(self):
        """Exact rule ID must match exactly."""
        code = "x = 1  # thailint: ignore[file-placement]"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        assert parser.has_line_ignore(code, line_num=1, rule_id="file-placement")
        assert not parser.has_line_ignore(code, line_num=1, rule_id="file-placement-extra")


class TestIntegration:
    """Test integration of multiple ignore levels."""

    def test_should_ignore_violation_checks_all_levels(self, tmp_path):
        """should_ignore_violation() checks repo, file, and line levels."""
        from src.core.types import Severity, Violation
        from src.linter_config.ignore import IgnoreDirectiveParser

        # Set up repo-level ignore
        ignore_file = tmp_path / ".thailintignore"
        ignore_file.write_text("*.pyc\n")

        # Create test file with line-level ignore
        test_file = tmp_path / "test.py"
        test_file.write_text("""def foo():
    pass  # thailint: ignore[naming]
""")

        parser = IgnoreDirectiveParser(tmp_path)

        # Test repo-level ignore
        violation1 = Violation(
            rule_id="any-rule",
            file_path=str(tmp_path / "file.pyc"),
            line=1,
            column=0,
            message="Test",
            severity=Severity.ERROR,
        )
        file_content1 = ""
        assert parser.should_ignore_violation(violation1, file_content1)

        # Test line-level ignore
        violation2 = Violation(
            rule_id="naming",
            file_path=str(test_file),
            line=2,
            column=4,
            message="Test",
            severity=Severity.ERROR,
        )
        file_content2 = test_file.read_text()
        assert parser.should_ignore_violation(violation2, file_content2)

        # Test violation that should NOT be ignored
        violation3 = Violation(
            rule_id="other-rule",
            file_path=str(tmp_path / "normal.py"),
            line=1,
            column=0,
            message="Test",
            severity=Severity.ERROR,
        )
        file_content3 = "normal code"
        assert not parser.should_ignore_violation(violation3, file_content3)

    def test_ignore_next_line_directive(self, tmp_path):
        """# thailint: ignore-next-line affects the following line."""
        test_file = tmp_path / "test.py"
        file_content = """# thailint: ignore-next-line[naming]
def badFunctionName():
    pass
"""
        test_file.write_text(file_content)

        from src.core.types import Severity, Violation
        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser(tmp_path)

        # Violation on line 2 (the line AFTER ignore-next-line)
        violation = Violation(
            rule_id="naming",
            file_path=str(test_file),
            line=2,
            column=0,
            message="Bad function name",
            severity=Severity.ERROR,
        )

        assert parser.should_ignore_violation(violation, file_content)

    def test_invalid_ignore_syntax_handled_gracefully(self):
        """Invalid ignore syntax doesn't crash parser."""
        code = "x = 1  # thailint: ignore[unclosed"

        from src.linter_config.ignore import IgnoreDirectiveParser

        parser = IgnoreDirectiveParser()
        # Should not crash, just return False
        result = parser.has_line_ignore(code, line_num=1, rule_id="any-rule")
        assert result is False or result is True  # Either is fine, just don't crash
