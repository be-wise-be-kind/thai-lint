"""
Purpose: Main Law of Demeter linter rule implementation

Scope: LawOfDemeterRule class implementing MultiLanguageLintRule interface

Overview: Implements the Law of Demeter linter rule that detects excessive attribute/method
    chaining in Python and TypeScript code. Orchestrates configuration loading, AST analysis
    (Python stdlib ast, TypeScript tree-sitter), chain classification through the 9-filter
    pipeline, and violation building. TypeScript analysis uses TypeScriptDemeterAnalyzer for
    tree-sitter-based chain extraction with optional chaining support.

Dependencies: src.core.base, src.core.linter_utils, src.core.types, src.linter_config.ignore,
    config, python_analyzer, typescript_analyzer, chain_classifier, violation_builder

Exports: LawOfDemeterRule

Interfaces: LawOfDemeterRule.check(context) -> list[Violation]

Implementation: Composition pattern with analyzer and classifier, AST-based analysis,
    optional chaining exclusion for TypeScript
"""

from typing import Any

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config, parse_python_ast
from src.core.types import Violation
from src.linter_config.ignore import get_ignore_parser

from .chain_classifier import classify_chain
from .config import LawOfDemeterConfig
from .python_analyzer import extract_chains, extract_imports
from .typescript_analyzer import TypeScriptDemeterAnalyzer, has_optional_chain
from .violation_builder import DemeterViolationBuilder


class LawOfDemeterRule(MultiLanguageLintRule):
    """Detects Law of Demeter violations in attribute/method chains."""

    def __init__(self) -> None:
        """Initialize the Law of Demeter rule."""
        self._ignore_parser = get_ignore_parser()
        self._violation_builder = DemeterViolationBuilder(self.rule_id)
        self._ts_analyzer = TypeScriptDemeterAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "law-of-demeter.chain-depth"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Law of Demeter Chain Depth"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Objects should only talk to their immediate friends, not reach through intermediaries"
        )

    def _load_config(self, context: BaseLintContext) -> LawOfDemeterConfig:
        """Load configuration from context.

        Tries underscore key first (normalized from YAML), then hyphenated
        key (for direct metadata injection in tests).

        Args:
            context: Lint context

        Returns:
            LawOfDemeterConfig instance
        """
        metadata = getattr(context, "metadata", {}) or {}
        if "law_of_demeter" in metadata:
            return load_linter_config(context, "law_of_demeter", LawOfDemeterConfig)
        return load_linter_config(context, "law-of-demeter", LawOfDemeterConfig)

    def _check_python(
        self, context: BaseLintContext, config: LawOfDemeterConfig
    ) -> list[Violation]:
        """Check Python code for LoD violations.

        Args:
            context: Lint context with Python file information
            config: Law of Demeter configuration

        Returns:
            List of violations found
        """
        tree, _errors = parse_python_ast(context, self._violation_builder)
        if tree is None:
            return []
        return self._analyze_python_tree(tree, config, context)

    def _analyze_python_tree(
        self, tree: Any, config: LawOfDemeterConfig, context: BaseLintContext
    ) -> list[Violation]:
        """Analyze parsed Python AST for LoD violations."""
        filepath = str(context.file_path or "")
        if not config.check_test_files and _is_test_filepath(filepath):
            return []
        py_imports = extract_imports(tree)
        chains = extract_chains(tree, config.min_chain_depth)
        violating = _filter_violating(chains, py_imports, filepath)
        return self._build_unignored(violating, context)

    def _check_typescript(
        self, context: BaseLintContext, config: LawOfDemeterConfig
    ) -> list[Violation]:
        """Check TypeScript code for LoD violations.

        Args:
            context: Lint context with TypeScript file information
            config: Law of Demeter configuration

        Returns:
            List of violations found
        """
        filepath = str(context.file_path or "")
        if not config.check_test_files and _is_test_filepath(filepath):
            return []
        return self._analyze_typescript_code(context, config, filepath)

    def _analyze_typescript_code(
        self, context: BaseLintContext, config: LawOfDemeterConfig, filepath: str
    ) -> list[Violation]:
        """Analyze TypeScript code for LoD violations."""
        root = self._ts_analyzer.parse_typescript(context.file_content or "")
        if root is None:
            return []

        ts_imports = self._ts_analyzer.extract_imports(root)
        chains = self._ts_analyzer.extract_chains(root, config.min_chain_depth)
        non_optional = _exclude_optional_chains(chains)
        violating = _filter_violating(non_optional, ts_imports, filepath)
        return self._build_unignored(violating, context)

    def _build_unignored(
        self,
        chain_pairs: list,
        context: BaseLintContext,
    ) -> list[Violation]:
        """Build violations from chain pairs, filtering ignored ones."""
        raw = [
            self._violation_builder.create_chain_violation(node, parts, context)
            for parts, node in chain_pairs
        ]
        return [v for v in raw if not self._should_ignore(v, context)]

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored via inline directive.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be suppressed
        """
        return self._ignore_parser.should_ignore_violation(violation, context.file_content or "")


def _exclude_optional_chains(chains: list) -> list:
    """Remove chains that use optional chaining."""
    return [(p, n) for p, n in chains if not has_optional_chain(p)]


def _filter_violating(chains: list, imports: Any, filepath: str) -> list:
    """Return chains that are not classified as legitimate patterns."""
    return [(p, n) for p, n in chains if not classify_chain(p, imports, filepath)]


def _is_test_filepath(filepath: str) -> bool:
    """Check if filepath looks like a test file.

    Checks filename for test_ prefix, _test.py suffix, and conftest.
    Checks directory components for tests/ and testing/ paths.
    """
    filename = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
    return _is_test_filename(filename) or _is_test_directory(filepath)


def _is_test_filename(filename: str) -> bool:
    """Check if filename matches test file patterns."""
    return filename.startswith("test_") or filename.endswith("_test.py") or "conftest" in filename


_TEST_DIRECTORY_MARKERS = frozenset(
    {
        "tests",
        "testing",
        "test",
        "fixtures",
        "test_data",
        "testdata",
    }
)


def _is_test_directory(filepath: str) -> bool:
    """Check if filepath is under a test or fixture directory."""
    parts = filepath.replace("\\", "/").split("/")
    return any(p in _TEST_DIRECTORY_MARKERS for p in parts)
