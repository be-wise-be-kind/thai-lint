# File Header Linter - AI Context

**Purpose**: AI agent context document for implementing File Header Linter feature

**Scope**: Comprehensive architectural context for file header validation across multiple programming languages

**Overview**: Comprehensive context document for AI agents working on the File Header Linter feature.
    Provides architectural overview, design decisions, integration patterns, and implementation guidance
    for building a multi-language file header linter that enforces AI-optimized documentation standards
    with mandatory field validation and atemporal language detection. Includes detailed context on parser
    selection, validation strategies, and dogfooding approach for systematic codebase updates.

**Dependencies**: BaseLintRule interface, Python AST, Tree-sitter, PyYAML, regex patterns, pytest framework

**Exports**: Architectural context, design decisions, integration patterns, and implementation guidance

**Related**: PR_BREAKDOWN.md for detailed implementation tasks, PROGRESS_TRACKER.md for current progress status

**Implementation**: Multi-language linter architecture with composition pattern, language-specific parsers, and unified validation logic

---

## Overview

The File Header Linter enforces comprehensive file header standards across Python, JavaScript/TypeScript, Bash, Markdown, CSS, and other file types. This linter represents a significant evolution in thai-lint's capabilities:

1. **First Multi-File-Type Linter**: Unlike existing linters (Python/TypeScript only), this supports 6+ file types including non-code files (Markdown, CSS)
2. **Documentation Quality Focus**: Shifts from code quality (complexity, DRY, SRP) to documentation quality
3. **AI-Optimized Standards**: Implements cutting-edge AI-optimized documentation format designed for LLM-assisted development
4. **Atemporal Language Enforcement**: Novel requirement detecting temporal language patterns (dates, "currently", state changes)
5. **Systematic Dogfooding**: Will update 200-300 project files, largest refactoring effort in thai-lint history

## Project Background

### Why This Linter?

**Problem**: Inconsistent and inadequate file documentation across the codebase
- Many files lack comprehensive headers
- Existing headers use temporal language ("currently", dates) that quickly becomes outdated
- No standard format optimized for AI code assistants
- Difficult for AI tools to quickly understand file purpose and dependencies

**Solution**: Automated enforcement of AI-optimized documentation standard
- Mandatory comprehensive headers for all files
- Atemporal language ensuring long-term accuracy
- Structured metadata optimized for LLM parsing
- Multi-language support for complete codebase coverage

### Historical Context

**Evolution of thai-lint**:
1. **Phase 1**: File placement linter (directory structure)
2. **Phase 2**: Code quality linters (nesting, SRP, DRY, magic-numbers)
3. **Phase 3**: Documentation quality linter (file-header) ← **THIS FEATURE**

**Prior Art**:
- Magic-numbers linter established multi-language pattern (Python + TypeScript)
- Nesting linter demonstrated Tree-sitter integration
- SRP/DRY linters showed composition pattern with helper classes

## Feature Vision

### Primary Goals

1. **Enforce Comprehensive Headers**: Every file has clear Purpose, Scope, Overview, Dependencies, Exports
2. **Atemporal Language**: Eliminate temporal references that decay over time
3. **Multi-Language Support**: Consistent standards across Python, TypeScript, Bash, Markdown, CSS
4. **AI-Optimized Format**: Structured metadata optimized for LLM code understanding
5. **100% Compliance**: Systematically update entire codebase (200-300 files)

### Success Vision

**End State**:
- Every file in thai-lint has comprehensive, atemporal header
- New files automatically validated by pre-commit hook
- AI coding assistants (Claude, Copilot, Cursor) get 2-3x better file understanding
- Documentation never becomes outdated (no temporal references)
- Team has clear, consistent documentation standards

**User Experience**:
```bash
# Developer adds new file without proper header
$ git commit -m "Add new feature"

# Pre-commit hook runs
Checking file headers...........................................................Failed
- file: src/new_feature.py
  error: Missing mandatory field: Purpose
  error: Missing mandatory field: Overview

# Developer fixes header, commit succeeds
$ thailint file-header src/new_feature.py
✓ All checks passed
```

## Current Application Context

### Existing Linter Architecture

