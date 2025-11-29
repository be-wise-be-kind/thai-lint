# File Header Linter

**Purpose**: Complete guide to using the file header linter for enforcing comprehensive documentation headers across all source files

**Scope**: Configuration, usage, mandatory fields, atemporal language detection, and best practices for file header validation

**Overview**: Comprehensive documentation for the file header linter that validates documentation headers in source files. Covers how the linter works using language-specific parsers, mandatory field requirements, atemporal language detection, configuration options, CLI and library usage, supported file types (Python, TypeScript, JavaScript, Bash, Markdown, CSS), and integration with CI/CD pipelines. Helps teams maintain consistent, AI-optimized documentation across entire codebases.

**Dependencies**: Python AST (Python), regex-based parsers (TypeScript, Bash, CSS), PyYAML (Markdown frontmatter)

**Exports**: Usage documentation, configuration examples, mandatory field specifications, atemporal language patterns

**Related**: cli-reference.md for CLI commands, configuration.md for config format, how-to-ignore-violations.md for ignore patterns, ai-doc-standard.md for AI-optimized header format

**Implementation**: Language-specific header parsing with unified validation logic and configurable mandatory fields

---

## Overview

The file header linter validates that source files have proper documentation headers containing required fields (Purpose, Scope, Overview, etc.) and don't use temporal language (dates, "currently", "now", etc.). It enforces consistent documentation patterns across entire codebases.

### Why File Headers?

File headers serve as **self-documentation** that helps developers (and AI assistants) quickly understand:

- **Purpose**: What does this file do?
- **Scope**: What area of the system does it cover?
- **Dependencies**: What does it rely on?
- **Exports**: What does it provide to other modules?

**Without headers:**
```python
# src/validators.py
import re
from typing import Optional

class EmailValidator:
    def validate(self, email: str) -> bool:
        # What is this file for? Who uses it? What pattern does it use?
        return bool(re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email))
```

**With headers:**
```python
"""
Purpose: Email validation utilities for user registration and authentication

Scope: Input validation layer, used by API endpoints and form handlers

Overview: Provides email format validation using RFC-compliant regex patterns.
    Validates email addresses during user registration, password reset, and
    profile updates. Handles edge cases like international domains and plus
    addressing.

Dependencies: re module for pattern matching, typing for type hints

Exports: EmailValidator class, validate_email() convenience function

Interfaces: validate(email: str) -> bool, batch_validate(emails: List[str]) -> Dict

Implementation: RFC 5322 simplified regex with configurable strictness levels
"""
import re
from typing import Optional

class EmailValidator:
    def validate(self, email: str) -> bool:
        return bool(re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email))
```

### Benefits

- **Improved onboarding**: New developers understand file purposes immediately
- **Better AI assistance**: AI tools work more effectively with context
- **Reduced cognitive load**: No need to read entire files to understand intent
- **Consistent documentation**: Every file follows the same pattern
- **Maintainability**: Clear documentation helps during refactoring
- **Code review efficiency**: Reviewers understand context quickly

### Atemporal Documentation

A key feature of the file header linter is **atemporal language detection**. File headers must be written without temporal references because:

- **No stale dates**: "Created 2023-01-15" becomes incorrect or misleading over time
- **No temporal qualifiers**: "Currently supports OAuth" implies future changes
- **Git tracks history**: Version control handles all time-related metadata
- **Evergreen documentation**: Headers remain accurate without maintenance

## How It Works

### Language-Specific Parsing

The linter uses specialized parsers for each supported file type:

1. **Python (.py)**: Extracts module docstring using Python's `ast.get_docstring()`
2. **TypeScript/JavaScript (.ts, .tsx, .js, .jsx)**: Parses JSDoc-style `/** ... */` comments
3. **Bash (.sh, .bash)**: Extracts `# comment` blocks after shebang
4. **Markdown (.md)**: Parses YAML frontmatter between `---` markers
5. **CSS (.css, .scss)**: Extracts `/* ... */` block comments

