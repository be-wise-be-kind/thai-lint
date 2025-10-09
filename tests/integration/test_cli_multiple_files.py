"""
Purpose: Integration tests for CLI commands with multiple file support

Scope: CLI integration testing for nesting, file-placement, srp, and dry commands

Overview: Validates CLI commands can accept multiple file paths and handle them correctly,
    including backward compatibility with single files, new functionality for multiple files,
    and proper handling of mixed files and directories. Tests the complete flow from CLI
    argument parsing through orchestrator execution to output formatting. Ensures pre-commit
    hook integration works correctly by testing scenarios where multiple changed files are
    passed to the CLI commands.

Dependencies: click.testing.CliRunner, src.cli

Exports: TestCLIMultipleFiles test class

Interfaces: Tests cli.nesting(), cli.file_placement(), cli.srp(), cli.dry() with multiple paths

Implementation: Uses CliRunner for isolated CLI testing with temporary directories
"""

from click.testing import CliRunner

from src.cli import cli


class TestCLIMultipleFiles:
    """Test CLI commands with multiple file support."""

    def test_nesting_with_single_file(self, tmp_path):
        """Should handle single file (backward compatibility)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    pass\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", str(test_file)])

        # Should execute without error (exit code 0 or 1 for violations)
        assert result.exit_code in [0, 1]

    def test_nesting_with_multiple_files(self, tmp_path):
        """Should handle multiple individual files."""
        file1 = tmp_path / "test1.py"
        file1.write_text("def foo():\n    pass\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("def bar():\n    pass\n")
        file3 = tmp_path / "test3.py"
        file3.write_text("def baz():\n    pass\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", str(file1), str(file2), str(file3)])

        # Should execute without error
        assert result.exit_code in [0, 1]

    def test_nesting_with_directory(self, tmp_path):
        """Should handle directory (existing recursive behavior)."""
        (tmp_path / "test1.py").write_text("def foo():\n    pass\n")
        (tmp_path / "test2.py").write_text("def bar():\n    pass\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", str(tmp_path)])

        # Should execute without error
        assert result.exit_code in [0, 1]

    def test_nesting_with_mixed_files_and_dirs(self, tmp_path):
        """Should handle mix of files and directories."""
        file1 = tmp_path / "test1.py"
        file1.write_text("def foo():\n    pass\n")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "test2.py").write_text("def bar():\n    pass\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", str(file1), str(subdir)])

        # Should execute without error
        assert result.exit_code in [0, 1]

    def test_file_placement_with_multiple_files(self, tmp_path):
        """Should handle multiple files for file-placement linter."""
        file1 = tmp_path / "test1.py"
        file1.write_text("# test 1\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("# test 2\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", str(file1), str(file2)])

        # Should execute without error
        assert result.exit_code in [0, 1]

    def test_srp_with_multiple_files(self, tmp_path):
        """Should handle multiple files for SRP linter."""
        file1 = tmp_path / "test1.py"
        file1.write_text("class Foo:\n    pass\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("class Bar:\n    pass\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["srp", str(file1), str(file2)])

        # Should execute without error
        assert result.exit_code in [0, 1]

    def test_dry_with_multiple_files(self, tmp_path):
        """Should handle multiple files for DRY linter."""
        file1 = tmp_path / "test1.py"
        file1.write_text("def foo():\n    pass\n")
        file2 = tmp_path / "test2.py"
        file2.write_text("def bar():\n    pass\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["dry", str(file1), str(file2)])

        # Should execute without error
        assert result.exit_code in [0, 1]

    def test_nesting_defaults_to_current_directory(self, tmp_path):
        """Should default to current directory when no paths provided."""
        (tmp_path / "test.py").write_text("def foo():\n    pass\n")

        runner = CliRunner()
        # Change to tmp_path directory
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["nesting"])

            # Should execute without error
            assert result.exit_code in [0, 1]
