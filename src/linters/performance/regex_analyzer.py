"""
Purpose: Python AST-based regex compilation in loop detector

Scope: Detect repeated regex compilation patterns using re.method() in for/while loops

Overview: Analyzes Python code to detect regex function calls inside loops using AST traversal.
    Detects calls to re.match(), re.search(), re.sub(), re.findall(), re.split(), and
    re.fullmatch() inside for/while loops. Tracks variables assigned from re.compile() to
    avoid false positives when compiled patterns are correctly used. Supports import
    variations including 'import re', 'from re import match', and 'import re as alias'.

Dependencies: ast module for Python parsing

Exports: PythonRegexInLoopAnalyzer class with find_violations method

Interfaces: find_violations(tree: ast.AST) -> list[RegexInLoopViolation]

Implementation: AST visitor pattern detecting regex calls in loop contexts with compiled
    pattern tracking

Suppressions:
    - srp.violation: Class uses many small methods to achieve A-grade cyclomatic complexity.
      This is an intentional tradeoff - low complexity is prioritized over strict SRP adherence.
"""

import ast
from dataclasses import dataclass

# Regex module functions that compile patterns on each call
RE_FUNCTIONS = frozenset(
    {
        "match",
        "search",
        "sub",
        "subn",
        "findall",
        "finditer",
        "split",
        "fullmatch",
    }
)


@dataclass
class RegexInLoopViolation:
    """Represents a regex-in-loop violation found in code."""

    method_name: str
    line_number: int
    column: int
    loop_type: str  # 'for' or 'while'