### Validation Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Detect file type from extension                          │
├─────────────────────────────────────────────────────────────┤
│ 2. Extract header using language-specific parser            │
├─────────────────────────────────────────────────────────────┤
│ 3. Parse header fields (Purpose, Scope, Overview, etc.)     │
├─────────────────────────────────────────────────────────────┤
│ 4. Validate mandatory fields are present and non-empty      │
├─────────────────────────────────────────────────────────────┤
│ 5. Scan for atemporal language violations                   │
├─────────────────────────────────────────────────────────────┤
│ 6. Check ignore directives (line, file, pattern)            │
├─────────────────────────────────────────────────────────────┤
│ 7. Report violations with line numbers and suggestions      │
└─────────────────────────────────────────────────────────────┘
```

### Mandatory Fields

All files must have these fields by default:

| Field | Description | Required |
|-------|-------------|----------|
| **Purpose** | Brief description of file's functionality (1-2 lines) | Yes |
| **Scope** | What areas/components this file covers | Yes |
| **Overview** | Comprehensive summary (3-5 sentences) | Yes |
| **Dependencies** | Key dependencies or related files | Recommended |
| **Exports** | Main classes, functions, or constants provided | Recommended |
| **Interfaces** | Key APIs or methods exposed | Optional |
| **Implementation** | Notable patterns or architectural decisions | Optional |

### Atemporal Language Patterns

The linter detects four categories of temporal language:

**1. Explicit Timestamps:**
- Dates: `2023-01-15`, `January 2023`, `01/15/2023`
- Version dates: `v1.0.0 (2023-01-15)`
- Creation dates: `Created:`, `Updated:`, `Modified:`

**2. Temporal Qualifiers:**
- "currently", "at present", "at this time"
- "now", "nowadays", "today"
- "recently", "lately", "just"

**3. State Change Language:**
- "replaces", "replaced", "replacing"
- "formerly", "previously", "was"
- "migrated from", "changed from", "moved from"
- "new", "old", "legacy", "deprecated"

**4. Future References:**
- "will be", "shall be", "to be"
- "planned", "upcoming", "future"
- "todo", "to do", "TBD"

## Configuration

### Quick Start: Generate Configuration

```bash
# Interactive mode
thailint init-config

# Non-interactive mode
thailint init-config --non-interactive
```

### Basic Configuration

Add to `.thailint.yaml`:

```yaml
file-header:
  enabled: true

  # Mandatory fields (must have non-empty values)
  mandatory_fields:
    - Purpose
    - Scope
    - Overview

  # Recommended fields (warned if missing)
  recommended_fields:
    - Dependencies
    - Exports

  # Files to ignore
  ignore:
    - "**/__init__.py"          # Init files exempt
    - "**/migrations/**"        # Database migrations exempt
    - "**/*.min.js"             # Minified files exempt
    - "**/vendor/**"            # Third-party code exempt
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable file header linter |
| `mandatory_fields` | array | `[Purpose, Scope, Overview]` | Fields that must be present |
| `recommended_fields` | array | `[Dependencies, Exports]` | Fields that generate warnings if missing |
| `check_atemporal` | boolean | `true` | Enable atemporal language detection |
| `ignore` | array | `[]` | Glob patterns for files to skip |

### Language-Specific Configuration

```yaml
file-header:
  enabled: true

  # Language-specific mandatory fields
  languages:
    python:
      mandatory_fields:
        - Purpose
        - Scope
        - Overview
        - Dependencies
        - Exports

    typescript:
      mandatory_fields:
        - Purpose
        - Scope
        - Overview
        - Dependencies
        - Exports

    markdown:
      mandatory_fields:
        - purpose      # YAML frontmatter uses lowercase
        - scope
        - overview
```

### JSON Configuration

```json
{
  "file-header": {
    "enabled": true,
    "mandatory_fields": ["Purpose", "Scope", "Overview"],
    "recommended_fields": ["Dependencies", "Exports"],
    "check_atemporal": true,
    "ignore": [
      "**/__init__.py",
      "**/migrations/**"
    ]
  }
}
```

### Ignoring Violations

See **[How to Ignore Violations](how-to-ignore-violations.md)** for complete ignore guide.

**Quick examples:**

```python
# File-level ignore (entire file exempt from header check)
# thailint: ignore-file[file-header]

# Line-level ignore for atemporal violation
"""
Purpose: OAuth integration module
Overview: Handles authentication. Created 2023-01-15.  # thailint: ignore[file-header]
"""
```

## Usage

### CLI Mode

#### Basic Usage

```bash
# Check current directory (recursive by default)
thailint file-header .

# Check specific directory
thailint file-header src/

# Check specific file
thailint file-header src/cli.py

# Check multiple paths
thailint file-header src/ tests/ docs/
```

#### With Configuration

```bash
# Use config file
thailint file-header --config .thailint.yaml src/

# Auto-discover config (.thailint.yaml or .thailint.json)
thailint file-header src/
```

#### Output Formats

