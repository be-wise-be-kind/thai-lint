"""
Purpose: Unit tests for conditional verbose logging pattern detection

Scope: Testing detection of if verbose: logger.*() anti-patterns in Python code

Overview: Comprehensive test suite for the ConditionalVerboseRule covering detection of various
    verbose condition patterns (simple names, attribute access, dict access, method calls) and
    logger call patterns. Validates that the linter correctly identifies conditional verbose
    logging patterns that should use log level configuration instead. Tests include edge cases,
    false positive avoidance, and ignore directive support.

Dependencies: pytest, pathlib.Path, unittest.mock.Mock,
    src.linters.print_statements.conditional_verbose_rule.ConditionalVerboseRule

Exports: TestBasicDetection, TestVerboseConditionPatterns, TestLoggerCallPatterns,
    TestIgnoreDirectives, TestEdgeCases test classes

Interfaces: Various test methods validating ConditionalVerboseRule.check(context)

Implementation: Uses Mock objects for context creation, inline Python code strings as test fixtures,
    validates violation line numbers and messages
"""

from pathlib import Path
from unittest.mock import Mock


class TestBasicDetection:
    """Test basic conditional verbose logging pattern detection."""

    def test_detects_simple_verbose_logger(self):
        """Should flag if verbose: logger.debug() pattern."""
        code = """
def process(verbose=False):
    if verbose:
        logger.debug("Processing started")
    do_work()
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert "logger.debug" in violations[0].message
        assert violations[0].rule_id == "improper-logging.conditional-verbose"

    def test_detects_multiple_logger_calls_in_block(self):
        """Should flag multiple logger calls in same verbose block."""
        code = """
def process(verbose=False):
    if verbose:
        logger.debug("Start")
        logger.info("Middle")
        logger.debug("End")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 3

    def test_no_violation_for_non_verbose_condition(self):
        """Should not flag logging under non-verbose conditions."""
        code = """
def process(enabled=False):
    if enabled:
        logger.debug("Processing")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0


class TestVerboseConditionPatterns:
    """Test various verbose condition patterns."""

    def test_detects_self_verbose(self):
        """Should flag if self.verbose: logger.*() pattern."""
        code = """
class Worker:
    def process(self):
        if self.verbose:
            logger.info("Processing")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("worker.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_config_verbose(self):
        """Should flag if config.verbose: logger.*() pattern."""
        code = """
def run(config):
    if config.verbose:
        logger.debug("Config loaded")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("runner.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_ctx_obj_subscript(self):
        """Should flag if ctx.obj["verbose"]: logger.*() pattern."""
        code = """
@click.command()
@click.pass_context
def cli(ctx):
    if ctx.obj["verbose"]:
        logger.info("Verbose mode")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("cli.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_ctx_obj_get(self):
        """Should flag if ctx.obj.get("verbose"): logger.*() pattern."""
        code = """
@click.command()
@click.pass_context
def cli(ctx):
    if ctx.obj.get("verbose"):
        logger.debug("Verbose enabled")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("cli.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_debug_variable(self):
        """Should flag if debug: logger.*() pattern."""
        code = """
def process(debug=False):
    if debug:
        logger.debug("Debug info")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1


class TestLoggerCallPatterns:
    """Test detection of various logger method calls."""

    def test_detects_logger_debug(self):
        """Should flag logger.debug() in verbose block."""
        code = """
if verbose:
    logger.debug("Debug message")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_logger_info(self):
        """Should flag logger.info() in verbose block."""
        code = """
if verbose:
    logger.info("Info message")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_logger_warning(self):
        """Should flag logger.warning() in verbose block."""
        code = """
if verbose:
    logger.warning("Warning message")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_logger_error(self):
        """Should flag logger.error() in verbose block."""
        code = """
if verbose:
    logger.error("Error message")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_detects_logging_module_calls(self):
        """Should flag logging.debug() in verbose block."""
        code = """
if verbose:
    logging.debug("Debug via module")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1


class TestIgnoreDirectives:
    """Test ignore directive support."""

    def test_respects_thailint_ignore(self):
        """Should respect thailint: ignore directive."""
        code = """
if verbose:
    logger.debug("flagged")
if verbose:
    logger.info("ignored")  # thailint: ignore
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1

    def test_respects_noqa(self):
        """Should respect noqa directive."""
        code = """
if verbose:
    logger.debug("flagged")
if verbose:
    logger.info("ignored")  # noqa
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_handles_empty_file(self):
        """Should handle empty file gracefully."""
        code = ""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("empty.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_handles_syntax_error(self):
        """Should handle files with syntax errors gracefully."""
        code = "if verbose\n    logger.debug("
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("broken.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0  # Graceful handling, no crash

    def test_ignores_non_python_files(self):
        """Should not flag patterns in non-Python files."""
        code = """
if (verbose) {
    logger.debug("test");
}
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.ts")
        context.file_content = code
        context.language = "typescript"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_no_false_positive_for_logging_outside_verbose(self):
        """Should not flag logging calls outside verbose conditions."""
        code = """
def process():
    logger.debug("Always logged")
    if condition:
        logger.info("Conditional but not verbose")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 0

    def test_violation_has_suggestion(self):
        """Should include helpful suggestion in violation."""
        code = """
if verbose:
    logger.debug("test")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert len(violations) == 1
        assert (
            "setLevel" in violations[0].suggestion.lower()
            or "logging level" in violations[0].suggestion.lower()
        )


class TestViolationDetails:
    """Test that violations contain appropriate details."""

    def test_violation_has_correct_rule_id(self):
        """Should set correct rule_id on violations."""
        code = """
if verbose:
    logger.debug("test")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].rule_id == "improper-logging.conditional-verbose"

    def test_violation_has_correct_line_number(self):
        """Should set correct line number on violations."""
        code = """
x = 1
y = 2
if verbose:
    logger.debug("on line 5")
"""
        from src.linters.print_statements.conditional_verbose_rule import ConditionalVerboseRule

        rule = ConditionalVerboseRule()
        context = Mock()
        context.file_path = Path("app.py")
        context.file_content = code
        context.language = "python"

        violations = rule.check(context)
        assert violations[0].line == 5