**BaseLintRule Interface** (`src/core/base.py`):
```python
class BaseLintRule(ABC):
    @property
    @abstractmethod
    def rule_id(self) -> str: ...

    @property
    @abstractmethod
    def rule_name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def check(self, context: BaseLintContext) -> List[Violation]: ...
```

**Multi-Language Support Pattern** (from magic-numbers):
```python
class MultiLanguageLintRule(BaseLintRule):
    """Base class for rules supporting multiple languages."""

    def check(self, context: BaseLintContext) -> List[Violation]:
        if context.language == "python":
            return self._check_python(context, config)
        elif context.language in ("typescript", "javascript"):
            return self._check_typescript(context, config)
        return []
```

**Composition Pattern** (from all linters):
- Main linter class orchestrates
- Focused helper classes for specific tasks
- Configuration model with defaults
- Violation builder for consistent messages

### Integration with Orchestrator

**Auto-Discovery** (`src/core/rule_discovery.py`):
```python
discover_rules("src.linters")  # Automatically finds all BaseLintRule implementations
```

**Linter Registration**: No manual registration needed - discovered automatically if:
1. Class inherits from `BaseLintRule` or `MultiLanguageLintRule`
2. Located in `src/linters/` directory
3. Implements all abstract methods

### CLI Integration Pattern

**Existing Commands** (from magic-numbers):
```python
@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--config", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def magic_numbers(paths, config, format):
    """Check for magic numbers."""
    # Implementation
```

**File-Header Command** (to be implemented):
```python
@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--config", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.option("--recursive", is_flag=True)
def file_header(paths, config, format, recursive):
    """Check file headers for mandatory fields and atemporal language."""
    # Implementation
```

## Target Architecture

### Core Components

```
src/linters/file_header/
├── __init__.py                 # Module exports
├── linter.py                   # FileHeaderRule - orchestrator
├── config.py                   # FileHeaderConfig - configuration model
├── violation_builder.py        # ViolationBuilder - message generation
│
├── python_parser.py            # Python docstring extraction (AST)
├── typescript_parser.py        # TypeScript JSDoc extraction (Tree-sitter)
├── bash_parser.py              # Bash comment extraction (regex)
├── markdown_parser.py          # Markdown frontmatter extraction (PyYAML)
├── css_parser.py               # CSS comment extraction (regex)
├── language_detector.py        # File extension → language mapping
│
├── field_validator.py          # Mandatory field validation
└── atemporal_detector.py       # Temporal language detection (regex)
```

### Component Responsibilities

**FileHeaderRule** (linter.py):
- Main orchestrator implementing `MultiLanguageLintRule`
- Routes to language-specific parsers
- Coordinates validation workflow
- Returns violations

**Language Parsers**:
- **PythonHeaderParser**: AST-based docstring extraction
- **TypeScriptParser**: Tree-sitter JSDoc comment extraction
- **BashParser**: Regex-based `#` comment extraction
- **MarkdownParser**: PyYAML frontmatter (YAML between `---` markers)
- **CSSParser**: Regex-based `/* */` comment extraction

**Validators**:
- **FieldValidator**: Checks mandatory fields present and non-empty
- **AtemporalDetector**: Regex patterns for temporal language

**Configuration**:
- **FileHeaderConfig**: Required fields per language, ignore patterns, atemporal enforcement

**Violation Builder**:
- **ViolationBuilder**: Creates formatted violation messages

### Parser Selection Strategy

**Decision Tree**:
```
File → Language Detection → Parser Selection
  ├─ .py          → "python"     → PythonHeaderParser (AST)
  ├─ .ts, .tsx    → "typescript" → TypeScriptParser (Tree-sitter)
  ├─ .js, .jsx    → "javascript" → TypeScriptParser (Tree-sitter, compatible)
  ├─ .sh, .bash   → "bash"       → BashParser (regex)
  ├─ .md          → "markdown"   → MarkdownParser (PyYAML)
  └─ .css, .scss  → "css"        → CSSParser (regex)
```

**Parser Technology Choices**:

| Language | Technology | Rationale |
|----------|-----------|-----------|
| Python | Python AST | Built-in, accurate, `ast.get_docstring()` |
| TypeScript/JavaScript | Tree-sitter | Proven pattern from magic-numbers/nesting linters |
| Bash | Regex | Simplest - just `#` comment lines at top |
| Markdown | PyYAML | YAML frontmatter standard format |
| CSS | Regex | Simple `/* */` block comments |

