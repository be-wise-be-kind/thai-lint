"""
Purpose: CollectionPipelineRule implementation for detecting loop filtering anti-patterns

Scope: Main rule class implementing BaseLintRule interface for collection-pipeline detection

Overview: Implements the BaseLintRule interface to detect for loops with embedded
    filtering logic that could be refactored to collection pipelines. Detects patterns
    like 'for x in iter: if not cond: continue; action(x)' which can be refactored to
    use generator expressions or filter(). Based on Martin Fowler's refactoring pattern.
    Integrates with thai-lint CLI and supports text, JSON, and SARIF output formats.

Dependencies: BaseLintRule, BaseLintContext, Violation, PipelinePatternDetector, CollectionPipelineConfig

Exports: CollectionPipelineRule class

Interfaces: CollectionPipelineRule.check(context) -> list[Violation], rule metadata properties

Implementation: Uses PipelinePatternDetector for AST analysis, composition pattern with config loading
"""

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Severity, Violation

from .config import CollectionPipelineConfig
from .detector import PatternMatch, PipelinePatternDetector


class CollectionPipelineRule(BaseLintRule):
    """Detects for loops with embedded filtering that could use collection pipelines."""

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "collection-pipeline.embedded-filter"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Embedded Loop Filtering"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "For loops with embedded if/continue filtering patterns should be "
            "refactored to use collection pipelines (generator expressions, filter())"
        )

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for collection pipeline anti-patterns.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if context.language != "python":
            return []

        content = context.file_content
        if not content:
            return []

        config = load_linter_config(context, "collection_pipeline", CollectionPipelineConfig)
        if not config.enabled:
            return []

        return self._analyze_python(context, config)

    def _analyze_python(
        self, context: BaseLintContext, config: CollectionPipelineConfig
    ) -> list[Violation]:
        """Analyze Python code for collection pipeline patterns.

        Args:
            context: Lint context with Python file information
            config: Collection pipeline configuration

        Returns:
            List of violations found
        """
        detector = PipelinePatternDetector(context.file_content or "")
        matches = detector.detect_patterns()

        violations: list[Violation] = []
        for match in matches:
            if len(match.conditions) >= config.min_continues:
                violation = self._create_violation(match, context)
                violations.append(violation)

        return violations

    def _create_violation(self, match: PatternMatch, context: BaseLintContext) -> Violation:
        """Create a Violation from a PatternMatch.

        Args:
            match: Detected pattern match
            context: Lint context

        Returns:
            Violation object for the detected pattern
        """
        message = self._build_message(match)
        file_path = str(context.file_path) if context.file_path else "unknown"

        return Violation(
            rule_id=self.rule_id,
            file_path=file_path,
            line=match.line_number,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=match.suggestion,
        )

    def _build_message(self, match: PatternMatch) -> str:
        """Build violation message.

        Args:
            match: Detected pattern match

        Returns:
            Human-readable message describing the violation
        """
        num_conditions = len(match.conditions)
        if num_conditions == 1:
            return (
                f"For loop over '{match.iterable}' has embedded filtering. "
                f"Consider using a generator expression."
            )
        return (
            f"For loop over '{match.iterable}' has {num_conditions} filter conditions. "
            f"Consider combining into a collection pipeline."
        )
