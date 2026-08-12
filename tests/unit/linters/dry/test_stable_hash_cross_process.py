"""
Purpose: Regression test proving block hashes must be stable across process boundaries

Scope: token_hasher.rolling_hash (and, by extension, python_analyzer/typescript_analyzer,
    which duplicate the same hashing logic)

Overview: Guards against a bug found while planning persistent DRY caching: rolling_hash uses
    Python's built-in hash(snippet), which salts string hashing with a per-process random seed
    (PYTHONHASHSEED) by default. That is harmless for today's single-process, single-run
    behavior, but fatal for any cache meant to be read back by a different process invocation -
    the same code block would get a different hash_value every time, so cross-run duplicate
    matching could never work. Verifies the same snippet hashes identically across independent
    Python subprocess invocations (not forked children, which would inherit the parent's seed
    and mask this bug - see the real subprocess spawn below).

Dependencies: pytest, subprocess, sys, src.linters.dry.token_hasher.rolling_hash

Exports: TestStableHashAcrossProcesses test class

Interfaces: Exercises token_hasher.rolling_hash(lines, window_size)

Implementation: Spawns three separate `python -c` subprocesses (each gets an independent random
    hash seed by default), computes rolling_hash on the same snippet in each, and asserts all
    three produce the identical hash_value
"""

import subprocess
import sys

_SNIPPET_LINES = ["def handler():", "    value = compute(1)", "    return value"]
_WINDOW_SIZE = len(_SNIPPET_LINES)

_SUBPROCESS_CODE = f"""
import sys
sys.path.insert(0, ".")
from src.linters.dry.token_hasher import rolling_hash
hashes = rolling_hash({_SNIPPET_LINES!r}, {_WINDOW_SIZE})
print(hashes[0][0])
"""


def _hash_in_fresh_subprocess() -> int:
    """Compute rolling_hash's hash_value for the fixture snippet in a brand-new process."""
    result = subprocess.run(
        [sys.executable, "-c", _SUBPROCESS_CODE],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout.strip())


class TestStableHashAcrossProcesses:
    """rolling_hash's hash_value must be a pure function of content, not of process identity."""

    def test_hash_value_matches_across_independent_process_invocations(self) -> None:
        """The same snippet must hash identically across separate Python process invocations."""
        hashes = [_hash_in_fresh_subprocess() for _ in range(3)]

        assert len(set(hashes)) == 1, (
            f"hash_value differed across independent process invocations: {hashes} - "
            "this means the same code block would never match itself in a persistent, "
            "cross-run duplicate index"
        )
