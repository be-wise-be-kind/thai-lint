# Enterprise Multi-Language Linter - PR Breakdown

**Purpose**: Detailed implementation breakdown of Enterprise Linter into manageable, atomic pull requests with TDD approach

**Scope**: Complete feature implementation from basic CLI through production-ready enterprise linter with 3 deployment modes

**Overview**: Comprehensive breakdown of the Enterprise Linter feature into 12 manageable, atomic pull requests. Each
    PR follows strict TDD methodology: write tests first, then implement to pass tests. PRs are designed to be
    self-contained, testable, and maintain application functionality while incrementally building toward the complete
    feature. Includes detailed implementation steps, file structures, testing requirements, and success criteria.

**Dependencies**: Python 3.11+, Poetry, pytest, Click, PyYAML, Docker

**Exports**: PR implementation plans, file structures, testing strategies, TDD workflows, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Strict TDD approach - Tests first, then implementation. Atomic PR design with detailed step-by-step guidance and comprehensive validation.

---

## 🚀 PROGRESS TRACKER - MUST BE UPDATED AFTER EACH PR!

### ✅ Completed PRs
- ⬜ None yet - Planning phase just completed

### 🎯 NEXT PR TO IMPLEMENT
➡️ **START HERE: PR1** - Foundation & Base Interfaces (TDD)

### 📋 Remaining PRs
- ⬜ PR1: Foundation & Base Interfaces (TDD)
- ⬜ PR2: Configuration System (TDD)
- ⬜ PR3: Multi-Language Orchestrator (TDD)
- ⬜ PR4: File Placement Tests (Pure TDD)
- ⬜ PR5: File Placement Linter Implementation
- ⬜ PR6: File Placement Integration (TDD)
- ⬜ PR7: CLI Interface (TDD)
- ⬜ PR8: Library API (TDD)
- ⬜ PR9: Docker Support (TDD)
- ⬜ PR10: Integration Test Suite (TDD)
- ⬜ PR11: Documentation & Examples (TDD)
- ⬜ PR12: PyPI & Distribution (TDD)

**Progress**: 0% Complete (0/12 PRs)

---

## Overview
This document breaks down the Enterprise Linter feature into 12 manageable, atomic PRs. Each PR:
- **Follows strict TDD**: Tests written before implementation
- **Is self-contained and testable**: Can be reviewed and merged independently
- **Maintains working application**: No broken states
- **Builds incrementally**: Each PR adds value
- **Is revertible**: Can be rolled back without breaking functionality

---

# Phase 1: Foundation & Core Framework (PR1-PR3)

## PR1: Foundation & Base Interfaces (TDD)

### Scope
Establish core abstractions for the plugin architecture: base classes, rule registry, and type system.

### TDD Workflow
**Step 1: Write Tests First (NO implementation)**

### Files to Create

#### Test Files (Write First)
```
tests/core/
├── __init__.py
├── test_base_interfaces.py
└── test_rule_registry.py
```

#### Implementation Files (Write After Tests)
```
src/core/
├── __init__.py
├── base.py          # Abstract base classes
├── registry.py      # Rule registry with auto-discovery
└── types.py         # Violation, Severity, LintContext
```

### Detailed Steps

#### Step 1: Write `tests/core/test_base_interfaces.py`

```python
"""Test suite for base interfaces."""
import pytest
from abc import ABC

class TestBaseLintRule:
    """Test BaseLintRule abstract base class."""

    def test_cannot_instantiate_base_rule_directly(self):
        """Base rule is abstract and cannot be instantiated."""
        from src.core.base import BaseLintRule
        with pytest.raises(TypeError):
            BaseLintRule()

    def test_rule_must_implement_rule_id(self):
        """Concrete rule must implement rule_id property."""
        # Test that subclass without rule_id fails
        pass

    def test_rule_must_implement_check(self):
        """Concrete rule must implement check method."""
        # Test that subclass without check() fails
        pass

    def test_concrete_rule_can_be_instantiated(self):
        """Properly implemented rule can be instantiated."""
        # Create minimal concrete rule, verify it works
        pass

class TestBaseLintContext:
    """Test BaseLintContext."""

    def test_context_has_file_path(self):
        """Context exposes file_path property."""
        pass

    def test_context_has_file_content(self):
        """Context exposes file_content property."""
        pass

    def test_context_has_language(self):
        """Context exposes language property."""
        pass

class TestBaseViolation:
    """Test Violation data class."""

    def test_violation_has_required_fields(self):
        """Violation has rule_id, file_path, line, message."""
        pass

    def test_violation_can_be_serialized(self):
        """Violation can be converted to dict/JSON."""
        pass

class TestSeverity:
    """Test Severity enum."""

    def test_severity_has_error_level(self):
        """Severity.ERROR exists (binary model)."""
        from src.core.types import Severity
        assert hasattr(Severity, 'ERROR')

    def test_severity_is_comparable(self):
        """Severity levels can be compared."""
        pass
```

#### Step 2: Write `tests/core/test_rule_registry.py`

