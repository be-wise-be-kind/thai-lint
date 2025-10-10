"""
Purpose: Test that single logical statements spanning multiple lines are NOT flagged

Scope: Verify DRY linter doesn't flag single statements as duplicate code

Overview: Tests that multi-line formatting of a single logical statement (like a decorator,
    function call, or list/dict literal) is not incorrectly flagged as duplicate code.
    A single statement that happens to span 3+ lines should not trigger a DRY violation,
    even if the same statement appears multiple times.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Test functions for single-statement filtering

Implementation: Creates files with identical multi-line single statements and verifies
    they are NOT flagged as violations.
"""

from src import Linter


def test_single_decorator_multiline_not_duplicate(tmp_path):
    """Test that a single decorator spanning 3 lines is NOT flagged as duplicate.

    This tests the real-world case where Click decorators are formatted across
    multiple lines for readability, but are logically a single statement.
    """
    file1 = tmp_path / "command1.py"
    file1.write_text("""
import click

@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text"
)
def command_one():
    return "one"
""")

    file2 = tmp_path / "command2.py"
    file2.write_text("""
import click

@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text"
)
def command_two():
    return "two"
""")

    file3 = tmp_path / "command3.py"
    file3.write_text("""
import click

@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text"
)
def command_three():
    return "three"
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Single statement (decorator) should NOT be flagged as duplicate
    assert len(violations) == 0, "Single decorator statement should not be flagged"


def test_single_function_call_multiline_not_duplicate(tmp_path):
    """Test that a single multi-line function call is NOT flagged as duplicate."""
    file1 = tmp_path / "config1.py"
    file1.write_text("""
result_one = some_function(
    arg1="value1", arg2="value2", arg3="value3"
)
""")

    file2 = tmp_path / "config2.py"
    file2.write_text("""
result_two = some_function(
    arg1="value1", arg2="value2", arg3="value3"
)
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Single function call should NOT be flagged as duplicate
    assert len(violations) == 0, "Single function call statement should not be flagged"


def test_constructor_arguments_not_duplicate(tmp_path):
    """Test that multi-line constructor arguments are NOT flagged as duplicate.

    This tests the real-world case from cache.py where CodeBlock constructor
    calls spanning multiple lines appear in multiple methods, but the arguments
    themselves (3 lines of key=value pairs) should not be flagged.
    """
    file1 = tmp_path / "loader1.py"
    file1.write_text("""
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeBlock:
    file_path: Path
    start_line: int
    end_line: int
    snippet: str
    hash_value: int

def load_blocks():
    blocks = []
    for hash_val, start, end, snippet in cursor:
        block = CodeBlock(
            file_path=file_path,
            start_line=start,
            end_line=end,
            snippet=snippet,
            hash_value=hash_val,
        )
        blocks.append(block)
    return blocks
""")

    file2 = tmp_path / "loader2.py"
    file2.write_text("""
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeBlock:
    file_path: Path
    start_line: int
    end_line: int
    snippet: str
    hash_value: int

def find_blocks():
    blocks = []
    for file_path_str, start, end, snippet, hash_val in rows:
        block = CodeBlock(
            file_path=Path(file_path_str),
            start_line=start,
            end_line=end,
            snippet=snippet,
            hash_value=hash_val,
        )
        blocks.append(block)
    return blocks
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Constructor arguments should NOT be flagged - they're part of a single statement
    assert len(violations) == 0, "Constructor arguments should not be flagged as duplicate"