```bash
# Human-readable text (default)
thailint file-header src/

# JSON output for CI/CD
thailint file-header --format json src/

# SARIF output for GitHub Code Scanning
thailint file-header --format sarif src/ > results.sarif
```

#### CLI Options

```bash
Options:
  -c, --config PATH               Path to config file
  -f, --format [text|json|sarif]  Output format
  --recursive / --no-recursive    Scan directories recursively
  --help                          Show this message and exit
```

### Library Mode

#### High-Level API

```python
from src import Linter

# Initialize with config file
linter = Linter(config_file='.thailint.yaml')

# Lint directory with file-header rule
violations = linter.lint('src/', rules=['file-header'])

# Process violations
if violations:
    for v in violations:
        print(f"{v.file_path}:{v.line_number} - {v.message}")
```

#### Direct File Header Linter API

```python
from src.linters.file_header import lint

# Lint specific path
violations = lint('src/config.py')

# Lint directory
violations = lint('src/')

# Process results
for violation in violations:
    print(f"Line {violation.line_number}: {violation.message}")
```

### Docker Mode

```bash
# Run with default config
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest file-header /workspace/src/

# With custom config file
docker run --rm \
  -v $(pwd):/workspace \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml:ro \
  washad/thailint:latest file-header \
  --config /config/.thailint.yaml /workspace/src/
```

## Supported File Types

### Python Files (.py)

**Format:** Module docstring (triple-quoted string at file start)

```python
"""
Purpose: User authentication and session management

Scope: Authentication layer, used by API endpoints and middleware

Overview: Provides secure user authentication using JWT tokens with refresh
    token rotation. Handles login, logout, session validation, and token
    refresh operations. Integrates with the user database for credential
    verification and maintains audit logs for security compliance.

Dependencies: jwt, bcrypt, sqlalchemy, datetime

Exports: AuthService class, authenticate(), refresh_token(), logout()

Interfaces: authenticate(email, password) -> Token, validate_session(token) -> User

Implementation: JWT with RS256 signing, bcrypt password hashing, Redis session cache
"""
import jwt
import bcrypt
from datetime import datetime
```

**Violation messages:**
```
src/auth.py:1 - Missing mandatory field: Purpose
src/auth.py:1 - Missing mandatory field: Scope
src/auth.py:3 - Atemporal language violation: "currently" found in header
```

### TypeScript/JavaScript Files (.ts, .tsx, .js, .jsx)

**Format:** JSDoc-style block comment

```typescript
/**
 * Purpose: React component for user profile display and editing
 *
 * Scope: User dashboard UI, profile management feature
 *
 * Overview: Displays user profile information with inline editing capabilities.
 *     Supports avatar upload, name changes, and bio updates. Handles validation
 *     client-side before submitting to API. Uses optimistic updates for
 *     better UX with rollback on server errors.
 *
 * Dependencies: React, react-query, axios, zod for validation
 *
 * Exports: UserProfile component, UserProfileProps interface
 *
 * Props/Interfaces: UserProfileProps { userId: string, editable?: boolean }
 *
 * State/Behavior: Uses react-query for data fetching, local state for form edits
 */
import React from 'react';
import { useQuery, useMutation } from 'react-query';
```

### Bash Scripts (.sh, .bash)

**Format:** Comment block after shebang

```bash
#!/bin/bash
# Purpose: Database backup and rotation script for production environment
#
# Scope: Database operations, scheduled backup system
#
# Overview: Creates compressed database backups and uploads to S3 storage.
#     Implements rotation policy keeping last 30 daily backups, 12 weekly
#     backups, and 6 monthly backups. Sends notifications on success/failure
#     via Slack webhook. Validates backup integrity using checksums.
#
# Dependencies: pg_dump, aws-cli, gzip, curl (for Slack notifications)
#
# Exports: Creates timestamped backup files in /backups directory
#
# Usage: ./backup.sh [--full|--incremental] [--notify]
#
# Environment: Requires DB_HOST, DB_NAME, S3_BUCKET, SLACK_WEBHOOK environment variables

set -euo pipefail
```

### Markdown Files (.md)

**Format:** YAML frontmatter between `---` markers

```markdown
---
purpose: API documentation for user authentication endpoints
scope: REST API, authentication feature
overview: >
  Complete reference for authentication API endpoints including login,
  logout, token refresh, and password reset. Covers request/response
  formats, error codes, rate limiting, and security considerations.
  Intended for frontend developers integrating with the auth system.
dependencies: [OpenAPI 3.0, JWT tokens]
related: [user-management.md, security-guidelines.md]
---

# Authentication API

## Overview

The authentication API provides secure access to user sessions...
```

