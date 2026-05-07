"""
Purpose: Shared filter constants for Law of Demeter chain classification

Scope: Frozen sets and tuples used by the 9-filter classification pipeline

Overview: Contains all constant data structures used by the chain classifier to distinguish
    genuine LoD violations from legitimate chaining patterns. Includes string method names,
    collection pipeline methods, builder methods, known module roots, AST node attributes,
    safe chain prefixes, safe terminal methods, and test file patterns. Derived from patterns
    observed across 23 real-world Python repos during prototype testing.

Dependencies: None (pure constants)

Exports: STR_METHODS, COLLECTION_PIPELINE_METHODS, BUILDER_METHODS, KNOWN_MODULE_ROOTS,
    AST_NODE_ATTRS, SAFE_CHAIN_PREFIXES, SAFE_TERMINAL_METHODS, TEST_FILE_PATTERNS

Interfaces: Import constants by name

Implementation: All collections are frozenset or tuple for immutability and fast lookup
"""

# ---------------------------------------------------------------------------
# Filter 3: Same-type method chaining (str, bytes returns same type)
# ---------------------------------------------------------------------------

STR_METHODS = frozenset(
    {
        "strip",
        "lstrip",
        "rstrip",
        "lower",
        "upper",
        "title",
        "capitalize",
        "casefold",
        "swapcase",
        "replace",
        "encode",
        "decode",
        "format",
        "format_map",
        "center",
        "ljust",
        "rjust",
        "zfill",
        "expandtabs",
        "translate",
        "removeprefix",
        "removesuffix",
        # Methods that return sequences of strings (split family)
        "split",
        "rsplit",
        "splitlines",
        "partition",
        "rpartition",
        # Regex match group access
        "group",
        "groups",
        "groupdict",
        # join operates on str
        "join",
    }
)

# ---------------------------------------------------------------------------
# Filter 4: Collection pipeline / ORM / builder chaining
# ---------------------------------------------------------------------------

COLLECTION_PIPELINE_METHODS = frozenset(
    {
        "filter",
        "map",
        "reduce",
        "sorted",
        "groupby",
        "reversed",
        "select",
        "where",
        "order_by",
        "limit",
        "offset",
        "join",
        "on",
        "having",
        "group_by",
        "distinct",
        "exclude",
        "annotate",
        "values_list",
        "prefetch_related",
        "select_related",
        "defer",
        "only",
        "query",
        "all",
        "first",
        "last",
        "count",
        "sum",
        "avg",
        "min",
        "max",
        "aggregate",
    }
)

BUILDER_METHODS = frozenset(
    {
        "set",
        "with_",
        "add",
        "configure",
        "option",
        "build",
        "then",
        "catch",
        "finally_",
        "chain",
        "pipe",
        "compose",
        "apply",
        "register",
        "route",
        "use",
        "middleware",
    }
)

# ---------------------------------------------------------------------------
# Filter 2: Module-qualified access (dotted imports, not object navigation)
# ---------------------------------------------------------------------------

KNOWN_MODULE_ROOTS = frozenset(
    {
        # Stdlib
        "os",
        "sys",
        "io",
        "re",
        "json",
        "yaml",
        "csv",
        "math",
        "logging",
        "pathlib",
        "collections",
        "itertools",
        "functools",
        "operator",
        "datetime",
        "typing",
        "abc",
        "enum",
        "dataclasses",
        "contextlib",
        "unittest",
        "subprocess",
        "importlib",
        "inspect",
        "ast",
        "copy",
        "hashlib",
        "hmac",
        "secrets",
        "tempfile",
        "shutil",
        "glob",
        "argparse",
        "textwrap",
        "string",
        "struct",
        "codecs",
        "threading",
        "multiprocessing",
        "concurrent",
        "asyncio",
        "http",
        "urllib",
        "email",
        "html",
        "xml",
        "sqlite3",
        "socket",
        "ssl",
        "signal",
        "warnings",
        "traceback",
        "pdb",
        # Common third-party top-level modules
        "rich",
        "click",
        "flask",
        "django",
        "fastapi",
        "starlette",
        "sqlalchemy",
        "pydantic",
        "pytest",
        "numpy",
        "np",
        "pandas",
        "pd",
        "requests",
        "httpx",
        "aiohttp",
        "celery",
        "redis",
        "pygments",
        "jinja2",
        "werkzeug",
        "marshmallow",
        "boto3",
        "botocore",
        "google",
        "azure",
        "aws_cdk",
        "loguru",
        "structlog",
        "sentry_sdk",
        "mypy",
        "pylint",
        "ruff",
        "black",
        "isort",
        "setuptools",
        "pkg_resources",
        "pip",
        "poetry",
        "docker",
        "kubernetes",
        "terraform",
    }
)

