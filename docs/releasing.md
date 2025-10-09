# Release Process Guide

**Purpose**: Complete guide for creating and publishing thailint package releases to PyPI

**Scope**: Pre-release validation, version management, publishing workflow, and post-release verification

**Overview**: Comprehensive release process documentation covering all steps from pre-release
    validation through PyPI publishing and post-release verification. Includes quality gate
    checklists, version bumping procedures, GitHub Actions workflow usage, PyPI Trusted Publishing
    configuration, and rollback procedures. Ensures consistent, validated releases with proper
    testing, documentation updates, and community communication.

**Dependencies**: Poetry (packaging), GitHub Actions (automation), PyPI account, git (version control)

**Exports**: Release process procedures, quality checklists, publishing workflows

**Related**: CHANGELOG.md (version history), pyproject.toml (version config), .github/workflows/publish-pypi.yml

**Implementation**: Systematic release workflow with automated testing, manual verification gates, and rollback procedures

---

## Overview

This guide covers the complete release process for publishing thailint to PyPI. The process is semi-automated using GitHub Actions with manual quality gates.

## Release Types

Following [Semantic Versioning](https://semver.org/):

- **MAJOR** (x.0.0): Breaking changes, incompatible API changes
- **MINOR** (1.x.0): New features, backwards compatible
- **PATCH** (1.0.x): Bug fixes, backwards compatible

## Pre-Release Checklist

Before starting a release, ensure all quality gates pass:

### 1. Code Quality

```bash
# Run full linting suite (must exit with code 0)
just lint-full
echo $?  # Should output: 0

# Run fast linting
just lint
echo $?  # Should output: 0

# Run type checking
poetry run mypy src/
echo $?  # Should output: 0
```

**Quality Gates:**
- [ ] `just lint-full` exits with code 0 (no Pylint violations)
- [ ] `just lint` exits with code 0 (no Ruff errors)
- [ ] `mypy src/` exits with code 0 (no type errors)
- [ ] No security vulnerabilities (`just lint-security`)
- [ ] Complexity metrics meet standards (`just lint-complexity`)

### 2. Test Suite

```bash
# Run all tests with coverage
just test-coverage

# Check coverage threshold (80% minimum)
poetry run coverage report --fail-under=80
```

**Quality Gates:**
- [ ] All tests pass (pytest exit code 0)
- [ ] Test coverage ≥80% overall
- [ ] Core modules ≥90% coverage
- [ ] No failing integration tests
- [ ] Docker tests pass (if applicable)

### 3. Documentation

**Quality Gates:**
- [ ] CHANGELOG.md updated with all changes for this version
- [ ] README.md reflects current features and usage
- [ ] All docstrings complete and accurate
- [ ] API examples tested and working
- [ ] Breaking changes documented in CHANGELOG
- [ ] Migration guide provided (if breaking changes)

### 4. Local Build Verification

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
poetry build

# Verify build artifacts
ls -lh dist/
# Should show: thailint-X.Y.Z.tar.gz and thailint-X.Y.Z-py3-none-any.whl

# Check package contents
tar -tzf dist/thailint-*.tar.gz | head -30
unzip -l dist/thailint-*.whl | head -30
```

**Quality Gates:**
- [ ] Build succeeds without errors
- [ ] Both `.tar.gz` and `.whl` files created
- [ ] Package includes necessary files (src/, README, LICENSE, CHANGELOG)
- [ ] Package excludes development files (tests/, .github/, .ai/)
- [ ] Package size reasonable (<5MB for source, <2MB for wheel)

### 5. Install Test in Clean Environment

```bash
# Create clean virtual environment
python -m venv /tmp/test-thailint-env
source /tmp/test-thailint-env/bin/activate

# Install from local build
pip install dist/thailint-*.whl

# Test CLI works
thailint --help
thailint --version

# Test library import
python -c "from thailint import Linter; print('Library import works')"

# Test file-placement linter
thailint lint file-placement --help

# Deactivate and cleanup
deactivate
rm -rf /tmp/test-thailint-env
```

**Quality Gates:**
- [ ] Package installs without errors
- [ ] CLI command `thailint` available in PATH
- [ ] `thailint --help` displays help text
- [ ] `thailint --version` shows correct version
- [ ] Library import `from thailint import Linter` works
- [ ] All three modes functional (CLI, Library, Docker)
- [ ] Entry points configured correctly

### 6. Docker Verification

```bash
# Build Docker image
docker build -t thailint/thailint:test .

# Test CLI in container
docker run --rm thailint/thailint:test --help
docker run --rm thailint/thailint:test --version

# Test with volume mount
docker run --rm -v $(pwd):/workspace thailint/thailint:test lint file-placement /workspace
```

**Quality Gates:**
- [ ] Docker image builds successfully
- [ ] Image size reasonable (≤300MB)
- [ ] CLI works in container
- [ ] Volume mounting works correctly
- [ ] Non-root user execution verified

## Version Bumping

### 1. Choose Version Number

Determine version using semantic versioning:

```bash
# Current version
grep '^version = ' pyproject.toml

# Examples:
# 1.0.0 → 1.0.1 (patch: bug fixes)
# 1.0.0 → 1.1.0 (minor: new features)
# 1.0.0 → 2.0.0 (major: breaking changes)
```

### 2. Update Version in pyproject.toml

```bash
# Option 1: Manual edit
vim pyproject.toml
# Update line: version = "X.Y.Z"

# Option 2: Poetry version command
poetry version patch   # 1.0.0 → 1.0.1
poetry version minor   # 1.0.0 → 1.1.0
poetry version major   # 1.0.0 → 2.0.0
```

### 3. Update CHANGELOG.md

```bash
# Edit CHANGELOG.md
vim CHANGELOG.md
```

1. Move `[Unreleased]` changes to new `[X.Y.Z] - YYYY-MM-DD` section
2. Add release date
3. Ensure all changes categorized correctly (Added, Changed, Fixed, etc.)
4. Add any missing changes
5. Create new empty `[Unreleased]` section

### 4. Commit Version Bump

```bash
# Stage version changes
git add pyproject.toml CHANGELOG.md

# Commit with conventional commit message
git commit -m "chore(release): Bump version to X.Y.Z

- Update version in pyproject.toml
- Update CHANGELOG.md with release notes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 5. Create and Push Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push commit and tag
git push origin main
git push origin vX.Y.Z
```

**Important:** Pushing the tag triggers the GitHub Actions workflow!

## Automated Publishing Workflow

Once the tag is pushed, GitHub Actions automatically:

1. **Runs Tests** (`test` job)
   - Installs dependencies
   - Runs linting (`just lint`)
   - Runs type checking (`mypy`)
   - Runs test suite with coverage
   - Verifies ≥80% coverage

2. **Builds Package** (`build` job)
   - Runs after tests pass
   - Builds with `poetry build`
   - Verifies package contents
   - Uploads artifacts

3. **Publishes to PyPI** (`publish-pypi` job)
   - Runs after build succeeds
   - Uses PyPI Trusted Publishing (OIDC)
   - No API tokens needed
   - Publishes both `.tar.gz` and `.whl`

4. **Creates GitHub Release** (`create-release` job)
   - Extracts changelog for version
   - Creates GitHub release
   - Attaches build artifacts
   - Links to PyPI package

### Monitor Workflow

```bash
# Watch workflow progress
gh run watch

# Or visit GitHub Actions UI:
# https://github.com/steve-e-jackson/thai-lint/actions
```

### Workflow Failure Handling

If any job fails:

1. **Test Failures**: Fix issues, commit, push to main, re-tag
2. **Build Failures**: Check build configuration, re-tag after fixes
3. **PyPI Publishing Failures**:
   - Check PyPI Trusted Publishing configuration
   - Verify package name not already taken for this version
   - Check PyPI status page
4. **Release Creation Failures**: Manually create release if needed

## PyPI Trusted Publishing Setup

**One-time setup** required before first release:

### 1. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create account and verify email
3. Enable 2FA (required for trusted publishing)

### 2. Configure Trusted Publishing

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `thailint`
   - **Owner**: `steve-e-jackson`
   - **Repository name**: `thai-lint`
   - **Workflow name**: `publish-pypi.yml`
   - **Environment name**: `pypi`
4. Click "Add"

### 3. First Release Requires Manual Intervention

For the **first release only**, PyPI may require manual approval:

1. Workflow will fail at publish step
2. Log into PyPI
3. Approve pending publisher
4. Re-run workflow or re-tag

Subsequent releases are automatic.

## Post-Release Verification

After workflow completes successfully:

### 1. Verify PyPI Publication

```bash
# Check package on PyPI
open https://pypi.org/project/thailint/X.Y.Z/

# Install from PyPI in clean environment
python -m venv /tmp/verify-pypi
source /tmp/verify-pypi/bin/activate
pip install thailint==X.Y.Z

# Test installation
thailint --version
thailint --help

# Cleanup
deactivate
rm -rf /tmp/verify-pypi
```

**Verification Checklist:**
- [ ] Package visible on PyPI
- [ ] Correct version number displayed
- [ ] README renders correctly on PyPI
- [ ] Installation from PyPI succeeds
- [ ] CLI works after PyPI install
- [ ] Library import works after PyPI install

### 2. Verify GitHub Release

```bash
# Check GitHub release
open https://github.com/steve-e-jackson/thai-lint/releases/tag/vX.Y.Z
```

**Verification Checklist:**
- [ ] Release created with correct version
- [ ] Changelog content extracted correctly
- [ ] Build artifacts attached (`.tar.gz` and `.whl`)
- [ ] Links to PyPI work
- [ ] Release not marked as draft/prerelease

### 3. Test Installation Methods

```bash
# Test pip install
pip install thailint

# Test Poetry install
poetry add thailint

# Test Docker pull (if published)
docker pull thailint/thailint:X.Y.Z
```

### 4. Update Documentation

- [ ] Update README badges (if version-specific)
- [ ] Update documentation site (if applicable)
- [ ] Post announcement (GitHub discussions, Twitter, etc.)

## Rollback Procedures

If critical issues are discovered after release:

### Option 1: Yank Release (Recommended)

```bash
# Yank release from PyPI (keeps metadata, prevents new installs)
pip install twine
twine upload --repository pypi --skip-existing dist/*
# Then manually yank on PyPI web interface
```

### Option 2: Publish Hotfix

```bash
# Immediately publish patch version with fix
# Example: 1.0.0 → 1.0.1

# 1. Fix issue
# 2. Bump version to X.Y.Z+1
# 3. Update CHANGELOG
# 4. Tag and push
```

### Option 3: Delete GitHub Release

```bash
# Delete GitHub release (doesn't affect PyPI)
gh release delete vX.Y.Z --yes

# Delete tag
git push --delete origin vX.Y.Z
git tag -d vX.Y.Z
```

**Important:** You cannot re-upload the same version to PyPI. If yanked, must publish new version.

## Common Issues

### Issue: PyPI Trusted Publishing Not Working

**Solutions:**
1. Verify environment name matches (`pypi`)
2. Check repository name spelling
3. Ensure 2FA enabled on PyPI account
4. Re-configure trusted publisher on PyPI

### Issue: Version Already Exists on PyPI

**Solutions:**
1. Cannot overwrite existing PyPI versions
2. Bump to next patch version
3. Update tag and re-push

### Issue: Tests Fail in CI but Pass Locally

**Solutions:**
1. Check Python version matches (3.11)
2. Verify all dependencies in pyproject.toml
3. Check for environment-specific issues
4. Review CI logs for specific failures

### Issue: Package Size Too Large

**Solutions:**
1. Review MANIFEST.in exclusions
2. Check for included test files
3. Verify .dockerignore patterns
4. Use `tar -tzf dist/*.tar.gz` to inspect

## Release Checklist Summary

Quick checklist for releases:

### Pre-Release
- [ ] All tests pass (`just test`)
- [ ] Linting clean (`just lint-full`)
- [ ] Documentation updated (CHANGELOG, README)
- [ ] Local build succeeds (`poetry build`)
- [ ] Clean environment install test passes
- [ ] Docker build and test passes (if applicable)

### Version Bump
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated with release notes
- [ ] Changes committed to main branch
- [ ] Git tag created (`git tag -a vX.Y.Z`)
- [ ] Tag pushed (`git push origin vX.Y.Z`)

### Post-Release
- [ ] GitHub Actions workflow completes successfully
- [ ] Package visible on PyPI
- [ ] GitHub release created
- [ ] PyPI installation verified
- [ ] All three modes tested (CLI, Library, Docker)
- [ ] Documentation updated

## Resources

- **PyPI**: https://pypi.org/project/thailint/
- **GitHub Releases**: https://github.com/steve-e-jackson/thai-lint/releases
- **Trusted Publishing Guide**: https://docs.pypi.org/trusted-publishers/
- **Semantic Versioning**: https://semver.org/
- **Keep a Changelog**: https://keepachangelog.com/

## Support

For release process questions:
- Check GitHub Actions logs
- Review PyPI publishing documentation
- Check CHANGELOG.md for version history
- Contact maintainers via GitHub Issues