```python
"""Test suite for rule registry."""
import pytest
from pathlib import Path

class TestRuleRegistry:
    """Test RuleRegistry functionality."""

    def test_can_register_rule(self):
        """Registry can register a rule."""
        from src.core.registry import RuleRegistry
        registry = RuleRegistry()
        # Create mock rule, register it
        # Verify it's in registry
        pass

    def test_can_retrieve_registered_rule(self):
        """Registry can retrieve rule by ID."""
        pass

    def test_duplicate_rule_id_raises_error(self):
        """Registering duplicate rule ID raises error."""
        pass

    def test_can_list_all_rules(self):
        """Registry can list all registered rules."""
        pass

class TestRuleDiscovery:
    """Test automatic rule discovery."""

    def test_discovers_rules_in_package(self):
        """Auto-discover rules in specified package."""
        # Create test package with rules
        # Verify discovery finds them
        pass

    def test_skips_abstract_base_classes(self):
        """Discovery skips ABC classes."""
        pass

    def test_only_discovers_lint_rule_subclasses(self):
        """Discovery only finds BaseLintRule subclasses."""
        pass
```

#### Step 3: Run Tests (Verify They All Fail)
```bash
pytest tests/core/ -v
# Expected: All tests fail (modules don't exist yet)
```

#### Step 4: Implement `src/core/types.py`

```python
"""Core type definitions."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class Severity(Enum):
    """Binary severity model - errors only."""
    ERROR = "error"

@dataclass
class Violation:
    """Represents a linting violation."""
    rule_id: str
    file_path: str
    line: int
    column: int
    message: str
    severity: Severity = Severity.ERROR
    suggestion: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'rule_id': self.rule_id,
            'file_path': self.file_path,
            'line': self.line,
            'column': self.column,
            'message': self.message,
            'severity': self.severity.value,
            'suggestion': self.suggestion,
        }
```

#### Step 5: Implement `src/core/base.py`

```python
"""Abstract base classes for linter framework."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from .types import Violation

class BaseLintContext(ABC):
    """Base class for lint context."""

    @property
    @abstractmethod
    def file_path(self) -> Path | None:
        """Get file path being analyzed."""
        raise NotImplementedError

    @property
    @abstractmethod
    def file_content(self) -> str | None:
        """Get file content."""
        raise NotImplementedError

    @property
    @abstractmethod
    def language(self) -> str:
        """Get programming language."""
        raise NotImplementedError

class BaseLintRule(ABC):
    """Base class for all linting rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        raise NotImplementedError

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable rule name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """Rule description."""
        raise NotImplementedError

    @abstractmethod
    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for violations."""
        raise NotImplementedError
```

#### Step 6: Implement `src/core/registry.py`

```python
"""Rule registry with plugin discovery."""
import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Type
from .base import BaseLintRule

class RuleRegistry:
    """Registry for linting rules with auto-discovery."""

    def __init__(self):
        self._rules: dict[str, BaseLintRule] = {}

    def register(self, rule: BaseLintRule) -> None:
        """Register a rule."""
        rule_id = rule.rule_id
        if rule_id in self._rules:
            raise ValueError(f"Rule {rule_id} already registered")
        self._rules[rule_id] = rule

    def get(self, rule_id: str) -> BaseLintRule | None:
        """Get rule by ID."""
        return self._rules.get(rule_id)

    def list_all(self) -> list[BaseLintRule]:
        """List all registered rules."""
        return list(self._rules.values())

    def discover_rules(self, package_path: str) -> int:
        """Auto-discover rules in package."""
        discovered = 0
        package = importlib.import_module(package_path)

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            full_name = f"{package_path}.{module_name}"
            module = importlib.import_module(full_name)

            for name, obj in inspect.getmembers(module):
                if self._is_rule_class(obj):
                    rule = obj()
                    self.register(rule)
                    discovered += 1

        return discovered

    def _is_rule_class(self, obj: any) -> bool:
        """Check if object is a concrete rule class."""
        return (
            inspect.isclass(obj) and
            issubclass(obj, BaseLintRule) and
            obj is not BaseLintRule and
            not inspect.isabstract(obj)
        )
```

#### Step 7: Run Tests Again (Should Pass)
```bash
pytest tests/core/ -v
# Expected: All tests pass
```

### Testing Requirements
- ✅ Test coverage >95% for all base classes
- ✅ All abstract methods tested
- ✅ Registry discovery tested with mock rules
- ✅ Type system fully tested

### Success Criteria
- [ ] All tests in `tests/core/` pass
- [ ] Can create concrete rules by subclassing BaseLintRule
- [ ] Registry can discover and register rules
- [ ] Type system complete (Violation, Severity)
- [ ] No abstract base classes can be instantiated directly

---

## PR2: Configuration System (TDD)

### Scope
Multi-format configuration loading (YAML/JSON) with 5-level ignore system (repo, directory, file, method, line).

### Files to Create

#### Test Files (Write First)
```
tests/config/
├── __init__.py
├── test_config_loader.py
├── test_ignore_directives.py
└── fixtures/
    ├── valid_config.yaml
    ├── valid_config.json
    └── invalid_config.yaml
```

#### Implementation Files
```
src/config/
├── __init__.py
├── loader.py       # YAML/JSON config loading
├── ignore.py       # 5-level ignore directive parser
└── schema.py       # Config validation
```

### Detailed Steps

#### Step 1: Write `tests/config/test_config_loader.py`

