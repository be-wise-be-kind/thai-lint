"""
File: tests/unit/linters/file_header/conftest.py
Purpose: Shared pytest fixtures and test helpers for file header linter tests
Exports: create_mock_context, VALID_TYPESCRIPT_HEADER, VALID_BASH_HEADER, etc.
Depends: pytest, pathlib.Path, unittest.mock.Mock, src.core.base.BaseLintContext
Related: All test files in this directory

Overview:
    Provides shared pytest fixtures and helper functions for file header linter
    test suite. Includes mock context creation utilities following the pattern
    established in magic_numbers linter tests. Helper functions simplify test
    setup and reduce duplication across test files. Supports multi-language
    testing with TypeScript, Bash, Markdown, and CSS fixtures.

Usage:
    context = create_mock_context(code="...", filename="test.py")
    context = create_mock_context(code="...", filename="test.ts", language="typescript")
"""

from pathlib import Path
from unittest.mock import Mock

from src.core.base import BaseLintContext


def create_mock_context(
    code: str, filename: str = "test.py", language: str = "python", metadata: dict | None = None
) -> BaseLintContext:
    """Create mock lint context for testing.

    Args:
        code: Source code content
        filename: Name of the file (default: test.py)
        language: Programming language (default: python)
        metadata: Optional metadata dictionary

    Returns:
        Mock BaseLintContext with configured attributes
    """
    context = Mock(spec=BaseLintContext)
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = metadata or {}
    return context


# =============================================================================
# Valid Header Examples for Multi-Language Testing
# =============================================================================

VALID_TYPESCRIPT_HEADER = """/**
 * File: src/utils/helper.ts
 * Purpose: Utility functions for data processing
 * Scope: Application-wide utility module
 * Overview: Provides common utility functions for data transformation,
 *     validation, and formatting used throughout the application.
 * Dependencies: lodash, date-fns
 * Exports: formatDate, validateInput, transformData
 * Props/Interfaces: UtilityOptions, TransformConfig
 * State/Behavior: Stateless utility module
 */

export function formatDate(date: Date): string {
    return date.toISOString();
}
"""

VALID_BASH_HEADER = """#!/bin/bash
# File: scripts/deploy.sh
# Purpose: Deployment script for production environment
# Scope: CI/CD deployment automation
# Overview: Handles production deployment including environment setup,
#     dependency installation, and service restart. Supports rollback.
# Dependencies: docker, kubectl, aws-cli
# Exports: deploy_app, rollback_app, check_health
# Usage: ./deploy.sh [env] [version]
# Environment: AWS_ACCESS_KEY, KUBE_CONFIG, DEPLOY_TOKEN

deploy_app() {
    echo "Deploying..."
}
"""

VALID_MARKDOWN_HEADER = """---
file: docs/architecture.md
purpose: System architecture documentation
scope: Technical architecture overview
overview: Comprehensive documentation of system architecture including component diagrams, data flows, and integration patterns
audience:
  - Engineers
  - Architects
dependencies:
  - mermaid
  - markdown
related:
  - docs/api.md
  - docs/deployment.md
status: approved
updated: 2025-01-15
---

# System Architecture

This document describes the system architecture.
"""

VALID_CSS_HEADER = """/**
 * File: styles/components.css
 * Purpose: Component-level CSS styles
 * Scope: Reusable UI component styling
 * Overview: Defines styles for common UI components including buttons,
 *     forms, cards, and navigation elements. Follows BEM naming convention.
 * Dependencies: variables.css, reset.css
 * Exports: .btn, .card, .nav, .form classes
 * Interfaces: CSS custom properties for theming
 * Environment: Browser, supports CSS Grid and Flexbox
 */

.btn {
    padding: 8px 16px;
}
"""

# =============================================================================
# Invalid/Missing Header Examples
# =============================================================================

TYPESCRIPT_NO_HEADER = """export function myFunction(): void {
    console.log("No header");
}
"""

BASH_NO_HEADER = """#!/bin/bash
echo "Script without header"
"""

MARKDOWN_NO_FRONTMATTER = """# Document Title

This markdown has no YAML frontmatter.
"""

CSS_NO_HEADER = """.button {
    color: blue;
}
"""

# =============================================================================
# Headers with Temporal Language Violations
# =============================================================================

TYPESCRIPT_TEMPORAL_HEADER = """/**
 * File: src/auth.ts
 * Purpose: Authentication module
 * Scope: User authentication
 * Overview: Currently supports OAuth and SAML authentication methods.
 *     Will be extended to support biometric auth in the future.
 * Dependencies: oauth2-client
 * Exports: authenticate, logout
 * Props/Interfaces: AuthConfig
 * State/Behavior: Manages auth state
 */
"""

BASH_TEMPORAL_HEADER = """#!/bin/bash
# File: scripts/migrate.sh
# Purpose: Database migration script
# Scope: Database schema updates
# Overview: This script was created on 2025-01-15 to handle migrations.
#     It replaces the old migration system and will soon support rollback.
# Dependencies: psql
# Exports: run_migration
# Usage: ./migrate.sh [direction]
# Environment: DB_HOST, DB_USER
"""
