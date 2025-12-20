"""
Purpose: Unit tests for duplicate constants detection in DRY linter

Scope: Tests for detecting duplicate constant definitions across multiple files

Overview: Comprehensive test suite for the duplicate constants detection feature of the
    DRY linter. Tests cover Python and TypeScript constant extraction, exact matching,
    fuzzy matching (word-set and edit distance), configuration options, and violation
    message formatting. Follows TDD methodology - tests written before implementation.

Dependencies: pytest, pathlib, src.Linter

Exports: Test classes for duplicate constants feature

Interfaces: Uses Linter class with config file and rules=['dry.duplicate-code']

Implementation: Uses tmp_path for isolated file fixtures with TDD approach
"""

from pathlib import Path

from src import Linter


class TestPythonConstantDetection:
    """Tests for detecting Python constants."""

    def test_single_file_constant_no_violation(self, tmp_path: Path):
        """Single file with constant should not produce violation."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Filter for constant-related violations only
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_two_files_same_constant_name_reports_violation(self, tmp_path: Path):
        """Same constant name in two files should produce violation."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("API_TIMEOUT = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1
        assert any("API_TIMEOUT" in v.message for v in violations)

    def test_two_files_different_constants_no_violation(self, tmp_path: Path):
        """Different constant names should not produce violation."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("MAX_RETRIES = 5\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_ignores_lowercase_names(self, tmp_path: Path):
        """Lowercase names should not be considered constants."""
        file1 = tmp_path / "module1.py"
        file1.write_text("api_timeout = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("api_timeout = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Should not report - lowercase are not constants
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_ignores_private_underscore_constants(self, tmp_path: Path):
        """Private constants (leading underscore) should be ignored."""
        file1 = tmp_path / "module1.py"
        file1.write_text("_INTERNAL_CONST = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("_INTERNAL_CONST = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Private constants should be ignored
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_module_level_only_not_class_level(self, tmp_path: Path):
        """Only module-level constants should be detected, not class-level."""
        file1 = tmp_path / "module1.py"
        file1.write_text(
            """
class Config:
    API_TIMEOUT = 30
"""
        )

        file2 = tmp_path / "module2.py"
        file2.write_text(
            """
class Settings:
    API_TIMEOUT = 60
