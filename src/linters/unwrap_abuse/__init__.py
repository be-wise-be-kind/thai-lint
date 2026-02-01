"""
Purpose: Rust unwrap abuse detector package exports

Scope: Detect .unwrap() and .expect() abuse in Rust code and suggest safer alternatives

Overview: Package providing unwrap/expect abuse detection for Rust code. Identifies .unwrap()
    and .expect() calls outside test code that may panic at runtime. Suggests safer alternatives
    including the ? operator, unwrap_or(), unwrap_or_default(), and match/if-let expressions.
    Supports configuration for allowing calls in test code, example files, and benchmark
    directories. Uses tree-sitter for accurate AST-based detection.

Dependencies: tree-sitter-rust (optional) for AST parsing, src.core for base classes

Exports: UnwrapAbuseConfig, UnwrapAbuseRule, RustUnwrapAnalyzer, UnwrapCall

Interfaces: UnwrapAbuseConfig.from_dict() for YAML configuration loading

Implementation: Tree-sitter AST-based pattern detection with configurable filtering
"""

from .config import UnwrapAbuseConfig
from .linter import UnwrapAbuseRule
from .rust_analyzer import RustUnwrapAnalyzer, UnwrapCall

__all__ = [
    "UnwrapAbuseConfig",
    "UnwrapAbuseRule",
    "RustUnwrapAnalyzer",
    "UnwrapCall",
]
