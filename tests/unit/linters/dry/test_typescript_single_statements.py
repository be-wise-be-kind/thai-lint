"""
Purpose: Unit tests for TypeScript single statement detection in DRY linter

Scope: Testing multi-line single statement filtering for TypeScript code patterns

Overview: Comprehensive test suite ensuring multi-line patterns representing single logical
    statements such as decorators, function calls, object literals, and class field definitions
    are filtered from duplicate detection. Mirrors Python single statement detection using
    tree-sitter AST analysis for TypeScript. Tests Angular decorators, React patterns, and
    configuration objects to validate filtering of common TypeScript idioms.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: test_decorator_pattern_not_flagged, test_object_literal_not_flagged,
    test_function_call_not_flagged test functions

Interfaces: Test functions accepting tmp_path fixture for file system operations

Implementation: Creates temporary TypeScript files with identical multi-line single statements,
    runs DRY linter with configured threshold, validates no violations for single statement patterns,
    follows TDD approach with tests written before implementation
"""

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
