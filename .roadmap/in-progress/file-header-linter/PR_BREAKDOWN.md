# File Header Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of File Header Linter into manageable, atomic pull requests

**Scope**: Complete feature implementation from documentation integration through production deployment with dogfooding

**Overview**: Comprehensive breakdown of the File Header Linter feature into 7 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR. Follows TDD methodology with test suites
    preceding implementations.

**Dependencies**: BaseLintRule interface, Python AST, Tree-sitter (TypeScript/JavaScript), PyYAML (Markdown), pytest framework

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview and architecture, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with TDD methodology, detailed step-by-step implementation guidance, and comprehensive testing validation

---

## Overview
This document breaks down the File Header Linter feature into 7 manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed
- Follows TDD methodology (tests before implementation)

---

## PR1: Foundation - Documentation Integration

### Objective
Integrate new AI-optimized documentation standard into project structure and update all relevant documentation references

### Scope
- Copy new AI-doc-standard.md to docs/ directory
- Update existing file header standards documentation
- Update AI agent instructions
- Update documentation index
- **Update all templates to match AI-optimized standard**
- Ensure all cross-references work

### Files to Create
1. **docs/ai-doc-standard.md**
   - Copy from `/home/stevejackson/Downloads/ai-doc-standard.md`
   - Preserve all 1949 lines
   - Verify formatting and links

### Files to Modify
1. **.ai/docs/FILE_HEADER_STANDARDS.md**
   - Add section: "## Relationship to AI-Optimized Standard"
   - Add: "This document defines our current header standards. For AI-optimized headers that maximize LLM effectiveness, see docs/ai-doc-standard.md"
   - Add reference in Overview section
   - Update "Related" field to include ai-doc-standard.md

2. **.ai/howtos/how-to-write-file-headers.md**
   - Add section: "## AI-Optimized Headers"
   - Reference ai-doc-standard.md for advanced usage
   - Add examples from new standard
   - Update "Resources" section

3. **AGENTS.md**
   - Update lines 100-110 (file header section)
   - Add atemporal language requirement
   - Reference ai-doc-standard.md
   - Update example headers to show atemporal language

4. **.ai/index.yaml**
   - Add under `documentation:` section:
     ```yaml
     - path: ../docs/ai-doc-standard.md
       description: AI-optimized documentation header standard for LLM-assisted development
       tags: [documentation, standards, ai, headers]
     ```

5. **.ai/templates/file-header-python.template**
   - Update to match AI-optimized standard
   - **Change**: Move `File:` field to FIRST position (currently `Purpose:` is first)
   - Format: `File: path/to/file.py` as line 2 (after opening `"""`)
   - Then: `Purpose:`, `Exports:`, `Depends:`, `Implements:`, `Related:`, `Overview:`, `Usage:`, `Notes:`

6. **.ai/templates/file-header-typescript.template**
   - Update to match AI-optimized standard
   - **Change**: Move `File:` field to FIRST position
   - Format: `File: src/path/to/file.ts` as first content line in JSDoc
   - Then: `Purpose:`, `Exports:`, `Depends:`, `Implements:`, `Related:`, `Overview:`, `Usage:`, `Notes:`

7. **.ai/templates/file-header-markdown.template**
   - Update to match AI-optimized standard
   - **Change**: Replace markdown header format with YAML frontmatter
   - Format:
     ```markdown
     ---
     file: docs/path/to/file.md
     purpose: One-line description
     audience: [Engineers, Architects]
     dependencies: [Tool1, Tool2]
     related: [path/to/doc1.md, path/to/doc2.md]
     status: draft|review|approved|deprecated
     version: 1.0.0
     updated: YYYY-MM-DD
     ---

     # Document Title

     **Overview:**
     2-4 sentence description...
     ```

8. **.ai/templates/file-header-yaml.template**
   - Update to match AI-optimized standard (minimal changes needed)
   - **Change**: Move `File:` field comment to FIRST position
   - Ensure comment format matches: `# File: path/to/config.yml`

### Step-by-Step Implementation

**Step 1: Copy New Standard**
```bash
cp /home/stevejackson/Downloads/ai-doc-standard.md docs/ai-doc-standard.md
```

**Step 2: Update FILE_HEADER_STANDARDS.md**
Add after line 20 (after "Overview" section):
```markdown
## Relationship to AI-Optimized Standard

This document defines thai-lint's current file header standards. For teams using AI-assisted development tools (Claude, GitHub Copilot, Cursor), see **docs/ai-doc-standard.md** for an AI-optimized header format that maximizes LLM effectiveness through:
- Machine-readable metadata for faster file scanning
- Progressive disclosure for token efficiency
- Explicit dependency mapping
- Front-loaded critical information

Both standards are valid; choose based on your workflow:
- **This document**: General-purpose, human-first headers
- **ai-doc-standard.md**: AI-first, optimized for LLM code understanding

The file-header linter will enforce atemporal language requirements from both standards.
```

**Step 3: Update how-to-write-file-headers.md**
Add section before "Examples":
```markdown
## AI-Optimized Headers (Optional)

For teams heavily using AI coding assistants, consider the AI-optimized header format documented in **docs/ai-doc-standard.md**. This format provides:
- Better token efficiency (2-3x more files in LLM context windows)
- Improved semantic search and retrieval
- Explicit dependency mapping
- Machine-readable metadata

Key differences:
- Front-loaded critical information (first 5 lines contain 80% of what AI needs)
- Explicit "Exports:" and "Depends:" fields
- Structured metadata before narrative
- Optimized for embedding models and RAG systems

See docs/ai-doc-standard.md for complete specification and examples.
```

**Step 4: Update AGENTS.md**
Replace lines 100-110 with:
```markdown
**BEFORE Writing Any Files**:
- ✅ Check `.ai/docs/FILE_HEADER_STANDARDS.md` for correct header template
- ✅ Use template matching file type (Python: lines 131-151, YAML: lines 177-193, etc.)
- ✅ Include ALL mandatory fields: Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Implementation
- ✅ **Use atemporal language** (no "currently", "now", "new", "old", dates, or temporal references)
- ✅ For AI-optimized headers, see `docs/ai-doc-standard.md` (recommended for new files)
```

