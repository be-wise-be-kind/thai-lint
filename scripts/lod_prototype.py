#!/usr/bin/env python3
"""Law of Demeter violation detector prototype (v2).

Scans Python files for chained attribute/method access that may violate
the Law of Demeter ("only talk to your immediate friends").

Usage:
    python scripts/lod_prototype.py <path> [--min-depth N] [--show-allowed]
    python scripts/lod_prototype.py /path/to/repo --min-depth 3
"""

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Filter: Same-type method chaining (str, bytes, list returns same type)
# ---------------------------------------------------------------------------

STR_METHODS = frozenset({
    "strip", "lstrip", "rstrip", "lower", "upper", "title", "capitalize",
    "casefold", "swapcase", "replace", "encode", "decode", "format",
    "format_map", "center", "ljust", "rjust", "zfill", "expandtabs",
    "translate", "removeprefix", "removesuffix",
    # Methods that return sequences of strings (split family)
    "split", "rsplit", "splitlines", "partition", "rpartition",
    # Regex match group access
    "group", "groups", "groupdict",
    # join operates on str
    "join",
})

# Methods that return a new collection of the same kind
COLLECTION_PIPELINE_METHODS = frozenset({
    "filter", "map", "reduce", "sorted", "groupby", "reversed",
    "select", "where", "order_by", "limit", "offset",
    "join", "on", "having", "group_by", "distinct",
    "exclude", "annotate", "values_list", "prefetch_related",
    "select_related", "defer", "only",
})

# Methods that are part of builder/fluent patterns (return self)
BUILDER_METHODS = frozenset({
    "set", "with_", "add", "configure", "option", "build",
    "then", "catch", "finally_", "chain", "pipe", "compose", "apply",
    "register", "route", "use", "middleware",
})

# ---------------------------------------------------------------------------
# Filter: Module-qualified access (dotted imports, not object navigation)
# ---------------------------------------------------------------------------

KNOWN_MODULE_ROOTS = frozenset({
    # Stdlib
    "os", "sys", "io", "re", "json", "yaml", "csv", "math", "logging",
    "pathlib", "collections", "itertools", "functools", "operator",
    "datetime", "typing", "abc", "enum", "dataclasses", "contextlib",
    "unittest", "subprocess", "importlib", "inspect", "ast", "copy",
    "hashlib", "hmac", "secrets", "tempfile", "shutil", "glob",
    "argparse", "textwrap", "string", "struct", "codecs",
    "threading", "multiprocessing", "concurrent", "asyncio",
    "http", "urllib", "email", "html", "xml",
    "sqlite3", "socket", "ssl", "signal",
    "warnings", "traceback", "pdb",
    # Common third-party top-level modules
    "rich", "click", "flask", "django", "fastapi", "starlette",
    "sqlalchemy", "pydantic", "pytest", "numpy", "np", "pandas", "pd",
    "requests", "httpx", "aiohttp", "celery", "redis",
    "pygments", "jinja2", "werkzeug", "marshmallow",
    "boto3", "botocore", "google", "azure", "aws_cdk",
    "loguru", "structlog", "sentry_sdk",
    "mypy", "pylint", "ruff", "black", "isort",
    "setuptools", "pkg_resources", "pip", "poetry",
    "docker", "kubernetes", "terraform",
})

# ---------------------------------------------------------------------------
# Filter: AST / compiler node traversal (data structure navigation)
# ---------------------------------------------------------------------------

AST_NODE_ATTRS = frozenset({
    # Python AST
    "func", "value", "attr", "args", "body", "orelse", "handlers",
    "targets", "target", "test", "iter", "elt", "elts", "keys",
    "values", "ops", "comparators", "left", "right", "operand",
    "slice", "ctx", "lineno", "col_offset", "end_lineno",
    "end_col_offset", "type_comment", "decorator_list", "returns",
    "annotation", "id", "arg", "defaults", "kw_defaults",
    "kwarg", "vararg", "posonlyargs", "kwonlyargs",
    # MyPy / type checker nodes
    "node", "info", "type", "fullname", "callee", "rvalue",
    "declared_metaclass", "names",
})