### CSS/SCSS Files (.css, .scss)

**Format:** Block comment at file start

```css
/*
Purpose: Global typography and font styles for the application

Scope: Site-wide typography, all text elements

Overview: Defines the typographic system including font families, sizes,
    weights, and line heights. Establishes a modular scale for consistent
    text sizing across all components. Includes responsive adjustments
    for different viewport sizes and dark mode typography variants.

Dependencies: Inter font (Google Fonts), CSS custom properties from theme.css

Exports: Typography utility classes (.text-sm, .text-lg, .heading-1, etc.)

Interfaces: CSS custom properties --font-size-*, --line-height-*, --font-weight-*

Implementation: Fluid typography using clamp(), modular scale ratio 1.25
*/

:root {
  --font-family-sans: 'Inter', system-ui, sans-serif;
  --font-size-base: clamp(1rem, 2vw, 1.125rem);
}
```

## Violation Examples

### Example 1: Missing Mandatory Fields

**Code with violations:**
```python
"""
Helper utilities for string manipulation.
"""
import re

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower())
```

**Violation messages:**
```
src/utils.py:1 - Missing mandatory field: Purpose
src/utils.py:1 - Missing mandatory field: Scope
src/utils.py:1 - Missing mandatory field: Overview
Consider adding: Purpose, Scope, Overview fields to file header
```

**Refactored code:**
```python
"""
Purpose: String manipulation utilities for URL-safe text processing

Scope: Utility functions, used throughout the application for URL generation

Overview: Provides string transformation functions for creating URL-safe slugs,
    sanitizing user input, and normalizing text. Functions are stateless and
    designed for high performance with large text inputs.

Dependencies: re module for pattern matching

Exports: slugify(), sanitize(), normalize_whitespace()

Implementation: Regex-based transformations with precompiled patterns
"""
import re

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower())
```

### Example 2: Atemporal Language Violations

**Code with violations:**
```python
"""
Purpose: OAuth 2.0 authentication integration

Scope: Third-party authentication, social login

Overview: Currently handles OAuth authentication with Google and GitHub.
    This module was recently refactored to support the new auth flow.
    Will be extended to support Apple Sign-In in the future.
    Created: 2023-06-15
    Updated: 2024-01-20

Dependencies: oauthlib, requests

Exports: OAuthProvider class
"""
```

**Violation messages:**
```
src/oauth.py:5 - Atemporal language: "Currently" (use present tense without temporal qualifiers)
src/oauth.py:6 - Atemporal language: "recently refactored" (avoid state change language)
src/oauth.py:7 - Atemporal language: "Will be extended" (avoid future references)
src/oauth.py:8 - Atemporal language: "Created: 2023-06-15" (dates tracked by git)
src/oauth.py:9 - Atemporal language: "Updated: 2024-01-20" (dates tracked by git)
```

**Refactored code:**
```python
"""
Purpose: OAuth 2.0 authentication integration

Scope: Third-party authentication, social login

Overview: Handles OAuth authentication with Google and GitHub providers.
    Implements the authorization code flow with PKCE for enhanced security.
    Manages token storage, refresh, and revocation. Supports multiple
    concurrent provider connections per user account.

Dependencies: oauthlib, requests

Exports: OAuthProvider class, authenticate(), revoke_token()

Implementation: Authorization code flow with PKCE, secure token storage
"""
```

### Example 3: No Header (File Missing Docstring)

**Code with violations:**
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self.cache = {}
```

**Violation messages:**
```
src/cache.py:1 - Missing file header: No module docstring found
Add a module-level docstring with Purpose, Scope, and Overview fields
```

## Refactoring Patterns

### Pattern 1: Adding Headers to Existing Files

**Before:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    email: str
    name: Optional[str] = None
```

**After:**
```python
"""
Purpose: User data model for authentication and profile management

Scope: Data models, used by auth, profile, and admin modules

Overview: Defines the User data class representing authenticated users in the
    system. Contains identity fields (id, email) and profile fields (name,
    avatar). Integrates with SQLAlchemy for database persistence and Pydantic
    for API serialization.

Dependencies: dataclasses, typing

Exports: User dataclass

Interfaces: User(id, email, name) - frozen dataclass with optional fields

Implementation: Immutable dataclass with optional profile fields
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    email: str
    name: Optional[str] = None
```

### Pattern 2: Converting Temporal to Atemporal

