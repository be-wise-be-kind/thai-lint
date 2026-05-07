"""
Purpose: Unit tests for version-freshness ignore directive integration

Scope: All 5 ignore levels - line, block, file, repo, and comment-less files

Overview: Tests that the version-freshness linter correctly integrates with the
    standard ignore directive system at all levels: line-level inline comments,
    block-level ignore-start/end, file-level ignore-file, repo-level patterns,
    and comment-less files that rely on repo-level ignores.
"""

from unittest.mock import patch

from src.linters.version_freshness.config import VersionFreshnessConfig
from src.linters.version_freshness.linter import VersionFreshnessRule

PYTHON_DATA = [
    {"cycle": "3.13", "eol": "2029-10-31"},
    {"cycle": "3.12", "eol": "2028-10-31"},
    {"cycle": "3.9", "eol": "2025-10-31"},
    {"cycle": "3.7", "eol": "2023-06-27"},
]


class TestLineIgnore:
    """Tests for line-level ignore directives."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_inline_ignore_suppresses_violation(self, mock_cache, tmp_path):
        """Inline ignore should suppress violation."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM python:3.7-slim  # thailint: ignore[version-freshness]\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_inline_ignore_specific_rule(self, mock_cache, tmp_path):
        """Should ignore specific sub-rule only."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.7-slim  # thailint: ignore[version-freshness.eol-version]\n"
        )

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_inline_ignore_wrong_rule_no_suppress(self, mock_cache, tmp_path):
        """Should NOT suppress when ignore is for different rule."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.7-slim  # thailint: ignore[version-freshness.outdated-runtime]\n"
        )

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        # Ignoring outdated-runtime should NOT suppress eol-version
        assert len(violations) == 1

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_wildcard_ignore_suppresses(self, mock_cache, tmp_path):
        """Wildcard ignore should suppress all sub-rules."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM python:3.7-slim  # thailint: ignore[version-freshness.*]\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0


class TestBlockIgnore:
    """Tests for block-level ignore directives."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_block_ignore_suppresses(self, mock_cache, tmp_path):
        """Block ignore should suppress violations within block."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "# thailint: ignore-start version-freshness\n"
            "FROM python:3.7-slim\n"
            "# thailint: ignore-end\n"
        )

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_block_ignore_yaml(self, mock_cache, tmp_path):
        """Block ignore should work in YAML files."""
        mock_cache.return_value = PYTHON_DATA
        workflows = tmp_path / ".github" / "workflows"
        workflows.mkdir(parents=True)
        workflow = workflows / "test.yml"
        workflow.write_text(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      # thailint: ignore-start version-freshness\n"
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.7'\n"
            "      # thailint: ignore-end\n"
        )

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([workflow])
        assert len(violations) == 0


class TestFileIgnore:
    """Tests for file-level ignore directives."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_file_ignore_suppresses(self, mock_cache, tmp_path):
        """File-level ignore should suppress all violations in file."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("# thailint: ignore-file[version-freshness]\nFROM python:3.7-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0


class TestRepoIgnore:
    """Tests for repository-level ignore patterns."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_repo_ignore_pattern(self, mock_cache, tmp_path):
        """Repo-level ignore pattern should skip matching files."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile.legacy"
        dockerfile.write_text("FROM python:3.7-slim\n")

        config = VersionFreshnessConfig(
            check_eol=True,
            ignore=["Dockerfile.legacy"],
        )
        rule = VersionFreshnessRule(config)
        violations = rule.check_paths([tmp_path])
        assert len(violations) == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_repo_ignore_glob(self, mock_cache, tmp_path):
        """Repo-level glob pattern should skip matching paths."""
        mock_cache.return_value = PYTHON_DATA
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        dockerfile = tests_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.7-slim\n")

        config = VersionFreshnessConfig(check_eol=True, ignore=["tests/**"])
        rule = VersionFreshnessRule(config)
        violations = rule.check_paths([tmp_path])
        assert len(violations) == 0


class TestCommentLessFiles:
    """Tests for files without comment syntax."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_python_version_file_emits_violation(self, mock_cache, tmp_path):
        """Comment-less files should still emit violations."""
        mock_cache.return_value = PYTHON_DATA
        pyver = tmp_path / ".python-version"
        pyver.write_text("3.7.17\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([tmp_path])
        assert len(violations) == 1

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_python_version_repo_ignore(self, mock_cache, tmp_path):
        """Comment-less files can be ignored via repo-level patterns."""
        mock_cache.return_value = PYTHON_DATA
        pyver = tmp_path / ".python-version"
        pyver.write_text("3.7.17\n")

        config = VersionFreshnessConfig(check_eol=True, ignore=[".python-version"])
        rule = VersionFreshnessRule(config)
        violations = rule.check_paths([tmp_path])
        assert len(violations) == 0


class TestNoIgnore:
    """Tests confirming violations are emitted without ignore directives."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_eol_without_ignore_emits_violation(self, mock_cache, tmp_path):
        """EOL version without any ignore should emit violation."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM python:3.7-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 1
        assert violations[0].rule_id == "version-freshness.eol-version"