# ---------------------------------------------------------------------------
# Filter 5: AST / compiler node traversal (data structure navigation)
# ---------------------------------------------------------------------------

AST_NODE_ATTRS = frozenset(
    {
        # Python AST
        "func",
        "value",
        "attr",
        "args",
        "body",
        "orelse",
        "handlers",
        "targets",
        "target",
        "test",
        "iter",
        "elt",
        "elts",
        "keys",
        "values",
        "ops",
        "comparators",
        "left",
        "right",
        "operand",
        "slice",
        "ctx",
        "lineno",
        "col_offset",
        "end_lineno",
        "end_col_offset",
        "type_comment",
        "decorator_list",
        "returns",
        "annotation",
        "id",
        "arg",
        "defaults",
        "kw_defaults",
        "kwarg",
        "vararg",
        "posonlyargs",
        "kwonlyargs",
        # MyPy / type checker nodes
        "node",
        "info",
        "type",
        "fullname",
        "callee",
        "rvalue",
        "declared_metaclass",
        "names",
    }
)

# ---------------------------------------------------------------------------
# Filter 5 threshold: fraction of intermediate parts that must be AST attrs
# ---------------------------------------------------------------------------

AST_TRAVERSAL_THRESHOLD = 0.6

# ---------------------------------------------------------------------------
# Filter 1: Known safe chain prefixes
# ---------------------------------------------------------------------------

SAFE_CHAIN_PREFIXES = (
    # self/cls access - own state is fine
    "self.",
    "cls.",
    # Module-level stdlib
    "os.path.",
    "os.environ.",
    "sys.stdout.",
    "sys.stderr.",
    "sys.stdin.",
    "sys.modules.",
    "sys.exc_info.",
    # Logging
    "logging.",
    "logger.",
    # Type hints
    "typing.",
    "t.",
    "T.",
    # Test patterns
    "mock.",
    "patch.",
    "mocker.",
    "exc_info.",
    # Settings / config namespace
    "settings.",
    "config.",
    "conf.",
    "cfg.",
    "options.",
    "args.",
    # Django / Flask
    "request.POST.",
    "request.GET.",
    "request.META.",
    "request.session.",
    "request.data.",
    "response.data.",
    "app.config.",
)

# ---------------------------------------------------------------------------
# Filter 8: Safe terminal methods (common endpoints of any chain)
# ---------------------------------------------------------------------------

SAFE_TERMINAL_METHODS = frozenset(
    {
        "__str__",
        "__repr__",
        "__format__",
        "__eq__",
        "__ne__",
        "__lt__",
        "__gt__",
        "__enter__",
        "__exit__",
        "__iter__",
        "__next__",
        "__len__",
        "__bool__",
        "items",
        "keys",
        "values",
        "get",
        "pop",
        "setdefault",
        "append",
        "extend",
        "insert",
        "update",
        "copy",
        "read",
        "write",
        "close",
        "flush",
        "encode",
        "decode",
        "format",
        "join",
        "exists",
        "is_file",
        "is_dir",
        "resolve",
        "absolute",
        "startswith",
        "endswith",
        "count",
        "add",
        "remove",
        "discard",
        "clear",
        "send",
        "throw",
        # Conversion terminals
        "as_dict",
        "to_dict",
        "to_json",
        "to_list",
        "to_string",
        "as_posix",
        "as_uri",
    }
)

# ---------------------------------------------------------------------------
# Filter 9: Test file patterns
# ---------------------------------------------------------------------------

TEST_FILE_PATTERNS = ("test_", "tests/", "testing/", "conftest", "_test.py")