**Before (temporal):**
```python
"""
Purpose: API rate limiting middleware

Overview: This is the new rate limiter that replaces the old token bucket
    implementation. Currently using sliding window algorithm which was
    migrated from the legacy system in January 2024.
"""
```

**After (atemporal):**
```python
"""
Purpose: API rate limiting middleware

Scope: Request throttling, API protection layer

Overview: Implements request rate limiting using a sliding window algorithm.
    Tracks request counts per client (by IP or API key) within configurable
    time windows. Supports burst allowances and graduated response codes
    for approaching limits.

Dependencies: redis for distributed state, time for window calculations

Exports: RateLimiter class, rate_limit decorator

Implementation: Sliding window counter algorithm with Redis-backed state
"""
```

### Pattern 3: TypeScript Component Headers

**Before:**
```typescript
import React, { useState } from 'react';

interface Props {
  items: string[];
  onSelect: (item: string) => void;
}

export const Dropdown: React.FC<Props> = ({ items, onSelect }) => {
  // Component implementation
};
```

**After:**
```typescript
/**
 * Purpose: Accessible dropdown menu component with keyboard navigation
 *
 * Scope: UI components library, form inputs
 *
 * Overview: Renders an accessible dropdown menu supporting single selection
 *     from a list of options. Implements full keyboard navigation (arrow keys,
 *     Enter, Escape) and ARIA attributes for screen reader compatibility.
 *     Supports custom rendering of options via render prop pattern.
 *
 * Dependencies: React, @radix-ui/react-dropdown-menu for accessibility
 *
 * Exports: Dropdown component, DropdownProps interface
 *
 * Props/Interfaces: DropdownProps { items, onSelect, placeholder?, disabled? }
 *
 * State/Behavior: Controlled via onSelect callback, internal open/close state
 */
import React, { useState } from 'react';

interface Props {
  items: string[];
  onSelect: (item: string) => void;
}

export const Dropdown: React.FC<Props> = ({ items, onSelect }) => {
  // Component implementation
};
```

## Language Support

### Python Support

**Fully Supported**

**Header format:** Module docstring (triple-quoted string)

**Parser:** Python `ast.get_docstring()` for reliable extraction

**Field extraction:** Colon-delimited format (`Field: Value`)

**Example patterns:**
```python
"""
Purpose: Description here

Scope: Scope description

Overview: Multi-line overview
    with continuation indentation
"""
```

### TypeScript/JavaScript Support

**Fully Supported**

**Header format:** JSDoc-style `/** ... */` block comments

**Parser:** Regex-based extraction of first block comment

**Field extraction:** Same colon-delimited format within JSDoc

**Supported extensions:** `.ts`, `.tsx`, `.js`, `.jsx`

### Bash Support

**Fully Supported**

**Header format:** Hash comments after shebang (`#!/bin/bash`)

**Parser:** Regex-based extraction of contiguous comment block

**Field extraction:** Comments with `# Field: Value` format

### Markdown Support

**Fully Supported**

**Header format:** YAML frontmatter between `---` markers

**Parser:** PyYAML for YAML parsing, regex fallback

**Field extraction:** YAML key-value pairs (lowercase keys)

### CSS/SCSS Support

**Fully Supported**

**Header format:** Block comment `/* ... */` at file start

**Parser:** Regex-based extraction of first block comment

**Field extraction:** Same colon-delimited format within comment

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  file-header-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install thailint
        run: pip install thailint

      - name: Check file headers
        run: |
          thailint file-header src/

      - name: Check headers (SARIF for Code Scanning)
        run: |
          thailint file-header --format sarif src/ > results.sarif

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: file-header-check
        name: Check file headers
        entry: thailint file-header
        language: python
        types: [python, javascript, typescript, markdown]
        pass_filenames: true
```

### Makefile Integration

```makefile
lint-headers:
	@echo "=== Checking file headers ==="
	@poetry run thailint file-header src/ || exit 1

lint-all: lint-headers
	@echo "All checks passed"
```

## Performance

The file header linter is designed for speed:

| Operation | Performance | Target |
|-----------|-------------|--------|
| Single file parse | ~5-15ms | <50ms |
| Single file analysis | ~2-5ms | <20ms |
| 100 files | ~200-400ms | <1s |
| 1000 files | ~1-2s | <5s |

**Optimizations:**
- Language detection via file extension (O(1))
- Regex patterns precompiled at module load
- Early exit on ignore pattern matches
- Minimal memory footprint per file

## Troubleshooting

### Common Issues

**Issue: False positive on third-party code**

```bash
# Problem
src/vendor/library.py:1 - Missing mandatory field: Purpose
```

**Solution:** Add to ignore patterns:
```yaml
file-header:
  ignore:
    - "**/vendor/**"
    - "**/node_modules/**"
