"""
Purpose: Unit tests for version-freshness extractors

Scope: Each file type extractor with valid, invalid, and edge cases

Overview: Tests all extractor functions for Dockerfiles, GitHub Actions workflows,
    version files (.python-version, .nvmrc), .tool-versions, mise.toml,
    Terraform configs, and pyproject.toml.
"""

from src.linters.version_freshness.extractors import (
    extract_from_dockerfile,
    extract_from_github_actions,
    extract_from_nvmrc,
    extract_from_pyproject_toml,
    extract_from_python_version_file,
    extract_from_terraform,
    extract_from_tool_versions,
)


class TestExtractFromDockerfile:
    """Tests for Dockerfile extractor."""

    def test_simple_from(self):
        """Should extract version from simple FROM line."""
        content = "FROM python:3.11-slim\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 1
        assert results[0].product == "python"
        assert results[0].version == "3.11-slim"
        assert results[0].line == 1

    def test_multi_stage(self):
        """Should extract from multi-stage builds."""
        content = "FROM python:3.11-slim AS builder\nFROM python:3.11-slim AS runtime\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 2

    def test_node_image(self):
        """Should map node image correctly."""
        content = "FROM node:18-alpine\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 1
        assert results[0].product == "nodejs"

    def test_golang_image(self):
        """Should map golang image correctly."""
        content = "FROM golang:1.21\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 1
        assert results[0].product == "go"

    def test_no_tag(self):
        """Should skip FROM without tag."""
        content = "FROM python\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 0

    def test_unknown_image(self):
        """Should skip unknown images."""
        content = "FROM my-custom-app:latest\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 0

    def test_platform_flag(self):
        """Should handle --platform flag."""
        content = "FROM --platform=linux/amd64 python:3.11-slim\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 1
        assert results[0].product == "python"

    def test_comment_lines_ignored(self):
        """Should not extract from comments."""
        content = "# FROM python:3.9\nFROM python:3.11\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 1
        assert results[0].version == "3.11"

    def test_empty_file(self):
        """Should handle empty files."""
        results = extract_from_dockerfile("", "Dockerfile")
        assert len(results) == 0

    def test_alpine_only_tag_skipped(self):
        """Should skip tags that are base image variants, not versions."""
        content = "FROM nginx:alpine\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 0

    def test_latest_tag_skipped(self):
        """Should skip 'latest' tag."""
        content = "FROM python:latest\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 0

    def test_registry_namespaced_image_not_matched(self):
        """Should not match multi-segment registry paths like playwright/python."""
        content = "FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 0

    def test_dotnet_sdk_namespaced(self):
        """Should match official namespaced images like dotnet/sdk."""
        content = "FROM dotnet/sdk:8.0\n"
        results = extract_from_dockerfile(content, "Dockerfile")
        assert len(results) == 1
        assert results[0].product == "dotnet"


class TestExtractFromGithubActions:
    """Tests for GitHub Actions extractor."""

    def test_simple_workflow(self):
        """Should extract python-version from workflow."""
        content = """
jobs:
  test:
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
"""
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 1
        assert results[0].product == "python"
        assert results[0].version == "3.11"

    def test_node_version(self):
        """Should extract node-version."""
        content = """
jobs:
  test:
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
"""
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 1
        assert results[0].product == "nodejs"
        assert results[0].version == "18"

    def test_matrix_versions(self):
        """Should handle matrix version strings."""
        content = """
jobs:
  test:
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11, 3.12'
"""
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 2

    def test_invalid_yaml(self):
        """Should return empty for invalid YAML."""
        results = extract_from_github_actions("{{invalid", ".github/workflows/test.yml")
        assert len(results) == 0

    def test_no_jobs(self):
        """Should handle workflow with no jobs."""
        content = "name: Test\non: push\n"
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 0

    def test_no_with_block(self):
        """Should skip steps without with block."""
        content = """
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
"""
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 0

    def test_template_expression_skipped(self):
        """Should skip ${{ matrix.* }} template expressions."""
        content = """
jobs:
  test:
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
"""
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 0

    def test_mixed_literal_and_template(self):
        """Should extract literal versions but skip template expressions."""
        content = """
jobs:
  build:
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
  test:
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
"""
        results = extract_from_github_actions(content, ".github/workflows/test.yml")
        assert len(results) == 1
        assert results[0].version == "3.11"


