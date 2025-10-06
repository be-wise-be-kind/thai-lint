# Python CLI Application How-To Guides

**Purpose**: Index of how-to guides for Python CLI application development with Click framework

**Scope**: Common tasks and patterns for CLI development, configuration, and distribution

**Overview**: This directory contains practical how-to guides for building and extending Python CLI
    applications. Each guide provides step-by-step instructions, complete code examples, and best
    practices for specific tasks. Guides focus on CLI-specific patterns including command structure,
    configuration management, packaging, and distribution strategies.

**Target Audience**: Developers building or extending Python CLI tools

**Related**: .ai/docs/python-cli-architecture.md, .ai/templates/python-cli/

---

## Available How-To Guides

### 1. How to Add CLI Commands

**File**: `how-to-add-cli-command.md`

**What You'll Learn**:
- Add simple commands to the CLI
- Create command groups and subcommands
- Add options, arguments, and flags
- Use Click context for shared state
- Handle command errors gracefully
- Test new commands

**When to Use**: Adding new functionality to your CLI tool

---

### 2. How to Handle Configuration Files

**File**: `how-to-handle-config-files.md`

**What You'll Learn**:
- Load configuration from YAML/JSON files
- Define configuration defaults
- Validate configuration schema
- Merge configuration from multiple sources
- Save configuration changes
- Handle missing or invalid configuration

**When to Use**: Managing application settings and user preferences

---

### 3. How to Package CLI Tools

**File**: `how-to-package-cli-tool.md`

**What You'll Learn**:
- Package CLI as Python package for pip installation
- Create Docker images for containerized distribution
- Build standalone executables
- Set up entry points and scripts
- Publish to PyPI
- Version and release management

**When to Use**: Preparing your CLI tool for distribution to users

---

### 4. How to Publish to PyPI

**File**: `how-to-publish-to-pypi.md`

**What You'll Learn**:
- Set up PyPI account and trusted publishing
- Configure OIDC authentication (no API tokens needed)
- Automate PyPI publishing with GitHub Actions
- Version management best practices
- Troubleshoot common publishing issues

**When to Use**: Publishing your CLI tool to Python Package Index for pip installation

---

### 5. How to Create GitHub Releases

**File**: `how-to-create-github-release.md`

**What You'll Learn**:
- Automate GitHub Releases with git tags
- Attach distribution artifacts (wheel, sdist)
- Write effective release notes
- Multi-platform distribution (PyPI, Docker Hub, GitHub)
- Manual release creation as fallback

**When to Use**: Creating versioned releases with downloadable artifacts and release notes

---

## Distribution & Publishing

### PyPI Publishing
- [how-to-publish-to-pypi.md](./how-to-publish-to-pypi.md) - Publish CLI tool to Python Package Index

### GitHub Releases
- [how-to-create-github-release.md](./how-to-create-github-release.md) - Create GitHub Releases with artifacts

---

## Quick Reference

### Common Tasks

| Task | Guide | Key Concepts |
|------|-------|--------------|
| Add new command | how-to-add-cli-command.md | Click decorators, command groups |
| Add command option | how-to-add-cli-command.md | @click.option, type validation |
| Load config file | how-to-handle-config-files.md | YAML parsing, defaults |
| Save config | how-to-handle-config-files.md | Config persistence, paths |
| Package for pip | how-to-package-cli-tool.md | pyproject.toml, entry points |
| Publish to PyPI | how-to-publish-to-pypi.md | Trusted publishing, OIDC |
| Create GitHub Release | how-to-create-github-release.md | Git tags, artifacts, automation |
| Create Docker image | how-to-package-cli-tool.md | Dockerfile, multi-stage builds |
| Test commands | how-to-add-cli-command.md | CliRunner, pytest fixtures |

### Code Examples Location

All guides include complete, runnable code examples. Templates for common patterns are available in:
- `.ai/templates/python-cli/cli-entrypoint.py.template`
- `.ai/templates/python-cli/config-loader.py.template`
- `.ai/templates/python-cli/setup.py.template`

## Related Documentation

### Architecture

For understanding the overall design:
- `.ai/docs/python-cli-architecture.md` - Complete architecture documentation

### Language Plugin

For Python-specific tooling:
- `plugins/languages/python/` - Python plugin documentation
- Python linting, formatting, and testing guides

### Infrastructure

For deployment and containerization:
- `plugins/infrastructure/containerization/docker/` - Docker plugin
- `plugins/infrastructure/ci-cd/github-actions/` - CI/CD plugin

## Contributing

To add new how-to guides:

1. Identify a common task or pattern
2. Write step-by-step instructions with code examples
3. Test all code examples to ensure they work
4. Add the guide to this index
5. Cross-reference with architecture docs

## Feedback

If you have questions or suggestions for additional guides:
- Open an issue in the ai-projen repository
- Request specific how-to guides
- Share your CLI development patterns
