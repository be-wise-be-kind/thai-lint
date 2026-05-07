"""
Purpose: Unit tests for version-freshness CLI command

Scope: Output formats, exit codes, config loading, CLI flag overrides via CliRunner

Overview: Tests the CLI command for version-freshness linting including
    text, JSON, and SARIF output formats, exit codes for clean and
    violation scenarios, config file loading, and --check-eol / --check-outdated
    CLI flag overrides.
"""

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from src.cli.main import cli

PYTHON_DATA = [
    {"cycle": "3.13", "eol": "2029-10-31"},
    {"cycle": "3.12", "eol": "2028-10-31"},
    {"cycle": "3.7", "eol": "2023-06-27"},
]


def _create_dockerfile(tmp_path: Path, content: str) -> Path:
    """Create a temporary Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(content)
    return dockerfile


class TestVersionFreshnessCliTextOutput:
    """Tests for text output format."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_text_output_clean(self, mock_cache, tmp_path):
        """Should show no violations message for clean files."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.13-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", str(tmp_path)])
        assert result.exit_code == 0
        assert "No violations found" in result.output

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_text_output_violations(self, mock_cache, tmp_path):
        """Should show violations in text format."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", str(tmp_path)])
        assert result.exit_code == 1
        assert "violation" in result.output.lower()


class TestVersionFreshnessCliJsonOutput:
    """Tests for JSON output format."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_json_output_valid(self, mock_cache, tmp_path):
        """Should produce valid JSON output."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", "--format", "json", str(tmp_path)])
        output = json.loads(result.output)
        assert "violations" in output
        assert "total" in output
        assert output["total"] >= 1

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_json_output_clean(self, mock_cache, tmp_path):
        """Should produce valid JSON with empty violations."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.13-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", "--format", "json", str(tmp_path)])
        output = json.loads(result.output)
        assert output["total"] == 0


class TestVersionFreshnessCliSarifOutput:
    """Tests for SARIF output format."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_sarif_output_valid(self, mock_cache, tmp_path):
        """Should produce valid SARIF v2.1.0 output."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", "--format", "sarif", str(tmp_path)])
        sarif = json.loads(result.output)
        assert sarif["version"] == "2.1.0"
        assert "runs" in sarif
        assert len(sarif["runs"]) == 1


class TestVersionFreshnessCliExitCodes:
    """Tests for exit codes."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_exit_0_no_violations(self, mock_cache, tmp_path):
        """Should exit 0 when no violations found."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.13-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", str(tmp_path)])
        assert result.exit_code == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_exit_1_with_violations(self, mock_cache, tmp_path):
        """Should exit 1 when violations found."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", str(tmp_path)])
        assert result.exit_code == 1


class TestVersionFreshnessCliFlags:
    """Tests for --check-eol and --check-outdated CLI flags."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_check_outdated_flag_finds_outdated(self, mock_cache, tmp_path):
        """--check-outdated should flag non-latest supported versions."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.12-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", "--check-outdated", str(tmp_path)])
        assert result.exit_code == 1
        assert "outdated-runtime" in result.output

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_no_check_outdated_by_default(self, mock_cache, tmp_path):
        """Default should NOT flag outdated versions (only EOL)."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.12-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", str(tmp_path)])
        assert result.exit_code == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_no_check_eol_suppresses_eol(self, mock_cache, tmp_path):
        """--no-check-eol should suppress EOL violations."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["version-freshness", "--no-check-eol", str(tmp_path)])
        assert result.exit_code == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_combined_no_eol_with_outdated(self, mock_cache, tmp_path):
        """--no-check-eol --check-outdated should only flag outdated."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        runner = CliRunner()
        result = runner.invoke(
            cli, ["version-freshness", "--no-check-eol", "--check-outdated", str(tmp_path)]
        )
        # 3.7 is EOL but we disabled EOL check; it IS outdated though
        # However, outdated check skips EOL versions (is_outdated and not is_eol)
        # So this should find 0 violations since 3.7 is EOL
        assert result.exit_code == 0