```python
"""Test configuration loading."""
import pytest
from pathlib import Path

class TestYAMLConfigLoading:
    """Test YAML configuration loading."""

    def test_load_valid_yaml_config(self, tmp_path):
        """Load valid YAML configuration."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
rules:
  file-placement:
    enabled: true
    config:
      layout_file: .ai/layout.yaml
""")
        from src.config.loader import ConfigLoader
        loader = ConfigLoader()
        config = loader.load(config_file)

        assert config['rules']['file-placement']['enabled'] is True

    def test_load_invalid_yaml_raises_error(self, tmp_path):
        """Invalid YAML raises clear error."""
        pass

    def test_load_nonexistent_file_returns_defaults(self):
        """Nonexistent config returns defaults."""
        pass

class TestJSONConfigLoading:
    """Test JSON configuration loading."""

    def test_load_valid_json_config(self, tmp_path):
        """Load valid JSON configuration."""
        pass

    def test_json_and_yaml_produce_same_result(self, tmp_path):
        """Equivalent YAML and JSON produce same config."""
        pass

class TestConfigValidation:
    """Test configuration schema validation."""

    def test_validates_rule_ids_exist(self):
        """Validation checks rule IDs are registered."""
        pass

    def test_validates_file_paths_exist(self):
        """Validation checks referenced files exist."""
        pass
```

#### Step 2: Write `tests/config/test_ignore_directives.py`

```python
"""Test 5-level ignore system."""
import pytest
from pathlib import Path

class TestRepoLevelIgnore:
    """Test repository-level ignore (.thailintignore file)."""

    def test_thailintignore_file_parsed(self, tmp_path):
        """Parse .thailintignore file."""
        ignore_file = tmp_path / ".thailintignore"
        ignore_file.write_text("*.pyc\n.git/\nnode_modules/\n")

        from src.config.ignore import IgnoreParser
        parser = IgnoreParser(tmp_path)

        assert parser.is_ignored(tmp_path / "test.pyc")
        assert parser.is_ignored(tmp_path / ".git" / "config")
        assert not parser.is_ignored(tmp_path / "src" / "main.py")

    def test_gitignore_style_patterns(self, tmp_path):
        """Support gitignore-style patterns."""
        pass

class TestDirectoryLevelIgnore:
    """Test directory-level ignores."""

    def test_directory_comment_ignores_children(self):
        """Comment in parent directory ignores children."""
        # Create test structure with ignore directive
        pass

class TestFileLevelIgnore:
    """Test file-level ignores."""

    def test_file_header_ignore_directive(self, tmp_path):
        """# thailint: ignore-file in first 10 lines."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""#!/usr/bin/env python3
# thailint: ignore-file

def some_function():
    pass
""")
        from src.config.ignore import IgnoreParser
        parser = IgnoreParser()

        assert parser.has_file_ignore(test_file)

    def test_specific_rule_ignore(self, tmp_path):
        """# thailint: ignore-file[rule-name]."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# thailint: ignore-file[file-placement]\n")

        parser = IgnoreParser()
        assert parser.has_file_ignore(test_file, rule_id="file-placement")
        assert not parser.has_file_ignore(test_file, rule_id="other-rule")

class TestMethodLevelIgnore:
    """Test method/function-level ignores."""

    def test_function_decorator_ignore(self):
        """Decorator or comment above function."""
        pass

class TestLineLevelIgnore:
    """Test line-level ignores."""

    def test_inline_ignore_comment(self):
        """# thailint: ignore at end of line."""
        code = "bad_code = True  # thailint: ignore"

        from src.config.ignore import IgnoreParser
        parser = IgnoreParser()

        assert parser.has_line_ignore(code, line_num=1)

    def test_specific_rule_line_ignore(self):
        """# thailint: ignore[rule-name]."""
        code = "bad = True  # thailint: ignore[file-placement]"

        parser = IgnoreParser()
        assert parser.has_line_ignore(code, line_num=1, rule_id="file-placement")
```

#### Step 3: Implement Config System

```python
# src/config/loader.py
"""Configuration file loader."""
import json
import yaml
from pathlib import Path

class ConfigLoader:
    """Load configuration from YAML or JSON."""

    def load(self, config_path: Path) -> dict:
        """Load configuration from file."""
        if not config_path.exists():
            return self.get_defaults()

        with open(config_path) as f:
            if config_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif config_path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {config_path.suffix}")

    def get_defaults(self) -> dict:
        """Get default configuration."""
        return {
            'rules': {},
            'ignore': [],
        }
```

```python
# src/config/ignore.py
"""Multi-level ignore directive parser."""
from pathlib import Path
import re

class IgnoreParser:
    """Parse and check ignore directives at all levels."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.repo_patterns = self._load_repo_ignores()

    def _load_repo_ignores(self) -> list[str]:
        """Load .thailintignore file."""
        ignore_file = self.project_root / ".thailintignore"
        if not ignore_file.exists():
            return []

        patterns = []
        for line in ignore_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
        return patterns

    def is_ignored(self, file_path: Path) -> bool:
        """Check if file matches repo-level ignores."""
        for pattern in self.repo_patterns:
            if self._matches_pattern(str(file_path), pattern):
                return True
        return False

    def has_file_ignore(self, file_path: Path, rule_id: str | None = None) -> bool:
        """Check for file-level ignore directive."""
        content = file_path.read_text()
        first_lines = content.splitlines()[:10]

        for line in first_lines:
            if '# thailint: ignore-file' in line:
                if rule_id:
                    match = re.search(r'ignore-file\[([^\]]+)\]', line)
                    if match and rule_id in match.group(1).split(','):
                        return True
                else:
                    return True
        return False

    def has_line_ignore(self, code: str, line_num: int, rule_id: str | None = None) -> bool:
        """Check for line-level ignore."""
        if '# thailint: ignore' in code:
            if rule_id:
                return f'ignore[{rule_id}]' in code
            return True
        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches gitignore-style pattern."""
        # Simple implementation - could use pathspec library
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
```

