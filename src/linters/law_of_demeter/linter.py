"""
Purpose: Main Law of Demeter linter rule implementation

Scope: LawOfDemeterRule class implementing MultiLanguageLintRule interface

Overview: Implements the Law of Demeter linter rule that detects excessive attribute/method
    chaining in Python code. Orchestrates configuration loading, Python AST analysis, chain
    classification through the 9-filter pipeline, and violation building. TypeScript support
    is stubbed for future implementation.

Dependencies: src.core.base, src.core.linter_utils, src.core.types, src.linter_config.ignore,
    config, python_analyzer, chain_classifier, violation_builder

Exports: LawOfDemeterRule

Interfaces: LawOfDemeterRule.check(context) -> list[Violation]

Implementation: Composition pattern with analyzer and classifier, AST-based analysis
"""

from typing import Any

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config, with_parsed_python
from src.core.types import Violation
from src.linter_config.ignore import get_ignore_parser

from .chain_classifier import classify_chain
from .config import LawOfDemeterConfig
from .filter_constants import TEST_FILE_PATTERNS
from .python_analyzer import extract_chains, extract_imports
from .violation_builder import DemeterViolationBuilder


class LawOfDemeterRule(MultiLanguageLintRule):
    """Detects Law of Demeter violations in attribute/method chains."""

    def __init__(self) -> None:
        """Initialize the Law of Demeter rule."""
        self._ignore_parser = get_ignore_parser()
        self._violation_builder = DemeterViolationBuilder(self.rule_id)

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

        Args:
            context: Lint context

        Returns:
            LawOfDemeterConfig instance
        """
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
        return with_parsed_python(
            context,
            self._violation_builder,
            lambda tree: self._analyze_python_tree(tree, config, context),
        )

    def _analyze_python_tree(
        self, tree: Any, config: LawOfDemeterConfig, context: BaseLintContext
    ) -> list[Violation]:
        """Analyze parsed Python AST for LoD violations."""
        filepath = str(context.file_path or "")
        if not config.check_test_files and _is_test_filepath(filepath):
            return []
        imports = extract_imports(tree)
        chains = extract_chains(tree, config.min_chain_depth)
        violating = _filter_violating(chains, imports, filepath)
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

    def _check_typescript(
        self, context: BaseLintContext, config: LawOfDemeterConfig
    ) -> list[Violation]:
        """Check TypeScript code for LoD violations (stub for PR 3).

        Args:
            context: Lint context with TypeScript file information
            config: Law of Demeter configuration

        Returns:
            Empty list (TypeScript not yet implemented)
        """
        return []

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored via inline directive.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be suppressed
        """
        return self._ignore_parser.should_ignore_violation(violation, context.file_content or "")


def _filter_violating(chains: list, imports: Any, filepath: str) -> list:
    """Return chains that are not classified as legitimate patterns."""
    return [(p, n) for p, n in chains if not classify_chain(p, imports, filepath)]


def _is_test_filepath(filepath: str) -> bool:
    """Check if filepath looks like a test file."""
    return any(pat in filepath for pat in TEST_FILE_PATTERNS)
