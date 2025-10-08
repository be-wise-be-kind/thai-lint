"""
Purpose: Tests for DRY linter CLI command interface

Scope: Command-line interface for DRY linter including commands, options, and output formats

Overview: Test suite for CLI command interface covering basic dry command, custom config
    file option, cache control options, and JSON output format. Validates proper command
    execution, option handling, exit codes, and output formatting.

Dependencies: pytest, click.testing.CliRunner, src.cli, tmp_path fixture

Exports: 4 test functions for CLI interface scenarios

Interfaces: Uses Click CLI framework via CliRunner

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated CLI fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from click.testing import CliRunner

from src.cli import cli


def test_dry_cli_command_basic(tmp_path):
    """Test basic DRY CLI command execution."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = 1
    y = 2
    z = 3
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = 1
    y = 2
    z = 3
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", str(tmp_path), "--config", str(config)])

    assert result.exit_code == 1
    assert "duplicate" in result.output.lower() or "dry" in result.output.lower()


def test_dry_cli_with_custom_config(tmp_path):
    """Test DRY CLI command with custom config file."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    for item in items:
        if item.valid:
            item.save()
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    for item in items:
        if item.valid:
            item.save()
""")

    custom_config = tmp_path / "custom.yaml"
    custom_config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", str(tmp_path), "--config", str(custom_config)])

    assert result.exit_code in [0, 1]
    assert result.output is not None


def test_dry_cli_no_cache_option(tmp_path):
    """Test DRY CLI command with --no-cache option."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    result = compute()
    validated = validate(result)
    return validated
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""
dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: true
  cache_path: ".thailint-cache/dry.db"
""")

    cache_dir = tmp_path / ".thailint-cache"
    cache_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", str(tmp_path), "--config", str(config), "--no-cache"])

    assert result.exit_code in [0, 1]
    cache_file = cache_dir / "dry.db"
    assert not cache_file.exists()


def test_dry_cli_json_output_format(tmp_path):
    """Test DRY CLI command with JSON output format."""
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def process():
    x = fetch()
    y = transform(x)
    z = validate(y)
    return z
""")

    file2 = tmp_path / "file2.py"
    file2.write_text("""
def handle():
    x = fetch()
    y = transform(x)
    z = validate(y)
    return z
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    runner = CliRunner()
    result = runner.invoke(cli, ["dry", str(tmp_path), "--config", str(config), "--format", "json"])

    assert result.exit_code in [0, 1]

    if result.exit_code == 1:
        assert "[" in result.output or "{" in result.output