### Success Criteria
- [ ] All config loading tests pass
- [ ] All 5 ignore levels functional
- [ ] YAML and JSON both supported
- [ ] Config validation working

---

## PR3: Multi-Language Orchestrator (TDD)

### Scope
File routing engine that detects language and executes appropriate rules.

### Files to Create

#### Test Files
```
tests/orchestrator/
├── __init__.py
├── test_orchestrator.py
├── test_file_router.py
└── test_language_detection.py
```

#### Implementation Files
```
src/orchestrator/
├── __init__.py
├── core.py               # Main orchestration engine
├── file_router.py        # Route files to analyzers
└── language_detector.py  # Detect language from file
```

### Detailed Steps

#### Step 1: Write Tests

```python
# tests/orchestrator/test_orchestrator.py
"""Test main orchestrator."""

class TestOrchestrator:
    """Test Orchestrator class."""

    def test_lint_single_file(self, tmp_path):
        """Lint a single file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file\n")

        from src.orchestrator import Orchestrator
        orch = Orchestrator()
        violations = orch.lint_file(test_file)

        assert isinstance(violations, list)

    def test_lint_directory_recursive(self, tmp_path):
        """Lint directory recursively."""
        (tmp_path / "file1.py").write_text("# file 1\n")
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / "file2.py").write_text("# file 2\n")

        from src.orchestrator import Orchestrator
        orch = Orchestrator()
        violations = orch.lint_directory(tmp_path, recursive=True)

        # Should find both files
        assert len(violations) >= 0  # May or may not have violations

    def test_respects_ignore_patterns(self, tmp_path):
        """Orchestrator respects ignore patterns."""
        (tmp_path / ".thailintignore").write_text("*.pyc\n")
        (tmp_path / "test.pyc").write_text("compiled")

        from src.orchestrator import Orchestrator
        orch = Orchestrator(project_root=tmp_path)
        violations = orch.lint_directory(tmp_path)

        # Should not lint .pyc file
        assert all('test.pyc' not in v.file_path for v in violations)
```

```python
# tests/orchestrator/test_language_detection.py
"""Test language detection."""

class TestLanguageDetection:
    """Test language detection from files."""

    def test_detect_python_from_extension(self, tmp_path):
        """Detect Python from .py extension."""
        test_file = tmp_path / "test.py"
        test_file.touch()

        from src.orchestrator.language_detector import detect_language
        assert detect_language(test_file) == "python"

    def test_detect_from_shebang(self, tmp_path):
        """Detect language from shebang."""
        test_file = tmp_path / "script"
        test_file.write_text("#!/usr/bin/env python3\n")

        from src.orchestrator.language_detector import detect_language
        assert detect_language(test_file) == "python"
```

#### Step 2: Implement Orchestrator

```python
# src/orchestrator/core.py
"""Main orchestration engine."""
from pathlib import Path
from src.core.base import BaseLintRule
from src.core.types import Violation
from src.core.registry import RuleRegistry
from src.config.loader import ConfigLoader
from src.config.ignore import IgnoreParser
from .language_detector import detect_language

class Orchestrator:
    """Main linter orchestrator."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.registry = RuleRegistry()
        self.config_loader = ConfigLoader()
        self.ignore_parser = IgnoreParser(self.project_root)
        self.config = self.config_loader.load(self.project_root / ".thailint.yaml")

    def lint_file(self, file_path: Path) -> list[Violation]:
        """Lint a single file."""
        if self.ignore_parser.is_ignored(file_path):
            return []

        violations = []
        language = detect_language(file_path)

        # Get applicable rules
        rules = self._get_rules_for_file(file_path, language)

        for rule in rules:
            # Create context
            context = self._create_context(file_path, language)
            # Run rule
            violations.extend(rule.check(context))

        return violations

    def lint_directory(self, dir_path: Path, recursive: bool = True) -> list[Violation]:
        """Lint all files in directory."""
        violations = []
        pattern = "**/*" if recursive else "*"

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                violations.extend(self.lint_file(file_path))

        return violations

    def _get_rules_for_file(self, file_path: Path, language: str) -> list[BaseLintRule]:
        """Get rules applicable to this file."""
        # For now, return all registered rules
        # Later: filter by language, config, etc.
        return self.registry.list_all()

    def _create_context(self, file_path: Path, language: str):
        """Create lint context for file."""
        from src.core.base import BaseLintContext

        class FileLintContext(BaseLintContext):
            def __init__(self, path: Path, lang: str):
                self._path = path
                self._language = lang
                self._content = path.read_text() if path.exists() else None

            @property
            def file_path(self) -> Path:
                return self._path

            @property
            def file_content(self) -> str | None:
                return self._content

            @property
            def language(self) -> str:
                return self._language

        return FileLintContext(file_path, language)
```

