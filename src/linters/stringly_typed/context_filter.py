"""
Purpose: Context-aware filtering for stringly-typed function call violations

Scope: Filter out false positive function call patterns based on function names and contexts

Overview: Implements a blocklist-based filtering approach to reduce false positives in the
    stringly-typed linter's function call detection. Excludes known false positive patterns
    including dictionary access methods, string processing functions, logging calls, framework
    validators, and external API functions. Uses function name pattern matching and parameter
    position filtering to achieve <5% false positive rate.

Dependencies: re module for pattern matching

Exports: FunctionCallFilter class

Interfaces: FunctionCallFilter.should_include(function_name, param_index, string_values) -> bool

Implementation: Blocklist-based filtering with function name patterns, parameter position rules,
    and string value pattern detection
"""

import re


class FunctionCallFilter:  # thailint: ignore srp - data-heavy class with extensive exclusion pattern lists
    """Filters function call violations to reduce false positives.

    Uses a blocklist approach to exclude known false positive patterns:
    - Dictionary/object access methods (.get, .set, .pop)
    - String processing methods (split, replace, strip, strftime)
    - Logging and output functions (logger.*, print, echo)
    - Framework-specific patterns (Pydantic validators, TypeVar)
    - External API functions (boto3, HTTP clients)
    - File and path operations
    """

    # Function name patterns to always exclude (case-insensitive suffix/contains match)
    _EXCLUDED_FUNCTION_PATTERNS: tuple[str, ...] = (
        # Dictionary/object access - these are metadata access, not domain values
        ".get",
        ".set",
        ".pop",
        ".setdefault",
        ".update",
        # List/collection operations
        ".append",
        ".extend",
        ".insert",
        ".add",
        ".remove",
        # String processing - delimiters and format strings
        ".split",
        ".rsplit",
        ".replace",
        ".strip",
        ".rstrip",
        ".lstrip",
        ".startswith",
        ".endswith",
        ".format",
        ".join",
        ".encode",
        ".decode",
        ".lower",
        ".upper",
        "strftime",
        "strptime",
        # Logging and output - human-readable messages
        "logger.debug",
        "logger.info",
        "logger.warning",
        "logger.error",
        "logger.critical",
        "logger.exception",
        "logging.debug",
        "logging.info",
        "logging.warning",
        "logging.error",
        "print",
        "echo",
        "console.print",
        "console.log",
        "typer.echo",
        "click.echo",
        # Regex - pattern strings
        "re.sub",
        "re.match",
        "re.search",
        "re.compile",
        "re.findall",
        "re.split",
        # Environment variables
        "os.environ.get",
        "os.getenv",
        "environ.get",
        "getenv",
        # File operations
        "open",
        "Path",
        # Framework validators - must be strings matching field names
        "field_validator",
        "validator",
        "computed_field",
        # Type system - required Python syntax
        "TypeVar",
        "Generic",
        "cast",
        # Numeric - string representations of numbers
        "Decimal",
        "int",
        "float",
        # Exception constructors - error messages
        "ValueError",
        "TypeError",
        "KeyError",
        "AttributeError",
        "RuntimeError",
        "Exception",
        "raise",
        "APIException",
        "HTTPException",
        "ValidationError",
        # CLI frameworks - short flags, option names, prompts
        "typer.Option",
        "typer.Argument",
        "typer.confirm",
        "typer.prompt",
        "click.option",
        "click.argument",
        "click.confirm",
        "click.prompt",
        ".command",
        # HTTP/API clients - external protocol strings
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "httpx.get",
        "httpx.post",
        "client.get",
        "client.post",
        "client.put",
        "client.delete",
        "session.client",
        "session.resource",
        "_request",
        # AWS SDK - service names and API parameters
        "boto3.client",
        "boto3.resource",
        "generate_presigned_url",
        # AWS CDK - infrastructure as code (broad patterns)
        "s3.",
        "ec2.",
        "logs.",
        "route53.",
        "lambda_.",
        "_lambda.",
        "tasks.",
        "iam.",
        "dynamodb.",
        "sqs.",
        "sns.",
        "apigateway.",
        "cloudfront.",
        "cdk.",
        "sfn.",
        "acm.",
        "cloudwatch.",
        "secretsmanager.",
        "cr.",
        "pipes.",
        "rds.",
        "elasticache.",
        "from_lookup",
        "generate_resource_name",
        "CfnPipe",
        "CfnOutput",
        # FastAPI/Starlette routing
        "router.get",
        "router.post",
        "router.put",
        "router.delete",
        "router.patch",
        "app.get",
        "app.post",
        "app.put",
        "app.delete",
        "@app.",
        "@router.",
        # DynamoDB attribute access
        "Key",
        "Attr",
        "ConditionExpression",
        # Azure CLI - external tool invocation
        "az",
        # Database/ORM - schema definitions
        "op.add_column",
        "op.drop_column",
        "op.create_table",
        "op.alter_column",
        "sa.Column",
        "sa.PrimaryKeyConstraint",
        "sa.ForeignKeyConstraint",
        "Column",
        "relationship",
        "postgresql.ENUM",
        "ENUM",
        # Python built-ins
        "getattr",
        "setattr",
        "hasattr",
        "delattr",
        "isinstance",
        "issubclass",
        # Pydantic/dataclass fields
        "Field",
        "PrivateAttr",
        # UI frameworks - display text
        "QLabel",
        "QPushButton",
        "QMessageBox",
        "QCheckBox",
        "setWindowTitle",
        "setText",
        "setToolTip",
        "setPlaceholderText",
        "setStatusTip",
        "Static",
        "Label",
        "Button",
        # Table/grid display - formatting
        "table.add_row",
        "add_row",
        "add_column",
        "Table",
        "Panel",
        "Console",
        # Testing - mocks and fixtures
        "monkeypatch.setattr",
        "patch",
        "Mock",
        "MagicMock",
        "PropertyMock",
        # CSS/styling
        "setStyleSheet",
        "add_class",
        "remove_class",
        # JSON/serialization - output identifiers
        "_output",
        "json.dumps",
        "json.loads",
        # Health checks - framework pattern
        "register_health_check",
    )

    # Function names where second parameter (index 1) should be excluded
    # These are typically default values, not keys
    _EXCLUDE_PARAM_INDEX_1: tuple[str, ...] = (
        ".get",
        "os.environ.get",
        "environ.get",
        "getattr",
        "os.getenv",
        "getenv",
    )

    # String value patterns that indicate false positives
    _EXCLUDED_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
        # strftime format strings
        re.compile(r"^%[A-Za-z%-]+$"),
        # Single character delimiters
        re.compile(r"^[\n\t\r,;:|/\\.\-_]$"),
        # Empty string or whitespace only
        re.compile(r"^\s*$"),
        # HTTP methods (external protocol)
        re.compile(r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$"),
        # Numeric strings (should use Decimal or int)
        re.compile(r"^-?\d+\.?\d*$"),
        # Short CLI flags
        re.compile(r"^-[a-zA-Z]$"),
        # CSS/Rich markup
        re.compile(r"^\[/?[a-z]+\]"),
        # File modes (only multi-char modes to avoid false positives on single letters)
        re.compile(r"^[rwa][bt]\+?$|^[rwa]\+$"),
    )

    def should_include(
        self,
        function_name: str,
        param_index: int,
        unique_values: set[str],
    ) -> bool:
        """Determine if a function call pattern should be included in violations.

        Args:
            function_name: Name of the function being called
            param_index: Index of the parameter (0-based)
            unique_values: Set of unique string values passed to this parameter

        Returns:
            True if this pattern should generate a violation, False to filter it out
        """
        # Check function name patterns
        if self._is_excluded_function(function_name):
            return False

        # Check parameter position for specific functions
        if self._is_excluded_param_position(function_name, param_index):
            return False

        # Check if all values match excluded patterns
        if self._all_values_excluded(unique_values):
            return False

        return True

    def are_all_values_excluded(self, unique_values: set[str]) -> bool:
        """Check if all values match excluded patterns (numeric strings, delimiters, etc.).

        Public interface for value-based filtering used by violation generator.

        Args:
            unique_values: Set of unique string values to check

        Returns:
            True if all values match excluded patterns, False otherwise
        """
        return self._all_values_excluded(unique_values)

    def _is_excluded_function(self, function_name: str) -> bool:
        """Check if function name matches any excluded pattern."""
        func_lower = function_name.lower()
        for pattern in self._EXCLUDED_FUNCTION_PATTERNS:
            if pattern.lower() in func_lower or func_lower.endswith(pattern.lower()):
                return True
        return False

    def _is_excluded_param_position(self, function_name: str, param_index: int) -> bool:
        """Check if this parameter position should be excluded for this function."""
        if param_index != 1:
            return False

        func_lower = function_name.lower()
        for pattern in self._EXCLUDE_PARAM_INDEX_1:
            if pattern.lower() in func_lower or func_lower.endswith(pattern.lower()):
                return True
        return False

    def _all_values_excluded(self, unique_values: set[str]) -> bool:
        """Check if all values in the set match excluded patterns."""
        if not unique_values:
            return True
        return all(self._is_excluded_value(value) for value in unique_values)

    def _is_excluded_value(self, value: str) -> bool:
        """Check if a single value matches any excluded pattern."""
        for pattern in self._EXCLUDED_VALUE_PATTERNS:
            if pattern.match(value):
                return True
        return False
