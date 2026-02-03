"""
Purpose: Rust blocking-in-async detector package exports

Scope: Detect blocking operations inside async functions in Rust code and suggest alternatives

Overview: Package providing blocking-in-async detection for Rust code. Identifies std::fs I/O
    operations, std::thread::sleep calls, and blocking std::net operations inside async functions.
    Suggests async-compatible alternatives including tokio::fs, tokio::time::sleep, and tokio::net
    equivalents. Supports configuration for allowing calls in test code, toggling individual
    pattern detection, and ignoring specific directories. Uses tree-sitter for accurate
    AST-based detection of async function contexts.

Dependencies: tree-sitter-rust (optional) for AST parsing, src.core for base classes

Exports: BlockingAsyncConfig, BlockingAsyncRule, RustBlockingAsyncAnalyzer, BlockingCall

Interfaces: BlockingAsyncConfig.from_dict() for YAML configuration loading

Implementation: Tree-sitter AST-based async context detection with blocking API pattern matching
"""

from .config import BlockingAsyncConfig
from .linter import BlockingAsyncRule
from .rust_analyzer import BlockingCall, RustBlockingAsyncAnalyzer

__all__ = [
    "BlockingAsyncConfig",
    "BlockingAsyncRule",
    "RustBlockingAsyncAnalyzer",
    "BlockingCall",
]
