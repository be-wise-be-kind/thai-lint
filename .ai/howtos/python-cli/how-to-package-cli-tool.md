# How to Package CLI Tool

**Purpose**: Guide for packaging and distributing Python CLI tools via PyPI, Docker, and standalone binaries

**Scope**: Package creation, distribution strategies, version management, and release workflows

**Overview**: This guide demonstrates multiple packaging approaches for Python CLI applications including
    PyPI packages for pip installation, Docker images for containerized distribution, and standalone
    binaries for platform-specific deployment. Covers build configuration, dependency management, entry
    points, versioning, and automated release pipelines with best practices for each distribution method.

**Prerequisites**: Python CLI application ready for distribution, basic understanding of packaging concepts

**Related**: .ai/docs/python-cli-architecture.md, .ai/templates/python-cli/setup.py.template

---

## Overview

Packaging options for CLI tools:
1. **PyPI Package**: Install via `pip install your-cli-tool`
2. **Docker Image**: Run in container
3. **Standalone Binary**: Self-contained executable (future)

## PyPI Package Distribution

### Step 1: Configure pyproject.toml

Your `pyproject.toml` should include all package metadata:

```toml
[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-cli-tool"
version = "1.0.0"
description = "Professional command-line tool for X"
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
license = {text = "MIT"}
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["cli", "tool", "automation"]

dependencies = [
    "click>=8.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/my-cli-tool"
Documentation = "https://my-cli-tool.readthedocs.io"
Repository = "https://github.com/yourusername/my-cli-tool"
Issues = "https://github.com/yourusername/my-cli-tool/issues"

[project.scripts]
my-cli-tool = "src.cli:cli"
mycli = "src.cli:cli"  # Short alias

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.setuptools.package-data]
src = ["py.typed"]
```

### Step 2: Build Package

```bash
# Install build tools
pip install build twine

# Build distribution packages
python -m build

# This creates:
# dist/my-cli-tool-1.0.0.tar.gz      # Source distribution
# dist/my_cli_tool-1.0.0-py3-none-any.whl  # Wheel distribution
```

### Step 3: Test Package Locally

```bash
# Create virtual environment for testing
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/my_cli_tool-1.0.0-py3-none-any.whl

# Test CLI works
my-cli-tool --help
mycli --help

# Deactivate when done
deactivate
```

### Step 4: Upload to PyPI

```bash
# Upload to Test PyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ my-cli-tool

# If everything works, upload to real PyPI
python -m twine upload dist/*
```

