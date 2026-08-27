"""
Purpose: Lint rule flagging mid-file comments whose referent is a change rather than the code

Scope: Comment prose below a file's header block, across hash-comment and slash-comment languages

Overview: Implements the comment-antecedents rule as a second rule inside the file header package. Where
    the header rule validates the prose above a file's first statement, this rule reads the prose below it
    and reports comments that describe the change which produced the code instead of the code itself. Such
    a comment cannot be evaluated by a reader holding the merged file, because its referent exists only in
    a diff that is no longer reachable. Reporting is per comment block rather than per line so that a
    wrapped paragraph yields one violation. The rule selects files by suffix rather than by detected
    language, which lets it read configuration formats the orchestrator classifies as unknown without
    altering what any other registered rule sees.

Dependencies: BaseLintRule and BaseLintContext from core, Violation and Severity from core types,
    comment_block_extractor for block grouping, antecedent_detector for phrase matching,
    FileHeaderConfig for settings, ignore engine for suppression

Exports: CommentAntecedentRule class

Interfaces: CommentAntecedentRule.check(context) -> list[Violation]

Implementation: Composition over the extractor and detector modules, with suffix gating, path ignore
    patterns, and the shared five-scope ignore engine applied before violations are returned
"""

from dataclasses import replace

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import is_ignored_path
from src.core.types import Severity, Violation
from src.linter_config.ignore import get_ignore_parser

from .antecedent_detector import detect_default_tier, detect_strict_tier
from .comment_block_extractor import (
    HASH_SUFFIXES,
    SLASH_SUFFIXES,
    CommentBlock,
    extract_comment_blocks,
)
from .config import FileHeaderConfig

SUPPORTED_SUFFIXES = HASH_SUFFIXES | SLASH_SUFFIXES

DEFAULT_VENDOR_IGNORES = [
    "**/node_modules/**",
    "node_modules/**",
    "**/vendor/**",
    "vendor/**",
    "**/site-packages/**",
    "**/dist/**",
    "**/.terragrunt-cache/**",
    "**/*.min.js",
]


class CommentAntecedentRule(BaseLintRule):
    """Detects mid-file comments describing a change rather than the code."""

    def __init__(self) -> None:
        """Initialize the rule with the shared ignore parser."""
        self._ignore_parser = get_ignore_parser()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "file-header.comment-antecedents"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Comment Antecedent Detection"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Comments must describe the code, not the change that produced it"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check mid-file comments for unresolvable antecedents.

        Args:
            context: Lint context with file information.

        Returns:
            List of violations, one per offending comment block.
        """
        if not self._is_analysable(context):
            return []

        config = self._load_config(context)
        if not config.check_comment_antecedents:
            return []
        if self._is_ignored_path(context, config):
            return []

        blocks = extract_comment_blocks(
            context.file_content or "", self._suffix_of(context).lower()
        )
        found = self._violations_for(blocks, context, config)
        return self._filter_suppressed(found, context)

    def _is_analysable(self, context: BaseLintContext) -> bool:
        """Whether the file's suffix is one this rule reads."""
        return bool(context.file_path) and self._suffix_of(context).lower() in SUPPORTED_SUFFIXES

    @staticmethod
    def _suffix_of(context: BaseLintContext) -> str:
        """Return the file suffix, treating a justfile name as its own suffix."""
        path = context.file_path
        if path is None:
            return ""
        return ".just" if path.name.endswith(".just") else path.suffix

    @staticmethod
    def _load_config(context: BaseLintContext) -> FileHeaderConfig:
        """Load file header configuration from the context."""
        metadata = getattr(context, "metadata", None)
        section = metadata.get("file_header") if isinstance(metadata, dict) else None
        if not isinstance(section, dict):
            return FileHeaderConfig()
        return FileHeaderConfig.from_dict(section, context.language)

    @staticmethod
    def _is_ignored_path(context: BaseLintContext, config: FileHeaderConfig) -> bool:
        """Whether the path matches a configured or default vendored ignore pattern."""
        path = str(context.file_path)
        return is_ignored_path(path, list(config.ignore) + DEFAULT_VENDOR_IGNORES)

    def _violations_for(
        self, blocks: list[CommentBlock], context: BaseLintContext, config: FileHeaderConfig
    ) -> list[tuple[Violation, CommentBlock]]:
        """Build one violation per offending comment block, paired with its block."""
        found = []
        for block in blocks:
            phrase = self._matched_phrase(block.text, config)
            if phrase:
                violation = self._build_violation(phrase, context, block.start_line)
                found.append((violation, block))
        return found

    @staticmethod
    def _matched_phrase(text: str, config: FileHeaderConfig) -> str | None:
        """Return the offending phrase in a block, honouring the strict-tier setting."""
        phrase = detect_default_tier(text)
        if phrase or not config.comment_antecedents_strict:
            return phrase
        return detect_strict_tier(text)

    def _build_violation(self, phrase: str, context: BaseLintContext, line: int) -> Violation:
        """Build a violation naming the offending phrase."""
        return Violation(
            rule_id=self.rule_id,
            message=(
                f'Comment antecedent does not resolve in the tree: "{phrase}". '
                "The referent exists only in the change that produced this code."
            ),
            file_path=str(context.file_path or ""),
            line=line,
            column=1,
            severity=Severity.ERROR,
            suggestion="Describe what the code does, not what changed to produce it",
        )

    def _filter_suppressed(
        self, found: list[tuple[Violation, CommentBlock]], context: BaseLintContext
    ) -> list[Violation]:
        """Drop violations suppressed by any ignore scope on any line of their block."""
        content = context.file_content or ""
        return [v for v, block in found if not self._is_suppressed(v, block, content)]

    def _is_suppressed(self, violation: Violation, block: CommentBlock, content: str) -> bool:
        """Whether any line of the block carries a directive suppressing this violation.

        A block is reported at its first line, but the phrase can sit on any line of it, and
        that is where a reader writes the inline directive.
        """
        lines = range(block.start_line, block.end_line + 1)
        probes = (replace(violation, line=line) for line in lines)
        return any(self._ignore_parser.should_ignore_violation(p, content) for p in probes)