### User Journey

**Journey 1: Developer Adds New Python File**

1. Developer creates `src/new_module.py`
2. Developer runs: `git commit -m "Add module"`
3. Pre-commit hook triggers: `thailint file-header`
4. Linter detects missing header, fails commit
5. Developer adds header with all mandatory fields
6. Pre-commit passes, commit succeeds

**Journey 2: Developer Updates Existing File**

1. Developer modifies `src/existing.py`
2. File has old header with temporal language: "Currently supports OAuth"
3. Pre-commit hook detects: "Temporal language: 'currently'"
4. Developer updates: "Supports OAuth authentication"
5. Pre-commit passes

**Journey 3: Team Dogfooding**

1. AI agent runs: `thailint file-header src/`
2. Finds 200 violations across 150 files
3. Agent systematically updates in 6 phases
4. Each phase: generate skeleton → manual review → commit batch
5. Final: 0 violations, 100% compliance

## Key Decisions Made

### Decision 1: Parser Technology Per Language

**Context**: Need to extract headers from 6+ different file types

**Options Considered**:
1. **Unified Regex Approach**: Single regex engine for all languages
   - Pros: Simple, no dependencies
   - Cons: Fragile, hard to maintain, poor accuracy
2. **Language-Specific Tools**: AST for Python, Tree-sitter for TS, YAML for MD, Regex for simple
   - Pros: Accurate, maintainable, proven patterns
   - Cons: Multiple dependencies, more complex
3. **Tree-sitter for Everything**: Universal parser generator
   - Pros: Consistent approach
   - Cons: Overkill for simple formats (Bash, CSS), larger dependency

**Decision**: **Language-Specific Tools** (Option 2)
- Python: AST (built-in, accurate)
- TypeScript/JavaScript: Tree-sitter (proven in project)
- Bash/CSS: Regex (simple enough)
- Markdown: PyYAML (standard for frontmatter)

**Rationale**:
- Leverages existing patterns (Tree-sitter already integrated)
- Balances accuracy with simplicity
- Each tool optimized for its file type
- Minimizes new dependencies (only PyYAML new)

### Decision 2: Atemporal Language Enforcement Level

**Context**: How strictly to enforce atemporal language requirements?

**Options Considered**:
1. **Warning Only**: Suggest but don't require atemporal language
2. **Error (Required)**: Block commits with temporal language
3. **Configurable**: Let teams choose severity

**Decision**: **Error (Required)** with escape hatch (ignore directives)

**Rationale**:
- Temporal language quickly becomes outdated (dates, "currently")
- Core value proposition of new standard
- Ignore directives available for rare exceptions
- Better to enforce strictly and adjust if needed

**Temporal Patterns Detected**:
1. **Dates**: `2025-01-15`, `January 2025`, `Created: 2024`
2. **Temporal Qualifiers**: "currently", "now", "recently", "soon"
3. **State Changes**: "replaces", "migrated from", "formerly", "old"/"new"
4. **Future References**: "will be", "planned", "to be added"

### Decision 3: Dogfooding Strategy

**Context**: Need to update 200-300 existing files with new headers

**Options Considered**:
1. **Big Bang**: Update all files in one massive PR
2. **Gradual Optional**: Update files as they're touched
3. **Systematic Phased**: Update in organized phases by priority

**Decision**: **Systematic Phased** (Option 3)

**Rationale**:
- Big Bang too risky, hard to review
- Gradual too slow, inconsistent coverage
- Phased approach:
  - Manageable review batches (20-30 files)
  - Prioritized by importance (core linters first)
  - Tests after each phase (catch breakage early)
  - Demonstrates linter effectiveness

**6 Phases**:
1. Core linter files (~50 files) - highest priority
2. Infrastructure (~20 files)
3. CLI/config (~10 files)
4. Tests (~100 files)
5. Documentation (~30 files)
6. Config files (~20 files)

### Decision 4: Mandatory Fields Per Language

**Context**: Different file types need different header information

**Decision**: Language-specific mandatory fields

**Python**:
- Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Implementation

**TypeScript/JavaScript**:
- Purpose, Scope, Overview, Dependencies, Exports, Props/Interfaces, State/Behavior

