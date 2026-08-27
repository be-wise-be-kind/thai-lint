"""
Purpose: Detects comment phrases whose referent is a change rather than the code in the tree

Scope: Phrase matching over mid-file comment blocks

Overview: Implements the phrase detection behind the comment-antecedents rule. Two patterns survived
    validation against three corpora: a past-tense copula describing a state the tree no longer holds,
    and a pre-change anchor paired with an existence verb. Both were selected because neither can
    describe an action code performs while running, which is what separates them from the change verbs
    that were measured and rejected. A habitual-past tier was built and measured at 82% precision on
    open-source code, then removed rather than shipped disabled; the measurement is recorded in the
    feature's AI_CONTEXT so it is not rebuilt.

Dependencies: re for pattern matching

Exports: detect_default_tier function, FORMER_STATE and PRE_CHANGE_STATE patterns

Interfaces: detect_default_tier(text) -> str | None, returning the matched phrase or None

Implementation: Pre-compiled regex patterns with a single passive-voice gate on the copula pattern
"""

import re

# The passive gate below is the only grammar check applied, and it earns its place:
# "16 bytes are used to be sure to cover all alignments" reads as "used in order to be",
# not as habitual past. A clause-initial gate was measured too and rejected — it would discard
# genuine findings that open a comment, such as "Used to be mask, now it's recordmask".
FORMER_STATE = re.compile(r"\bused to be\b", re.IGNORECASE)

PRE_CHANGE_STATE = re.compile(
    r"\bbefore this \w+ (?:existed|exists|was|were|went live|declared|landed|shipped)\b"
    r"|\bbefore this (?:change|commit|PR|diff)\b",
    re.IGNORECASE,
)

_PASSIVE_SENSE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|not|also|only|can be|could be|to be)\s+used to\b",
    re.IGNORECASE,
)


def detect_default_tier(text: str) -> str | None:
    """Return the matched phrase in a comment block, or None.

    Args:
        text: Comment block text with markers already stripped.

    Returns:
        The matched phrase, or None when the block carries no matching phrase.
    """
    pre_change = PRE_CHANGE_STATE.search(text)
    if pre_change:
        return pre_change.group(0)

    former = FORMER_STATE.search(text)
    if former and not _PASSIVE_SENSE.search(text):
        return former.group(0)
    return None
