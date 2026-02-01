"""
Purpose: Rust clone abuse detector package exports

Scope: Detect .clone() abuse patterns in Rust code and suggest safer alternatives

Overview: Package providing clone abuse detection for Rust code. Identifies .clone() calls
    in loop bodies, chained .clone().clone() calls, and unnecessary clones where the source
    is not used after cloning. Suggests safer alternatives including borrowing, Rc/Arc for
    shared ownership, and Cow for clone-on-write patterns. Supports configuration for allowing
    calls in test code, toggling individual pattern detection, and ignoring specific directories.
    Uses tree-sitter for accurate AST-based detection.

Dependencies: tree-sitter-rust (optional) for AST parsing, src.core for base classes

Exports: CloneAbuseConfig, CloneAbuseRule, RustCloneAnalyzer, CloneCall

Interfaces: CloneAbuseConfig.from_dict() for YAML configuration loading

Implementation: Tree-sitter AST-based pattern detection with configurable filtering
"""

from .config import CloneAbuseConfig
from .linter import CloneAbuseRule
from .rust_analyzer import CloneCall, RustCloneAnalyzer

__all__ = [
    "CloneAbuseConfig",
    "CloneAbuseRule",
    "RustCloneAnalyzer",
    "CloneCall",
]