# ---------------------------------------------------------------------------
# Filter: Dunder / protocol access (framework internals)
# ---------------------------------------------------------------------------

DUNDER_PATTERN_PREFIXES = ("__",)  # attrs starting with __ are protocol access

# ---------------------------------------------------------------------------
# Filter: Known safe chain prefixes
# ---------------------------------------------------------------------------

SAFE_CHAIN_PREFIXES = [
    # self/cls access - own state is fine
    "self.", "cls.",
    # Module-level stdlib
    "os.path.", "os.environ.",
    "sys.stdout.", "sys.stderr.", "sys.stdin.",
    "sys.modules.", "sys.exc_info.",
    # Logging
    "logging.", "logger.",
    # Type hints
    "typing.", "t.", "T.",
    # Test patterns
    "mock.", "patch.", "mocker.",
    "exc_info.",
    # Settings / config namespace
    "settings.", "config.", "conf.", "cfg.", "options.", "args.",
    # Django / Flask
    "request.POST.", "request.GET.", "request.META.",
    "request.session.", "request.data.",
    "response.data.",
    "app.config.",
]

# ---------------------------------------------------------------------------
# Filter: Safe terminal methods (common endpoints of any chain)
# ---------------------------------------------------------------------------

SAFE_TERMINAL_METHODS = frozenset({
    "__str__", "__repr__", "__format__",
    "__eq__", "__ne__", "__lt__", "__gt__",
    "__enter__", "__exit__",
    "__iter__", "__next__", "__len__", "__bool__",
    "items", "keys", "values",
    "get", "pop", "setdefault",
    "append", "extend", "insert", "update", "copy",
    "read", "write", "close", "flush",
    "encode", "decode",
    "format", "join",
    "exists", "is_file", "is_dir", "resolve", "absolute",
    "startswith", "endswith", "count",
    "add", "remove", "discard", "clear",
    "send", "throw",
    # Conversion terminals
    "as_dict", "to_dict", "to_json", "to_list", "to_string",
    "as_posix", "as_uri",
})

# ---------------------------------------------------------------------------
# Filter: Test file patterns
# ---------------------------------------------------------------------------

TEST_FILE_PATTERNS = ("test_", "tests/", "testing/", "conftest", "_test.py")


@dataclass
class ChainInfo:
    """Represents a detected attribute/method chain."""

    file: str
    line: int
    col: int
    chain: str
    depth: int
    source_line: str = ""
    allowed_reason: str = ""


@dataclass
class FileImports:
    """Tracks what names are imported as modules vs objects in a file."""

    module_names: set = field(default_factory=set)
    from_imports: dict = field(default_factory=dict)  # name -> module


@dataclass
class Stats:
    """Aggregate statistics."""

    total_files: int = 0
    total_chains: int = 0
    violations: int = 0
    allowed: int = 0
    by_reason: dict = field(default_factory=dict)


