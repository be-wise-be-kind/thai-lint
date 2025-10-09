"""
Purpose: Test single statement detection for TypeScript DRY linter

Scope: Verify that single logical statements spanning multiple lines are NOT flagged

Overview: Tests that multi-line patterns representing single logical statements (decorators,
    function calls, object literals, class field definitions) are filtered from duplicate
    detection. Mirrors Python's single statement detection using tree-sitter AST analysis.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Parametrized tests for each single statement pattern type

Implementation: Comprehensive tests following TDD approach - tests written first, then implementation
"""

import pytest

from src import Linter


def test_decorator_pattern_not_flagged(tmp_path):
    """Test that decorator patterns are NOT flagged as duplicates."""
    file1 = tmp_path / "component1.ts"
    file1.write_text("""
@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})
class AppComponent {
    title = 'app1';
}
""")

    file2 = tmp_path / "component2.ts"
    file2.write_text("""
@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})
class OtherComponent {
    title = 'app2';
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Decorator arguments should NOT be flagged (single statement pattern)
    assert len(violations) == 0, "Decorator patterns should not be flagged as duplicate"


def test_function_call_arguments_not_flagged(tmp_path):
    """Test that multi-line function call arguments are NOT flagged."""
    file1 = tmp_path / "call1.ts"
    file1.write_text("""
const result1 = someFunction(
    arg1,
    arg2,
    arg3
);
""")

    file2 = tmp_path / "call2.ts"
    file2.write_text("""
const result2 = someFunction(
    arg1,
    arg2,
    arg3
);
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Function call arguments should NOT be flagged (single statement)
    assert len(violations) == 0, "Function call arguments should not be flagged as duplicate"


def test_object_literal_not_flagged(tmp_path):
    """Test that multi-line object literals are NOT flagged."""
    file1 = tmp_path / "config1.ts"
    file1.write_text("""
const config1 = {
    host: 'localhost',
    port: 3000,
    timeout: 5000
};
""")

    file2 = tmp_path / "config2.ts"
    file2.write_text("""
const config2 = {
    host: 'localhost',
    port: 3000,
    timeout: 5000
};
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Object literal properties should NOT be flagged (single statement)
    assert len(violations) == 0, "Object literals should not be flagged as duplicate"


def test_class_field_definitions_not_flagged(tmp_path):
    """Test that class field definitions are NOT flagged."""
    file1 = tmp_path / "model1.ts"
    file1.write_text("""
class User {
    id: string;
    name: string;
    email: string;

    process(): void {
        doSomething();
    }
}
""")

    file2 = tmp_path / "model2.ts"
    file2.write_text("""
class Product {
    id: string;
    name: string;
    email: string;

    handle(): void {
        doOtherThing();
    }
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Class field definitions should NOT be flagged (single statement pattern)
    assert len(violations) == 0, "Class field definitions should not be flagged as duplicate"


def test_array_destructuring_not_flagged(tmp_path):
    """Test that multi-line array destructuring is NOT flagged."""
    file1 = tmp_path / "destructure1.ts"
    file1.write_text("""
const [
    first,
    second,
    third
] = getValues();
""")

    file2 = tmp_path / "destructure2.ts"
    file2.write_text("""
const [
    first,
    second,
    third
] = getOtherValues();
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Array destructuring should NOT be flagged (single statement)
    assert len(violations) == 0, "Array destructuring should not be flagged as duplicate"


@pytest.mark.skip(
    reason="Tree-sitter TypeScript parser parses JSX as type assertions in non-TSX mode"
)
def test_jsx_props_not_flagged(tmp_path):
    """Test that multi-line JSX props are NOT flagged.

    Known limitation: tree-sitter-typescript parses JSX differently depending on file extension.
    This test is kept for future improvement when we add proper JSX/TSX support.
    """
    file1 = tmp_path / "component1.tsx"
    file1.write_text("""
function Component1() {
    return <MyComponent
        prop1="value1"
        prop2="value2"
        prop3="value3"
    />;
}
""")

    file2 = tmp_path / "component2.tsx"
    file2.write_text("""
function Component2() {
    return <MyComponent
        prop1="value1"
        prop2="value2"
        prop3="value3"
    />;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # JSX props should NOT be flagged (single statement pattern)
    assert len(violations) == 0, "JSX props should not be flagged as duplicate"


def test_multiple_separate_statements_still_flagged(tmp_path):
    """Test that multiple separate statements ARE still flagged."""
    file1 = tmp_path / "logic1.ts"
    file1.write_text("""
function process1(data: any): any {
    const validated = validate(data);
    const transformed = transform(validated);
    const saved = save(transformed);
    return saved;
}
""")

    file2 = tmp_path / "logic2.ts"
    file2.write_text("""
function process2(data: any): any {
    const validated = validate(data);
    const transformed = transform(validated);
    const saved = save(transformed);
    return saved;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Multiple separate statements SHOULD be flagged
    assert len(violations) >= 2, "Multiple separate statements should be flagged as duplicate"


def test_chained_method_calls_not_flagged(tmp_path):
    """Test that chained method calls (single expression) are NOT flagged."""
    file1 = tmp_path / "chain1.ts"
    file1.write_text("""
const result1 = data
    .filter(x => x.active)
    .map(x => x.id)
    .sort();
""")

    file2 = tmp_path / "chain2.ts"
    file2.write_text("""
const result2 = data
    .filter(x => x.active)
    .map(x => x.id)
    .sort();
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Chained method calls should NOT be flagged (single expression)
    assert len(violations) == 0, "Chained method calls should not be flagged as duplicate"


def test_type_assertion_not_flagged(tmp_path):
    """Test that multi-line type assertions are NOT flagged."""
    file1 = tmp_path / "assert1.ts"
    file1.write_text("""
const user1 = getValue() as {
    id: string;
    name: string;
    email: string;
};
""")

    file2 = tmp_path / "assert2.ts"
    file2.write_text("""
const user2 = getOtherValue() as {
    id: string;
    name: string;
    email: string;
};
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Type assertions should NOT be flagged (single statement)
    assert len(violations) == 0, "Type assertions should not be flagged as duplicate"


def test_nested_function_calls_not_flagged(tmp_path):
    """Test that nested function calls are NOT flagged."""
    file1 = tmp_path / "nested1.ts"
    file1.write_text("""
const result1 = outer(
    inner(
        arg1,
        arg2
    )
);
""")

    file2 = tmp_path / "nested2.ts"
    file2.write_text("""
const result2 = outer(
    inner(
        arg1,
        arg2
    )
);
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Nested function calls should NOT be flagged (single statement)
    assert len(violations) == 0, "Nested function calls should not be flagged as duplicate"