```python
# src/orchestrator/language_detector.py
"""Language detection from files."""
from pathlib import Path

EXTENSION_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.go': 'go',
}

def detect_language(file_path: Path) -> str:
    """Detect programming language from file."""
    # Check extension first
    ext = file_path.suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    # Check shebang
    if file_path.exists():
        first_line = file_path.read_text().split('\n')[0]
        if first_line.startswith('#!'):
            if 'python' in first_line:
                return 'python'

    return 'unknown'
```

### Success Criteria
- [ ] Can route files by language
- [ ] Executes rules on files
- [ ] Respects ignore patterns
- [ ] Returns structured violations

---

# Phase 2: File Placement Linter (PR4-PR6)

## PR4: File Placement Tests (Pure TDD)

### Scope
**CRITICAL**: Write complete test suite with ZERO implementation. All tests must fail initially.

### Files to Create

```
tests/linters/file_placement/
├── __init__.py
├── test_config_loading.py       # 6 tests
├── test_allow_patterns.py       # 8 tests
├── test_deny_patterns.py        # 8 tests
├── test_directory_scoping.py    # 7 tests
├── test_ignore_directives.py    # 9 tests
├── test_output_formatting.py    # 5 tests
├── test_cli_interface.py        # 4 tests
├── test_library_api.py          # 3 tests
└── fixtures/
    ├── layout_rules.yaml
    ├── layout_rules.json
    └── sample_project/
```

### Complete Test Suite

