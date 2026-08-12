"""
Purpose: Regression test for block filters re-splitting the whole file per block (issue #233)

Scope: PythonDuplicateAnalyzer.analyze line-splitting when block filters evaluate blocks

Overview: Guards against a second O(blocks x filesize) blow-up in the same family as issue #233:
    every BaseBlockFilter.should_filter implementation (KeywordArgumentFilter, ImportGroupFilter,
    LoggerCallFilter, ExceptionReraiseFilter) called file_content.split("\\n") independently on
    every candidate block, splitting the entire file's content once per block per filter instead
    of once per file. Verifies analyze() splits a file's content into lines a single time and
    reuses that list across every filter's every block check, by counting str.split calls (via a
    str subclass, since the built-in type cannot be patched directly) during one analyze() run on
    an input with many candidate blocks.

Dependencies: pytest, pathlib.Path, src.linters.dry.config, src.linters.dry.python_analyzer

Exports: TestBlockFilterSplitOnce test class

Interfaces: Tests PythonDuplicateAnalyzer.analyze(file_path, content, config) -> list[CodeBlock]

Implementation: Passes a str subclass instance as file content that counts calls to its own
    split() method, then asserts the count stays small independent of block count
"""

from pathlib import Path

from src.linters.dry.config import DRYConfig
from src.linters.dry.python_analyzer import PythonDuplicateAnalyzer

# Enough keyword-shaped attribute groups to generate many rolling-hash windows,
# each of which is currently re-split by every registered block filter.
MANY_GROUPS = 50


class _CountingStr(str):
    """str subclass that counts calls to split() (built-in str can't be patched)."""

    def __new__(cls, value: str) -> "_CountingStr":
        instance = super().__new__(cls, value)
        instance.split_calls = 0
        return instance

    def split(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self.split_calls += 1
        return super().split(*args, **kwargs)


def _build_source(n: int) -> str:
    """Build Python source with many single-line "key = value" attribute groups."""
    lines = ["class Config:", "    def _dummy():", "        pass", ""]
    for i in range(n):
        lines.append(f'    message_{i} = "value_{i}"')
        lines.append(f'    severity_{i} = "ERROR"')
        lines.append(f'    suggestion_{i} = "fix_{i}"')
    return "\n".join(lines)


class TestBlockFilterSplitOnce:
    """Block filters must not re-split the whole file's content per candidate block."""

    def test_analyze_splits_content_a_constant_number_of_times(self) -> None:
        """analyze() must not re-split file content once per block per filter."""
        content = _CountingStr(_build_source(MANY_GROUPS))
        analyzer = PythonDuplicateAnalyzer()
        config = DRYConfig(enabled=True, min_duplicate_lines=3)

        analyzer.analyze(Path("big.py"), content, config)

        # A small constant number of splits is expected (line tokenization plus a
        # couple of incidental uses). The previous code split the whole file once
        # per block per registered filter (hundreds of times here).
        assert content.split_calls <= 5, (
            f"expected a constant number of splits, got {content.split_calls}"
        )