**Step 5: Update .ai/index.yaml**
Add entry in documentation section (maintain alphabetical order):
```yaml
documentation:
  # ... existing entries ...
  - path: ../docs/ai-doc-standard.md
    description: AI-optimized documentation header standard for LLM-assisted development workflows
    tags: [documentation, standards, ai, headers, llm]
  # ... more entries ...
```

**Step 6: Update Python Template**
Edit `.ai/templates/file-header-python.template`:
- Change the actual header section (after the template instructions)
- Move `File:` to line 2 (first field after opening `"""`)
- Update field order to: `File:`, `Purpose:`, `Exports:`, `Depends:`, `Implements:`, `Related:`, `Overview:`, `Usage:`, `Notes:`

Current (WRONG):
```python
"""
Purpose: {{PURPOSE}}

Scope: {{SCOPE}}
```

New (CORRECT):
```python
"""
File: {{FILE_PATH}}
Purpose: {{PURPOSE}}
Exports: {{EXPORTS}}
Depends: {{DEPENDENCIES}}
Implements: {{IMPLEMENTS}}
Related: {{RELATED}}

Overview:
    {{OVERVIEW}}

Usage:
    {{USAGE}}

Notes: {{NOTES}}
"""
```

**Step 7: Update TypeScript Template**
Edit `.ai/templates/file-header-typescript.template`:
- Move `File:` to first content line in JSDoc block
- Update field order to match AI-optimized standard

Current (WRONG):
```typescript
/**
 * Purpose: {{PURPOSE}}
 *
 * Scope: {{SCOPE}}
 */
```

New (CORRECT):
```typescript
/**
 * File: {{FILE_PATH}}
 * Purpose: {{PURPOSE}}
 * Exports: {{EXPORTS}}
 * Depends: {{DEPENDENCIES}}
 * Implements: {{IMPLEMENTS}}
 * Related: {{RELATED}}
 *
 * Overview:
 *   {{OVERVIEW}}
 *
 * Usage:
 *   {{USAGE}}
 *
 * Notes: {{NOTES}}
 */
```

**Step 8: Update Markdown Template**
Edit `.ai/templates/file-header-markdown.template`:
- Replace entire format with YAML frontmatter approach

Current (WRONG):
```markdown
# {{DOCUMENT_TITLE}}

**Purpose**: {{PURPOSE}}
```

New (CORRECT):
```markdown
<!--
Template instructions here...
-->

---
file: {{FILE_PATH}}
purpose: {{PURPOSE}}
audience: {{AUDIENCE}}
dependencies: {{DEPENDENCIES}}
related: {{RELATED}}
status: {{STATUS}}
version: {{VERSION}}
updated: {{UPDATED}}
---

# {{DOCUMENT_TITLE}}

**Overview:**
{{OVERVIEW}}

**When to use:** {{WHEN_TO_USE}}
**When NOT to use:** {{WHEN_NOT_TO_USE}}
```

**Step 9: Update YAML Template**
Edit `.ai/templates/file-header-yaml.template`:
- Move `# File:` to first line of actual header (after template instructions)
- Minimal changes needed as YAML already uses `#` comments

Current (WRONG):
```yaml
# Purpose: {{PURPOSE}}
# Scope: {{SCOPE}}
```

New (CORRECT):
```yaml
# File: {{FILE_PATH}}
# Purpose: {{PURPOSE}}
# Exports: {{EXPORTS}}
# Depends: {{DEPENDENCIES}}
```

### Testing
- [ ] All documentation links resolve correctly
- [ ] Markdown formatting renders properly
- [ ] Cross-references between documents work
- [ ] No broken links in any modified files
- [ ] Documentation readable and clear

### Success Criteria
- [ ] `docs/ai-doc-standard.md` exists and is complete (1949 lines)
- [ ] FILE_HEADER_STANDARDS.md references new standard
- [ ] how-to-write-file-headers.md includes AI-optimized section
- [ ] AGENTS.md includes atemporal language requirement
- [ ] .ai/index.yaml includes new documentation entry
- [ ] **All 4 templates updated** (Python, TypeScript, Markdown, YAML)
- [ ] **Templates have `File:` field FIRST** (AI-optimized format)
- [ ] Markdown template uses YAML frontmatter
- [ ] All cross-references work
- [ ] No linting errors

### Dependencies
- None (foundation PR)

---

## PR2: Test Suite - Python Header Detection

### Objective
Write comprehensive test suite for Python file header validation using TDD methodology (RED phase)

### Scope
- Create test infrastructure for file-header linter
- Write 40-50 comprehensive tests for Python headers
- All tests must initially FAIL (no implementation exists yet)
- Cover all aspects: mandatory fields, atemporal language, configuration, edge cases

### Files to Create
1. **tests/unit/linters/file_header/__init__.py**
   - Empty init file for test module

2. **tests/unit/linters/file_header/conftest.py**
   - Test fixtures and helpers
   - Mock context creation helper
   - Common test data

3. **tests/unit/linters/file_header/test_python_header_validation.py** (~10 tests)
   - Basic header structure validation
   - Docstring extraction tests
   - Header presence detection

4. **tests/unit/linters/file_header/test_mandatory_fields.py** (~12 tests)
   - Purpose field validation
   - Scope field validation
   - Overview field validation
   - Dependencies field validation
   - Exports field validation
   - Interfaces field validation
   - Implementation field validation
   - Missing field detection
   - Empty field detection

5. **tests/unit/linters/file_header/test_atemporal_language.py** (~12 tests)
   - Date pattern detection (YYYY-MM-DD, Month YYYY, etc.)
   - Temporal qualifier detection ("currently", "now", "recently")
   - State change language ("replaces", "migrated from", "formerly")
   - Future reference detection ("will be", "planned", "to be added")
   - Acceptable language patterns (present-tense, factual)
   - Multiple violations in single header