"""
        )

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Class-level constants should not be detected
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0


class TestTypeScriptConstantDetection:
    """Tests for detecting TypeScript constants."""

    def test_typescript_const_uppercase_detected(self, tmp_path: Path):
        """TypeScript const with UPPER_SNAKE_CASE should be detected."""
        file1 = tmp_path / "module1.ts"
        file1.write_text("export const API_TIMEOUT = 30;\n")

        file2 = tmp_path / "module2.ts"
        file2.write_text("const API_TIMEOUT = 60;\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1
        assert any("API_TIMEOUT" in v.message for v in violations)

    def test_typescript_let_uppercase_not_detected(self, tmp_path: Path):
        """TypeScript let (not const) should not be detected."""
        file1 = tmp_path / "module1.ts"
        file1.write_text("let API_TIMEOUT = 30;\n")

        file2 = tmp_path / "module2.ts"
        file2.write_text("let API_TIMEOUT = 60;\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # let is not a constant, should not be detected
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_typescript_camelcase_not_detected(self, tmp_path: Path):
        """TypeScript const with camelCase should not be detected."""
        file1 = tmp_path / "module1.ts"
        file1.write_text("const apiTimeout = 30;\n")

        file2 = tmp_path / "module2.ts"
        file2.write_text("const apiTimeout = 60;\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # camelCase is not a constant naming convention
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0


class TestFuzzyMatching:
    """Tests for fuzzy matching of constant names."""

    def test_word_set_match_reversed_order(self, tmp_path: Path):
        """API_TIMEOUT and TIMEOUT_API should match (same words, different order)."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("TIMEOUT_API = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1
        # Should indicate fuzzy match with both names
        combined_message = " ".join(v.message for v in violations)
        assert "API_TIMEOUT" in combined_message or "TIMEOUT_API" in combined_message

    def test_word_set_match_reordered(self, tmp_path: Path):
        """MAX_RETRY_COUNT and RETRY_MAX_COUNT should match (reordered words)."""
        file1 = tmp_path / "module1.py"
        file1.write_text("MAX_RETRY_COUNT = 3\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("RETRY_MAX_COUNT = 5\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1

    def test_edit_distance_match_typo(self, tmp_path: Path):
        """MAX_RETRYS and MAX_RETRIES should match (typo, edit distance <= 2)."""
        file1 = tmp_path / "module1.py"
        file1.write_text("MAX_RETRYS = 3\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("MAX_RETRIES = 5\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1

    def test_single_word_exact_only_no_fuzzy(self, tmp_path: Path):
        """Single-word constants should only use exact matching."""
        # MAX and MIN are different - should not fuzzy match
        file1 = tmp_path / "module1.py"
        file1.write_text("MAX = 100\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("MIN = 0\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Single-word constants should not fuzzy match
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_fuzzy_requires_2_plus_words(self, tmp_path: Path):
        """Fuzzy matching should only apply to constants with 2+ words."""
        # Same single-word constant in two files - exact match should work
        file1 = tmp_path / "module1.py"
        file1.write_text("TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("TIMEOUT = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Exact match should still work for single-word constants
        assert len(violations) >= 1
        assert any("TIMEOUT" in v.message for v in violations)

    def test_antonym_pairs_not_fuzzy_matched(self, tmp_path: Path):
        """Constants with antonym words (MAX vs MIN) should NOT be fuzzy matched."""
        file1 = tmp_path / "module1.py"
        file1.write_text("RETRY_MAX_WAIT = 60\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("RETRY_MIN_WAIT = 1\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # MAX vs MIN are antonyms - should NOT be matched as similar constants
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_antonym_start_end_not_fuzzy_matched(self, tmp_path: Path):
        """Constants with START vs END antonyms should NOT be fuzzy matched."""
        file1 = tmp_path / "module1.py"
        file1.write_text("INDEX_START_OFFSET = 0\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("INDEX_END_OFFSET = 100\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # START vs END are antonyms - should NOT be matched
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0


class TestSingleLetterConstantFiltering:
    """Tests for filtering out single-letter constant names."""

    def test_single_letter_type_params_ignored(self, tmp_path: Path):
        """Single-letter type parameters (P, T, K, V) should not be detected."""
        file1 = tmp_path / "module1.py"
        file1.write_text("from typing import ParamSpec\nP = ParamSpec('P')\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("from typing import ParamSpec\nP = ParamSpec('P')\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Single-letter names like P should be ignored
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        # Filter for violations that specifically mention single-letter P
        p_violations = [v for v in constant_violations if "'P'" in v.message]
        assert len(p_violations) == 0

    def test_single_letter_typevar_ignored(self, tmp_path: Path):
        """Single-letter TypeVars (T) should not be detected."""
        file1 = tmp_path / "module1.py"
        file1.write_text("from typing import TypeVar\nT = TypeVar('T')\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("from typing import TypeVar\nT = TypeVar('T')\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Single-letter names like T should be ignored
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        t_violations = [v for v in constant_violations if "'T'" in v.message]
        assert len(t_violations) == 0

    def test_two_letter_constants_still_detected(self, tmp_path: Path):
        """Two-letter constants (OK, ID) should still be detected."""
        file1 = tmp_path / "module1.py"
        file1.write_text("OK = 200\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("OK = 200\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Two-letter constants like OK should still be detected
        assert len(violations) >= 1
        assert any("OK" in v.message for v in violations)


class TestConfiguration:
    """Tests for duplicate constants configuration."""

    def test_enabled_by_default(self, tmp_path: Path):
        """Duplicate constants detection should be enabled by default."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("API_TIMEOUT = 60\n")

        # Config without detect_duplicate_constants - should still detect
        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Feature is enabled by default, should detect constants
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) >= 1

    def test_disabled_via_config_flag(self, tmp_path: Path):
        """Duplicate constants detection can be disabled via config."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("API_TIMEOUT = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: false\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Feature is explicitly disabled, should not detect constants
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0

    def test_respects_min_occurrences_threshold(self, tmp_path: Path):
        """Should respect min_constant_occurrences threshold."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("API_TIMEOUT = 60\n")

        # Set threshold to 3 - need 3+ files to report
        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n"
            "  min_constant_occurrences: 3\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        # Only 2 files, threshold is 3, should not report
        constant_violations = [v for v in violations if "constant" in v.message.lower()]
        assert len(constant_violations) == 0


class TestViolationMessages:
    """Tests for violation message formatting."""

    def test_violation_includes_all_file_locations(self, tmp_path: Path):
        """Violation message should include all file locations."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("API_TIMEOUT = 60\n")

        file3 = tmp_path / "module3.py"
        file3.write_text("API_TIMEOUT = 45\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1
        # Message should reference multiple files
        combined_message = " ".join(v.message for v in violations)
        assert "module" in combined_message.lower()

    def test_violation_shows_values_for_context(self, tmp_path: Path):
        """Violation message should show values for context."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("API_TIMEOUT = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1
        # Message should show values (30 and 60)
        combined_message = " ".join(v.message for v in violations)
        assert "30" in combined_message or "60" in combined_message

    def test_fuzzy_match_shows_both_names(self, tmp_path: Path):
        """Fuzzy match violation should show both constant names."""
        file1 = tmp_path / "module1.py"
        file1.write_text("API_TIMEOUT = 30\n")

        file2 = tmp_path / "module2.py"
        file2.write_text("TIMEOUT_API = 60\n")

        config = tmp_path / ".thailint.yaml"
        config.write_text(
            "dry:\n  enabled: true\n  detect_duplicate_constants: true\n  cache_enabled: false"
        )

        linter = Linter(config_file=config, project_root=tmp_path)
        violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

        assert len(violations) >= 1
        # Message should show both names for fuzzy match
        combined_message = " ".join(v.message for v in violations)
        assert "API_TIMEOUT" in combined_message
        assert "TIMEOUT_API" in combined_message