def extract_imports(tree: ast.AST) -> FileImports:
    """Extract import information from an AST to identify module-level names."""
    imports = FileImports()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports.module_names.add(name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports.from_imports[name] = module
    return imports


def chain_to_parts(node: ast.AST) -> list[str]:
    """Walk an AST node and extract the chain of attribute/method names.

    Returns list of parts like ["obj", "method()", "attr", "method()"].
    """
    parts: list[str] = []
    current = node

    while True:
        if isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        elif isinstance(current, ast.Call):
            current = current.func
            if parts:
                parts[-1] = parts[-1] + "()"
            if isinstance(current, ast.Name):
                parts.append(current.id + "()")
                break
        elif isinstance(current, ast.Subscript):
            parts.append("[…]")
            current = current.value
        elif isinstance(current, ast.Name):
            parts.append(current.id)
            break
        else:
            parts.append("?")
            break

    parts.reverse()
    return parts


def _clean(part: str) -> str:
    """Strip () and [...] markers from a chain part."""
    return part.replace("[…]", "").rstrip("()")


def _is_subscript(part: str) -> bool:
    """Check if a chain part represents a subscript access."""
    return "[…]" in part


def _is_test_file(filepath: str) -> bool:
    """Check if a filepath looks like a test file."""
    return any(pat in filepath for pat in TEST_FILE_PATTERNS)


def classify_chain(parts: list[str], imports: FileImports, filepath: str) -> str:
    """Classify a chain. Returns reason string if allowed, empty string if violation."""
    chain_str = ".".join(_clean(p) for p in parts)
    root = _clean(parts[0])

    # ---- 1. Safe chain prefixes (self., cls., config., etc.) ----
    for prefix in SAFE_CHAIN_PREFIXES:
        if chain_str.startswith(prefix):
            return f"safe-prefix:{prefix.rstrip('.')}"

    # ---- 2. Module-qualified access (import-aware) ----
    if root in imports.module_names or root in KNOWN_MODULE_ROOTS:
        return f"module-access:{root}"

    # ---- 3. Same-type string/bytes chaining ----
    # Filter out chains that are purely string/sequence manipulation.
    # Covers: text.split("x")[0].lower(), obj.name.replace("a").replace("b"),
    #         version.partition('+')[0].split('.'), m.groupdict()['key'].split(',')
    non_root = parts[1:]
    non_sub = [_clean(p) for p in non_root if not _is_subscript(p)]
    non_sub_nonempty = [m for m in non_sub if m]  # drop empty strings from cleaned subscripts

    if non_sub_nonempty and all(m in STR_METHODS for m in non_sub_nonempty):
        return "same-type:str"

    # Also catch obj.attr.str_method().str_method() — the tail (after first attr)
    # is all string ops (e.g., node.type.replace("a").replace("b"))
    if len(parts) >= 3:
        tail = parts[2:]
        tail_clean = [_clean(p) for p in tail if not _is_subscript(p)]
        tail_nonempty = [m for m in tail_clean if m]
        if tail_nonempty and all(m in STR_METHODS for m in tail_nonempty):
            return "same-type:str-attr"

    # ---- 4. Collection pipeline / ORM chaining ----
    if non_sub_nonempty and all(
        m in COLLECTION_PIPELINE_METHODS | BUILDER_METHODS for m in non_sub_nonempty
    ):
        return "fluent-chain"

    # ---- 5. AST / compiler node traversal ----
    # If most intermediate parts are AST node attributes, it's data structure navigation
    intermediates = [_clean(p) for p in parts[1:-1] if not _is_subscript(p)]
    if intermediates:
        ast_count = sum(1 for a in intermediates if a in AST_NODE_ATTRS)
        if ast_count >= len(intermediates) * 0.6:
            return "ast-traversal"

    # ---- 6. Dunder / protocol access ----
    non_root = [_clean(p) for p in parts[1:]]
    dunder_count = sum(1 for a in non_root if a.startswith("__") and a.endswith("__"))
    if dunder_count > 0:
        return "dunder-access"

    # ---- 7. Subscript-heavy chains (dict/list navigation, not object navigation) ----
    subscript_count = sum(1 for p in parts if _is_subscript(p))
    if subscript_count >= 1 and len(parts) - subscript_count <= 2:
        # Most of the "depth" comes from subscripts, not attribute access
        return "subscript-access"

    # ---- 8. Safe terminal method ----
    terminal = _clean(parts[-1])
    if terminal in SAFE_TERMINAL_METHODS:
        return f"safe-terminal:{terminal}"

    # ---- 9. Test file leniency (deeper chains common in assertions) ----
    if _is_test_file(filepath):
        return "test-file"

    return ""


def extract_chains(tree: ast.AST, min_depth: int) -> list[tuple[list[str], ast.AST]]:
    """Extract all attribute/method chains from an AST that meet min_depth."""
    chains = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Attribute, ast.Call)):
            parts = chain_to_parts(node)
            depth = len(parts) - 1
            if depth >= min_depth:
                chains.append((parts, node))

    # Deduplicate: keep only the longest chain per line
    seen: dict[int, tuple[list[str], ast.AST]] = {}
    for parts, node in chains:
        lineno = getattr(node, "lineno", 0)
        if lineno not in seen or len(parts) > len(seen[lineno][0]):
            seen[lineno] = (parts, node)

    return list(seen.values())