6. **tests/unit/linters/file_header/test_ignore_directives.py** (~6 tests)
   - Line-level ignore directives
   - File-level ignore directives
   - Pattern-based ignore in configuration
   - Generic ignore support

7. **tests/unit/linters/file_header/test_configuration.py** (~8 tests)
   - Default configuration loading
   - Custom configuration from .thailint.yaml
   - Required fields configuration
   - Ignore patterns configuration
   - Invalid configuration handling

8. **tests/unit/linters/file_header/test_edge_cases.py** (~8 tests)
   - Files without docstrings
   - Malformed docstrings
   - Very long headers
   - Unicode in headers
   - Multi-line field values
   - Empty files
   - Files with only comments

### Example Tests (test_mandatory_fields.py)

```python
"""
Purpose: Test suite for mandatory field validation in Python file headers
Scope: File header linter Python mandatory fields detection
Overview: Comprehensive tests for detecting missing or invalid mandatory fields in Python
    file headers. Tests all required fields (Purpose, Scope, Overview, Dependencies, Exports,
    Interfaces, Implementation) and validates error messages and violation details.
Dependencies: pytest, BaseLintContext mock, FileHeaderRule
Exports: Test functions for mandatory field validation
Interfaces: pytest test functions following project conventions
Implementation: Mock-based testing pattern from magic-numbers linter
"""

import pytest
from src.core.base import BaseLintContext
from src.linters.file_header.linter import FileHeaderRule


class TestMandatoryFieldsDetection:
    """Tests for detecting missing mandatory fields."""

    def test_detects_missing_purpose_field(self):
        """Should detect when Purpose field is missing."""
        code = '''"""
Scope: Test scope
Overview: Test overview
Dependencies: None
Exports: TestClass
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        context = self._create_context(code, "test.py")
        rule = FileHeaderRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert "Purpose" in violations[0].message
        assert "missing" in violations[0].message.lower()

    def test_detects_missing_scope_field(self):
        """Should detect when Scope field is missing."""
        code = '''"""
Purpose: Test purpose
Overview: Test overview
Dependencies: None
Exports: TestClass
Interfaces: test_method()
Implementation: Test implementation
"""
'''
        context = self._create_context(code, "test.py")
        rule = FileHeaderRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert "Scope" in violations[0].message

    def test_detects_multiple_missing_fields(self):
        """Should detect multiple missing mandatory fields."""
        code = '''"""
Purpose: Test purpose only
"""
'''
        context = self._create_context(code, "test.py")
        rule = FileHeaderRule()
        violations = rule.check(context)

        # Should have violations for: Scope, Overview, Dependencies, Exports, Interfaces, Implementation
        assert len(violations) >= 6
        missing_fields = [v.message for v in violations]
        assert any("Scope" in msg for msg in missing_fields)
        assert any("Overview" in msg for msg in missing_fields)

    def test_accepts_all_mandatory_fields_present(self):
        """Should not flag when all mandatory fields present."""
        code = '''"""
Purpose: Complete header with all fields
Scope: Test module scope
Overview: Comprehensive overview explaining module purpose and functionality
Dependencies: pytest, mock
Exports: TestClass, test_function
Interfaces: public_method(), another_method()
Implementation: Uses composition pattern with helper classes
"""
'''
        context = self._create_context(code, "test.py")
        rule = FileHeaderRule()
        violations = rule.check(context)

        # Filter out any non-mandatory-field violations
        mandatory_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(mandatory_violations) == 0

    def _create_context(self, code: str, filename: str) -> BaseLintContext:
        """Create mock context for testing."""
        context = BaseLintContext()
        context.file_content = code
        context.file_path = filename
        context.language = "python"
        return context
```

### Example Tests (test_atemporal_language.py)

```python
"""
Purpose: Test suite for atemporal language detection in file headers
Scope: File header linter atemporal language validation
Overview: Comprehensive tests for detecting temporal language patterns that violate atemporal
    documentation requirements. Tests date detection, temporal qualifiers, state change language,
    and future references. Validates that only present-tense, factual descriptions are accepted.
Dependencies: pytest, BaseLintContext mock, FileHeaderRule
Exports: Test functions for atemporal language validation
Interfaces: pytest test functions following project conventions
Implementation: Pattern-based testing using regex detection
"""

import pytest
from src.core.base import BaseLintContext
from src.linters.file_header.linter import FileHeaderRule


class TestAtemporalLanguageDetection:
    """Tests for detecting temporal language violations."""

    def test_detects_iso_date_format(self):
        """Should detect ISO date format (YYYY-MM-DD)."""
        code = '''"""
Purpose: Created 2025-01-15 for user authentication
Scope: Authentication module
Overview: Handles user login and session management
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1
        assert any("2025-01-15" in v.message or "temporal" in v.message.lower() for v in violations)

    def test_detects_month_year_format(self):
        """Should detect Month YYYY format."""
        code = '''"""
Purpose: Authentication handler
Scope: Updated January 2025 with new features
Overview: Handles user authentication
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_currently_qualifier(self):
        """Should detect 'currently' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Currently supports OAuth and SAML authentication methods
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() or "currently" in v.message for v in violations)

    def test_detects_now_qualifier(self):
        """Should detect 'now' temporal qualifier."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Now includes support for multi-factor authentication
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1

    def test_detects_state_change_language(self):
        """Should detect state change language like 'replaces'."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: This replaces the old authentication system with a new implementation
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() for v in violations)

    def test_detects_future_reference(self):
        """Should detect future reference language."""
        code = '''"""
Purpose: Authentication handler
Scope: Authentication module
Overview: Will be extended to support biometric authentication
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1

    def test_accepts_present_tense_factual(self):
        """Should accept present-tense factual descriptions."""
        code = '''"""
Purpose: Authentication handler for user login
Scope: Authentication module across the application
Overview: Handles user authentication using OAuth and SAML protocols.
    Provides secure login functionality with session management and token handling.
    Supports multi-factor authentication and password reset workflows.
Dependencies: oauth2, saml, bcrypt
Exports: AuthHandler, AuthToken, AuthError
Interfaces: authenticate(), validate_token(), refresh_session()
Implementation: Uses JWT tokens with 24-hour expiration and refresh token rotation
"""
'''
        violations = self._check_code(code)
        # Filter only temporal violations
        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0

    def _check_code(self, code: str) -> list:
        """Helper to check code and return violations."""
        context = BaseLintContext()
        context.file_content = code
        context.file_path = "test.py"
        context.language = "python"
        rule = FileHeaderRule()
        return rule.check(context)
```