class TestExtractFromPythonVersionFile:
    """Tests for .python-version extractor."""

    def test_simple_version(self):
        """Should extract version from single line."""
        results = extract_from_python_version_file("3.11.5\n", ".python-version")
        assert len(results) == 1
        assert results[0].product == "python"
        assert results[0].version == "3.11.5"

    def test_empty_file(self):
        """Should handle empty file."""
        results = extract_from_python_version_file("", ".python-version")
        assert len(results) == 0

    def test_whitespace_only(self):
        """Should handle whitespace-only file."""
        results = extract_from_python_version_file("  \n  \n", ".python-version")
        assert len(results) == 0


class TestExtractFromNvmrc:
    """Tests for .nvmrc extractor."""

    def test_simple_version(self):
        """Should extract version string."""
        results = extract_from_nvmrc("18.17.0\n", ".nvmrc")
        assert len(results) == 1
        assert results[0].product == "nodejs"
        assert results[0].version == "18.17.0"

    def test_v_prefix(self):
        """Should preserve v prefix (normalization happens later)."""
        results = extract_from_nvmrc("v20\n", ".nvmrc")
        assert len(results) == 1
        assert results[0].version == "v20"

    def test_empty(self):
        """Should handle empty file."""
        results = extract_from_nvmrc("", ".nvmrc")
        assert len(results) == 0


class TestExtractFromToolVersions:
    """Tests for .tool-versions extractor."""

    def test_multiple_tools(self):
        """Should extract multiple tool versions."""
        content = "python 3.11.5\nnodejs 18.17.0\nruby 3.2.0\n"
        results = extract_from_tool_versions(content, ".tool-versions")
        assert len(results) == 3
        products = {r.product for r in results}
        assert products == {"python", "nodejs", "ruby"}

    def test_comments_ignored(self):
        """Should skip comment lines."""
        content = "# Python version\npython 3.11.5\n"
        results = extract_from_tool_versions(content, ".tool-versions")
        assert len(results) == 1

    def test_unknown_tool(self):
        """Should skip unknown tools."""
        content = "terraform 1.5.0\n"
        results = extract_from_tool_versions(content, ".tool-versions")
        assert len(results) == 0

    def test_empty_lines(self):
        """Should skip empty lines."""
        content = "\npython 3.11.5\n\n"
        results = extract_from_tool_versions(content, ".tool-versions")
        assert len(results) == 1


class TestExtractFromTerraform:
    """Tests for Terraform extractor."""

    def test_required_version(self):
        """Should extract required_version constraint."""
        content = 'required_version = ">= 1.3.0"\n'
        results = extract_from_terraform(content, "main.tf")
        assert len(results) == 1
        assert results[0].product == "terraform"
        assert results[0].version == ">= 1.3.0"

    def test_no_version(self):
        """Should handle file without required_version."""
        content = 'resource "aws_instance" "example" {\n  ami = "abc"\n}\n'
        results = extract_from_terraform(content, "main.tf")
        assert len(results) == 0


class TestExtractFromPyprojectToml:
    """Tests for pyproject.toml extractor."""

    def test_poetry_python_dep(self):
        """Should extract Python version from Poetry dependencies."""
        content = """
[tool.poetry.dependencies]
python = "^3.11"
"""
        results = extract_from_pyproject_toml(content, "pyproject.toml")
        assert len(results) == 1
        assert results[0].product == "python"
        assert results[0].version == "^3.11"

    def test_pep621_requires_python(self):
        """Should extract requires-python from project section."""
        content = """
[project]
requires-python = ">=3.11"
"""
        results = extract_from_pyproject_toml(content, "pyproject.toml")
        assert len(results) == 1
        assert results[0].product == "python"
        assert results[0].version == ">=3.11"

    def test_no_python_version(self):
        """Should handle pyproject.toml without Python version."""
        content = """
[tool.poetry]
name = "myproject"
"""
        results = extract_from_pyproject_toml(content, "pyproject.toml")
        assert len(results) == 0

    def test_invalid_toml(self):
        """Should handle invalid TOML."""
        results = extract_from_pyproject_toml("{{invalid", "pyproject.toml")
        assert len(results) == 0