```python
# tests/linters/file_placement/test_config_loading.py
"""Test configuration loading for file placement linter."""
import pytest
from pathlib import Path

class TestConfigurationLoading:
    """Test loading allow/deny patterns from config."""

    def test_load_json_config(self, tmp_path):
        """Load file placement rules from JSON."""
        config_file = tmp_path / "layout.json"
        config_file.write_text("""{
  "file_placement": {
    "directories": {
      "src/": {
        "allow": ["^src/.*\\\\.py$"]
      }
    }
  }
}""")
        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(config_file=str(config_file))
        assert linter.config is not None

    def test_load_yaml_config(self, tmp_path):
        """Load file placement rules from YAML."""
        config_file = tmp_path / "layout.yaml"
        config_file.write_text("""
file_placement:
  directories:
    src/:
      allow:
        - "^src/.*\\.py$"
""")
        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(config_file=str(config_file))
        assert linter.config is not None

    def test_handle_missing_config_file(self):
        """Missing config file falls back to defaults."""
        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(config_file="nonexistent.yaml")
        # Should not crash, should use defaults
        assert linter is not None

    def test_handle_malformed_json(self, tmp_path):
        """Malformed JSON raises clear error."""
        config_file = tmp_path / "bad.json"
        config_file.write_text("{invalid json}")

        from src.linters.file_placement import FilePlacementLinter
        with pytest.raises(Exception):  # Should raise parse error
            FilePlacementLinter(config_file=str(config_file))

    def test_validate_regex_patterns_on_load(self, tmp_path):
        """Invalid regex patterns caught on load."""
        config_file = tmp_path / "layout.yaml"
        config_file.write_text("""
file_placement:
  directories:
    src/:
      allow:
        - "[invalid(regex"
""")
        from src.linters.file_placement import FilePlacementLinter
        with pytest.raises(Exception):  # Should catch bad regex
            FilePlacementLinter(config_file=str(config_file))

    def test_support_inline_json_object(self):
        """Support passing JSON object directly (not file path)."""
        config_obj = {
            'file_placement': {
                'directories': {
                    'src/': {'allow': [r'^src/.*\.py$']}
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(config_obj=config_obj)
        assert linter.config == config_obj


# tests/linters/file_placement/test_allow_patterns.py
"""Test allow pattern matching."""

class TestAllowPatternMatching:
    """Test files matching allow patterns."""

    def test_match_simple_allow_pattern(self, tmp_path):
        """File matches simple allow regex."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {'allow': [r'^src/.*\.py$']}
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter
        linter = FilePlacementLinter(config_obj=config)

        # This file should be allowed
        violations = linter.lint_path(tmp_path / "src" / "main.py")
        assert len(violations) == 0

    def test_match_multiple_allow_patterns(self):
        """File can match any of multiple allow patterns."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {
                        'allow': [r'^src/.*\.py$', r'^src/.*\.pyi$']
                    }
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/main.py"))
        assert linter.check_file_allowed(Path("src/types.pyi"))

    def test_reject_files_not_matching_allow(self):
        """File not matching any allow pattern is rejected."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {'allow': [r'^src/.*\.py$']}
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/README.md"))
        assert len(violations) > 0
        assert "does not match allowed patterns" in violations[0].message

    def test_case_insensitive_matching(self):
        """Pattern matching is case-insensitive."""
        pass

    def test_nested_directory_patterns(self):
        """Support **/ for nested directories."""
        config = {
            'file_placement': {
                'global_patterns': {
                    'allow': [r'.*\.py$']  # Any .py anywhere
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/utils/helpers.py"))
        assert linter.check_file_allowed(Path("deep/nested/path/file.py"))

    def test_file_extension_wildcards(self):
        """Support wildcard extensions."""
        pass

    def test_directory_specific_allow_patterns(self):
        """Different directories have different allow patterns."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {'allow': [r'^src/.*\.py$']},
                    'tests/': {'allow': [r'^tests/test_.*\.py$']}
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        assert linter.check_file_allowed(Path("src/main.py"))
        assert linter.check_file_allowed(Path("tests/test_main.py"))

        violations = linter.lint_path(Path("tests/helper.py"))
        assert len(violations) > 0  # Not test_*.py

    def test_root_vs_subdirectory_allow(self):
        """Root directory has different rules than subdirectories."""
        pass


# tests/linters/file_placement/test_deny_patterns.py
"""Test deny pattern matching."""

class TestDenyPatternMatching:
    """Test files matching deny patterns."""

    def test_match_simple_deny_pattern(self):
        """File matches simple deny regex."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {
                        'deny': [
                            {'pattern': r'.*test.*\.py$', 'reason': 'Tests in src/'}
                        ]
                    }
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/test_utils.py"))
        assert len(violations) > 0
        assert "Tests in src/" in violations[0].message

    def test_deny_takes_precedence_over_allow(self):
        """Deny patterns override allow patterns."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {
                        'allow': [r'^src/.*\.py$'],
                        'deny': [{'pattern': r'.*debug.*'}]
                    }
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/debug_utils.py"))
        assert len(violations) > 0  # Denied despite matching allow

    def test_multiple_deny_patterns(self):
        """File can match any of multiple deny patterns."""
        pass

    def test_deny_with_custom_error_messages(self):
        """Deny pattern includes custom error message."""
        config = {
            'file_placement': {
                'global_deny': [
                    {'pattern': r'.*\.tmp$', 'reason': 'No temp files in repo'}
                ]
            }
        }
        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("data.tmp"))
        assert "No temp files in repo" in violations[0].message

    def test_temporary_file_patterns(self):
        """Detect temporary files (.tmp, .log, .bak)."""
        pass

    def test_debug_file_patterns_in_production(self):
        """Detect debug files in production directories."""
        pass

    def test_absolute_path_detection(self):
        """Detect and deny absolute paths in code."""
        # This would require code parsing, not just path checking
        # May be future enhancement
        pass

    def test_platform_specific_path_separators(self):
        """Handle both / and \\ path separators."""
        pass


# tests/linters/file_placement/test_directory_scoping.py
"""Test directory scanning and scoping."""

class TestDirectoryScoping:
    """Test flat vs recursive scanning."""

    def test_flat_directory_scanning(self, tmp_path):
        """Scan directory non-recursively."""
        (tmp_path / "file1.py").write_text("#\n")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.py").write_text("#\n")

        linter = FilePlacementLinter()
        violations = linter.lint_directory(tmp_path, recursive=False)

        # Should only find file1.py, not file2.py
        files_checked = {v.file_path for v in violations}
        assert "file1.py" in str(files_checked)
        assert "file2.py" not in str(files_checked)

    def test_recursive_directory_scanning(self, tmp_path):
        """Scan directory recursively."""
        (tmp_path / "file1.py").write_text("#\n")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.py").write_text("#\n")

        linter = FilePlacementLinter()
        violations = linter.lint_directory(tmp_path, recursive=True)

        # Should find both files
        pass

    def test_specific_file_path_linting(self):
        """Lint a specific file path."""
        linter = FilePlacementLinter()
        violations = linter.lint_path(Path("src/main.py"))
        assert isinstance(violations, list)

    def test_mixed_file_and_directory_inputs(self):
        """Accept mix of files and directories."""
        pass

    def test_exclude_patterns(self, tmp_path):
        """Respect exclude patterns (.git/, node_modules/)."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")

        linter = FilePlacementLinter()
        violations = linter.lint_directory(tmp_path, recursive=True)

        # Should not lint .git/
        assert all('.git' not in v.file_path for v in violations)

    def test_respect_thailintignore_file(self, tmp_path):
        """Respect .thailintignore file."""
        (tmp_path / ".thailintignore").write_text("*.pyc\n")
        (tmp_path / "test.pyc").write_text("compiled")
        (tmp_path / "test.py").write_text("#\n")

        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_directory(tmp_path)

        # Should skip .pyc file
        assert all('test.pyc' not in v.file_path for v in violations)

    def test_handle_symlinks_and_special_files(self):
        """Handle symlinks gracefully."""
        pass


# tests/linters/file_placement/test_ignore_directives.py
"""Test 5-level ignore system."""

class TestIgnoreDirectives:
    """Test all 5 levels of ignore directives."""

    def test_repo_level_ignore_thailintignore(self, tmp_path):
        """Repo-level: .thailintignore file."""
        (tmp_path / ".thailintignore").write_text("build/\n*.pyc\n")
        (tmp_path / "build").mkdir()
        (tmp_path / "build" / "output.txt").write_text("data")

        linter = FilePlacementLinter(project_root=tmp_path)
        violations = linter.lint_directory(tmp_path)

        assert all('build/' not in v.file_path for v in violations)

    def test_directory_level_ignore(self):
        """Directory-level: ignore directive in parent."""
        # Implementation TBD - may use special .lint-config file in directory
        pass

    def test_file_level_ignore_directive(self, tmp_path):
        """File-level: # thailint: ignore-file."""
        test_file = tmp_path / "ignored.py"
        test_file.write_text("""#!/usr/bin/env python3
# thailint: ignore-file

# This entire file is ignored
""")

        linter = FilePlacementLinter()
        violations = linter.lint_path(test_file)

        assert len(violations) == 0  # Entire file ignored

    def test_file_level_specific_rule_ignore(self, tmp_path):
        """File-level: # thailint: ignore-file[file-placement]."""
        test_file = tmp_path / "ignored.py"
        test_file.write_text("# thailint: ignore-file[file-placement]\n")

        linter = FilePlacementLinter()
        violations = linter.lint_path(test_file)

        assert len(violations) == 0

    def test_method_level_ignore(self):
        """Method-level: decorator or comment above function."""
        # May require AST parsing - defer to later PR
        pass

    def test_line_level_ignore(self):
        """Line-level: # thailint: ignore."""
        # For file placement, line-level doesn't apply
        # But test framework should support it
        pass

    def test_ignore_patterns_with_wildcards(self):
        """Ignore patterns support wildcards."""
        pass

    def test_multiple_ignore_levels_interaction(self):
        """Test interaction when multiple ignore levels apply."""
        pass

    def test_validate_ignore_directive_syntax(self):
        """Invalid ignore directive syntax produces warning."""
        pass


# tests/linters/file_placement/test_output_formatting.py
"""Test violation output formatting."""

class TestOutputFormatting:
    """Test consistent violation message format."""

    def test_consistent_violation_format(self):
        """Violations have consistent structure."""
        linter = FilePlacementLinter()
        # Create violation scenario
        violations = linter.lint_path(Path("bad/location/file.py"))

        if violations:
            v = violations[0]
            assert hasattr(v, 'rule_id')
            assert hasattr(v, 'file_path')
            assert hasattr(v, 'message')
            assert hasattr(v, 'severity')

    def test_file_path_relative_to_project_root(self):
        """File paths shown relative to project root."""
        pass

    def test_error_message_includes_pattern_violated(self):
        """Error message shows which pattern was violated."""
        pass

    def test_suggestion_for_correct_placement(self):
        """Violation includes suggestion for where file should go."""
        config = {
            'file_placement': {
                'directories': {
                    'src/': {'allow': [r'^src/.*\.py$']}
                }
            }
        }
        linter = FilePlacementLinter(config_obj=config)
        violations = linter.lint_path(Path("wrong/location/file.py"))

        if violations:
            assert violations[0].suggestion is not None
            assert "src/" in violations[0].suggestion

    def test_machine_readable_json_output(self):
        """Violations can be output as JSON."""
        linter = FilePlacementLinter()
        violations = linter.lint_path(Path("file.py"))

        # Should be serializable to JSON
        import json
        json_output = json.dumps([v.to_dict() for v in violations])
        assert json_output is not None


# tests/linters/file_placement/test_cli_interface.py
"""Test CLI interface for file placement linter."""

class TestCLIInterface:
    """Test command-line interface."""

    def test_cli_command_structure(self):
        """thai lint file-placement <path> command works."""
        from click.testing import CliRunner
        from src.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['lint', 'file-placement', '.'])

        assert result.exit_code in [0, 1]  # 0 = pass, 1 = violations

    def test_accept_json_object_via_flag(self):
        """Accept JSON object via --rules flag."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'lint', 'file-placement',
            '--rules', '{"allow": [".*\\.py$"]}',
            '.'
        ])
        assert result.exit_code in [0, 1]

    def test_accept_json_file_via_config_flag(self, tmp_path):
        """Accept JSON file via --config flag."""
        config_file = tmp_path / "rules.json"
        config_file.write_text('{"allow": [".*\\\\.py$"]}')

        runner = CliRunner()
        result = runner.invoke(cli, [
            'lint', 'file-placement',
            '--config', str(config_file),
            '.'
        ])
        assert result.exit_code in [0, 1]

    def test_exit_codes(self):
        """Exit code 0 = pass, 1 = violations found."""
        runner = CliRunner()

        # Create scenario with no violations
        result_pass = runner.invoke(cli, ['lint', 'file-placement', 'src/'])
        # Assuming src/ is clean, should be 0

        # Create scenario with violations
        # (Would need to set up test project with violations)
        pass


# tests/linters/file_placement/test_library_api.py
"""Test library/programmatic API."""

class TestLibraryAPI:
    """Test using linter as importable library."""

    def test_import_linter(self):
        """Can import file_placement_linter."""
        from thailinter.linters import file_placement_linter
        assert file_placement_linter is not None

    def test_function_call_interface(self):
        """Call linter.lint(path, config)."""
        from thailinter.linters import file_placement_linter as fpl

        config = {'allow': [r'.*\.py$']}
        violations = fpl.lint(Path('.'), config)

        assert isinstance(violations, list)

    def test_return_structured_violations(self):
        """Violations returned as structured data."""
        from thailinter.linters import file_placement_linter as fpl

        violations = fpl.lint(Path('.'))

        if violations:
            v = violations[0]
            assert hasattr(v, 'rule_id')
            assert hasattr(v, 'file_path')
            assert hasattr(v, 'to_dict')
```

