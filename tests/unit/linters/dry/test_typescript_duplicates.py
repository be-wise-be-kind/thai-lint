"""
Purpose: Tests for TypeScript/JavaScript duplicate code detection in DRY linter

Scope: TypeScript and JavaScript language duplicate detection with language-specific patterns

Overview: Comprehensive test suite covering TypeScript and JavaScript duplicates including
    arrow functions, class methods, interface patterns, and React components. Tests exact
    duplicates, near-duplicates with comments, and language-specific constructs. Validates
    proper tokenization and detection for TS/JS syntax.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: 15 test functions for TypeScript/JavaScript duplicate scenarios

Interfaces: Uses Linter class with config file and rules=['dry.duplicate-code']

Implementation: TDD approach - tests written before implementation. All tests should
    initially fail with ModuleNotFoundError. Uses tmp_path for isolated file fixtures.
    Tests use cache_enabled: false for isolation, which triggers in-memory fallback mode
    (Decision 6): DRYRule maintains dict[int, list[CodeBlock]] instead of SQLite, providing
    same stateful behavior without persistence between test runs.
"""

from src import Linter


def test_arrow_function_duplicates(tmp_path):
    """Test duplicate detection in arrow functions."""
    file1 = tmp_path / "handlers1.ts"
    file1.write_text("""
const processUsers = (users: User[]) => {
    const filtered = users.filter(u => u.active);
    const mapped = filtered.map(u => u.id);
    return mapped.sort();
};
""")

    file2 = tmp_path / "handlers2.ts"
    file2.write_text("""
const handleUsers = (users: User[]) => {
    const filtered = users.filter(u => u.active);
    const mapped = filtered.map(u => u.id);
    return mapped.sort();
};
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_class_method_duplicates(tmp_path):
    """Test duplicate detection in TypeScript class methods."""
    file1 = tmp_path / "UserService.ts"
    file1.write_text("""
class UserService {
    validate(user: User): boolean {
        if (!user.email) return false;
        if (!user.name) return false;
        if (user.age < 0) return false;
        return true;
    }
}
""")

    file2 = tmp_path / "ProductService.ts"
    file2.write_text("""
class ProductService {
    validate(product: Product): boolean {
        if (!user.email) return false;
        if (!user.name) return false;
        if (user.age < 0) return false;
        return true;
    }
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_react_component_patterns(tmp_path):
    """Test duplicate detection in React component patterns."""
    file1 = tmp_path / "Button1.tsx"
    file1.write_text("""
export const Button1: React.FC<Props> = ({ onClick }) => {
    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        onClick();
    };

    return <button onClick={handleClick}>Click</button>;
};
""")

    file2 = tmp_path / "Button2.tsx"
    file2.write_text("""
export const Button2: React.FC<Props> = ({ onClick }) => {
    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        onClick();
    };

    return <button onClick={handleClick}>Submit</button>;
};
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_typescript_with_comment_differences(tmp_path):
    """Test near-duplicate with different comments."""
    file1 = tmp_path / "util1.ts"
    file1.write_text("""
function process(data: Data[]) {
    // Filter active items
    const active = data.filter(d => d.active);
    const sorted = active.sort((a, b) => a.id - b.id);
    return sorted.map(d => d.value);
}
""")

    file2 = tmp_path / "util2.ts"
    file2.write_text("""
function handle(data: Data[]) {
    // Filter items that are active
    const active = data.filter(d => d.active);
    const sorted = active.sort((a, b) => a.id - b.id);
    return sorted.map(d => d.value);
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_promise_chain_duplicates(tmp_path):
    """Test that Promise chains (chained method calls) are NOT flagged.

    Note: Promise chains like .then().then().catch() are filtered as single
    expressions (member_expression chaining), similar to data.filter().map().sort().
    This is intentional to reduce false positives from common chaining patterns.
    """
    file1 = tmp_path / "fetch1.ts"
    file1.write_text("""
function loadUser(id: string) {
    return fetch(`/users/${id}`)
        .then(res => res.json())
        .then(data => validateUser(data))
        .catch(err => handleError(err));
}
""")

    file2 = tmp_path / "fetch2.ts"
    file2.write_text("""
function getUser(id: string) {
    return fetch(`/users/${id}`)
        .then(res => res.json())
        .then(data => validateUser(data))
        .catch(err => handleError(err));
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Promise chains are filtered as chained method calls (single expression)
    assert len(violations) == 0, "Promise chains should not be flagged (chained method calls)"


def test_interface_definitions_should_not_be_duplicates(tmp_path):
    """Test that interface definitions are NOT flagged as duplicates."""
    file1 = tmp_path / "types1.ts"
    file1.write_text("""
interface User {
    id: string;
    name: string;
    email: string;
}
""")

    file2 = tmp_path / "types2.ts"
    file2.write_text("""
interface Product {
    id: string;
    name: string;
    email: string;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0


def test_no_duplicates_typescript(tmp_path):
    """Test that unique TypeScript code produces no violations."""
    file1 = tmp_path / "unique1.ts"
    file1.write_text("""
function processUsers(users: User[]) {
    return users.map(u => u.name);
}
""")

    file2 = tmp_path / "unique2.ts"
    file2.write_text("""
function processProducts(products: Product[]) {
    return products.filter(p => p.active);
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0