**Bash**:
- Purpose, Scope, Overview, Dependencies, Exports, Usage, Environment

**Markdown**:
- purpose, scope, overview, audience, status, updated, related

**CSS**:
- Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Environment

**Rationale**:
- Each language has unique needs (e.g., TypeScript has Props, Bash has Usage)
- Reflects ai-doc-standard.md recommendations
- Balances comprehensiveness with practicality

### Decision 5: TDD Approach

**Context**: How to implement multi-language support?

**Decision**: Strict TDD with two test phases
- PR2: Python tests (RED)
- PR3: Python implementation (GREEN)
- PR4: Multi-language tests (RED)
- PR5: Multi-language implementation (GREEN)

**Rationale**:
- Proven pattern from magic-numbers linter
- Ensures comprehensive test coverage
- Validates design before implementation
- Each PR is independently revertible
- Clear success criteria (tests pass)

## Integration Points

### With Existing Features

**Pre-commit Hooks** (`.pre-commit-config.yaml`):
- Add file-header-check hook
- Run on relevant file types: python, javascript, typescript, bash, markdown, css
- Initial severity: WARNING (grace period)
- Later: ERROR (enforcement)

**CLI Integration** (`src/cli.py`):
- New command: `thailint file-header [PATHS]`
- Options: --config, --format, --recursive
- Consistent with existing commands (magic-numbers, nesting, etc.)

**Configuration System** (`.thailint.yaml`):
```yaml
file-header:
  enforce_atemporal: true
  required_fields:
    python: [Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Implementation]
    typescript: [Purpose, Scope, Overview, Dependencies, Exports, Props/Interfaces, State/Behavior]
  ignore:
    - "test/**"
    - "**/migrations/**"
    - "**/__init__.py"
```

**Orchestrator** (`src/orchestrator/core.py`):
- Auto-discovery via `discover_rules("src.linters")`
- No manual registration needed
- FileHeaderRule detected automatically

### With Documentation System

**.ai/ Directory Updates**:
- `docs/ai-doc-standard.md` - new comprehensive standard (1949 lines)
- `.ai/docs/FILE_HEADER_STANDARDS.md` - reference to new standard
- `.ai/howtos/how-to-write-file-headers.md` - updated with new examples
- `AGENTS.md` - atemporal language requirement added

**Documentation Standards Alignment**:
- File-header linter enforces standards documented in .ai/docs/
- Creates feedback loop: docs define standards, linter enforces them
- Living documentation: standards must be implementable

## Success Metrics

### Technical Metrics
- [ ] Test coverage ≥ 85% (targeting 90%)
- [ ] 100-110 total tests passing (100% pass rate)
- [ ] Pylint 10.00/10 across all modules
- [ ] Xenon A-grade complexity
- [ ] CI/CD pipeline green

### Feature Metrics
- [ ] Supports 6+ file types (Python, TypeScript, JavaScript, Bash, Markdown, CSS)
- [ ] Detects all mandatory field violations
- [ ] Detects 20+ atemporal language patterns
- [ ] False positive rate < 5%
- [ ] Configuration support via .thailint.yaml

### Adoption Metrics
- [ ] 100% file compliance (200-300 files)
- [ ] 0 header violations in codebase
- [ ] Pre-commit hook enabled
- [ ] Team trained on new standard
- [ ] Documentation complete (600-800 lines)

## Technical Constraints

### Performance Constraints
- **Per-File Parse Time**: < 100ms per file
  - Most linters run on large codebases
  - Need to stay fast for good DX
- **Memory Usage**: Stream large files, don't load entirely into memory
- **Regex Performance**: Avoid catastrophic backtracking in atemporal patterns

### Compatibility Constraints
- **Python Version**: 3.10+ (project standard)
- **Tree-sitter**: Must work with existing tree-sitter integration
- **PyYAML**: Standard library or PyPI, stable API

### Quality Constraints
- **All Code**: Pylint 10.00/10, Xenon A-grade
- **No Suppressions**: Without explicit user permission
- **Test Coverage**: ≥ 85% on all modules
- **Existing Patterns**: Follow magic-numbers architecture

## AI Agent Guidance

### When Implementing Parsers

