"""
Purpose: Extracts contiguous mid-file comment blocks from source files below the header block

Scope: Lexical comment scanning for hash-comment and slash-comment languages

Overview: Groups runs of adjacent comment lines into blocks so that the comment-antecedents rule
    reports once per prose paragraph rather than once per line. Skips whatever the file uses as its
    header so that header prose stays the concern of header validation: for Python that is the module
    docstring, and for every other supported suffix it is the leading contiguous comment run after any
    shebang. A blank line or a line of code closes the current block. Comment markers and surrounding
    whitespace are stripped, and the remaining text is joined with single spaces so that phrase matching
    works across a wrapped sentence.

Dependencies: dataclasses for the CommentBlock record, itertools.groupby for run grouping

Exports: CommentBlock dataclass, extract_comment_blocks function, HASH_SUFFIXES, SLASH_SUFFIXES

Interfaces: extract_comment_blocks(content: str, suffix: str) -> list[CommentBlock]

Implementation: Single forward pass over lines with a header-skip offset computed per comment family,
    accumulating adjacent comment lines into blocks
"""

from collections.abc import Iterator
from dataclasses import dataclass
from itertools import groupby

HASH_SUFFIXES = frozenset(
    {".py", ".sh", ".bash", ".yaml", ".yml", ".tf", ".hcl", ".just", ".toml", ".cfg"}
)
SLASH_SUFFIXES = frozenset({".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"})

_DOCSTRING_QUOTES = ('"""', "'''")


@dataclass(frozen=True)
class CommentBlock:
    """A run of adjacent comment lines below a file's header block."""

    start_line: int
    text: str


def _marker_for(suffix: str) -> str | None:
    """Return the line comment marker for a suffix, or None when unsupported."""
    if suffix in HASH_SUFFIXES:
        return "#"
    if suffix in SLASH_SUFFIXES:
        return "//"
    return None


def _first_content_index(lines: list[str]) -> int:
    """Index of the first line that is neither blank nor a shebang."""
    index = 0
    while index < len(lines) and (not lines[index].strip() or lines[index].startswith("#!")):
        index += 1
    return index


def _docstring_end(lines: list[str], start: int) -> int:
    """Index just past a module docstring beginning at start."""
    opening = lines[start].lstrip()
    quote = opening[:3]
    if opening.count(quote) >= 2 and len(opening.strip()) > 3:
        return start + 1
    for index in range(start + 1, len(lines)):
        if quote in lines[index]:
            return index + 1
    return len(lines)


def _python_header_end(lines: list[str]) -> int:
    """Index just past a Python module docstring, or the first content line."""
    start = _first_content_index(lines)
    if start < len(lines) and lines[start].lstrip().startswith(_DOCSTRING_QUOTES):
        return _docstring_end(lines, start)
    return start


def _comment_header_end(lines: list[str], marker: str) -> int:
    """Index just past a leading contiguous comment run."""
    start = _first_content_index(lines)
    index = start
    while index < len(lines) and lines[index].lstrip().startswith(marker):
        index += 1
    return index if index > start else start


def _header_end(lines: list[str], suffix: str, marker: str) -> int:
    """Index of the first line below the file's header block."""
    if suffix == ".py":
        return _python_header_end(lines)
    return _comment_header_end(lines, marker)


_DIRECTIVE_PREFIXES = ("thailint:", "thailint-ignore", "design-lint:", "noqa", "type: ignore")


def _is_directive_only(text: str) -> bool:
    """Whether a comment line carries only a linter directive rather than prose.

    Such a line must not join the block it annotates, or a preceding-line suppression would
    anchor the block to the directive's own line and never match.
    """
    return text.lower().startswith(_DIRECTIVE_PREFIXES)


def _comment_text(line: str, marker: str) -> str | None:
    """Strip the comment marker from a line, or None when the line is not prose."""
    stripped = line.strip()
    if not stripped.startswith(marker):
        return None
    text = stripped[len(marker) :].strip()
    return None if _is_directive_only(text) else text


def _prose_lines(lines: list[str], marker: str, body_start: int) -> list[tuple[int, str]]:
    """Numbered prose comment lines below the header, directives excluded."""
    numbered = enumerate(lines[body_start:], start=body_start + 1)
    candidates = ((number, _comment_text(line, marker)) for number, line in numbered)
    return [(number, text) for number, text in candidates if text is not None]


def _run_key(item: tuple[int, tuple[int, str]]) -> int:
    """Group key that is constant across a run of consecutive line numbers."""
    index, (line_number, _text) = item
    return line_number - index


def _block_from(run: Iterator[tuple[int, tuple[int, str]]]) -> CommentBlock:
    """Build one block from a run of consecutive prose comment lines."""
    entries = [entry for _, entry in run]
    return CommentBlock(entries[0][0], " ".join(text for _, text in entries))


def extract_comment_blocks(content: str, suffix: str) -> list[CommentBlock]:
    """Extract contiguous mid-file comment blocks from source content.

    Args:
        content: Full text of the source file.
        suffix: File suffix used to select the comment marker and header handling.

    Returns:
        Comment blocks below the header block, in file order. Empty when the suffix is
        unsupported or the file holds no mid-file comments.
    """
    marker = _marker_for(suffix)
    if marker is None or not content:
        return []

    lines = content.split("\n")
    prose = _prose_lines(lines, marker, _header_end(lines, suffix, marker))
    return [_block_from(run) for _, run in groupby(enumerate(prose), _run_key)]
