"""
Purpose: Split a Suppressions section into rule ID and justification pairs

Scope: Line grouping and entry splitting for file header Suppressions sections

Overview: Provides the line-grouping logic used to turn the raw text of a Suppressions
    section into discrete entries. Groups wrapped justification prose with the entry it
    belongs to, so that a continuation line is never mistaken for a new suppression, and
    splits each entry on the first colon that is followed by whitespace, so that rule IDs
    containing colons stay intact while justification prose may contain colons freely.
    Recognizes bullet markers and indentation to decide where one entry ends and the next
    begins, and strips JSDoc comment prefixes when the whole section carries them.

Dependencies: re for pattern matching, dataclasses for the internal entry accumulator

Exports: split_entries

Interfaces: split_entries(section: str) -> list[tuple[str, str]]

Implementation: Single pass over section lines accumulating entries, with bullet and
    indentation heuristics distinguishing entry starts from wrapped continuation lines
"""

import re
from dataclasses import dataclass, field

# Matches an entry line: optional bullet, a rule ID, then a colon followed by justification.
# The rule ID may contain colons that are immediately followed by a non-space character
# (type:ignore[arg-type]), so the split happens at the first colon followed by whitespace.
ENTRY_PATTERN = re.compile(
    r"^(?P<indent>[ \t]*)(?:(?P<bullet>[-*•])[ \t]+)?"
    r"(?P<rule>\S(?:[^:]|:(?=\S))*):(?:[ \t]+(?P<text>.*))?$"
)

# Matches the leading comment prefix of a JSDoc line (" * ")
JSDOC_PREFIX = re.compile(r"^[ \t]*\*[ \t]?")


@dataclass
class _Entry:
    """A single suppression entry being accumulated across lines."""

    rule_id: str
    indent: int
    bulleted: bool
    lines: list[str] = field(default_factory=list)


def split_entries(section: str) -> list[tuple[str, str]]:
    """Split a Suppressions section into (rule_id, justification) pairs.

    Args:
        section: Raw text of the Suppressions section.

    Returns:
        List of (rule_id, justification) tuples in declaration order. Rule IDs keep
        their original case; wrapped justifications are joined into a single string.
    """
    entries: list[_Entry] = []
    for line in _strip_jsdoc(section.splitlines()):
        _consume_line(line, entries)
    return [(entry.rule_id, " ".join(entry.lines).strip()) for entry in entries]


def _strip_jsdoc(lines: list[str]) -> list[str]:
    """Remove JSDoc comment prefixes when every content line carries one."""
    if not _is_jsdoc_block(lines):
        return lines
    return [JSDOC_PREFIX.sub("", line) for line in lines]


def _is_jsdoc_block(lines: list[str]) -> bool:
    """Check whether every non-blank line starts with a JSDoc comment prefix."""
    content = [line for line in lines if line.strip()]
    return bool(content) and all(JSDOC_PREFIX.match(line) for line in content)


def _consume_line(line: str, entries: list[_Entry]) -> None:
    """Add a line to the entry list, either starting an entry or continuing one."""
    stripped = line.strip()
    if not stripped:
        return

    match = _entry_start_match(line, entries)
    if match is not None:
        entries.append(_new_entry(match))
    elif entries:
        entries[-1].lines.append(stripped)


def _entry_start_match(line: str, entries: list[_Entry]) -> re.Match[str] | None:
    """Return the match for a line that starts a new entry, or None for a continuation."""
    match = ENTRY_PATTERN.match(line)
    if match is None:
        return None
    if not entries:
        return match
    return match if _starts_new_entry(match, entries[-1]) else None


def _starts_new_entry(match: re.Match[str], current: _Entry) -> bool:
    """Decide whether an entry-shaped line starts a new entry or wraps the current one.

    A bullet marker always starts an entry. A line indented no deeper than the current
    entry starts one too. A deeper line wraps a bulleted entry, and otherwise starts an
    entry only when its rule ID is a single token, since wrapped prose contains spaces.
    """
    if match.group("bullet"):
        return True
    if len(match.group("indent")) <= current.indent:
        return True
    if current.bulleted:
        return False
    return not _contains_whitespace(match.group("rule"))


def _contains_whitespace(text: str) -> bool:
    """Check whether text contains any whitespace character."""
    return any(char.isspace() for char in text)


def _new_entry(match: re.Match[str]) -> _Entry:
    """Build an entry accumulator from an entry-start match."""
    text = match.group("text")
    return _Entry(
        rule_id=match.group("rule").strip(),
        indent=len(match.group("indent")),
        bulleted=bool(match.group("bullet")),
        lines=[text.strip()] if text else [],
    )
