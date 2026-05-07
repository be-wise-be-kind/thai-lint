"""
Purpose: Extract version declarations from infrastructure and configuration files

Scope: File-type-specific extractors for Dockerfiles, GitHub Actions, version files, and Terraform

Overview: Provides one pure function per file type that reads content and returns a list of
    ExtractedVersion instances. Each extractor handles the specific syntax of its file type:
    regex for Dockerfiles and Terraform, YAML parsing for GitHub Actions, simple string parsing
    for .python-version and .nvmrc, TOML parsing for mise.toml and pyproject.toml, and
    space-delimited parsing for .tool-versions.

Dependencies: re, yaml (stdlib pyyaml), product_mapper module

Exports: extract_from_dockerfile, extract_from_github_actions, extract_from_python_version_file,
    extract_from_nvmrc, extract_from_tool_versions, extract_from_mise_toml,
    extract_from_terraform, extract_from_pyproject_toml

Interfaces: Each function takes (content: str, file_path: str) -> list[ExtractedVersion]

Implementation: Pure functions with no side effects, regex-based or parser-based extraction
"""

import logging
import re
from typing import Any

import yaml

from src.linters.version_freshness.product_mapper import (
    ExtractedVersion,
    is_version_tag,
    map_docker_image,
    map_gha_version_key,
)

logger = logging.getLogger(__name__)

# Regex for Dockerfile FROM lines: FROM [--platform=...] image[:tag] [AS alias] [# comment]
_DOCKERFILE_FROM_RE = re.compile(
    r"^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)",
    re.IGNORECASE | re.MULTILINE,
)

# Regex for Terraform required_version
_TERRAFORM_VERSION_RE = re.compile(
    r'required_version\s*=\s*"([^"]+)"',
)

# Version key pattern for GitHub Actions with: blocks
_GHA_VERSION_KEYS = {
    "python-version",
    "node-version",
    "go-version",
    "java-version",
    "ruby-version",
    "dotnet-version",
    "elixir-version",
    "php-version",
}


