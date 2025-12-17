"""
Purpose: Test suite for stateless-class linter configuration and ignore system support

Scope: Configuration loading from .thailint.yaml and 5-level ignore directive system

Overview: TDD test suite for stateless-class linter configuration and ignore support
    covering config loading from .thailint.yaml, linter-specific ignore patterns,
    file-level ignore directives (# thailint: ignore-file), line-level ignore directives
    (# thailint: ignore), and block-level ignore directives. Tests define expected
    behavior following Red-Green-Refactor methodology to add full config support.

Dependencies: pytest for testing framework, src.linters.stateless_class for detector,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestConfigLoading, TestIgnorePatterns, TestFileLevelIgnore, TestLineLevelIgnore

Interfaces: Tests StatelessClassRule with config dict and ignore directives

Implementation: TDD approach - tests written to fail initially, then implementation
    makes them pass. Uses inline Python code strings as test fixtures with mock contexts.
"""

from pathlib import Path
from unittest.mock import Mock


class TestConfigLoading:
    """Test configuration loading from .thailint.yaml."""

    def test_loads_enabled_flag_from_config(self) -> None:
        """Should respect enabled: false in config to disable linter."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"stateless-class": {"enabled": False}}

        violations = rule.check(context)
        assert len(violations) == 0, "Linter should be disabled when enabled=False"

    def test_loads_min_methods_threshold_from_config(self) -> None:
        """Should respect min_methods threshold from config."""
        code = """
class ThreeMethodClass:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1

    def method3(self, z):
        return z - 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        # Default min_methods is 2, but set to 4 so this class passes
        context.config = {"stateless-class": {"min_methods": 4}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should not flag class when below min_methods threshold"

    def test_default_config_when_not_provided(self) -> None:
        """Should use default config when no config provided."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None  # No config

        violations = rule.check(context)
        assert len(violations) == 1, "Should use defaults and detect violation"


class TestIgnorePatterns:
    """Test linter-specific ignore patterns from config."""

    def test_ignores_file_matching_pattern(self) -> None:
        """Should ignore files matching ignore patterns in config."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("tests/test_helpers.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"stateless-class": {"ignore": ["tests/"]}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore files in tests/ directory"

    def test_ignores_file_matching_glob_pattern(self) -> None:
        """Should support glob patterns in ignore list."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/utils/helpers.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"stateless-class": {"ignore": ["**/helpers.py"]}}

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore files matching glob pattern"

    def test_does_not_ignore_non_matching_file(self) -> None:
        """Should not ignore files that don't match any pattern."""
        code = """
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("src/core/main.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = {"stateless-class": {"ignore": ["tests/", "**/helpers.py"]}}

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation in non-ignored file"


class TestFileLevelIgnore:
    """Test file-level ignore directives."""

    def test_ignores_file_with_ignore_file_directive(self) -> None:
        """Should ignore entire file with # thailint: ignore-file directive."""
        code = """# thailint: ignore-file
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore file with ignore-file directive"

    def test_ignores_file_with_rule_specific_ignore_file(self) -> None:
        """Should ignore file with rule-specific ignore directive."""
        code = """# thailint: ignore-file[stateless-class]
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore file with rule-specific directive"

    def test_does_not_ignore_file_with_different_rule_ignore(self) -> None:
        """Should not ignore file if ignore directive is for different rule."""
        code = """# thailint: ignore-file[srp]
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation when ignore is for different rule"


class TestLineLevelIgnore:
    """Test line-level ignore directives."""

    def test_ignores_class_with_inline_ignore_directive(self) -> None:
        """Should ignore class with inline # thailint: ignore comment."""
        code = """
class StatelessHelper:  # thailint: ignore
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore class with inline ignore"

    def test_ignores_class_with_rule_specific_inline_ignore(self) -> None:
        """Should ignore class with rule-specific inline ignore."""
        code = """
class StatelessHelper:  # thailint: ignore[stateless-class]
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore class with rule-specific inline ignore"

    def test_does_not_ignore_class_with_different_rule_inline_ignore(self) -> None:
        """Should not ignore class if inline ignore is for different rule."""
        code = """
class StatelessHelper:  # thailint: ignore[srp]
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation when ignore is for different rule"

    def test_ignores_class_with_ignore_next_line_directive(self) -> None:
        """Should ignore class with # thailint: ignore-next-line above it."""
        code = """
# thailint: ignore-next-line
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore class with ignore-next-line directive"


class TestBlockLevelIgnore:
    """Test block-level ignore directives."""

    def test_ignores_class_within_ignore_block(self) -> None:
        """Should ignore class within ignore-start/ignore-end block."""
        code = """
# thailint: ignore-start
class StatelessHelper:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
# thailint: ignore-end

class AnotherStateless:
    def method1(self, x):
        return x * 2

    def method2(self, y):
        return y + 1
"""
        from src.linters.stateless_class.linter import StatelessClassRule

        rule = StatelessClassRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should only flag class outside ignore block"
        assert "AnotherStateless" in violations[0].message


class TestConfigDataclass:
    """Test StatelessClassConfig dataclass."""

    def test_config_dataclass_exists(self) -> None:
        """StatelessClassConfig dataclass should exist."""
        from src.linters.stateless_class.config import StatelessClassConfig

        config = StatelessClassConfig()
        assert config.enabled is True, "Default enabled should be True"
        assert config.min_methods == 2, "Default min_methods should be 2"
        assert config.ignore == [], "Default ignore should be empty list"

    def test_config_from_dict(self) -> None:
        """StatelessClassConfig should load from dictionary."""
        from src.linters.stateless_class.config import StatelessClassConfig

        config = StatelessClassConfig.from_dict(
            {
                "enabled": False,
                "min_methods": 3,
                "ignore": ["tests/", "**/helpers.py"],
            }
        )
        assert config.enabled is False
        assert config.min_methods == 3
        assert config.ignore == ["tests/", "**/helpers.py"]

    def test_config_from_none(self) -> None:
        """StatelessClassConfig should use defaults when dict is None."""
        from src.linters.stateless_class.config import StatelessClassConfig

        config = StatelessClassConfig.from_dict(None)
        assert config.enabled is True
        assert config.min_methods == 2
        assert config.ignore == []