# thailint: ignore-next-line[srp.violation] Uses small focused methods to reduce complexity
class PythonRegexInLoopAnalyzer:
    """Detects regex function calls in loops for Python code."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self._compiled_patterns: set[str] = set()
        self._re_aliases: set[str] = set()  # Module aliases like 'regex' from 'import re as regex'
        self._direct_imports: set[str] = set()  # Direct imports like 'match' from 'from re import'

    def find_violations(self, tree: ast.AST) -> list[RegexInLoopViolation]:
        """Find all regex-in-loop violations.

        Args:
            tree: Python AST to analyze

        Returns:
            List of violations found
        """
        violations: list[RegexInLoopViolation] = []
        self._compiled_patterns = set()
        self._re_aliases = {"re"}  # Default 're' is always valid
        self._direct_imports = set()

        # First pass: identify imports and compiled patterns
        self._identify_imports(tree)
        self._identify_compiled_patterns(tree)

        # Second pass: find regex calls in loops
        self._find_regex_in_loops(tree, violations)

        return violations

    def _identify_imports(self, tree: ast.AST) -> None:
        """Identify re module imports and aliases.

        Args:
            tree: AST to analyze
        """
        for node in ast.walk(tree):
            self._process_import_node(node)

    def _process_import_node(self, node: ast.AST) -> None:
        """Process a single import node."""
        if isinstance(node, ast.Import):
            self._process_regular_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._process_from_import(node)

    def _process_regular_import(self, node: ast.Import) -> None:
        """Process 'import re' or 'import re as regex' style imports."""
        for alias in node.names:
            if alias.name == "re":
                # import re as regex -> add 'regex' as valid alias
                self._re_aliases.add(alias.asname or "re")

    def _process_from_import(self, node: ast.ImportFrom) -> None:
        """Process 'from re import match' style imports."""
        if node.module != "re":
            return
        for alias in node.names:
            self._add_direct_import_if_re_function(alias)

    def _add_direct_import_if_re_function(self, alias: ast.alias) -> None:
        """Add alias to direct imports if it's a regex function."""
        if alias.name not in RE_FUNCTIONS:
            return
        imported_name = alias.asname or alias.name
        self._direct_imports.add(imported_name)

    def _identify_compiled_patterns(self, tree: ast.AST) -> None:
        """Identify variables assigned from re.compile().

        Args:
            tree: AST to analyze
        """
        for node in ast.walk(tree):
            self._check_for_compile_assignment(node)

    def _check_for_compile_assignment(self, node: ast.AST) -> None:
        """Check if node is an assignment from re.compile()."""
        if isinstance(node, ast.Assign):
            self._process_compile_assign(node)
        elif isinstance(node, ast.AnnAssign):
            self._process_compile_ann_assign(node)

    def _process_compile_assign(self, node: ast.Assign) -> None:
        """Process simple assignment for re.compile()."""
        if not self._is_re_compile_call(node.value):
            return
        for target in node.targets:
            self._add_compiled_pattern_if_name(target)

    def _add_compiled_pattern_if_name(self, target: ast.expr) -> None:
        """Add target to compiled patterns if it's a Name node."""
        if isinstance(target, ast.Name):
            self._compiled_patterns.add(target.id)

    def _process_compile_ann_assign(self, node: ast.AnnAssign) -> None:
        """Process annotated assignment for re.compile()."""
        if node.value and self._is_re_compile_call(node.value):
            if isinstance(node.target, ast.Name):
                self._compiled_patterns.add(node.target.id)

    def _is_re_compile_call(self, node: ast.expr) -> bool:
        """Check if expression is a call to re.compile().

        Args:
            node: Expression node to check

        Returns:
            True if this is a re.compile() call
        """
        if not isinstance(node, ast.Call):
            return False

        func = node.func

        # re.compile() style
        if isinstance(func, ast.Attribute):
            return self._is_module_compile(func)

        return False

    def _is_module_compile(self, func: ast.Attribute) -> bool:
        """Check if attribute access is module.compile()."""
        if func.attr != "compile":
            return False
        if isinstance(func.value, ast.Name):
            return func.value.id in self._re_aliases
        return False

    def _find_regex_in_loops(
        self,
        node: ast.AST,
        violations: list[RegexInLoopViolation],
        in_loop: str | None = None,
    ) -> None:
        """Recursively find regex calls in loops.

        Args:
            node: Current AST node
            violations: List to append violations to
            in_loop: Type of enclosing loop ('for' or 'while'), None if not in loop
        """
        current_loop = self._get_loop_type(node) or in_loop
        self._check_for_regex_call(node, violations, current_loop)

        for child in ast.iter_child_nodes(node):
            self._find_regex_in_loops(child, violations, current_loop)

    def _get_loop_type(self, node: ast.AST) -> str | None:
        """Get the loop type if node is a loop, else None."""
        if isinstance(node, ast.For):
            return "for"
        if isinstance(node, ast.While):
            return "while"
        return None

    def _check_for_regex_call(
        self,
        node: ast.AST,
        violations: list[RegexInLoopViolation],
        loop_type: str | None,
    ) -> None:
        """Check if node is a regex call in a loop and add violation if so."""
        if not loop_type or not isinstance(node, ast.Call):
            return

        violation = self._create_violation_if_regex_call(node, loop_type)
        if violation:
            violations.append(violation)

    def _create_violation_if_regex_call(
        self,
        node: ast.Call,
        loop_type: str,
    ) -> RegexInLoopViolation | None:
        """Create violation if this is an uncompiled regex call.

        Args:
            node: Call node
            loop_type: Type of enclosing loop

        Returns:
            Violation if uncompiled regex call, None otherwise
        """
        method_name = self._get_regex_method_name(node)
        if method_name:
            return RegexInLoopViolation(
                method_name=method_name,
                line_number=node.lineno,
                column=node.col_offset,
                loop_type=loop_type,
            )
        return None

    def _get_regex_method_name(self, node: ast.Call) -> str | None:
        """Get regex method name if this is an uncompiled regex call.

        Args:
            node: Call node to check

        Returns:
            Method name (e.g., 'match', 'search') if uncompiled regex call, None otherwise
        """
        func = node.func

        # re.match() style or regex.match() style
        if isinstance(func, ast.Attribute):
            return self._check_module_regex_call(func)

        # Direct import: match() from 'from re import match'
        if isinstance(func, ast.Name):
            return self._check_direct_import_call(func)

        return None

    def _check_module_regex_call(self, func: ast.Attribute) -> str | None:
        """Check if this is re.method() style call.

        Args:
            func: Attribute node (e.g., re.match)

        Returns:
            Method name if uncompiled regex call, None otherwise
        """
        method = func.attr

        # Not a regex function we care about
        if method not in RE_FUNCTIONS:
            return None

        # Check if it's called on a compiled pattern variable
        if isinstance(func.value, ast.Name):
            caller = func.value.id

            # Called on compiled pattern: pattern.match() -> OK
            if caller in self._compiled_patterns:
                return None

            # Called on re module or alias: re.match() -> Violation
            if caller in self._re_aliases:
                return f"re.{method}"

        return None

    def _check_direct_import_call(self, func: ast.Name) -> str | None:
        """Check if this is a directly imported regex function call.

        Args:
            func: Name node (e.g., match)

        Returns:
            Method name if directly imported regex function, None otherwise
        """
        if func.id in self._direct_imports:
            return func.id
        return None