### Success Criteria
- [ ] 40+ tests written
- [ ] **ALL tests FAIL** (no implementation exists)
- [ ] Test coverage plan documented
- [ ] Fixtures created

---

## PR5: File Placement Linter Implementation

### Scope
Implement file placement linter to pass **ALL** tests from PR4.

### Implementation Plan

1. **Copy reference implementation** from `/home/stevejackson/Projects/durable-code-test/tools/design_linters/rules/organization/file_placement_rules.py`

2. **Adapt to our architecture**:
   - Use our base classes (PR1)
   - Use our config system (PR2)
   - Integrate with orchestrator (PR3)

3. **Run tests iteratively**:
   ```bash
   pytest tests/linters/file_placement/ -v
   # Fix failures one by one until all pass
   ```

### Files to Create

```
src/linters/file_placement/
├── __init__.py
├── linter.py              # Main FilePlacementLinter class
├── pattern_matcher.py     # Regex pattern matching
├── config_loader.py       # Layout file loading
└── violation_factory.py   # Create violations
```

### Success Criteria
- [ ] ALL 40+ tests from PR4 pass
- [ ] No regressions in other tests
- [ ] Code coverage >95%

---

## PR6: File Placement Integration (TDD)

### Scope
End-to-end integration with orchestrator, CLI, and library API.

