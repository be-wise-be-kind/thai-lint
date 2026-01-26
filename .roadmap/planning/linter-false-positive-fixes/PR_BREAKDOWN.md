# Linter False Positive Fixes - PR Breakdown

**Purpose**: Detailed implementation breakdown into manageable, atomic pull requests

**Scope**: Complete false positive fixes from evaluation findings through merged PRs

**Overview**: Comprehensive breakdown into 5 manageable, atomic pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality while incrementally reducing false positive rates.

**Dependencies**: Evaluation results, existing linter implementations

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: TDD approach with real false positive examples from evaluation

---

## Overview
This document breaks down the false positive fixes into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally reduces false positive rate
- Revertible if needed

---

## PR1: Stateless Class Test Exemptions

### Scope
Add exemptions to stateless-class linter for test classes.

### Files to Modify
```
src/linters/stateless_class/
├── config.py              # Add exempt_test_classes config option
├── linter.py              # Add test class detection logic
└── python_analyzer.py     # Implement exemption checks

tests/unit/linters/stateless_class/
├── test_test_class_exemption.py  # NEW - Test exemption behavior
```

### Implementation Steps

1. **Add config option** in `config.py`:
   ```python
   exempt_test_classes: bool = True
   ```

2. **Add detection helper** in `python_analyzer.py`:
   ```python
   def _is_test_class(self, class_node: ast.ClassDef, file_path: Path) -> bool:
       """Check if class is a test class that should be exempt."""
       # Check class name starts with Test
       if class_node.name.startswith("Test"):
           return True
       # Check file is in tests directory or starts with test_
       if "tests" in file_path.parts or file_path.name.startswith("test_"):
           return True
       # Check inherits from unittest.TestCase
       for base in class_node.bases:
           if isinstance(base, ast.Attribute) and base.attr == "TestCase":
               return True
           if isinstance(base, ast.Name) and base.id == "TestCase":
               return True
       return False
   ```

3. **Integrate into analyzer**:
   - Call `_is_test_class()` before flagging
   - Skip if config.exempt_test_classes is True and class is test class

4. **Write tests** with real examples:
   ```python
   def test_exempts_class_named_test():
       code = '''
       class TestHelpers:
           def test_get_debug_flag(self):
               assert get_debug_flag() == True
       '''
       violations = analyze(code, file_path="tests/test_helpers.py")
       assert len(violations) == 0

   def test_exempts_unittest_testcase():
       code = '''
       import unittest
       class MyTest(unittest.TestCase):
           def test_something(self):
               pass
       '''
       violations = analyze(code)
       assert len(violations) == 0
   ```

### Testing Requirements
- Test each exemption pattern independently
- Test config option to disable exemption
- Test that non-test stateless classes still flagged

### Success Criteria
- [ ] All new tests pass
- [ ] Existing tests still pass
- [ ] Re-run on Flask/Requests shows test classes exempted

---

## PR2: Stateless Class Mixin Exemptions

### Scope
Add exemptions for mixin classes that provide behavior to composed classes.

### Files to Modify
```
src/linters/stateless_class/
├── config.py              # Add exempt_mixins config option
├── python_analyzer.py     # Implement mixin detection

tests/unit/linters/stateless_class/
├── test_mixin_exemption.py  # NEW - Test mixin exemption
```

### Implementation Steps

1. **Add config option**:
   ```python
   exempt_mixins: bool = True
   ```

2. **Add mixin detection**:
   ```python
   def _is_mixin_class(self, class_node: ast.ClassDef) -> bool:
       """Check if class is a mixin that provides behavior."""
       # Check name contains Mixin
       if "Mixin" in class_node.name:
           return True
       return False
   ```

3. **Write tests** with real examples:
   ```python
   def test_exempts_mixin_by_name():
       code = '''
       class RequestEncodingMixin:
           @property
           def path_url(self):
               p = urlsplit(self.url)
               return p.path or "/"
       '''
       violations = analyze(code)
       assert len(violations) == 0
   ```

### Success Criteria
- [ ] Mixin classes exempted by name
- [ ] Config option to disable
- [ ] Existing tests pass

---

## PR3: Magic Numbers Definition File Exemption

### Scope
Detect and exempt files that ARE constant definitions (like status_codes.py).

### Files to Modify
```
src/linters/magic_numbers/
├── config.py              # Add exempt_definition_files config
├── linter.py              # Add definition file detection
├── definition_detector.py # NEW - Detect constant definition files

tests/unit/linters/magic_numbers/
├── test_definition_file_exemption.py  # NEW
```

### Implementation Steps

1. **Create definition detector**:
   ```python
   def is_constant_definition_file(content: str, file_path: Path) -> bool:
       """Detect if file is a constant definition file.

       Patterns detected:
       - Dict mapping int keys to string values (status codes)
       - Module with UPPER_CASE = <number> assignments
       - File named *_codes.py, *_constants.py, constants.py
       """
       # Check filename patterns
       name_lower = file_path.name.lower()
       if name_lower in ("constants.py", "status_codes.py"):
           return True
       if "_codes.py" in name_lower or "_constants.py" in name_lower:
           return True

       # Check content pattern: dict with int keys
       tree = ast.parse(content)
       for node in ast.walk(tree):
           if isinstance(node, ast.Dict):
               if all(isinstance(k, ast.Constant) and isinstance(k.value, int)
                      for k in node.keys if k is not None):
                   return True
       return False
   ```

