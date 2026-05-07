"""
Purpose: Unit tests for version-freshness product mapper

Scope: Version normalization, cycle extraction, Docker/GHA product mapping

Overview: Tests the product mapper module including version string normalization,
    product-specific cycle extraction, Docker image to product mapping, and
    GitHub Actions version key mapping.
"""

from src.linters.version_freshness.product_mapper import (
    ExtractedVersion,
    extract_cycle,
    map_docker_image,
    map_gha_version_key,
    normalize_version,
)


class TestNormalizeVersion:
    """Tests for version string normalization."""

    def test_strips_v_prefix(self):
        """Should strip leading v."""
        assert normalize_version("v3.11.5") == "3.11.5"

    def test_strips_caret(self):
        """Should strip caret prefix."""
        assert normalize_version("^3.11") == "3.11"

    def test_strips_tilde(self):
        """Should strip tilde prefix."""
        assert normalize_version("~3.11") == "3.11"

    def test_strips_gte(self):
        """Should strip >= prefix."""
        assert normalize_version(">=3.11") == "3.11"

    def test_strips_wildcards(self):
        """Should strip trailing .x or .* wildcards."""
        assert normalize_version("3.11.*") == "3.11"
        assert normalize_version("3.x") == "3"

    def test_strips_whitespace(self):
        """Should strip surrounding whitespace."""
        assert normalize_version("  3.11  ") == "3.11"

    def test_plain_version_unchanged(self):
        """Should pass through plain versions unchanged."""
        assert normalize_version("3.11.5") == "3.11.5"

    def test_combined_prefixes(self):
        """Should strip combined prefixes."""
        assert normalize_version(">=3.11.0") == "3.11.0"


class TestExtractCycle:
    """Tests for product-specific cycle extraction."""

    def test_python_major_minor(self):
        """Python should extract major.minor cycle."""
        assert extract_cycle("python", "3.11.5") == "3.11"

    def test_python_from_constraint(self):
        """Python should handle constraint versions."""
        assert extract_cycle("python", "^3.11") == "3.11"

    def test_nodejs_major_only(self):
        """Node.js should extract major-only cycle."""
        assert extract_cycle("nodejs", "18.17.0") == "18"

    def test_nodejs_with_v_prefix(self):
        """Node.js should handle v prefix."""
        assert extract_cycle("nodejs", "v20.10.0") == "20"

    def test_go_major_only(self):
        """Go should extract major-only cycle."""
        assert extract_cycle("go", "1.21.3") == "1"

    def test_java_major_only(self):
        """Java should extract major-only cycle."""
        assert extract_cycle("java", "17.0.8") == "17"

    def test_single_component(self):
        """Should handle single-component versions."""
        assert extract_cycle("python", "3") == "3"

    def test_empty_version(self):
        """Should handle empty version string."""
        assert extract_cycle("python", "") == ""


class TestMapDockerImage:
    """Tests for Docker image to product mapping."""

    def test_python_image(self):
        """Should map python image."""
        assert map_docker_image("python") == "python"

    def test_node_image(self):
        """Should map node to nodejs."""
        assert map_docker_image("node") == "nodejs"

    def test_golang_image(self):
        """Should map golang to go."""
        assert map_docker_image("golang") == "go"

    def test_postgres_image(self):
        """Should map postgres to postgresql."""
        assert map_docker_image("postgres") == "postgresql"

    def test_case_insensitive(self):
        """Should be case insensitive."""
        assert map_docker_image("Python") == "python"

    def test_unknown_image(self):
        """Should return None for unknown images."""
        assert map_docker_image("custom-app") is None

    def test_registry_prefix(self):
        """Should strip registry prefix."""
        assert map_docker_image("docker.io/python") == "python"


class TestMapGhaVersionKey:
    """Tests for GitHub Actions version key mapping."""

    def test_python_version(self):
        """Should map python-version."""
        assert map_gha_version_key("python-version") == "python"

    def test_node_version(self):
        """Should map node-version."""
        assert map_gha_version_key("node-version") == "nodejs"

    def test_go_version(self):
        """Should map go-version."""
        assert map_gha_version_key("go-version") == "go"

    def test_unknown_key(self):
        """Should return None for unknown keys."""
        assert map_gha_version_key("unknown-version") is None


class TestExtractedVersion:
    """Tests for the ExtractedVersion dataclass."""

    def test_creates_instance(self):
        """Should create an ExtractedVersion instance."""
        ev = ExtractedVersion(
            product="python",
            version="3.11.5",
            file_path="Dockerfile",
            line=1,
            column=0,
            source="dockerfile",
        )
        assert ev.product == "python"
        assert ev.version == "3.11.5"
        assert ev.file_path == "Dockerfile"
        assert ev.line == 1
        assert ev.column == 0
        assert ev.source == "dockerfile"
