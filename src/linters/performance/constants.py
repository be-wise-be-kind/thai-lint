"""
Purpose: Shared constants for performance linter rules

Scope: Common patterns and constants used across Python and TypeScript analyzers

Overview: Provides shared constants for the performance linter, including variable
    name patterns that suggest string building. Used by both PythonStringConcatAnalyzer
    and TypeScriptStringConcatAnalyzer to detect likely string concatenation.

Dependencies: None

Exports: STRING_VARIABLE_PATTERNS, LOOP_NODE_TYPES_TS

Interfaces: Frozen sets of patterns

Implementation: Constants shared between analyzers
"""

# Variable names that suggest string building
STRING_VARIABLE_PATTERNS = frozenset(
    {
        "result",
        "output",
        "message",
        "msg",
        "text",
        "html",
        "content",
        "body",
        "buffer",
        "response",
        "data",
        "line",
        "lines",
        "string",
        "str",
        "s",
    }
)

# Tree-sitter node types for loops (TypeScript)
LOOP_NODE_TYPES_TS = frozenset(
    {
        "for_statement",
        "for_in_statement",
        "while_statement",
        "do_statement",
    }
)