**Pattern to Follow** (from magic-numbers):
```python
class LanguageParser:
    """Extracts header from [language] files."""

    def extract_header(self, code: str) -> Optional[str]:
        """Extract header text from file content."""
        pass

    def parse_fields(self, header: str) -> dict[str, str]:
        """Parse structured fields from header."""
        pass
```

**Python Parser** (AST-based):
```python
def extract_header(self, code: str) -> Optional[str]:
    try:
        tree = ast.parse(code)
        return ast.get_docstring(tree)  # Module-level docstring
    except SyntaxError:
        return None
```

**TypeScript Parser** (Tree-sitter):
```python
def extract_header(self, code: str) -> Optional[str]:
    root = self._parse_typescript(code)
    # Find first JSDoc comment (/** ... */)
    # Return comment text without /** */ markers
```

**Bash/CSS Parsers** (Regex):
```python
def extract_header(self, code: str) -> Optional[str]:
    # Extract contiguous comment block at top of file
    # Stop at first non-comment line
```

**Markdown Parser** (PyYAML):
```python
def extract_header(self, code: str) -> Optional[dict]:
    # Extract YAML between --- markers
    # Parse with yaml.safe_load()
    # Return as dictionary
```

### When Writing Tests

**TDD Pattern** (critical):
1. Write test describing expected behavior
2. Run test - it MUST fail (RED phase)
3. Implement minimal code to pass test
4. Run test - it MUST pass (GREEN phase)
5. Refactor for quality (A-grade complexity)

**Test Structure** (from magic-numbers):
```python
class TestMandatoryFieldsDetection:
    """Group related tests in classes."""

    def test_detects_missing_purpose_field(self):
        """Clear test name describing what's tested."""
        code = '''"""
Scope: Test
Overview: Test
"""
'''
        violations = self._check_code(code)
        assert len(violations) >= 1
        assert "Purpose" in violations[0].message

    def _check_code(self, code: str) -> list:
        """Helper to reduce duplication."""
        context = self._create_context(code, "test.py")
        rule = FileHeaderRule()
        return rule.check(context)
```

### When Implementing Validation

**Field Validation Pattern**:
```python
class FieldValidator:
    def validate_fields(self, fields: dict, language: str) -> List[Tuple[str, str]]:
        violations = []
        required = self._get_required_fields(language)

        for field_name in required:
            if field_name not in fields:
                violations.append((field_name, f"Missing: {field_name}"))
            elif not fields[field_name].strip():
                violations.append((field_name, f"Empty: {field_name}"))

        return violations
```

**Atemporal Detection Pattern**:
```python
class AtemporalDetector:
    # Define patterns as class constants
    DATE_PATTERNS = [
        (r'\d{4}-\d{2}-\d{2}', 'ISO date'),
        # ...
    ]

    def detect_violations(self, text: str) -> List[Tuple]:
        violations = []
        for pattern, description in self.ALL_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                violations.append((pattern, description, line_num))
        return violations
```

### Common Patterns

**Composition Over Inheritance**:
```python
class FileHeaderRule(MultiLanguageLintRule):
    def __init__(self):
        self._python_parser = PythonHeaderParser()
        self._field_validator = FieldValidator(config)
        self._atemporal_detector = AtemporalDetector()
        self._violation_builder = ViolationBuilder(self.rule_id)
```

**Configuration Loading** (from magic-numbers):
```python
def _load_config(self, context: BaseLintContext) -> FileHeaderConfig:
    # Try production config
    if hasattr(context, "metadata") and "file_header" in context.metadata:
        return load_linter_config(context, "file_header", FileHeaderConfig)

    # Use defaults
    return FileHeaderConfig()
```

**Helper Method Extraction** (for A-grade complexity):
```python
# ❌ Bad: Too complex (>4 branches)
def check(self, context):
    if not header:
        return [missing_header_violation]
    if not fields:
        return [parse_error_violation]
    violations = []
    if "Purpose" not in fields:
        violations.append(...)
    if "Scope" not in fields:
        violations.append(...)
    # ... more checks
    return violations

# ✅ Good: Extracted helpers
def check(self, context):
    header = self._extract_header(context)
    if not header:
        return self._build_missing_header_violation(context)

    violations = self._validate_fields(header, context)
    violations.extend(self._check_atemporal(header, context))
    return violations
```

## Risk Mitigation

### Risk 1: Large-Scale Dogfooding (PR6)

