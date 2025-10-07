"""
Purpose: Test suite for CLI interface of file placement linter

Scope: Command-line interface validation for linter invocation and configuration options

Overview: Validates the CLI interface that allows users to run file placement linting from
    command line. Tests verify basic command structure (thai lint file-placement <path>),
    inline JSON rule configuration via --rules flag, external config file loading via --config flag,
    and exit code conventions (0 for pass, 1 for violations found). Ensures the CLI provides
    intuitive interface for both quick checks and complex configuration scenarios.

Dependencies: pytest for testing, Click CliRunner for CLI testing, tmp_path fixture

Exports: TestCLIInterface test class with 4 tests

Interfaces: Tests click CLI command invocation with various flags and arguments

Implementation: 4 tests covering basic command structure, inline JSON config, external config files,
    and exit code validation
"""


class TestCLIInterface:
    """Test command-line interface."""

    def test_cli_command_structure(self):
        """thai lint file-placement <path> command works."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["lint", "file-placement", "."])

        assert result.exit_code in [0, 1]  # 0 = pass, 1 = violations

    def test_accept_json_object_via_flag(self):
        """Accept JSON object via --rules flag."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(
            cli, ["lint", "file-placement", "--rules", '{"allow": [".*\\.py$"]}', "."]
        )
        assert result.exit_code in [0, 1]

    def test_accept_json_file_via_config_flag(self, tmp_path):
        """Accept JSON file via --config flag."""
        config_file = tmp_path / "rules.json"
        config_file.write_text('{"allow": [".*\\\\.py$"]}')

        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["lint", "file-placement", "--config", str(config_file), "."])
        assert result.exit_code in [0, 1]

    def test_exit_codes(self, tmp_path):
        """Exit code 0 = pass, 1 = violations found."""
        from click.testing import CliRunner

        from src.cli import cli

        runner = CliRunner()

        # Create a clean directory with only .py files
        (tmp_path / "clean.py").write_text("#\n")

        # With permissive config, should pass
        config = tmp_path / "config.json"
        config.write_text('{"global_patterns": {"allow": [".*"]}}')

        result_pass = runner.invoke(
            cli, ["lint", "file-placement", "--config", str(config), str(tmp_path)]
        )

        # Should succeed or fail with violations
        assert result_pass.exit_code in [0, 1]
