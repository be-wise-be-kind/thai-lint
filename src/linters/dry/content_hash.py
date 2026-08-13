"""
Purpose: Stable whole-file content hashing for persistent cache freshness checks

Scope: Single function computing a deterministic hash of a file's full content

Overview: Computes a stable hash of a file's content, used to detect whether a file indexed by
    a prior run has since changed on disk (DRYCache.needs_rescan). Distinct from
    token_hasher.stable_hash, which hashes individual code-block snippets for duplicate matching
    - this hashes an entire file's content as one unit, for cache freshness only.

Dependencies: hashlib (stdlib)

Exports: compute_content_hash function

Interfaces: compute_content_hash(content: str) -> str

Implementation: blake2b digest, hex-encoded for storage in a TEXT column
"""

import hashlib


def compute_content_hash(content: str) -> str:
    """Compute a stable hash of a file's full content.

    Args:
        content: File content to hash

    Returns:
        Hex-encoded blake2b digest of the content
    """
    return hashlib.blake2b(content.encode("utf-8")).hexdigest()
