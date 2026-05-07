"""
Purpose: Map file-extracted versions to endoflife.date product identifiers

Scope: Version normalization, cycle extraction, and Docker/GHA product mapping

Overview: Provides the data model for extracted versions and the mapping logic that
    connects file-specific version strings to endoflife.date product names. Handles
    Docker image name to product mapping (e.g., python->python, node->nodejs), GitHub
    Actions version key mapping, version string normalization (stripping prefixes,
    ranges), and cycle extraction (e.g., "3.11.5" -> "3.11" for Python).

Dependencies: re, dataclasses

Exports: ExtractedVersion dataclass, normalize_version, extract_cycle,
    map_docker_image, map_gha_version_key

Interfaces: Pure functions for version string manipulation and product mapping

Implementation: Lookup tables for Docker/GHA mappings, regex for normalization,
    product-specific cycle extraction logic
"""

import re
from dataclasses import dataclass

# Tags that are not version numbers — just base image variants or aliases
_NON_VERSION_TAGS = {
    "alpine",
    "slim",
    "latest",
    "lts",
    "stable",
    "edge",
    "beta",
    "rc",
    "nightly",
    "bullseye",
    "bookworm",
    "buster",
    "jammy",
    "noble",
    "focal",
    "bionic",
}

# Docker image name -> endoflife.date product name
_DOCKER_IMAGE_MAP: dict[str, str] = {
    "python": "python",
    "node": "nodejs",
    "nodejs": "nodejs",
    "ruby": "ruby",
    "golang": "go",
    "go": "go",
    "openjdk": "java",
    "eclipse-temurin": "java",
    "amazoncorretto": "java",
    "php": "php",
    "elixir": "elixir",
    "erlang": "erlang",
    "rust": "rust",
    "dotnet/sdk": "dotnet",
    "dotnet/runtime": "dotnet",
    "dotnet/aspnet": "dotnet",
    "postgres": "postgresql",
    "mysql": "mysql",
    "mariadb": "mariadb",
    "redis": "redis",
    "nginx": "nginx",
    "httpd": "apache-http-server",
    "alpine": "alpine",
    "ubuntu": "ubuntu",
    "debian": "debian",
    "centos": "centos",
    "amazonlinux": "amazon-linux",
}

# GitHub Actions `with:` key -> endoflife.date product name
_GHA_VERSION_KEY_MAP: dict[str, str] = {
    "python-version": "python",
    "node-version": "nodejs",
    "go-version": "go",
    "java-version": "java",
    "ruby-version": "ruby",
    "dotnet-version": "dotnet",
    "elixir-version": "elixir",
    "php-version": "php",
}

# Products that use major-only cycles (e.g., Node 18, not 18.17)
_MAJOR_ONLY_PRODUCTS: set[str] = {
    "nodejs",
    "java",
    "go",
    "dotnet",
    "ruby",
    "php",
    "elixir",
    "erlang",
    "rust",
    "redis",
    "nginx",
    "postgresql",
    "mysql",
    "mariadb",
    "alpine",
    "ubuntu",
    "debian",
    "centos",
    "amazon-linux",
    "apache-http-server",
}


@dataclass
class ExtractedVersion:
    """A version extracted from a file."""

    product: str
    """endoflife.date product name (e.g., 'python', 'nodejs')."""

    version: str
    """Raw version string as found in the file."""

    file_path: str
    """Path to the file containing this version."""

    line: int
    """Line number (1-indexed)."""

    column: int
    """Column number (0-indexed)."""

    source: str
    """Source type (e.g., 'dockerfile', 'github-actions', 'python-version-file')."""


def is_version_tag(tag: str) -> bool:
    """Check if a Docker tag looks like a version number.

    Rejects tags that are purely base image variants (alpine, latest, lts)
    or don't contain any digits.

    Args:
        tag: Docker image tag string

    Returns:
        True if tag appears to be a version
    """
    if tag.lower() in _NON_VERSION_TAGS:
        return False
    return bool(re.search(r"\d", tag))


def normalize_version(version: str) -> str:
    """Normalize a version string by removing common prefixes, constraints, and suffixes.

    Strips leading 'v', '^', '~', '>=', '<=', '>', '<', '=', trailing
    wildcard components (.x, .*), and Docker tag variant suffixes
    (-slim, -alpine, -bullseye, etc.).

    Args:
        version: Raw version string

    Returns:
        Cleaned version string
    """
    cleaned = version.strip()
    cleaned = re.sub(r"^[v~^>=<!]+", "", cleaned)
    cleaned = re.sub(r"[.][*xX]+$", "", cleaned)
    # Strip Docker tag variant suffixes (e.g., -slim, -alpine, -bullseye, -bookworm)
    cleaned = re.sub(r"-(?:slim|alpine|bullseye|bookworm|buster|jammy|noble|focal).*$", "", cleaned)
    return cleaned.strip()


def extract_cycle(product: str, version: str) -> str:
    """Extract the cycle identifier from a version string.

    Different products use different cycle granularity on endoflife.date:
    - Python: "3.11" (major.minor)
    - Node.js: "18" (major only)
    - Ubuntu: "22.04" (major.minor)

    Args:
        product: endoflife.date product name
        version: Normalized version string

    Returns:
        Cycle string suitable for matching against endoflife.date data
    """
    normalized = normalize_version(version)
    parts = normalized.split(".")

    if not parts or not parts[0]:
        return normalized

    if product in _MAJOR_ONLY_PRODUCTS:
        return parts[0]

    # Default: major.minor (e.g., Python 3.11)
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return parts[0]


def map_docker_image(image_name: str) -> str | None:
    """Map a Docker image name to an endoflife.date product.

    Handles three Docker image name formats:
    - Library images: "python", "nginx" -> lookup directly
    - Official namespaced: "library/python" -> use last segment
    - Multi-segment (registries/orgs): "mcr.microsoft.com/playwright/python" -> check full path first

    Only falls back to the last segment for Docker Hub library images (1-2 segments).
    Multi-segment paths (3+) like registry/org/image are not matched to avoid false positives
    (e.g., playwright/python should not map to Python).

    Args:
        image_name: Docker image name (e.g., "python", "node", "dotnet/sdk")

    Returns:
        endoflife.date product name, or None if unmapped
    """
    name_lower = image_name.lower()

    # Try exact match first (handles "dotnet/sdk", "dotnet/runtime", etc.)
    product = _DOCKER_IMAGE_MAP.get(name_lower)
    if product:
        return product

    # For Docker Hub library images (1-2 segments), try the last segment
    segments = name_lower.split("/")
    if len(segments) <= 2:
        return _DOCKER_IMAGE_MAP.get(segments[-1])

    # Multi-segment paths (registry/org/image) — don't guess
    return None


def map_gha_version_key(key: str) -> str | None:
    """Map a GitHub Actions version key to an endoflife.date product.

    Args:
        key: GitHub Actions `with:` key (e.g., "python-version", "node-version")

    Returns:
        endoflife.date product name, or None if unmapped
    """
    return _GHA_VERSION_KEY_MAP.get(key.lower())