```

**Issue: Init files flagged**

```bash
# Problem
src/__init__.py:1 - Missing mandatory field: Purpose
```

**Solution:** Init files are typically exempt by default, but ensure config includes:
```yaml
file-header:
  ignore:
    - "**/__init__.py"
```

**Issue: Date in code comment flagged**

```python
# Problem
def parse_date(date_str: str) -> datetime:
    """Parse date from format YYYY-MM-DD."""  # False positive
```

**Solution:** The linter only checks file headers, not function docstrings. If this triggers, ensure you have a proper file-level header.

**Issue: "Currently" in technical context**

```python
# Problem - describing concurrent behavior
"""
Overview: Handles currently active connections...
"""
```

**Solution:** Use alternative phrasing:
```python
"""
Overview: Handles active connections...
"""
```

**Issue: Migration files flagged**

```bash
# Problem
migrations/0001_initial.py:1 - Missing mandatory field: Purpose
```

**Solution:** Add migration directories to ignore:
```yaml
file-header:
  ignore:
    - "**/migrations/**"
```

## Best Practices

### 1. Write Purpose First

Always start with a clear, concise Purpose field:

```python
# Good - Immediately clear
"""
Purpose: JWT token generation and validation for API authentication
"""

# Bad - Too vague
"""
Purpose: Authentication stuff
"""
```

### 2. Make Overview Actionable

Overview should help developers understand what to expect:

```python
# Good - Specific and actionable
"""
Overview: Provides CRUD operations for user entities. Handles validation,
    permission checking, and audit logging. Integrates with the email
    service for notifications on user creation and password changes.
"""

# Bad - Too generic
"""
Overview: This module has user-related code and functions.
"""
```

### 3. List Actual Dependencies

Only list dependencies that aren't obvious from imports:

```python
# Good - Non-obvious dependencies highlighted
"""
Dependencies: Redis (for caching), PostgreSQL (via SQLAlchemy)
"""

# Unnecessary - Obvious from imports
"""
Dependencies: os, sys, json, typing
"""
```

### 4. Be Specific with Exports

List the main public API, not internal helpers:

```python
# Good - Public API clear
"""
Exports: UserService class, create_user(), delete_user(), get_user_by_email()
"""

# Bad - Includes internal helpers
"""
Exports: UserService, _validate_email, _hash_password, _generate_id
"""
```

### 5. Use Atemporal Language

Always describe what code does, not its history:

```python
# Good - Timeless description
"""
Overview: Implements OAuth 2.0 authorization code flow with PKCE.
"""

# Bad - Temporal references
"""
Overview: New OAuth implementation replacing the old token-based auth.
    Recently updated to support PKCE (added January 2024).
"""
```

### 6. Keep Headers Current

When modifying a file significantly, update the header:

- Added a major new function? Update Exports
- Changed the implementation approach? Update Implementation
- Added a new dependency? Update Dependencies

### 7. Use Templates

Create editor snippets for consistent headers:

```python
# Python file header template
"""
Purpose: ${1:Brief description}

Scope: ${2:What area this covers}

Overview: ${3:Comprehensive summary explaining role and operation}

Dependencies: ${4:Key dependencies}

Exports: ${5:Main classes, functions, constants}

Interfaces: ${6:Key APIs exposed}

Implementation: ${7:Notable patterns or decisions}
"""
```

## Related Documentation

- **[AI Documentation Standard](ai-doc-standard.md)** - AI-optimized header format specification
- **[How to Ignore Violations](how-to-ignore-violations.md)** - Complete ignore guide
- **[Configuration Reference](configuration.md)** - Config file format
- **[CLI Reference](cli-reference.md)** - Command-line usage
- **[API Reference](api-reference.md)** - Library API documentation

## Examples Repository

See **[examples/file_header_usage.py](../examples/file_header_usage.py)** for complete working examples.

## Version History

- **v0.5.0**: File header linter release
  - Python, TypeScript, JavaScript, Bash, Markdown, CSS support
  - Language-specific parsers with unified validation
  - Atemporal language detection (4 pattern categories)
  - Configurable mandatory and recommended fields
  - SARIF output for CI/CD integration
  - Self-dogfooded on thai-lint codebase (0 violations, 49+ files compliant)
