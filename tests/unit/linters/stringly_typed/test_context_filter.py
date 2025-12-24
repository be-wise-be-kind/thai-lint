"""
Purpose: Tests for stringly-typed context-aware false positive filtering

Scope: Test FunctionCallFilter class for blocklist-based filtering

Overview: Test suite validating the context-aware filtering of function call patterns
    to reduce false positives. Tests cover function name exclusion, parameter position
    exclusion, and value pattern exclusion.

Dependencies: pytest, src.linters.stringly_typed.context_filter

Exports: Test functions for context filter validation

Interfaces: Direct testing of FunctionCallFilter class

Implementation: TDD approach with isolated test cases
"""

import pytest

from src.linters.stringly_typed.context_filter import FunctionCallFilter


class TestFunctionNameExclusion:
    """Tests for function name pattern exclusion."""

    @pytest.fixture
    def filter(self):
        """Create filter instance."""
        return FunctionCallFilter()

    def test_excludes_dict_get(self, filter):
        """Test that dict.get() is excluded."""
        assert not filter.should_include("obj.get", 0, {"key1", "key2"})

    def test_excludes_dict_set(self, filter):
        """Test that dict.set() is excluded."""
        assert not filter.should_include("obj.set", 0, {"key1", "key2"})

    def test_excludes_dict_pop(self, filter):
        """Test that dict.pop() is excluded."""
        assert not filter.should_include("config.pop", 0, {"key1", "key2"})

    def test_excludes_string_split(self, filter):
        """Test that str.split() is excluded."""
        assert not filter.should_include("text.split", 0, {",", ";"})

    def test_excludes_string_replace(self, filter):
        """Test that str.replace() is excluded."""
        assert not filter.should_include("value.replace", 0, {"old", "new"})

    def test_excludes_logger_info(self, filter):
        """Test that logger.info() is excluded."""
        assert not filter.should_include("logger.info", 0, {"message1", "message2"})

    def test_excludes_logger_warning(self, filter):
        """Test that logger.warning() is excluded."""
        assert not filter.should_include("logger.warning", 0, {"warn1", "warn2"})

    def test_excludes_print(self, filter):
        """Test that print() is excluded."""
        assert not filter.should_include("print", 0, {"output1", "output2"})

    def test_excludes_typer_option(self, filter):
        """Test that typer.Option() is excluded."""
        assert not filter.should_include("typer.Option", 0, {"--flag", "--verbose"})

    def test_excludes_value_error(self, filter):
        """Test that ValueError() is excluded."""
        assert not filter.should_include("ValueError", 0, {"error1", "error2"})

    def test_excludes_boto3_client(self, filter):
        """Test that boto3.client() is excluded."""
        assert not filter.should_include("boto3.client", 0, {"s3", "dynamodb"})

    def test_excludes_getattr(self, filter):
        """Test that getattr() is excluded."""
        assert not filter.should_include("getattr", 0, {"attr1", "attr2"})

    def test_excludes_router_get(self, filter):
        """Test that router.get() is excluded."""
        assert not filter.should_include("router.get", 0, {"/path1", "/path2"})

    def test_excludes_s3_bucket(self, filter):
        """Test that s3.Bucket() is excluded (AWS CDK)."""
        assert not filter.should_include("s3.Bucket", 0, {"bucket1", "bucket2"})

    def test_includes_custom_function(self, filter):
        """Test that custom functions are included."""
        assert filter.should_include("process_status", 0, {"active", "inactive"})

    def test_includes_domain_function(self, filter):
        """Test that domain-specific functions are included."""
        assert filter.should_include("set_environment", 0, {"production", "staging"})


class TestParameterPositionExclusion:
    """Tests for parameter position-based exclusion."""

    @pytest.fixture
    def filter(self):
        """Create filter instance."""
        return FunctionCallFilter()

    def test_excludes_get_default_value(self, filter):
        """Test that dict.get() default value (param 1) is excluded."""
        assert not filter.should_include("config.get", 1, {"default1", "default2"})

    def test_includes_get_key(self, filter):
        """Test that dict.get() key (param 0) is excluded for other reasons."""
        # Note: .get is excluded entirely, so this returns False
        assert not filter.should_include("config.get", 0, {"key1", "key2"})

    def test_excludes_getattr_default(self, filter):
        """Test that getattr() default value (param 1) is excluded."""
        assert not filter.should_include("getattr", 1, {"default1", "default2"})

    def test_excludes_environ_get_default(self, filter):
        """Test that os.environ.get() default (param 1) is excluded."""
        assert not filter.should_include("os.environ.get", 1, {"default1", "default2"})


class TestValuePatternExclusion:
    """Tests for value pattern-based exclusion."""

    @pytest.fixture
    def filter(self):
        """Create filter instance."""
        return FunctionCallFilter()

    def test_excludes_numeric_strings(self, filter):
        """Test that all-numeric string sets are excluded."""
        assert not filter.should_include("func", 0, {"1", "2", "3"})

    def test_excludes_single_char_delimiters(self, filter):
        """Test that single character delimiters are excluded."""
        assert not filter.should_include("func", 0, {",", ";", ":"})

    def test_excludes_http_methods(self, filter):
        """Test that HTTP methods are excluded."""
        assert not filter.should_include("func", 0, {"GET", "POST", "PUT"})

    def test_excludes_strftime_formats(self, filter):
        """Test that strftime format strings are excluded."""
        assert not filter.should_include("func", 0, {"%Y", "%m", "%d"})

    def test_excludes_file_modes(self, filter):
        """Test that file mode strings are excluded."""
        # Only multi-char modes are excluded to avoid false positives
        assert not filter.should_include("func", 0, {"rb", "wb", "r+"})

    def test_includes_mixed_values(self, filter):
        """Test that mixed value sets are included."""
        # Not all values are excluded patterns, so should be included
        assert filter.should_include("func", 0, {"active", "inactive"})

    def test_includes_domain_values(self, filter):
        """Test that domain-specific values are included."""
        assert filter.should_include("func", 0, {"pending", "approved", "rejected"})


class TestCombinedFiltering:
    """Tests for combined filtering scenarios."""

    @pytest.fixture
    def filter(self):
        """Create filter instance."""
        return FunctionCallFilter()

    def test_valid_stringly_typed_pattern(self, filter):
        """Test that valid stringly-typed patterns are included."""
        # Custom function with domain values should be included
        assert filter.should_include("validate_status", 0, {"active", "pending", "closed"})

    def test_excludes_framework_pattern(self, filter):
        """Test that framework patterns are excluded."""
        # Pydantic field_validator should be excluded
        assert not filter.should_include("field_validator", 0, {"field1", "field2"})

    def test_excludes_aws_cdk_pattern(self, filter):
        """Test that AWS CDK patterns are excluded."""
        assert not filter.should_include("logs.LogGroup", 0, {"group1", "group2"})

    def test_case_insensitive_matching(self, filter):
        """Test that function name matching is case-insensitive."""
        assert not filter.should_include("Logger.INFO", 0, {"msg1", "msg2"})

    def test_empty_values_excluded(self, filter):
        """Test that empty value sets are excluded."""
        assert not filter.should_include("func", 0, set())
