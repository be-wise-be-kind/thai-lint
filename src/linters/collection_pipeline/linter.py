"""
Purpose: CollectionPipelineRule implementation for detecting loop filtering anti-patterns

Scope: Main rule class implementing BaseLintRule interface for collection-pipeline detection

Overview: Implements the BaseLintRule interface to detect for loops with embedded
    filtering logic that could be refactored to collection pipelines. Detects patterns
    like 'for x in iter: if not cond: continue; action(x)' which can be refactored to
    use generator expressions or filter(). Based on Martin Fowler's refactoring pattern.
    Integrates with thai-lint CLI and supports text, JSON, and SARIF output formats.
    Supports comprehensive 5-level ignore system including project-level patterns,
    linter-specific ignore patterns, file-level directives, line-level directives,
    and block-level directives via IgnoreDirectiveParser.

Dependencies: BaseLintRule, BaseLintContext, Violation, PipelinePatternDetector,
    CollectionPipelineConfig, IgnoreDirectiveParser

Exports: CollectionPipelineRule class

Interfaces: CollectionPipelineRule.check(context) -> list[Violation], rule metadata properties

Implementation: Uses PipelinePatternDetector for AST analysis, composition pattern with
    config loading and comprehensive ignore checking via IgnoreDirectiveParser
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Severity, Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import CollectionPipelineConfig
from .detector import PatternMatch, PipelinePatternDetector


class CollectionPipelineRule(BaseLintRule):  # thailint: ignore[srp,dry]
    """Detects for loops with embedded filtering that could use collection pipelines."""

    def __init__(self) -> None:
        """Initialize the rule with ignore parser."""
        self._ignore_parser = IgnoreDirectiveParser()

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
        if not self._should_analyze(context):
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []

        if self._is_file_ignored(context, config):
            return []

        if self._has_file_level_ignore(context):
            return []

        return self._analyze_python(context, config)

    def _should_analyze(self, context: BaseLintContext) -> bool:
        """Check if context should be analyzed.

        Args:
            context: Lint context

        Returns:
            True if should analyze
        """
        return context.language == "python" and context.file_content is not None

    def _get_config_dict(self, context: BaseLintContext) -> dict | None:
        """Get configuration dictionary from context.

        Args:
            context: Lint context

        Returns:
            Config dict or None
        """
        if hasattr(context, "config") and context.config is not None:
            return context.config
        if hasattr(context, "metadata") and context.metadata is not None:
            return context.metadata
        return None

    def _load_config(self, context: BaseLintContext) -> CollectionPipelineConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            CollectionPipelineConfig instance
        """
        config_dict = self._get_config_dict(context)
        if config_dict is None or not isinstance(config_dict, dict):
            return CollectionPipelineConfig()

        # Check for collection_pipeline or collection-pipeline specific config
        linter_config = config_dict.get(
            "collection_pipeline", config_dict.get("collection-pipeline", config_dict)
        )
        return CollectionPipelineConfig.from_dict(linter_config)

    def _is_file_ignored(self, context: BaseLintContext, config: CollectionPipelineConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: Configuration

        Returns:
            True if file should be ignored
        """
        if not config.ignore:
            return False

        if not context.file_path:
            return False

        file_path = Path(context.file_path)
        for pattern in config.ignore:
            if self._matches_pattern(file_path, pattern):
                return True
        return False

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file path matches a glob pattern.

        Args:
            file_path: Path to check
            pattern: Glob pattern

        Returns:
            True if path matches pattern
        """
        if file_path.match(pattern):
            return True
        if pattern in str(file_path):
            return True
        return False

    def _has_file_level_ignore(self, context: BaseLintContext) -> bool:
        """Check if file has file-level ignore directive.

        Args:
            context: Lint context

        Returns:
            True if file should be ignored at file level
        """
        if not context.file_content:
            return False

        # Check first 10 lines for ignore-file directive
        lines = context.file_content.splitlines()[:10]
        for line in lines:
            if self._is_file_ignore_directive(line):
                return True
        return False

    def _is_file_ignore_directive(self, line: str) -> bool:
        """Check if line is a file-level ignore directive.

        Args:
            line: Line to check

        Returns:
            True if line has file-level ignore for this rule
        """
        line_lower = line.lower()
        if "thailint: ignore-file" not in line_lower:
            return False

        # Check for general ignore-file (no rule specified)
        if "ignore-file[" not in line_lower:
            return True

        # Check for rule-specific ignore
        return self._matches_rule_ignore(line_lower, "ignore-file")

    def _matches_rule_ignore(self, line: str, directive: str) -> bool:
        """Check if line matches rule-specific ignore.

        Args:
            line: Line to check (lowercase)
            directive: Directive name (ignore-file or ignore)

        Returns:
            True if ignore applies to this rule
        """
        import re

        pattern = rf"{directive}\[([^\]]+)\]"
        match = re.search(pattern, line)
        if not match:
            return False

        rules = [r.strip().lower() for r in match.group(1).split(",")]
        return any(self._rule_matches(r) for r in rules)

    def _rule_matches(self, rule_pattern: str) -> bool:
        """Check if rule pattern matches this rule.

        Args:
            rule_pattern: Rule pattern to check

        Returns:
            True if pattern matches this rule
        """
        rule_id_lower = self.rule_id.lower()
        pattern_lower = rule_pattern.lower()

        # Exact match
        if rule_id_lower == pattern_lower:
            return True

        # Prefix match: collection-pipeline matches collection-pipeline.embedded-filter
        if rule_id_lower.startswith(pattern_lower + "."):
            return True

        # Wildcard match: collection-pipeline.* matches collection-pipeline.embedded-filter
        if pattern_lower.endswith("*"):
            prefix = pattern_lower[:-1]
            return rule_id_lower.startswith(prefix)

        return False

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

        return self._filter_matches_to_violations(matches, config, context)

    def _filter_matches_to_violations(
        self,
        matches: list[PatternMatch],
        config: CollectionPipelineConfig,
        context: BaseLintContext,
    ) -> list[Violation]:
        """Filter matches by threshold and ignore rules.

        Args:
            matches: Detected pattern matches
            config: Configuration with thresholds
            context: Lint context

        Returns:
            List of violations after filtering
        """
        violations: list[Violation] = []
        for match in matches:
            violation = self._process_match(match, config, context)
            if violation:
                violations.append(violation)
        return violations

    def _process_match(
        self,
        match: PatternMatch,
        config: CollectionPipelineConfig,
        context: BaseLintContext,
    ) -> Violation | None:
        """Process a single match into a violation if applicable.

        Args:
            match: Pattern match to process
            config: Configuration with thresholds
            context: Lint context

        Returns:
            Violation if match should be reported, None otherwise
        """
        if len(match.conditions) < config.min_continues:
            return None

        violation = self._create_violation(match, context)
        if self._should_ignore_violation(violation, match.line_number, context):
            return None

        return violation

    def _should_ignore_violation(
        self, violation: Violation, line_num: int, context: BaseLintContext
    ) -> bool:
        """Check if violation should be ignored.

        Args:
            violation: Violation to check
            line_num: Line number of the violation
            context: Lint context

        Returns:
            True if violation should be ignored
        """
        if not context.file_content:
            return False

        # Check using IgnoreDirectiveParser for comprehensive ignore checking
        if self._ignore_parser.should_ignore_violation(violation, context.file_content):
            return True

        # Also check inline ignore on loop line
        return self._has_inline_ignore(line_num, context)

    def _has_inline_ignore(self, line_num: int, context: BaseLintContext) -> bool:
        """Check for inline ignore directive on loop line.

        Args:
            line_num: Line number to check
            context: Lint context

        Returns:
            True if line has ignore directive
        """
        line = self._get_line_text(line_num, context)
        if not line:
            return False

        return self._is_ignore_directive(line.lower())

    def _get_line_text(self, line_num: int, context: BaseLintContext) -> str | None:
        """Get text of a specific line.

        Args:
            line_num: Line number (1-indexed)
            context: Lint context

        Returns:
            Line text or None if invalid
        """
        if not context.file_content:
            return None

        lines = context.file_content.splitlines()
        if line_num <= 0 or line_num > len(lines):
            return None

        return lines[line_num - 1]

    def _is_ignore_directive(self, line: str) -> bool:
        """Check if line contains ignore directive for this rule.

        Args:
            line: Line text (lowercase)

        Returns:
            True if line has applicable ignore directive
        """
        if "thailint:" not in line or "ignore" not in line:
            return False

        # General ignore (no rule specified)
        if "ignore[" not in line:
            return True

        # Rule-specific ignore
        return self._matches_rule_ignore(line, "ignore")

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
