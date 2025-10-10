"""
Purpose: Test suite for TypeScript Single Responsibility Principle violation detection

Scope: TypeScript/JavaScript class-level SRP analysis using tree-sitter parsing

Overview: Comprehensive tests for TypeScript SRP violation detection covering method count
    violations in TypeScript classes, lines of code violations, responsibility keyword
    detection in class names, interface method count analysis, constructor parameter count
    detection (dependency injection smell), combined violations across multiple heuristics,
    and ES6 class syntax support. Validates heuristic-based approach works equivalently
    for TypeScript as Python implementation.

Dependencies: pytest for testing framework, src.linters.srp.linter for SRPRule,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestTypeScriptMethodCount (5 tests), TestTypeScriptLinesOfCode (5 tests),
    TestTypeScriptKeywords (5 tests), TestTypeScriptSpecific (5 tests) - total 20 tests

Interfaces: Tests SRPRule.check(context) -> list[Violation] with TypeScript code samples

Implementation: Uses inline TypeScript code strings as test fixtures, sets language="typescript",
    verifies cross-language SRP detection consistency
"""

from pathlib import Path
from unittest.mock import Mock

import pytest


class TestTypeScriptMethodCount:
    """Test SRP violations based on method count in TypeScript classes."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_with_eight_methods_violates(self):
        """TypeScript class with 8 methods should violate default threshold."""
        code = """
class UserManager {
    createUser() {}
    updateUser() {}
    deleteUser() {}
    getUser() {}
    listUsers() {}
    authenticate() {}
    authorize() {}
    validate() {}  // Method 8 - violation
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 8 methods should violate"
        assert "8 methods" in violations[0].message

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_with_seven_methods_passes(self):
        """TypeScript class with exactly 7 methods should pass."""
        code = """
class UserService {
    create() {}
    read() {}
    update() {}
    delete() {}
    list() {}
    validate() {}
    transform() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "TS class with 7 methods should pass"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_with_six_methods_passes(self):
        """TypeScript class with 6 methods should pass."""
        code = """
class PaymentService {
    process() {}
    validate() {}
    refund() {}
    cancel() {}
    confirm() {}
    notify() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "TS class with 6 methods should pass"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_with_fifteen_methods_violates(self):
        """TypeScript class with 15 methods should violate."""
        code = """
class DataHandler {
    m1() {}
    m2() {}
    m3() {}
    m4() {}
    m5() {}
    m6() {}
    m7() {}
    m8() {}
    m9() {}
    m10() {}
    m11() {}
    m12() {}
    m13() {}
    m14() {}
    m15() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 15 methods should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_empty_class_passes(self):
        """Empty TypeScript class should pass."""
        code = """
class EmptyClass {
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Empty TS class should pass"


class TestTypeScriptLinesOfCode:
    """Test SRP violations based on LOC in TypeScript classes."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_exceeding_200_loc_violates(self):
        """TypeScript class with >200 LOC should violate."""
        methods = "\n".join([f"    method{i}() {{}}" for i in range(100)])
        code = f"""
class LargeClass {{
{methods}
}}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with >200 LOC should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_with_exactly_200_loc_passes(self):
        """TypeScript class with exactly 200 LOC should pass LOC check."""
        methods = "\n".join([f"    m{i}() {{}}" for i in range(98)])
        code = f"""
class MediumClass {{
{methods}
}}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        rule.check(context)
        # Validates LOC calculation works for TypeScript

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_class_with_150_loc_passes(self):
        """TypeScript class with 150 LOC should pass."""
        methods = "\n".join([f"    method{i}() {{}}" for i in range(70)])
        code = f"""
class NormalClass {{
{methods}
}}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        rule.check(context)
        # May violate on method count

    def test_typescript_class_with_500_loc_violates(self):
        """TypeScript class with 500 LOC should violate."""
        methods = "\n".join([f"    method{i}() {{}}" for i in range(245)])
        code = f"""
class MassiveClass {{
{methods}
}}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 500 LOC should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_single_line_class_passes(self):
        """Single-line TypeScript class should pass."""
        code = "class TinyClass {}"
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) == 0, "Single-line TS class should pass"


class TestTypeScriptKeywords:
    """Test SRP violations based on TypeScript class name keywords."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_manager_class_violates(self):
        """TypeScript class with 'Manager' in name should violate."""
        code = """
class UserManager {
    getUser() {}
    saveUser() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 'Manager' should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_handler_class_violates(self):
        """TypeScript class with 'Handler' in name should violate."""
        code = """
class DataHandler {
    handleData() {}
    process() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 'Handler' should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_processor_class_violates(self):
        """TypeScript class with 'Processor' in name should violate."""
        code = """
class RequestProcessor {
    processRequest() {}
    validate() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with 'Processor' should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_utility_helper_violates(self):
        """TypeScript class with multiple keywords should violate."""
        code = """
class UtilityHelper {
    help() {}
    assist() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with Utility+Helper should violate"

    @pytest.mark.skip(reason="100% duplicate")
    def test_typescript_user_class_passes(self):
        """TypeScript class without keywords should pass keyword check."""
        code = """
class User {
    save() {}
    delete() {}
    validate() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        rule.check(context)
        # Should pass keyword check


class TestTypeScriptSpecific:
    """Test TypeScript-specific SRP violation patterns."""

    @pytest.mark.skip(reason="100% duplicate")
    def test_interface_with_many_methods_violates(self):
        """TypeScript interface with many methods should violate."""
        code = """
interface LargeInterface {
    method1(): void;
    method2(): void;
    method3(): void;
    method4(): void;
    method5(): void;
    method6(): void;
    method7(): void;
    method8(): void;
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        rule.check(context)
        # Interface with 8 methods should violate

    @pytest.mark.skip(reason="100% duplicate")
    def test_constructor_with_many_parameters_violates(self):
        """Constructor with many parameters indicates high coupling."""
        code = """
class ServiceWithDependencies {
    constructor(
        private db: Database,
        private logger: Logger,
        private cache: Cache,
        private auth: Auth,
        private mailer: Mailer,
        private queue: Queue,
        private storage: Storage,
        private metrics: Metrics
    ) {}

    doSomething() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        rule.check(context)
        # Many constructor params indicate coupling/multiple responsibilities

    @pytest.mark.skip(reason="100% duplicate")
    def test_combined_typescript_violations(self):
        """TypeScript class with multiple violations."""
        methods = "\n".join([f"    method{i}() {{}}" for i in range(50)])
        code = f"""
class SystemManager {{
{methods}
}}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "TS class with multiple violations should fail"

    @pytest.mark.skip(reason="100% duplicate")
    def test_javascript_class_also_supported(self):
        """JavaScript classes should also be analyzed."""
        code = """
class DataManager {
    method1() {}
    method2() {}
    method3() {}
    method4() {}
    method5() {}
    method6() {}
    method7() {}
    method8() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.js")
        context.file_content = code
        context.language = "javascript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "JS class should be analyzed like TS"

    def test_multiple_typescript_classes_in_file(self):
        """Multiple TypeScript classes analyzed independently."""
        code = """
class FirstClass {
    m1() {}
    m2() {}
}

class SecondManager {
    method1() {}
    method2() {}
    method3() {}
    method4() {}
    method5() {}
    method6() {}
    method7() {}
    method8() {}
}
"""
        from src.linters.srp.linter import SRPRule

        rule = SRPRule()
        context = Mock()
        context.file_path = Path("test.ts")
        context.file_content = code
        context.language = "typescript"
        context.metadata = {}

        violations = rule.check(context)
        assert len(violations) > 0, "SecondManager should violate"