def scan_file(filepath: Path, min_depth: int) -> list[ChainInfo]:
    """Scan a single Python file for LoD chains."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports = extract_imports(tree)
    lines = source.splitlines()
    results = []

    for parts, node in extract_chains(tree, min_depth):
        lineno = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)
        depth = len(parts) - 1
        chain_str = ".".join(parts)
        source_line = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""
        allowed = classify_chain(parts, imports, str(filepath))

        results.append(ChainInfo(
            file=str(filepath),
            line=lineno,
            col=col,
            chain=chain_str,
            depth=depth,
            source_line=source_line,
            allowed_reason=allowed,
        ))

    return results


SKIP_DIRS = frozenset({
    "node_modules", "__pycache__", "venv", ".venv", "env",
    "site-packages", ".tox", ".eggs", "dist", "build", ".git",
    "htmlcov", ".mypy_cache", ".pytest_cache", ".ruff_cache",
})


def scan_directory(root: Path, min_depth: int) -> list[ChainInfo]:
    """Recursively scan a directory for Python files."""
    all_results = []
    py_files = sorted(root.rglob("*.py"))

    for filepath in py_files:
        rel_parts = filepath.relative_to(root).parts
        if any(p.startswith(".") or p in SKIP_DIRS for p in rel_parts):
            continue
        all_results.extend(scan_file(filepath, min_depth))

    return all_results


def print_results(results: list[ChainInfo], show_allowed: bool, target: Path) -> Stats:
    """Print results and return statistics."""
    stats = Stats()
    stats.total_chains = len(results)

    violations = [r for r in results if not r.allowed_reason]
    allowed = [r for r in results if r.allowed_reason]
    stats.violations = len(violations)
    stats.allowed = len(allowed)

    for r in allowed:
        reason_type = r.allowed_reason.split(":")[0]
        stats.by_reason[reason_type] = stats.by_reason.get(reason_type, 0) + 1

    if violations:
        print(f"\n{'='*80}")
        print(f"POTENTIAL LAW OF DEMETER VIOLATIONS ({len(violations)})")
        print(f"{'='*80}")
        for v in violations:
            rel = Path(v.file)
            try:
                rel = rel.relative_to(target)
            except ValueError:
                pass
            print(f"\n  {rel}:{v.line}:{v.col}")
            print(f"    Chain ({v.depth} deep): {v.chain}")
            print(f"    Source: {v.source_line}")

    if show_allowed and allowed:
        print(f"\n{'='*80}")
        print(f"ALLOWED CHAINS ({len(allowed)})")
        print(f"{'='*80}")
        for v in allowed:
            rel = Path(v.file)
            try:
                rel = rel.relative_to(target)
            except ValueError:
                pass
            print(f"  {rel}:{v.line} [{v.allowed_reason}] {v.chain}")

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"  Total chains detected:  {stats.total_chains}")
    print(f"  Violations:             {stats.violations}")
    print(f"  Allowed (filtered):     {stats.allowed}")
    if stats.total_chains > 0:
        filter_pct = stats.allowed / stats.total_chains * 100
        print(f"  Filter rate:            {filter_pct:.1f}%")
    print(f"\n  Allowed breakdown:")
    for reason, count in sorted(stats.by_reason.items(), key=lambda x: -x[1]):
        print(f"    {reason:25s} {count:5d}")

    return stats


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Law of Demeter prototype detector (v2)")
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument("--min-depth", type=int, default=3,
                        help="Minimum chain depth to report (default: 3)")
    parser.add_argument("--show-allowed", action="store_true",
                        help="Show chains that were filtered as allowed")
    args = parser.parse_args()

    target = args.path.resolve()
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    if target.is_file():
        results = scan_file(target, args.min_depth)
    else:
        results = scan_directory(target, args.min_depth)

    print_results(results, args.show_allowed, target)


if __name__ == "__main__":
    main()