**Risk**: Updating 200-300 files could introduce bugs or break tests

**Mitigation**:
1. **Phased Approach**: 6 phases with clear boundaries
2. **Small Batches**: 20-30 files per commit
3. **Test After Each Phase**: Run `just test` after every batch
4. **Automated Skeleton Generation**: Script generates headers, manual review adds details
5. **Rollback Plan**: Each batch is independently revertible

### Risk 2: False Positives in Atemporal Detection

**Risk**: Regex patterns might flag valid language as temporal

**Mitigation**:
1. **Careful Pattern Design**: Test patterns thoroughly
2. **Ignore Directives**: `# thailint: ignore[file-header]` escape hatch
3. **Iterative Refinement**: Start strict, relax if needed
4. **User Feedback**: Document common false positives, adjust patterns

### Risk 3: Parser Complexity

**Risk**: Multi-language parsing could be fragile

**Mitigation**:
1. **Leverage Existing Tools**: AST (built-in), Tree-sitter (proven), PyYAML (standard)
2. **Comprehensive Tests**: 100+ tests covering edge cases
3. **Graceful Degradation**: If parse fails, report error but don't crash
4. **Follow Proven Patterns**: Magic-numbers linter established multi-language pattern

### Risk 4: Performance with Large Files

**Risk**: Large files could slow down linter

**Mitigation**:
1. **Parse Headers Only**: Don't analyze entire file
2. **Early Exit**: Stop after finding header (first docstring/comment block)
3. **Performance Tests**: Benchmark on real-world large files
4. **Streaming**: Don't load entire file if possible

## Future Enhancements

### Phase 2 Enhancements (Post-Launch)

**Additional File Types**:
- Go (.go files)
- Rust (.rs files)
- Java (.java files)
- SQL (.sql files)
- YAML/TOML (config files)

**Advanced Atemporal Detection**:
- Machine learning model for temporal language (beyond regex)
- Context-aware detection (some temporal language acceptable in certain contexts)
- Suggestions for atemporal alternatives

**Auto-Fixing**:
- Generate headers automatically from code structure
- AI-powered header completion (use LLM to write comprehensive overview)
- Interactive mode for header creation

**Integration Enhancements**:
- IDE plugins (VSCode, PyCharm) for real-time validation
- GitHub Action for PR validation
- Dashboard showing codebase documentation health

**Analytics**:
- Track header quality metrics over time
- Identify files with weakest documentation
- Team documentation contribution metrics

### Research Areas

**LLM-Powered Validation**:
- Use LLM to evaluate header quality (comprehensiveness, clarity)
- AI suggestions for improving headers
- Automated header generation from code

**Semantic Validation**:
- Check that header descriptions match actual code
- Detect outdated headers (code changed but header didn't)
- Verify exported functions are documented in Exports field

**Documentation Coverage**:
- Extend to function/method-level documentation
- Class-level documentation validation
- API documentation completeness checks

---

## Implementation Checklist

Use this checklist when implementing each component:

### Parser Implementation
- [ ] Extract header from file format correctly
- [ ] Parse structured fields from header text
- [ ] Handle missing/malformed headers gracefully
- [ ] Return None for unparseable files (don't crash)
- [ ] Follow existing parser patterns (magic-numbers)
- [ ] Tests cover valid headers, missing headers, malformed headers

### Validator Implementation
- [ ] Check all mandatory fields for language
- [ ] Detect empty fields (not just missing)
- [ ] Build clear violation messages
- [ ] Support configuration for required fields
- [ ] Tests cover all mandatory fields
- [ ] Tests cover edge cases (very long fields, unicode, etc.)

### Linter Integration
- [ ] Implement MultiLanguageLintRule interface
- [ ] Route to correct parser by language
- [ ] Coordinate validation workflow
- [ ] Support ignore patterns
- [ ] Load configuration correctly
- [ ] Return well-formed violations
- [ ] All tests pass (target: 100+ tests)
- [ ] Code quality: Pylint 10/10, Xenon A-grade

---

**Remember**: This is a complex, multi-PR feature. Take time to understand patterns from magic-numbers linter. Test thoroughly. Update PROGRESS_TRACKER.md after each PR. Ask user for guidance when uncertain about atemporal patterns or design decisions.
