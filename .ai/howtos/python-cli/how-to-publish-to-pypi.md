# How to Publish Python CLI Tool to PyPI

**Purpose**: Guide for publishing Python CLI tool to Python Package Index (PyPI)

**Scope**: PyPI account setup, trusted publishing configuration, versioning, and automated release

**Overview**: Step-by-step instructions for publishing a Python CLI tool to PyPI using GitHub Actions
    trusted publishing (no API tokens needed). Covers account setup, version management, and automated
    publishing triggered by git tags.

**Prerequisites**: Python CLI tool built with python-cli plugin, GitHub repository, PyPI account

**Dependencies**: GitHub Actions, Poetry, PyPI trusted publishing

**Related**: how-to-create-github-release.md, release.yml workflow

---

## Prerequisites

- Python CLI tool built with this plugin
- GitHub repository with CLI code
- PyPI account (free): https://pypi.org/account/register/

## Setup PyPI Trusted Publishing

Trusted publishing eliminates the need for API tokens by using OIDC.

### Step 1: Create PyPI Account

1. Visit https://pypi.org/account/register/
2. Create account and verify email
3. Enable 2FA (recommended)

### Step 2: Configure Trusted Publisher

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: Your CLI tool name (from pyproject.toml)
   - **Owner**: Your GitHub username or org
   - **Repository name**: Your repo name
   - **Workflow name**: `release.yml`
   - **Environment name**: (leave blank)
4. Save pending publisher

### Step 3: Verify pyproject.toml

Ensure your `pyproject.toml` has correct metadata:

```toml
[tool.poetry]
name = "your-cli-tool"
version = "0.1.0"  # Will be updated for each release
description = "Your CLI tool description"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
license = "MIT"
homepage = "https://github.com/yourusername/your-cli-tool"
repository = "https://github.com/yourusername/your-cli-tool"
documentation = "https://github.com/yourusername/your-cli-tool#readme"

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[tool.poetry.scripts]
your-cli-tool = "src.cli:cli"
```

## Publishing Process

### Step 1: Update Version

Edit `pyproject.toml` and bump version:

```toml
version = "1.0.0"  # Update this
```

### Step 2: Commit Version Bump

```bash
git add pyproject.toml
git commit -m "chore: bump version to 1.0.0"
git push
```

### Step 3: Create and Push Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag (triggers release workflow)
git push origin v1.0.0
```

### Step 4: Monitor Release

1. Go to GitHub Actions tab
2. Watch "Release" workflow run
3. Verify three jobs complete:
   - ✅ Publish to PyPI
   - ✅ Publish to Docker Hub
   - ✅ Create GitHub Release

### Step 5: Verify on PyPI

1. Visit https://pypi.org/project/your-cli-tool/
2. Confirm version published
3. Test installation:

```bash
pip install your-cli-tool
your-cli-tool --help
```

## Troubleshooting

### Issue: "Project name not found on PyPI"
**Solution**: The pending publisher must match exact project name. Create publisher on PyPI first.

### Issue: "OIDC token verification failed"
**Solution**: Ensure workflow file is named `release.yml` and matches PyPI configuration.

### Issue: "Version already exists"
**Solution**: PyPI doesn't allow re-uploading same version. Bump version and create new tag.

### Issue: "Build fails during poetry build"
**Solution**: Run `poetry build` locally first to test. Check pyproject.toml for errors.

## Manual Publishing (Fallback)

If GitHub Actions unavailable:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (requires API token)
twine upload dist/*
```

## Version Management Best Practices

- Use semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
- Always update version in pyproject.toml before tagging
- Use annotated tags: `git tag -a v1.0.0 -m "message"`

## References

- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/
- Python Packaging: https://packaging.python.org/
- Semantic Versioning: https://semver.org/