### Test Organization Checklist
- [ ] All test files created
- [ ] conftest.py with shared fixtures
- [ ] Mock context creation helper
- [ ] Test data for valid/invalid headers
- [ ] ~40-50 total tests written
- [ ] All tests initially FAIL (implementation doesn't exist)
- [ ] Tests follow pytest conventions
- [ ] Tests pass linting (Pylint 10/10)
- [ ] Tests have A-grade complexity

### Success Criteria
- [ ] Test suite created with 40-50 tests
- [ ] ALL tests fail (RED phase - no implementation)
- [ ] Tests cover all mandatory fields
- [ ] Tests cover atemporal language patterns
- [ ] Tests cover configuration loading
- [ ] Tests cover ignore directives
- [ ] Tests cover edge cases
- [ ] Tests pass linting (Pylint 10/10, Xenon A-grade)
- [ ] Test code is maintainable and clear

### Dependencies
- PR1 complete (documentation in place)

---

## PR3: Implementation - Python Header Linter

### Objective
Implement Python file header validation to pass all PR2 tests (TDD GREEN phase)

### Scope
- Create file_header linter module
- Implement FileHeaderRule class
- Python docstring parser
- Mandatory field validator
- Atemporal language detector
- Configuration support
- Make ALL PR2 tests pass

### Module Structure

```
src/linters/file_header/
├── __init__.py
├── linter.py                    # Main FileHeaderRule class
├── python_parser.py             # Python docstring extraction
├── field_validator.py           # Mandatory field validation
├── atemporal_detector.py        # Temporal language detection
├── config.py                    # Configuration model
└── violation_builder.py         # Violation message generation
```

### Files to Create

#### 1. src/linters/file_header/__init__.py
```python
"""
Purpose: File header linter module initialization
Scope: Exports main FileHeaderRule class for file header validation
Overview: Initializes the file header linter module providing multi-language file header
    validation with mandatory field checking, atemporal language detection, and configuration
    support. Main entry point for file header linting functionality.
Dependencies: FileHeaderRule from linter module
Exports: FileHeaderRule
Interfaces: FileHeaderRule.check() for validation
Implementation: Module-level exports for clean API
"""

from .linter import FileHeaderRule

__all__ = ["FileHeaderRule"]
```

#### 2. src/linters/file_header/config.py
```python
"""
Purpose: Configuration model for file header linter
Scope: FileHeaderConfig dataclass with validation and defaults
Overview: Defines configuration structure for file header linter including required fields
    per language, ignore patterns, and validation options. Provides defaults matching
    ai-doc-standard.md requirements and supports loading from .thailint.yaml configuration.
Dependencies: dataclasses, pathlib
Exports: FileHeaderConfig dataclass
Interfaces: from_dict() class method for configuration loading
Implementation: Dataclass with validation and language-specific defaults
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileHeaderConfig:
    """Configuration for file header linting."""

    # Required fields by language
    required_fields_python: list[str] = field(default_factory=lambda: [
        "Purpose", "Scope", "Overview", "Dependencies", "Exports",
        "Interfaces", "Implementation"
    ])

    # Enforce atemporal language checking
    enforce_atemporal: bool = True

    # Patterns to ignore (file paths)
    ignore: list[str] = field(default_factory=lambda: [
        "test/**",
        "**/migrations/**",
        "**/__init__.py"
    ])

    @classmethod
    def from_dict(cls, config_dict: dict, language: str) -> "FileHeaderConfig":
        """Create config from dictionary."""
        return cls(
            required_fields_python=config_dict.get("required_fields", {}).get("python", cls().required_fields_python),
            enforce_atemporal=config_dict.get("enforce_atemporal", True),
            ignore=config_dict.get("ignore", cls().ignore)
        )
```

#### 3. src/linters/file_header/python_parser.py
```python
"""
Purpose: Python docstring extraction and parsing for file headers
Scope: Parse Python files and extract module-level docstrings
Overview: Extracts module-level docstrings from Python files using AST parsing.
    Parses structured header fields from docstring content and handles both
    well-formed and malformed headers. Provides field extraction and validation
    support for FileHeaderRule.
Dependencies: Python ast module
Exports: PythonHeaderParser class
Interfaces: extract_header(), parse_fields()
Implementation: AST-based docstring extraction with field parsing
"""

import ast
from typing import Optional


class PythonHeaderParser:
    """Extracts and parses Python file headers from docstrings."""

    def extract_header(self, code: str) -> Optional[str]:
        """Extract module-level docstring from Python code.

        Args:
            code: Python source code

        Returns:
            Module docstring or None if not found
        """
        try:
            tree = ast.parse(code)
            return ast.get_docstring(tree)
        except SyntaxError:
            return None

    def parse_fields(self, header: str) -> dict[str, str]:
        """Parse structured fields from header text.

        Args:
            header: Header docstring text

        Returns:
            Dictionary of field_name -> field_value
        """
        fields = {}
        current_field = None
        current_value = []

        for line in header.split('\n'):
            # Check if line starts a new field (e.g., "Purpose: ...")
            if ':' in line and not line.startswith(' '):
                # Save previous field
                if current_field:
                    fields[current_field] = '\n'.join(current_value).strip()

                # Start new field
                field_name, field_value = line.split(':', 1)
                current_field = field_name.strip()
                current_value = [field_value.strip()]
            elif current_field:
                # Continuation of current field
                current_value.append(line.strip())

        # Save last field
        if current_field:
            fields[current_field] = '\n'.join(current_value).strip()

        return fields
```

#### 4. src/linters/file_header/atemporal_detector.py
```python
"""
Purpose: Detects temporal language patterns in file headers
Scope: Atemporal language validation for all file types
Overview: Implements pattern-based detection of temporal language that violates atemporal
    documentation requirements. Detects dates, temporal qualifiers, state change language,
    and future references using regex patterns. Provides violation details for each pattern match.
Dependencies: re module for regex matching
Exports: AtemporalDetector class
Interfaces: detect_violations(), check_text()
Implementation: Regex-based pattern matching with configurable patterns
"""

import re
from typing import List, Tuple


class AtemporalDetector:
    """Detects temporal language patterns in text."""

    # Date patterns
    DATE_PATTERNS = [
        (r'\d{4}-\d{2}-\d{2}', 'ISO date format (YYYY-MM-DD)'),
        (r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', 'Month Year format'),
        (r'(?:Created|Updated|Modified):\s*\d{4}', 'Date metadata'),
    ]

    # Temporal qualifiers
    TEMPORAL_QUALIFIERS = [
        (r'\bcurrently\b', 'temporal qualifier "currently"'),
        (r'\bnow\b', 'temporal qualifier "now"'),
        (r'\brecently\b', 'temporal qualifier "recently"'),
        (r'\bsoon\b', 'temporal qualifier "soon"'),
        (r'\bfor now\b', 'temporal qualifier "for now"'),
    ]

    # State change language
    STATE_CHANGE = [
        (r'\breplaces?\b', 'state change "replaces"'),
        (r'\bmigrated from\b', 'state change "migrated from"'),
        (r'\bformerly\b', 'state change "formerly"'),
        (r'\bold implementation\b', 'state change "old"'),
        (r'\bnew implementation\b', 'state change "new"'),
    ]

    # Future references
    FUTURE_REFS = [
        (r'\bwill be\b', 'future reference "will be"'),
        (r'\bplanned\b', 'future reference "planned"'),
        (r'\bto be added\b', 'future reference "to be added"'),
        (r'\bcoming soon\b', 'future reference "coming soon"'),
    ]

    def detect_violations(self, text: str) -> List[Tuple[str, str, int]]:
        """Detect all temporal language violations in text.

        Args:
            text: Text to check

        Returns:
            List of (pattern, description, line_number) tuples
        """
        violations = []

        # Check all pattern categories
        all_patterns = (
            self.DATE_PATTERNS +
            self.TEMPORAL_QUALIFIERS +
            self.STATE_CHANGE +
            self.FUTURE_REFS
        )

        lines = text.split('\n')
        for line_num, line in enumerate(lines, start=1):
            for pattern, description in all_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append((pattern, description, line_num))

        return violations
```

#### 5. src/linters/file_header/field_validator.py
```python
"""
Purpose: Validates mandatory fields in file headers
Scope: Field validation for all supported languages
Overview: Validates presence and quality of mandatory header fields. Checks that all
    required fields are present, non-empty, and meet minimum content requirements.
    Supports language-specific required fields and provides detailed violation messages.
Dependencies: FileHeaderConfig for field requirements
Exports: FieldValidator class
Interfaces: validate_fields(), check_required_fields()
Implementation: Configuration-driven validation with field presence checking
"""

from typing import List, Tuple
from .config import FileHeaderConfig


class FieldValidator:
    """Validates mandatory fields in headers."""

    def __init__(self, config: FileHeaderConfig):
        """Initialize validator with configuration."""
        self.config = config

    def validate_fields(self, fields: dict[str, str], language: str) -> List[Tuple[str, str]]:
        """Validate all required fields are present.

        Args:
            fields: Dictionary of parsed header fields
            language: File language (python, typescript, etc.)

        Returns:
            List of (field_name, error_message) tuples for missing/invalid fields
        """
        violations = []
        required_fields = self._get_required_fields(language)

        for field_name in required_fields:
            if field_name not in fields:
                violations.append((field_name, f"Missing mandatory field: {field_name}"))
            elif not fields[field_name] or len(fields[field_name].strip()) == 0:
                violations.append((field_name, f"Empty mandatory field: {field_name}"))

        return violations

    def _get_required_fields(self, language: str) -> List[str]:
        """Get required fields for language."""
        if language == "python":
            return self.config.required_fields_python
        return []  # Other languages in PR5
```

#### 6. src/linters/file_header/violation_builder.py
```python
"""
Purpose: Builds violation messages for file header linter
Scope: Violation creation for all violation types
Overview: Creates formatted violation messages for file header validation failures.
    Handles missing fields, atemporal language, and other header issues with clear,
    actionable messages. Provides consistent violation format across all validation types.
Dependencies: Violation type from core
Exports: ViolationBuilder class
Interfaces: build_missing_field(), build_atemporal_violation()
Implementation: Message templates with context-specific details
"""

from src.core.types import Violation


class ViolationBuilder:
    """Builds violation messages for file header issues."""

    def __init__(self, rule_id: str):
        """Initialize with rule ID."""
        self.rule_id = rule_id

    def build_missing_field(
        self, field_name: str, file_path: str, line: int = 1
    ) -> Violation:
        """Build violation for missing mandatory field.

        Args:
            field_name: Name of missing field
            file_path: Path to file
            line: Line number

        Returns:
            Violation object
        """
        return Violation(
            rule_id=self.rule_id,
            message=f"Missing mandatory field: {field_name}",
            file_path=file_path,
            line=line,
            column=1,
            severity="error",
            suggestion=f"Add '{field_name}:' field to file header"
        )

    def build_atemporal_violation(
        self, pattern: str, description: str, file_path: str, line: int
    ) -> Violation:
        """Build violation for temporal language.

        Args:
            pattern: Matched pattern
            description: Description of temporal language
            file_path: Path to file
            line: Line number

        Returns:
            Violation object
        """
        return Violation(
            rule_id=self.rule_id,
            message=f"Temporal language detected: {description}",
            file_path=file_path,
            line=line,
            column=1,
            severity="error",
            suggestion="Use present-tense factual descriptions without temporal references"
        )
```

#### 7. src/linters/file_header/linter.py
```python
"""
Purpose: Main file header linter rule implementation
Scope: FileHeaderRule class implementing BaseLintRule interface
Overview: Orchestrates file header validation for Python files using focused helper classes.
    Coordinates docstring extraction, field validation, atemporal language detection, and
    violation building. Supports configuration from .thailint.yaml and ignore directives.
    Validates headers against mandatory field requirements and atemporal language standards.
Dependencies: BaseLintRule, PythonHeaderParser, FieldValidator, AtemporalDetector, ViolationBuilder
Exports: FileHeaderRule class
Interfaces: FileHeaderRule.check(context) returns list[Violation]
Implementation: Composition pattern with helper classes, AST-based Python parsing
"""

from pathlib import Path
from typing import List

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation

from .atemporal_detector import AtemporalDetector
from .config import FileHeaderConfig
from .field_validator import FieldValidator
from .python_parser import PythonHeaderParser
from .violation_builder import ViolationBuilder


class FileHeaderRule(BaseLintRule):
    """Validates file headers for mandatory fields and atemporal language."""

    def __init__(self) -> None:
        """Initialize the file header rule."""
        self._violation_builder = ViolationBuilder(self.rule_id)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "file-header.validation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "File Header Validation"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Validates file headers for mandatory fields and atemporal language"

    def check(self, context: BaseLintContext) -> List[Violation]:
        """Check file header for violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations
        """
        # Only Python for now (PR3), multi-language in PR5
        if context.language != "python":
            return []

        # Load configuration
        config = self._load_config(context)

        # Check if file should be ignored
        if self._should_ignore_file(context, config):
            return []

        # Extract and validate header
        return self._check_python_header(context, config)

    def _load_config(self, context: BaseLintContext) -> FileHeaderConfig:
        """Load configuration from context."""
        # Try production config first
        if hasattr(context, "metadata") and isinstance(context.metadata, dict):
            if "file_header" in context.metadata:
                return load_linter_config(context, "file_header", FileHeaderConfig)

        # Use defaults
        return FileHeaderConfig()

    def _should_ignore_file(self, context: BaseLintContext, config: FileHeaderConfig) -> bool:
        """Check if file matches ignore patterns."""
        if not context.file_path:
            return False

        file_path = Path(context.file_path)
        for pattern in config.ignore:
            if file_path.match(pattern):
                return True

        return False

    def _check_python_header(
        self, context: BaseLintContext, config: FileHeaderConfig
    ) -> List[Violation]:
        """Check Python file header."""
        violations = []

        # Extract docstring
        parser = PythonHeaderParser()
        header = parser.extract_header(context.file_content or "")

        if not header:
            return [self._violation_builder.build_missing_field(
                "docstring", context.file_path or "", 1
            )]

        # Parse fields
        fields = parser.parse_fields(header)

        # Validate mandatory fields
        field_validator = FieldValidator(config)
        field_violations = field_validator.validate_fields(fields, context.language)

        for field_name, error_message in field_violations:
            violations.append(
                self._violation_builder.build_missing_field(
                    field_name, context.file_path or "", 1
                )
            )

        # Check atemporal language if enabled
        if config.enforce_atemporal:
            atemporal_detector = AtemporalDetector()
            atemporal_violations = atemporal_detector.detect_violations(header)

            for pattern, description, line_num in atemporal_violations:
                violations.append(
                    self._violation_builder.build_atemporal_violation(
                        pattern, description, context.file_path or "", line_num
                    )
                )

        return violations
```

### Implementation Checklist
- [ ] All module files created
- [ ] Config model with defaults
- [ ] Python parser extracts docstrings
- [ ] Field validator checks mandatory fields
- [ ] Atemporal detector with regex patterns
- [ ] Violation builder with clear messages
- [ ] Main FileHeaderRule class orchestrates
- [ ] Configuration loading from .thailint.yaml
- [ ] Ignore pattern support
- [ ] All PR2 tests pass (40-50/40-50)
- [ ] Code passes linting (Pylint 10/10, A-grade)
- [ ] Test coverage ≥ 85%

### Success Criteria
- [ ] All modules created and functional
- [ ] FileHeaderRule implements BaseLintRule
- [ ] All PR2 tests pass (40-50/40-50 tests GREEN)
- [ ] Code passes linting (Pylint 10.00/10, Xenon A-grade)
- [ ] Test coverage ≥ 85%
- [ ] No regressions in other linters
- [ ] Documentation strings follow standards

### Dependencies
- PR2 complete (tests written and failing)

---

## PR4: Test Suite - Multi-Language Support

### Objective
Write comprehensive test suite for JavaScript/TypeScript, Bash, Markdown, CSS header validation (TDD RED phase)

### Scope
- Tests for TypeScript/JavaScript JSDoc comments (~20 tests)
- Tests for Bash comment headers (~15 tests)
- Tests for Markdown YAML frontmatter (~15 tests)
- Tests for CSS comment headers (~10 tests)
- All tests must initially FAIL

### Files to Create

1. **tests/unit/linters/file_header/test_typescript_headers.py** (~20 tests)
   - JSDoc comment extraction
   - TypeScript mandatory fields
   - JSDoc format validation
   - Multi-line JSDoc comments
   - Missing/malformed JSDoc

2. **tests/unit/linters/file_header/test_bash_headers.py** (~15 tests)
   - Bash comment header extraction
   - Bash mandatory fields
   - Multi-line bash comments
   - Shebang handling

3. **tests/unit/linters/file_header/test_markdown_headers.py** (~15 tests)
   - YAML frontmatter extraction
   - Markdown mandatory fields (purpose, scope, audience, status, updated)
   - Invalid YAML handling
   - Missing frontmatter

4. **tests/unit/linters/file_header/test_css_headers.py** (~10 tests)
   - CSS comment extraction
   - CSS mandatory fields
   - Multi-line CSS comments

5. **tests/unit/linters/file_header/test_multi_language_validation.py** (~10 tests)
   - Language detection
   - Parser selection
   - Cross-language field validation
   - Language-specific required fields

### Example Test Structure (TypeScript)

```python
"""
Purpose: Test suite for TypeScript/JavaScript file header validation
Scope: File header linter TypeScript JSDoc validation
Overview: Tests for TypeScript and JavaScript file header validation including JSDoc
    comment extraction, mandatory field detection, and format validation. Covers both
    .ts and .tsx files with TypeScript-specific requirements.
Dependencies: pytest, BaseLintContext, FileHeaderRule
Exports: Test classes for TypeScript header validation
Interfaces: pytest test functions
Implementation: Mock-based testing with Tree-sitter integration tests
"""

import pytest
from src.linters.file_header.linter import FileHeaderRule


class TestTypeScriptHeaderExtraction:
    """Tests for extracting headers from TypeScript files."""

    def test_extracts_jsdoc_comment(self):
        """Should extract JSDoc comment from TypeScript file."""
        code = '''/**
 * Purpose: TypeScript module
 * Scope: Application utilities
 * Overview: Provides utility functions
 * Dependencies: lodash
 * Exports: utility functions
 * Props/Interfaces: UtilityOptions interface
 * State/Behavior: Stateless utility module
 */

export function utility() {}
'''
        context = self._create_context(code, "test.ts", "typescript")
        rule = FileHeaderRule()
        violations = rule.check(context)

        # Should not have "missing docstring" violation
        assert not any("docstring" in v.message.lower() for v in violations)
```

### Testing Checklist
- [ ] TypeScript JSDoc tests (~20 tests)
- [ ] Bash comment tests (~15 tests)
- [ ] Markdown frontmatter tests (~15 tests)
- [ ] CSS comment tests (~10 tests)
- [ ] Multi-language tests (~10 tests)
- [ ] All tests initially FAIL (no multi-language implementation)
- [ ] Tests pass linting (Pylint 10/10, A-grade)
- [ ] Total: ~60 new tests

### Success Criteria
- [ ] ~60 new tests written
- [ ] All tests initially FAIL (RED phase)
- [ ] Tests cover all 4 new languages
- [ ] Tests cover language-specific mandatory fields
- [ ] Tests pass linting (Pylint 10/10, Xenon A-grade)
- [ ] Clear test organization and naming

### Dependencies
- PR3 complete (Python implementation working)

---

## PR5: Implementation - Multi-Language Header Linter

### Objective
Implement multi-language file header validation to pass all PR4 tests (TDD GREEN phase)

### Scope
- TypeScript/JavaScript JSDoc parser (Tree-sitter)
- Bash comment parser (regex)
- Markdown frontmatter parser (PyYAML)
- CSS comment parser (regex)
- Unified validation across languages
- Update FileHeaderRule for multi-language support

### Files to Create

1. **src/linters/file_header/typescript_parser.py**
   - Tree-sitter based JSDoc extraction
   - Field parsing from JSDoc comments
   - TypeScript/JavaScript support

2. **src/linters/file_header/bash_parser.py**
   - Regex-based comment extraction
   - Bash-specific field parsing
   - Shebang handling

3. **src/linters/file_header/markdown_parser.py**
   - PyYAML frontmatter extraction
   - YAML field validation
   - Markdown-specific fields

4. **src/linters/file_header/css_parser.py**
   - Regex-based CSS comment extraction
   - Multi-line comment handling
   - CSS-specific fields

5. **src/linters/file_header/language_detector.py**
   - File extension to language mapping
   - Parser selection logic

### Files to Modify

1. **src/linters/file_header/config.py**
   - Add required_fields_typescript
   - Add required_fields_bash
   - Add required_fields_markdown
   - Add required_fields_css

2. **src/linters/file_header/field_validator.py**
   - Support all language field requirements

3. **src/linters/file_header/linter.py**
   - Multi-language check() method
   - Parser routing by language
   - Update to MultiLanguageLintRule

### Implementation Notes
- Reuse Tree-sitter from magic-numbers/nesting linters
- PyYAML for markdown frontmatter
- Regex for Bash/CSS (simpler approach)
- Each language has specific required fields:
  - TypeScript: Purpose, Scope, Overview, Dependencies, Exports, Props/Interfaces, State/Behavior
  - Bash: Purpose, Scope, Overview, Dependencies, Exports, Usage, Environment
  - Markdown: purpose, scope, overview, audience, status, updated, related
  - CSS: Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Environment

### Success Criteria
- [ ] All parsers implemented
- [ ] Language detection working
- [ ] All PR4 tests pass (~60/60 tests GREEN)
- [ ] Code passes linting (Pylint 10/10, Xenon A-grade)
- [ ] Test coverage ≥ 85%
- [ ] No regressions in Python support

### Dependencies
- PR4 complete (multi-language tests written)

---

## PR6: Dogfooding - Update Project Files

### Objective
Systematically update all project files with new AI-optimized headers

### Scope
- Audit all files (~200-300 files)
- Update in 6 systematic phases
- Run linter after each phase
- Achieve 0 violations

### Phase Breakdown

**Phase 1: Core Linter Files** (~50 files)
- `src/linters/magic_numbers/*.py`
- `src/linters/nesting/*.py`
- `src/linters/srp/*.py`
- `src/linters/dry/*.py`
- `src/linters/file_placement/*.py`
- `src/linters/file_header/*.py` (new)

**Phase 2: Infrastructure** (~20 files)
- `src/core/*.py`
- `src/orchestrator/*.py`
- `src/analyzers/*.py`
- `src/linter_config/*.py`

**Phase 3: CLI and Config** (~10 files)
- `src/cli.py`
- `src/config.py`
- `src/api.py`
- `src/utils/*.py`

**Phase 4: Tests** (~100 files)
- `tests/unit/linters/**/*.py`
- `tests/integration/**/*.py`
- `tests/conftest.py`

**Phase 5: Documentation** (~30 files)
- `.ai/docs/*.md`
- `docs/*.md`
- `.ai/howtos/*.md`

**Phase 6: Config Files** (~20 files)
- `.github/workflows/*.yml`
- `.pre-commit-config.yaml`
- `pyproject.toml` (add comment headers)
- `justfile`

### Implementation Strategy

1. **Create Helper Script**: `scripts/add_file_headers.py`
   - Analyze file structure
   - Generate skeleton headers
   - Extract imports for Dependencies
   - Extract classes/functions for Exports
   - Leave [TODO] for manual completion

2. **Process Each Phase**:
   - Run helper script to generate skeletons
   - Manually review and complete [TODO] markers
   - Commit batch (20-30 files)
   - Run linter: `just lint-full`
   - Run tests: `just test`
   - Fix any issues
   - Repeat for next batch

3. **Validation After Each Phase**:
   - `python -m src.cli file-header src/` (or relevant directory)
   - `just lint-full` (must exit 0)
   - `just test` (must exit 0)

### Success Criteria
- [ ] All 6 phases complete
- [ ] ~200-300 files updated
- [ ] 0 file-header violations
- [ ] All tests still pass
- [ ] All linting passes (Pylint 10/10, Xenon A-grade)
- [ ] No regressions introduced

### Dependencies
- PR5 complete (multi-language linter working)

---

## PR7: Documentation and Integration

### Objective
Complete documentation, CLI integration, examples, and pre-commit hook

### Scope
- Comprehensive documentation
- CLI command integration
- Usage examples
- Pre-commit hook
- README update

### Files to Create

1. **docs/file-header-linter.md** (~600-800 lines)
   - Overview and motivation
   - Configuration reference
   - Supported file types and mandatory fields
   - Atemporal language rules and patterns
   - Ignore directives
   - Usage examples for all file types
   - Troubleshooting guide
   - Best practices
   - Migration guide

2. **examples/file_header_usage.py**
   - Working Python example
   - API usage demonstration
   - Configuration examples

### Files to Modify

1. **src/cli.py**
   - Add `file-header` command
   - Options: --config, --format, --recursive
   - Help text and examples

2. **README.md**
   - Add file-header linter section
   - Quick start examples
   - Link to comprehensive docs

3. **.pre-commit-config.yaml**
   - Add file-header-check hook
   - WARNING severity initially

4. **.ai/howtos/**
   - Update how-to-write-file-headers.md
   - Add troubleshooting examples

### CLI Integration

```python
# In src/cli.py, add command:

@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--config", type=click.Path(exists=True), help="Path to .thailint.yaml")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.option("--recursive", is_flag=True, help="Recursively check directories")
def file_header(paths, config, format, recursive):
    """Check file headers for mandatory fields and atemporal language.

    Examples:
        thailint file-header src/
        thailint file-header --recursive src/ tests/
        thailint file-header --format json src/cli.py
    """
    # Implementation
```

### Pre-commit Hook

```yaml
# In .pre-commit-config.yaml:
repos:
  - repo: local
    hooks:
      - id: file-header-check
        name: Check file headers
        entry: python -m src.cli file-header
        language: system
        types: [python, javascript, typescript, bash, markdown, css]
        pass_filenames: true
        # Start with warning, upgrade to error after grace period
        verbose: true
```

### Success Criteria
- [ ] Documentation complete (600-800 lines)
- [ ] CLI command functional
- [ ] Examples working
- [ ] README updated
- [ ] Pre-commit hook configured
- [ ] All tests pass (100-110 total)
- [ ] Linting passes (Pylint 10/10, Xenon A-grade)

### Dependencies
- PR6 complete (all files updated)

---

## Implementation Guidelines

### Code Standards
- All code must pass `just lint-full` (Pylint 10.00/10, Xenon A-grade)
- Follow existing linter patterns (magic-numbers structure)
- Use composition pattern with focused helper classes
- Maximum cyclomatic complexity: A-grade (≤ 4 branches per function)
- Type hints required for all functions
- Docstrings required (Google-style)

### Testing Requirements
- TDD approach: tests before implementation (PR2→PR3, PR4→PR5)
- Target test coverage: 85-90%
- Tests must be maintainable and clear
- Mock-based testing for contexts
- Follow pytest conventions
- Test both positive and negative cases

### Documentation Standards
- All modules need comprehensive headers
- Follow new AI-optimized standard
- Atemporal language required
- Clear purpose, scope, overview
- Document dependencies and exports

### Security Considerations
- No secrets in headers
- Validate user input
- Safe file path handling
- Proper error messages (no path disclosure)

### Performance Targets
- Parser performance: < 100ms per file
- Memory efficient (stream large files)
- Minimal regex backtracking
- Cache compiled patterns

---

## Rollout Strategy

### Phase 1: Foundation (PR1)
- Documentation integrated
- Standards established
- Team aware of new requirements

### Phase 2: Python Support (PR2-PR3)
- TDD implementation
- Python files validated
- Initial dogfooding possible

### Phase 3: Multi-Language (PR4-PR5)
- Full language support
- Comprehensive validation
- Production-ready linter

### Phase 4: Adoption (PR6)
- Systematic file updates
- Team training
- 100% compliance

### Phase 5: Integration (PR7)
- CLI and tooling
- Pre-commit enforcement
- Documentation complete

---

## Success Metrics

### Launch Metrics
- [ ] 7 PRs merged successfully
- [ ] 100-110 tests passing (100% pass rate)
- [ ] Pylint 10.00/10 score
- [ ] Xenon A-grade complexity
- [ ] Test coverage ≥ 85%

### Ongoing Metrics
- [ ] 0 file-header violations in codebase
- [ ] 100% file compliance (~200-300 files)
- [ ] Pre-commit hook active
- [ ] Documentation complete
- [ ] Team trained on new standard
- [ ] False positive rate < 5%
