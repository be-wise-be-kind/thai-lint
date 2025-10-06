# How to Create GitHub Releases for Python CLI

**Purpose**: Guide for creating GitHub Releases with automated artifact publishing

**Scope**: GitHub Release creation, artifact uploads, release notes, and automation

**Overview**: Step-by-step instructions for creating GitHub Releases for Python CLI tools
    with automatic artifact uploads (wheel, sdist), Docker image links, and formatted release notes.

**Prerequisites**: GitHub repository with release workflow, PyPI publishing configured

**Dependencies**: GitHub Actions, release.yml workflow, git tags

**Related**: how-to-publish-to-pypi.md, release.yml workflow

---

## Overview

GitHub Releases provide:
- Tagged version history
- Downloadable artifacts (wheel, sdist)
- Release notes and changelog
- Multi-platform distribution links

The release workflow automatically creates releases when you push a git tag.

## Automated Release Process

### Step 1: Prepare Release

1. Update version in `pyproject.toml`:
   ```toml
   version = "1.0.0"
   ```

2. Update CHANGELOG.md (if you have one):
   ```markdown
   ## [1.0.0] - 2025-10-03

   ### Added
   - New feature X

   ### Fixed
   - Bug Y
   ```

3. Commit changes:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: prepare release v1.0.0"
   git push
   ```

### Step 2: Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0

New features:
- Feature X
- Feature Y

Bug fixes:
- Fix Z"

# Push tag (triggers release workflow)
git push origin v1.0.0
```

### Step 3: Workflow Creates Release

The release workflow automatically:
1. ✅ Builds Python package (wheel + sdist)
2. ✅ Publishes to PyPI
3. ✅ Builds multi-arch Docker image
4. ✅ Pushes to Docker Hub
5. ✅ Creates GitHub Release with:
   - Release notes (installation methods)
   - Package artifacts attached
   - Docker image links
   - Version info

### Step 4: Verify Release

1. Go to https://github.com/youruser/yourrepo/releases
2. See new release created
3. Check artifacts attached
4. Verify release notes

## Manual Release Creation (Fallback)

If automation unavailable:

### Step 1: Build Artifacts

```bash
# Build Python package
poetry build

# Artifacts in dist/
ls dist/
# your-cli-tool-1.0.0-py3-none-any.whl
# your-cli-tool-1.0.0.tar.gz
```

### Step 2: Create Release on GitHub

1. Go to https://github.com/youruser/yourrepo/releases/new
2. Choose tag: `v1.0.0`
3. Release title: `Release v1.0.0`
4. Description:
   ```markdown
   ## Installation

   **PyPI**:
   ```bash
   pip install your-cli-tool
   ```

   **Docker**:
   ```bash
   docker pull youruser/your-cli-tool:1.0.0
   ```

   ## Changes
   - Feature X added
   - Bug Y fixed
   ```
5. Upload artifacts from `dist/`
6. Click "Publish release"

## Release Notes Best Practices

### Good Release Notes Include:

1. **Installation Instructions**:
   - pip install command
   - Docker pull command
   - From source instructions

2. **What's New**:
   - New features added
   - Breaking changes (if any)
   - Deprecations

3. **Bug Fixes**:
   - Issues fixed
   - Performance improvements

4. **Links**:
   - PyPI package
   - Docker image
   - Documentation

### Example Release Notes

```markdown
## 🚀 Release v1.0.0

### ✨ New Features
- Added interactive mode with prompt_toolkit
- Support for YAML and JSON config files
- Multi-command parallel execution

### 🐛 Bug Fixes
- Fixed exit code handling in error scenarios
- Resolved config file parsing edge cases

### 📦 Installation

**PyPI**:
```bash
pip install your-cli-tool==1.0.0
```

**Docker**:
```bash
docker pull youruser/your-cli-tool:1.0.0
```

**From Source**:
```bash
git clone https://github.com/youruser/your-cli-tool.git
cd your-cli-tool
git checkout v1.0.0
poetry install
```

### 📋 Full Changelog
See: https://github.com/youruser/your-cli-tool/compare/v0.9.0...v1.0.0
```

## Troubleshooting

### Issue: "Release not created automatically"
**Solution**: Check GitHub Actions workflow ran successfully. Look for errors in logs.

### Issue: "Artifacts not attached"
**Solution**: Verify `dist/` contains wheel and sdist. Check workflow upload step.

### Issue: "Release marked as draft"
**Solution**: Workflow has `draft: false`. If draft, manually publish from GitHub UI.

## References

- GitHub Releases: https://docs.github.com/en/repositories/releasing-projects-on-github
- Release Best Practices: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