2. **Integrate into linter**:
   - Check at file level before analyzing
   - Skip entire file if detected as definition file

3. **Write tests** with real status_codes.py content

### Success Criteria
- [ ] status_codes.py exempted
- [ ] Regular files with magic numbers still flagged
- [ ] Configurable exemption

---

## PR4: Magic Numbers Standard Values Allowlist

### Scope
Add configurable allowlist for well-known values.

### Files to Modify
```
src/linters/magic_numbers/
├── config.py              # Add allowlist config
├── linter.py              # Check allowlist before flagging

tests/unit/linters/magic_numbers/
├── test_allowlist.py      # NEW
```

### Implementation Steps

1. **Add config**:
   ```python
   @dataclass
   class MagicNumbersConfig:
       # Default allowlist of well-known values
       allowlist: set[int] = field(default_factory=lambda: {
           0, 1,           # Common exit codes and booleans
           80, 443,        # HTTP/HTTPS ports
           22, 21,         # SSH/FTP ports
       })
       # Additional user-defined allowlist
       additional_allowlist: set[int] = field(default_factory=set)
   ```

2. **Implement check**:
   ```python
   def _is_allowed_value(self, value: int) -> bool:
       combined = self.config.allowlist | self.config.additional_allowlist
       return value in combined
   ```

3. **Write tests**:
   ```python
   def test_allows_standard_ports():
       code = 'if port == 80: pass'
       violations = analyze(code)
       assert len(violations) == 0

   def test_allows_custom_allowlist():
       config = MagicNumbersConfig(additional_allowlist={42})
       code = 'answer = 42'
       violations = analyze(code, config=config)
       assert len(violations) == 0
   ```

### Success Criteria
- [ ] Default allowlist works
- [ ] Custom allowlist works
- [ ] Non-allowed numbers still flagged

---

## PR5: Nesting Linter Elif Bug Fix

### Scope
Fix the nesting depth calculation to correctly handle elif branches as flat, not nested.

### Files to Modify
```
src/linters/nesting/
├── python_analyzer.py     # Fix depth calculation for elif

tests/unit/linters/nesting/
├── test_elif_depth.py     # NEW - Test elif chain depth
```

### Implementation Steps

1. **Identify the bug location** in `python_analyzer.py`:
   - Find where nesting depth is incremented
   - Check handling of `elif` vs nested `if`

2. **Fix the depth calculation**:
   ```python
   # elif should not increase depth, only nested blocks should
   # if/elif/elif = depth 1, not depth 3

   # Pseudo-fix approach:
   # When encountering If node, check if it's the else_ of a parent If
   # If so, don't increment depth for the elif case
   ```

3. **Write tests** with real examples:
   ```python
   def test_elif_chain_counts_as_one_level():
       code = '''
       def process(x):
           if x == 1:
               return "one"
           elif x == 2:
               return "two"
           elif x == 3:
               return "three"
           else:
               return "other"
       '''
       # Should be depth 1 (def -> if), not depth 4
       violations = analyze(code, max_depth=3)
       assert len(violations) == 0

   def test_nested_if_inside_elif_counts_correctly():
       code = '''
       def process(x, y):
           if x == 1:
               return "one"
           elif x == 2:
               if y > 0:  # This IS nested - depth 2
                   return "positive"
           else:
               return "other"
       '''
       # Should report depth 2 for the nested if, not more
       violations = analyze(code, max_depth=1)
       assert len(violations) == 1
   ```

### Testing Requirements
- Test flat elif chains (should be depth 1)
- Test nested if inside elif (should increase depth)
- Test mixed patterns
- Verify real false positive examples now pass

### Success Criteria
- [ ] Elif chains counted as depth 1
- [ ] Nested ifs inside elif still counted correctly
- [ ] `legacy_windows_render` no longer flagged
- [ ] All existing tests pass

---

## Implementation Guidelines

### Code Standards
- Follow existing linter patterns
- Use dataclasses for config
- Type hints on all functions
- Docstrings following project style

### Testing Requirements
- TDD: Write failing tests first
- Use real examples from evaluation
- Test edge cases
- Test config options

### Documentation Standards
- Update linter docstrings
- Add config options to docs
- Document exemption behavior

### Security Considerations
- N/A for this feature

### Performance Targets
- No measurable performance impact
- Definition file detection should be O(n) on file size

## Rollout Strategy

1. **PR1 & PR2**: Can be developed in parallel, merge independently
2. **PR3**: Higher complexity, may need iteration
3. **PR4**: Simple after PR3 patterns established
4. **PR5**: Independent, can be done any time - high impact fix

## Success Metrics

### Launch Metrics
- False positive reduction >50% on evaluation repos
- Zero regression in true positive detection

### Ongoing Metrics
- Monitor user feedback for new false positive patterns
- Track false positive reports in GitHub issues