def extract_from_dockerfile(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract versions from Dockerfile FROM lines.

    Args:
        content: Dockerfile content
        file_path: Path to the Dockerfile

    Returns:
        List of extracted versions
    """
    results: list[ExtractedVersion] = []
    for match in _DOCKERFILE_FROM_RE.finditer(content):
        token = match.group(1)
        image, tag = _split_docker_token(token)
        if not tag or not is_version_tag(tag):
            continue
        product = map_docker_image(image)
        if not product:
            continue
        line_num = content[: match.start()].count("\n") + 1
        col = match.start() - content.rfind("\n", 0, match.start()) - 1
        results.append(
            ExtractedVersion(
                product=product,
                version=tag,
                file_path=file_path,
                line=line_num,
                column=max(0, col),
                source="dockerfile",
            )
        )
    return results


def _split_docker_token(token: str) -> tuple[str, str | None]:
    """Split a Docker image token into image name and tag.

    Args:
        token: Docker image token (e.g., "python:3.11-slim", "python")

    Returns:
        Tuple of (image_name, tag) where tag may be None
    """
    if ":" in token:
        parts = token.split(":", 1)
        return parts[0], parts[1]
    return token, None


def extract_from_github_actions(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract versions from GitHub Actions workflow files.

    Parses YAML and walks the structure looking for version keys
    in `with:` blocks of steps.

    Args:
        content: YAML workflow content
        file_path: Path to the workflow file

    Returns:
        List of extracted versions
    """
    jobs = _parse_gha_jobs(content)
    if not jobs:
        return []

    results: list[ExtractedVersion] = []
    for job in jobs.values():
        _extract_gha_job_versions(job, content, file_path, results)
    return results


def _parse_gha_jobs(content: str) -> dict | None:
    """Parse YAML and return the jobs dict, or None on failure.

    Args:
        content: YAML workflow content

    Returns:
        Jobs dict or None
    """
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    jobs = data.get("jobs", {})
    return jobs if isinstance(jobs, dict) else None


def _extract_gha_job_versions(
    job: Any, content: str, file_path: str, results: list[ExtractedVersion]
) -> None:
    """Extract versions from a single GHA job's steps.

    Args:
        job: Parsed job dict
        content: Full file content for line number lookup
        file_path: Path to the workflow file
        results: List to append found versions to
    """
    if not isinstance(job, dict):
        return
    steps = job.get("steps", [])
    if not isinstance(steps, list):
        return
    for step in steps:
        _extract_gha_step_versions(step, content, file_path, results)


def _extract_gha_step_versions(
    step: Any, content: str, file_path: str, results: list[ExtractedVersion]
) -> None:
    """Extract version from a single GHA step's with: block.

    Args:
        step: Parsed step dict
        content: Full file content for line number lookup
        file_path: Path to the workflow file
        results: List to append found versions to
    """
    with_block = _get_step_with_block(step)
    if not with_block:
        return

    for key in _GHA_VERSION_KEYS:
        _extract_gha_key_versions(with_block, key, content, file_path, results)


def _get_step_with_block(step: Any) -> dict | None:
    """Get the with: block from a step, or None if invalid.

    Args:
        step: Parsed step dict

    Returns:
        The with block dict or None
    """
    if not isinstance(step, dict):
        return None
    with_block = step.get("with", {})
    return with_block if isinstance(with_block, dict) else None


def _extract_gha_key_versions(
    with_block: dict, key: str, content: str, file_path: str, results: list[ExtractedVersion]
) -> None:
    """Extract versions for a single GHA version key from a with: block.

    Args:
        with_block: Parsed with block dict
        key: Version key name (e.g., "python-version")
        content: Full file content for line number lookup
        file_path: Path to the workflow file
        results: List to append found versions to
    """
    value = with_block.get(key)
    if value is None:
        return
    product = map_gha_version_key(key)
    if not product:
        return
    for ver in _parse_gha_version_value(str(value)):
        line_num = _find_key_line(content, key, ver)
        results.append(
            ExtractedVersion(
                product=product,
                version=ver,
                file_path=file_path,
                line=line_num,
                column=0,
                source="github-actions",
            )
        )


def _parse_gha_version_value(value: str) -> list[str]:
    """Parse a GHA version value which may be a single version or matrix list.

    Skips template expressions like ${{ matrix.python-version }}.

    Args:
        value: Version string (e.g., "3.11", "3.11, 3.12", "['3.11', '3.12']")

    Returns:
        List of individual version strings (excludes template expressions)
    """
    cleaned = value.strip().strip("[]")
    parts = re.split(r"[,\n]+", cleaned)
    return [p.strip().strip("'\"") for p in parts if p.strip().strip("'\"") and "${{" not in p]


def _find_key_line(content: str, key: str, value: str) -> int:
    """Find line number where a key-value pair appears.

    Args:
        content: File content
        key: YAML key to search for
        value: Value to search for

    Returns:
        Line number (1-indexed), or 1 if not found
    """
    lines = content.splitlines()
    return _find_exact_key_value_line(lines, key, value) or _find_key_only_line(lines, key) or 1


def _find_exact_key_value_line(lines: list[str], key: str, value: str) -> int:
    """Find line containing both key and value.

    Args:
        lines: File lines
        key: Key to search for
        value: Value to search for

    Returns:
        Line number (1-indexed), or 0 if not found
    """
    for i, line in enumerate(lines, 1):
        if key in line and value in line:
            return i
    return 0


def _find_key_only_line(lines: list[str], key: str) -> int:
    """Find first line containing a key.

    Args:
        lines: File lines
        key: Key to search for

    Returns:
        Line number (1-indexed), or 0 if not found
    """
    for i, line in enumerate(lines, 1):
        if key in line:
            return i
    return 0


def extract_from_python_version_file(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract version from .python-version file.

    Args:
        content: File content (single version string)
        file_path: Path to the file

    Returns:
        List with one ExtractedVersion, or empty if content is blank
    """
    version = content.strip()
    if not version:
        return []
    return [
        ExtractedVersion(
            product="python",
            version=version,
            file_path=file_path,
            line=1,
            column=0,
            source="python-version-file",
        )
    ]


def extract_from_nvmrc(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract version from .nvmrc or .node-version file.

    Args:
        content: File content (single version string, optionally prefixed with 'v')
        file_path: Path to the file

    Returns:
        List with one ExtractedVersion, or empty if content is blank
    """
    version = content.strip()
    if not version:
        return []
    return [
        ExtractedVersion(
            product="nodejs",
            version=version,
            file_path=file_path,
            line=1,
            column=0,
            source="nvmrc",
        )
    ]


_TOOL_VERSIONS_MAP: dict[str, str] = {
    "python": "python",
    "nodejs": "nodejs",
    "ruby": "ruby",
    "golang": "go",
    "java": "java",
    "elixir": "elixir",
    "erlang": "erlang",
    "php": "php",
    "rust": "rust",
}


def extract_from_tool_versions(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract versions from .tool-versions file (asdf format).

    Each line has format: `tool version [version ...]`

    Args:
        content: File content
        file_path: Path to the file

    Returns:
        List of extracted versions
    """
    return [
        extracted
        for line_num, raw_line in enumerate(content.splitlines(), 1)
        if (extracted := _parse_tool_versions_line(raw_line, line_num, file_path))
    ]


def _parse_tool_versions_line(
    raw_line: str, line_num: int, file_path: str
) -> ExtractedVersion | None:
    """Parse a single .tool-versions line into an ExtractedVersion.

    Args:
        raw_line: Raw line content
        line_num: Line number (1-indexed)
        file_path: Path to the file

    Returns:
        ExtractedVersion or None if line is not a valid tool entry
    """
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split()
    if len(parts) < 2:
        return None
    product = _TOOL_VERSIONS_MAP.get(parts[0])
    if not product:
        return None
    return ExtractedVersion(
        product=product,
        version=parts[1],
        file_path=file_path,
        line=line_num,
        column=0,
        source="tool-versions",
    )


_MISE_TOOL_MAP: dict[str, str] = {
    "python": "python",
    "node": "nodejs",
    "ruby": "ruby",
    "go": "go",
    "java": "java",
    "elixir": "elixir",
    "erlang": "erlang",
    "php": "php",
    "rust": "rust",
}


def extract_from_mise_toml(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract versions from mise.toml [tools] section.

    Args:
        content: TOML file content
        file_path: Path to the file

    Returns:
        List of extracted versions
    """
    tools = _parse_mise_tools(content)
    if not tools:
        return []

    results: list[ExtractedVersion] = []
    for tool_name, version_val in tools.items():
        product = _MISE_TOOL_MAP.get(tool_name)
        if not product:
            continue
        version = str(version_val) if not isinstance(version_val, list) else str(version_val[0])
        line_num = _find_key_line(content, tool_name, version)
        results.append(
            ExtractedVersion(
                product=product,
                version=version,
                file_path=file_path,
                line=line_num,
                column=0,
                source="mise-toml",
            )
        )
    return results


def _parse_mise_tools(content: str) -> dict | None:
    """Parse mise.toml and return the [tools] section.

    Args:
        content: TOML file content

    Returns:
        Tools dict or None on failure
    """
    try:
        import tomllib
    except ImportError:
        return None
    try:
        data = tomllib.loads(content)
    except Exception:
        return None
    tools = data.get("tools", {})
    return tools if isinstance(tools, dict) else None


def extract_from_terraform(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract Terraform required_version constraints.

    Args:
        content: Terraform file content
        file_path: Path to the .tf file

    Returns:
        List of extracted versions (mapped to 'terraform' product)
    """
    results: list[ExtractedVersion] = []
    for match in _TERRAFORM_VERSION_RE.finditer(content):
        version_constraint = match.group(1)
        line_num = content[: match.start()].count("\n") + 1
        results.append(
            ExtractedVersion(
                product="terraform",
                version=version_constraint,
                file_path=file_path,
                line=line_num,
                column=0,
                source="terraform",
            )
        )
    return results


def extract_from_pyproject_toml(content: str, file_path: str) -> list[ExtractedVersion]:
    """Extract Python version constraint from pyproject.toml.

    Looks for [tool.poetry.dependencies] python or [project] requires-python.

    Args:
        content: TOML file content
        file_path: Path to pyproject.toml

    Returns:
        List of extracted versions
    """
    try:
        import tomllib
    except ImportError:
        return []

    try:
        data = tomllib.loads(content)
    except Exception:
        return []

    results: list[ExtractedVersion] = []
    _extract_poetry_python(data, content, file_path, results)
    _extract_project_python(data, content, file_path, results)
    return results


def _extract_poetry_python(
    data: dict, content: str, file_path: str, results: list[ExtractedVersion]
) -> None:
    """Extract Python version from Poetry dependencies.

    Args:
        data: Parsed TOML data
        content: Raw file content for line lookup
        file_path: Path to pyproject.toml
        results: List to append found versions to
    """
    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    python_ver = poetry_deps.get("python")
    if python_ver:
        line_num = _find_key_line(content, "python", str(python_ver))
        results.append(
            ExtractedVersion(
                product="python",
                version=str(python_ver),
                file_path=file_path,
                line=line_num,
                column=0,
                source="pyproject-toml",
            )
        )


def _extract_project_python(
    data: dict, content: str, file_path: str, results: list[ExtractedVersion]
) -> None:
    """Extract Python version from PEP 621 requires-python.

    Args:
        data: Parsed TOML data
        content: Raw file content for line lookup
        file_path: Path to pyproject.toml
        results: List to append found versions to
    """
    requires_python = data.get("project", {}).get("requires-python")
    if requires_python:
        line_num = _find_key_line(content, "requires-python", str(requires_python))
        results.append(
            ExtractedVersion(
                product="python",
                version=str(requires_python),
                file_path=file_path,
                line=line_num,
                column=0,
                source="pyproject-toml",
            )
        )