### Steps
1. Write integration tests
2. Register linter with orchestrator
3. Add CLI command
4. Export library API
5. Dogfood on own codebase

### Success Criteria
- [ ] `thai lint file-placement .` works
- [ ] Library import works
- [ ] Can lint own codebase
- [ ] All integration tests pass

---

# Phase 3: Deployment Modes (PR7-PR9)

## PR7: CLI Interface (TDD)

### Scope
Professional CLI with `thai lint <rule> <path>` structure.

### Files
```
src/cli/commands/
├── lint.py         # Main lint command
└── formatters/
    ├── text.py
    ├── json.py
    └── sarif.py
```

### CLI Design
```bash
thai lint <rule> [PATH] [OPTIONS]
  --config FILE       Config file
  --rules JSON        Inline rules
  --format text|json  Output format
  --recursive         Scan recursively
```

### Success Criteria
- [ ] All CLI tests pass
- [ ] Help text complete
- [ ] Exit codes correct

---

## PR8: Library API (TDD)

### Scope
Clean programmatic API for library usage.

### API Design
```python
from thailinter import Linter
from thailinter.linters import file_placement_linter

# High-level
linter = Linter(config_file='.thailint.yaml')
violations = linter.lint('src/', rules=['file-placement'])

# Direct import
violations = file_placement_linter.lint('src/', config)
```

### Success Criteria
- [ ] All API tests pass
- [ ] Examples work
- [ ] Documentation complete

---

## PR9: Docker Support (TDD)

### Scope
Multi-stage Docker build with volume mounting.

### Docker Usage
```bash
docker pull thailint/thailint:latest
docker run -v $(pwd):/workspace thailint/thailint lint file-placement /workspace
```

### Success Criteria
- [ ] Docker tests pass
- [ ] Image builds
- [ ] Runs correctly

---

# Phase 4: Testing & Quality (PR10-PR11)

## PR10: Integration Test Suite (TDD)

### Scope
Real-world testing and performance benchmarks.

### Tests
- Test on real repositories
- Performance benchmarks
- All three modes (CLI, library, Docker)

### Success Criteria
- [ ] <100ms single file
- [ ] <5s for 1000 files

---

## PR11: Documentation & Examples (TDD)

### Scope
Comprehensive user documentation.

### Deliverables
- Getting started guide
- Configuration reference
- API documentation
- Working examples

### Success Criteria
- [ ] All examples tested
- [ ] Documentation complete

---

# Phase 5: Publishing (PR12)

## PR12: PyPI & Distribution (TDD)

### Scope
Package for PyPI, automated publishing.

### Steps
1. Update `pyproject.toml`
2. Create `MANIFEST.in`
3. GitHub Actions for publishing
4. Version tagging

### Success Criteria
- [ ] `pip install thailint` works
- [ ] All modes functional

---

## Implementation Guidelines

### Code Standards
- Follow PEP 8 (enforced by Ruff)
- Type hints required (checked by mypy --strict)
- Docstrings required (Google style)
- File headers required (see `.ai/templates/`)

### Testing Requirements
- **TDD mandatory**: Tests before implementation
- Coverage >95%
- All tests must pass before PR merge
- Integration tests for all features

### Documentation Standards
- All public APIs documented
- Examples tested and working
- File headers on all Python files
- Update `.ai/docs/` for architectural changes

### Security Considerations
- No secrets in code
- Validate all file paths
- Sandbox regex execution
- Limit file sizes read

### Performance Targets
- <100ms for single file lint
- <5s for 1000 files
- <500MB memory for large projects
- Parallel processing where possible

## Rollout Strategy

### Phase 1: Foundation (Weeks 1-2)
PR1-PR3: Core framework

### Phase 2: File Linter (Weeks 3-4)
PR4-PR6: Complete file placement linter

### Phase 3: Deployment (Week 5)
PR7-PR9: All three modes

### Phase 4: Polish (Week 6)
PR10-PR12: Testing, docs, publish

## Success Metrics

### Launch Metrics
- [ ] Published to PyPI
- [ ] Docker image published
- [ ] Documentation live
- [ ] Example repos available

### Ongoing Metrics
- [ ] Dogfooded on own codebase
- [ ] Used in CI/CD pipelines
- [ ] Community adoption
