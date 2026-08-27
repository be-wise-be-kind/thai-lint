"""
Purpose: Detects comment phrases whose referent is a change rather than the code in the tree

Scope: Phrase matching over mid-file comment blocks, covering a default tier and an opt-in strict tier

Overview: Implements the phrase detection behind the comment-antecedents rule. The default tier holds two
    patterns that survived validation against three corpora: a past-tense copula describing a state the
    tree no longer holds, and a pre-change anchor paired with an existence verb. Both were selected because
    neither can describe an action code performs while running, which is what separates them from the
    change verbs that were measured and rejected. The strict tier adds habitual-past detection, gated by
    grammar checks that exclude the passive and purposive senses of the same phrase and by a proximity
    requirement on a nearby contrast word. Strict detection measured below the project's precision
    threshold on open-source code, so callers enable it deliberately rather than by default.

Dependencies: re for pattern matching

Exports: detect_default_tier, detect_strict_tier functions

Interfaces: detect_default_tier(text) -> str | None and detect_strict_tier(text) -> str | None, each
    returning the matched phrase or None

Implementation: Pre-compiled regex patterns with a character-window proximity check for the strict tier
"""

import re

CONTRAST_WINDOW = 80

# The passive gate below is the only grammar check the default tier applies, and it earns its
# place: "16 bytes are used to be sure to cover all alignments" reads as "used in order to be",
# not as habitual past. A clause-initial gate was measured too and rejected — it would discard
# genuine findings that open a comment, such as "Used to be mask, now it's recordmask".
FORMER_STATE = re.compile(r"\bused to be\b", re.IGNORECASE)

PRE_CHANGE_STATE = re.compile(
    r"\bbefore this \w+ (?:existed|exists|was|were|went live|declared|landed|shipped)\b"
    r"|\bbefore this (?:change|commit|PR|diff)\b",
    re.IGNORECASE,
)

_HABITUAL_PAST = re.compile(r"\bused to\b", re.IGNORECASE)
_PASSIVE_SENSE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|not|also|only|can be|could be|to be)\s+used to\b",
    re.IGNORECASE,
)
_CLAUSE_INITIAL = re.compile(r"(?:^|[.;:]\s+|—\s+|\(\s*|-\s+)used to\b", re.IGNORECASE)
_COMMA_PRECEDED = re.compile(r",\s*used to\b", re.IGNORECASE)
_CONTRAST = re.compile(
    r"\b(?:now|no longer|instead|rather than|today|which meant)\b", re.IGNORECASE
)


def detect_default_tier(text: str) -> str | None:
    """Return the matched default-tier phrase in a comment block, or None.

    Args:
        text: Comment block text with markers already stripped.

    Returns:
        The matched phrase, or None when the block carries no default-tier phrase.
    """
    pre_change = PRE_CHANGE_STATE.search(text)
    if pre_change:
        return pre_change.group(0)

    former = FORMER_STATE.search(text)
    if former and not _PASSIVE_SENSE.search(text):
        return former.group(0)
    return None


def _has_nearby_contrast(text: str) -> bool:
    """Whether a contrast word sits within the proximity window of a habitual-past phrase."""
    for match in _HABITUAL_PAST.finditer(text):
        start = max(0, match.start() - CONTRAST_WINDOW)
        end = min(len(text), match.end() + CONTRAST_WINDOW)
        if _CONTRAST.search(text[start:end]):
            return True
    return False


def _is_purposive_sense(text: str) -> bool:
    """Whether the phrase reads as 'utilised to' rather than habitual past."""
    return bool(
        _PASSIVE_SENSE.search(text) or _CLAUSE_INITIAL.search(text) or _COMMA_PRECEDED.search(text)
    )


def detect_strict_tier(text: str) -> str | None:
    """Return the matched habitual-past phrase in a comment block, or None.

    Args:
        text: Comment block text with markers already stripped.

    Returns:
        The matched phrase, or None when the block carries no habitual-past phrase that
        clears the grammar and proximity gates.
    """
    match = _HABITUAL_PAST.search(text)
    if not match or _is_purposive_sense(text):
        return None
    if not _has_nearby_contrast(text):
        return None
    return match.group(0)