**PyPI Configuration** (`.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### Step 5: Users Install Your Tool

```bash
# Users can now install with
pip install my-cli-tool

# And run with
my-cli-tool --help
```

## Docker Distribution

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy source and build wheel
COPY . .
RUN python -m build --wheel

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy wheel from builder
COPY --from=builder /app/dist/*.whl /tmp/

# Install CLI tool
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

# Create non-root user
RUN useradd -m -u 1000 cliuser && \
    chown -R cliuser:cliuser /app

USER cliuser

# Set entrypoint to CLI
ENTRYPOINT ["my-cli-tool"]
CMD ["--help"]
```

### Step 2: Build Docker Image

```bash
# Build image
docker build -t my-cli-tool:1.0.0 -t my-cli-tool:latest .

# Test image
docker run --rm my-cli-tool:latest --help

# Run with volume mounts for config/data
docker run --rm \
    -v $(pwd)/config:/config \
    -v $(pwd)/data:/data \
    my-cli-tool:latest hello --name Docker
```

### Step 3: Create docker-compose.cli.yml

Create `docker-compose.cli.yml`:

```yaml
# Purpose: Docker Compose configuration for CLI tool distribution
# Scope: CLI container with volume mounts for config and data
# Overview: Provides containerized CLI tool with externalized configuration and data persistence.
#     Includes volume mounts for config files and data directories, environment variable support,
#     and flexible command execution. Enables running CLI in isolated container environment.
# Dependencies: Docker Engine >=20.10, Docker Compose >=2.0
# Exports: CLI service configuration for containerized execution
# Environment: Development and production CLI tool deployment

services:
  cli:
    build:
      context: .
      dockerfile: Dockerfile
    image: my-cli-tool:latest
    volumes:
      # Mount config directory
      - ./config:/config:ro
      # Mount data directory
      - ./data:/data
    environment:
      - CLI_CONFIG_PATH=/config/config.yaml
      - LOG_LEVEL=INFO
    command: ["--help"]

  # Service for interactive use
  cli-interactive:
    extends: cli
    stdin_open: true
    tty: true
```

Usage:

```bash
# Run CLI command
docker-compose -f docker-compose.cli.yml run --rm cli hello --name "World"

# Interactive mode
docker-compose -f docker-compose.cli.yml run --rm cli-interactive
```

### Step 4: Publish to Docker Registry

```bash
# Tag for Docker Hub
docker tag my-cli-tool:latest yourusername/my-cli-tool:1.0.0
docker tag my-cli-tool:latest yourusername/my-cli-tool:latest

# Push to Docker Hub
docker push yourusername/my-cli-tool:1.0.0
docker push yourusername/my-cli-tool:latest

# Users can now run with
docker run --rm yourusername/my-cli-tool:latest --help
```

## Version Management

### Step 1: Single Source of Truth

Use `__version__` in your package:

```python
# src/__init__.py
"""
Purpose: Package initialization and version definition

Scope: Package-level exports and metadata

Overview: Initializes the CLI application package, defines version number, and exports
    public API. Provides single source of truth for version information used by CLI,
    setup tools, and documentation.

Exports: __version__, cli, load_config, ConfigError
"""

__version__ = "1.0.0"

from src.cli import cli
from src.config import load_config, ConfigError

__all__ = ['cli', 'load_config', 'ConfigError', '__version__']
```

### Step 2: Display Version in CLI

```python
# src/cli.py
import click
from src import __version__

@cli.command()
def version():
    """Display version information."""
    click.echo(f"my-cli-tool version {__version__}")

# Or as an option
@click.group()
@click.version_option(version=__version__)
def cli():
    """CLI with version option."""
    pass
```

### Step 3: Automate Version Bumping

Use `bump2version` for version management:

```bash
# Install bump2version
pip install bump2version

# Create .bumpversion.cfg
cat > .bumpversion.cfg <<EOF
[bumpversion]
current_version = 1.0.0
commit = True
tag = True

[bumpversion:file:src/__init__.py]

[bumpversion:file:pyproject.toml]
EOF

# Bump version
bump2version patch  # 1.0.0 -> 1.0.1
bump2version minor  # 1.0.1 -> 1.1.0
bump2version major  # 1.1.0 -> 2.0.0
```

## Release Automation with GitHub Actions

### Step 1: Create Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*

      - name: Build Docker image
        run: |
          docker build -t ${{ github.repository }}:${GITHUB_REF#refs/tags/v} .
          docker build -t ${{ github.repository }}:latest .

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Push Docker image
        run: |
          docker push ${{ github.repository }}:${GITHUB_REF#refs/tags/v}
          docker push ${{ github.repository }}:latest

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          generate_release_notes: true
```

### Step 2: Create Release

```bash
# Commit your changes
git add .
git commit -m "Release version 1.0.0"

# Create and push tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build Python package
# 2. Publish to PyPI
# 3. Build Docker image
# 4. Push to Docker Hub
# 5. Create GitHub release
```

## Standalone Binary (PyInstaller)

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Create Binary

```bash
# Create standalone executable
pyinstaller --onefile \
    --name my-cli-tool \
    --add-data "src:src" \
    src/cli.py

# Binary created at dist/my-cli-tool

# Test binary
./dist/my-cli-tool --help
```

### Step 3: Create PyInstaller Spec File

For more control, create `my-cli-tool.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'click',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='my-cli-tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Build with spec:

```bash
pyinstaller my-cli-tool.spec
```

## Distribution Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **PyPI** | Easy install with pip, dependency management, standard Python distribution | Requires Python installed, dependency conflicts | Python developers |
| **Docker** | Isolated environment, consistent across platforms, includes all dependencies | Requires Docker, larger size | Server deployment, consistent environments |
| **Binary** | No Python required, single file, fast startup | Large size, platform-specific, harder updates | End users, non-technical users |

## Changelog and Release Notes

### Step 1: Maintain CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-02

### Added
- Initial release
- Hello command with greeting options
- Config management commands
- Docker support
- Comprehensive test suite

### Changed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2025-09-15

### Added
- Basic CLI structure
- Configuration loading
```

### Step 2: Generate Release Notes

```bash
# Install git-changelog
pip install git-changelog

# Generate changelog
git-changelog --output CHANGELOG.md

# Or use GitHub's auto-generated release notes
```

## Testing Packaging

### Step 1: Test in Clean Environment

```bash
# Create test environment
python -m venv test-package-env
source test-package-env/bin/activate

# Install from wheel
pip install dist/my_cli_tool-1.0.0-py3-none-any.whl

# Run tests
my-cli-tool --version
my-cli-tool --help
my-cli-tool hello --name Test

# Check dependencies
pip list | grep my-cli-tool

# Clean up
deactivate
rm -rf test-package-env
```

### Step 2: Test Docker Image

```bash
# Test basic functionality
docker run --rm my-cli-tool:latest --version
docker run --rm my-cli-tool:latest --help

# Test with config
mkdir -p test-config
echo "log_level: DEBUG" > test-config/config.yaml

docker run --rm \
    -v $(pwd)/test-config:/config:ro \
    my-cli-tool:latest config show

# Clean up
rm -rf test-config
```

## Best Practices

### Versioning

1. **Semantic Versioning**: Use MAJOR.MINOR.PATCH (e.g., 1.2.3)
2. **Tag Releases**: Create git tags for each release
3. **Changelog**: Maintain detailed changelog
4. **Version Source**: Single source of truth in `src/__init__.py`

### Package Metadata

1. **Descriptive**: Clear name and description
2. **Classifiers**: Proper PyPI classifiers
3. **Dependencies**: Pin major versions, allow minor updates
4. **README**: Comprehensive README.md included

### Testing

1. **Clean Environment**: Test installation in clean virtual environment
2. **Multiple Platforms**: Test on Linux, macOS, Windows
3. **Python Versions**: Test on all supported Python versions
4. **Integration**: Test actual usage, not just installation

### Security

1. **Dependency Scanning**: Use pip-audit or safety
2. **Secrets**: Never include secrets in package
3. **Code Signing**: Sign releases (future)
4. **SBOM**: Generate Software Bill of Materials

## Troubleshooting

### Issue: Package won't install
**Solution**: Check dependencies in pyproject.toml, test in clean environment

### Issue: Entry point not found
**Solution**: Verify `[project.scripts]` in pyproject.toml points to correct function

### Issue: Docker image too large
**Solution**: Use multi-stage builds, alpine base image, minimize dependencies

### Issue: PyInstaller binary fails
**Solution**: Check hidden imports, test on target platform

## Next Steps

- **Documentation**: Create comprehensive docs with Sphinx
- **CI/CD**: Automate testing and releases
- **Monitoring**: Track package downloads and usage
- **Feedback**: Collect user feedback for improvements

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Publishing](https://pypi.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
