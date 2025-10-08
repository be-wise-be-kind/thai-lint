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


def test_typescript_exact_3_line_duplicate(tmp_path):
    """Test TypeScript duplicate detection with 3-line duplicate."""
    file1 = tmp_path / "file1.ts"
    file1.write_text("""
function processData(items: Item[]) {
    for (const item of items) {
        if (item.isValid()) {
            item.save();
        }
    }
}
""")

    file2 = tmp_path / "file2.ts"
    file2.write_text("""
function handleRecords(records: Record[]) {
    for (const item of items) {
        if (item.isValid()) {
            item.save();
        }
    }
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
    assert all(v.rule_id == "dry.duplicate-code" for v in violations)


def test_javascript_exact_duplicate(tmp_path):
    """Test JavaScript (.js) duplicate detection."""
    file1 = tmp_path / "service1.js"
    file1.write_text("""
function validateInput(data) {
    if (!data) {
        throw new Error('Data required');
    }
    if (!data.id) {
        throw new Error('ID required');
    }
    return true;
}
""")

    file2 = tmp_path / "service2.js"
    file2.write_text("""
function checkInput(data) {
    if (!data) {
        throw new Error('Data required');
    }
    if (!data.id) {
        throw new Error('ID required');
    }
    return true;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


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


def test_async_await_duplicates(tmp_path):
    """Test duplicate detection in async/await patterns."""
    file1 = tmp_path / "api1.ts"
    file1.write_text("""
async function fetchData(id: string) {
    const response = await fetch(`/api/data/${id}`);
    const data = await response.json();
    return processData(data);
}
""")

    file2 = tmp_path / "api2.ts"
    file2.write_text("""
async function getData(id: string) {
    const response = await fetch(`/api/data/${id}`);
    const data = await response.json();
    return processData(data);
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


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
    """Test duplicate detection in Promise chains."""
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

    assert len(violations) == 2


def test_object_destructuring_duplicates(tmp_path):
    """Test duplicate detection with object destructuring."""
    file1 = tmp_path / "extract1.ts"
    file1.write_text("""
function processUser(user: User) {
    const { name, email, age } = user;
    const validated = validateEmail(email);
    const formatted = formatName(name);
    return { validated, formatted, age };
}
""")

    file2 = tmp_path / "extract2.ts"
    file2.write_text("""
function handleUser(user: User) {
    const { name, email, age } = user;
    const validated = validateEmail(email);
    const formatted = formatName(name);
    return { validated, formatted, age };
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) >= 2


def test_typescript_generics_duplicates(tmp_path):
    """Test duplicate detection in generic functions."""
    file1 = tmp_path / "generic1.ts"
    file1.write_text("""
function transform<T>(items: T[]): T[] {
    const filtered = items.filter(item => item !== null);
    const unique = Array.from(new Set(filtered));
    return unique.sort();
}
""")

    file2 = tmp_path / "generic2.ts"
    file2.write_text("""
function process<T>(items: T[]): T[] {
    const filtered = items.filter(item => item !== null);
    const unique = Array.from(new Set(filtered));
    return unique.sort();
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


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


def test_switch_statement_duplicates(tmp_path):
    """Test duplicate detection in switch statements."""
    switch_block = """
    switch (status) {
        case 'pending':
            return 0;
        case 'active':
            return 1;
        case 'completed':
            return 2;
        default:
            return -1;
    }
"""

    file1 = tmp_path / "status1.ts"
    file1.write_text(f"function getCode1(status: string): number {{\n{switch_block}}}\n")

    file2 = tmp_path / "status2.ts"
    file2.write_text(f"function getCode2(status: string): number {{\n{switch_block}}}\n")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 5\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


def test_try_catch_duplicates_typescript(tmp_path):
    """Test duplicate detection in TypeScript try-catch blocks."""
    file1 = tmp_path / "error1.ts"
    file1.write_text("""
async function execute1() {
    try {
        const result = await riskyOperation();
        return result;
    } catch (error) {
        logger.error(error);
        throw error;
    }
}
""")

    file2 = tmp_path / "error2.ts"
    file2.write_text("""
async function execute2() {
    try {
        const result = await riskyOperation();
        return result;
    } catch (error) {
        logger.error(error);
        throw error;
    }
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2


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


def test_mixed_js_ts_duplicates(tmp_path):
    """Test duplicate detection across .js and .ts files."""
    file1 = tmp_path / "handler.js"
    file1.write_text("""
function validate(data) {
    if (!data) return false;
    if (!data.id) return false;
    if (!data.value) return false;
    return true;
}
""")

    file2 = tmp_path / "validator.ts"
    file2.write_text("""
function check(data: any) {
    if (!data) return false;
    if (!data.id) return false;
    if (!data.value) return false;
    return true;
}
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 4\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 2
