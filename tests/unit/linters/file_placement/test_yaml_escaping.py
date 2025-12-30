"""Test YAML escaping for file placement patterns."""

import logging
import re
from pathlib import Path

import pytest
import yaml

logger = logging.getLogger(__name__)


class TestYamlPatternEscaping:
    """Tests to debug YAML pattern escaping issues."""

    def test_yaml_single_quote_one_backslash(self) -> None:
        """Test single-quoted YAML string with one backslash."""
        yaml_content = """
patterns:
  single: '.*\\.py$'
"""
        parsed = yaml.safe_load(yaml_content)
        pattern = parsed["patterns"]["single"]

        logger.info(f"Pattern repr: {repr(pattern)}")
        logger.info(f"Pattern length: {len(pattern)}")
        logger.info(f"Pattern chars: {list(pattern)}")

        # In YAML single quotes, \\ is two literal backslashes
        # So '.*\\.py$' means the pattern is '.*\.py$' (7 chars)
        assert len(pattern) == 7, f"Expected 7 chars, got {len(pattern)}: {repr(pattern)}"
        assert pattern == r".*\.py$"

    def test_yaml_single_quote_two_backslashes(self) -> None:
        """Test single-quoted YAML string with two backslashes."""
        yaml_content = """
patterns:
  double: '.*\\\\.py$'
"""
        parsed = yaml.safe_load(yaml_content)
        pattern = parsed["patterns"]["double"]

        logger.info(f"Pattern repr: {repr(pattern)}")
        logger.info(f"Pattern length: {len(pattern)}")
        logger.info(f"Pattern chars: {list(pattern)}")

        # In YAML single quotes, \\\\ is four literal backslashes
        # So '.*\\\\.py$' means the pattern is '.*\\.py$' (8 chars)
        assert len(pattern) == 8, f"Expected 8 chars, got {len(pattern)}: {repr(pattern)}"
        assert pattern == r".*\\.py$"

    def test_actual_config_file_escaping(self) -> None:
        """Test actual .thailint.yaml file pattern escaping."""
        with Path(".thailint.yaml").open() as f:
            config = yaml.safe_load(f)

        src_allow = config["file-placement"]["directories"]["src"]["allow"]
        logger.info(f"src allow patterns: {src_allow}")

        # Check that the first pattern (Python files) has correct escaping
        py_pattern = src_allow[0]
        logger.info(f"Python pattern repr: {repr(py_pattern)}")
        logger.info(f"Pattern chars: {list(py_pattern)}")

        # Pattern should have single backslash for escaping (not double)
        # r".*\.py$" has 7 chars, r".*\\.py$" would have 8 chars
        expected = r".*\.py$"
        assert py_pattern == expected, f"Expected {repr(expected)}, got {repr(py_pattern)}"

        # Verify patterns don't have double backslashes (common YAML escaping mistake)
        for pattern in src_allow:
            assert "\\\\" not in pattern, f"Pattern has double backslash: {repr(pattern)}"

    def test_pattern_matching_correct_pattern(self) -> None:
        """Test that correct pattern matches .py files."""
        correct_pattern = r".*\.py$"
        test_path = "src/linters/file_placement/rule_checker.py"

        compiled = re.compile(correct_pattern, re.IGNORECASE)
        match = compiled.search(test_path)

        logger.info(f"Pattern: {repr(correct_pattern)}")
        logger.info(f"Path: {test_path}")
        logger.info(f"Match: {match}")

        assert match is not None, "Correct pattern should match .py file"

    def test_pattern_matching_double_backslash_pattern(self) -> None:
        """Test that double-backslash pattern does NOT match .py files."""
        wrong_pattern = r".*\\.py$"  # Two backslashes - matches literal backslash
        test_path = "src/linters/file_placement/rule_checker.py"

        compiled = re.compile(wrong_pattern, re.IGNORECASE)
        match = compiled.search(test_path)

        logger.info(f"Pattern: {repr(wrong_pattern)}")
        logger.info(f"Path: {test_path}")
        logger.info(f"Match: {match}")

        assert match is None, "Double-backslash pattern should NOT match normal .py file"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v", "-s"])
